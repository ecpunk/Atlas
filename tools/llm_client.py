from __future__ import annotations

import fcntl
import json
import logging
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

_FALLBACK_MODELS = ("claude-sonnet-4-6", "claude-sonnet-4-5")
_MODEL_PRICING_USD_PER_MTOKEN = {
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
}
_DEFAULT_MAX_USD = 1.00
_DEFAULT_DAILY_MAX_USD = 3.00
_SPEND_FILE = Path(__file__).parent.parent / ".atlas-spend.json"

_LOGGER = logging.getLogger("atlas.llm_client")
if not _LOGGER.handlers:
    _HANDLER = logging.StreamHandler(sys.stderr)
    _HANDLER.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    _LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)


def _load_max_usd() -> float:
    raw_value = (os.environ.get("ATLAS_LLM_MAX_USD") or "").strip()
    if not raw_value:
        return _DEFAULT_MAX_USD

    try:
        parsed = float(raw_value)
    except ValueError:
        _LOGGER.warning(
            "Invalid ATLAS_LLM_MAX_USD=%r; falling back to %.2f",
            raw_value,
            _DEFAULT_MAX_USD,
        )
        return _DEFAULT_MAX_USD

    if parsed <= 0:
        _LOGGER.warning(
            "Non-positive ATLAS_LLM_MAX_USD=%.4f; falling back to %.2f",
            parsed,
            _DEFAULT_MAX_USD,
        )
        return _DEFAULT_MAX_USD

    return parsed


_ATLAS_LLM_MAX_USD = _load_max_usd()
_cost_tracker: dict[str, int | float] = {"tokens_in": 0, "tokens_out": 0, "est_usd": 0.0}
_LOGGER.info("Loaded ATLAS_LLM_MAX_USD=%.2f", _ATLAS_LLM_MAX_USD)


def _load_daily_max_usd() -> float:
    raw_value = (os.environ.get("ATLAS_LLM_DAILY_MAX_USD") or "").strip()
    if not raw_value:
        return _DEFAULT_DAILY_MAX_USD
    try:
        parsed = float(raw_value)
    except ValueError:
        _LOGGER.warning(
            "Invalid ATLAS_LLM_DAILY_MAX_USD=%r; falling back to %.2f",
            raw_value,
            _DEFAULT_DAILY_MAX_USD,
        )
        return _DEFAULT_DAILY_MAX_USD
    if parsed <= 0:
        _LOGGER.warning(
            "Non-positive ATLAS_LLM_DAILY_MAX_USD=%.4f; falling back to %.2f",
            parsed,
            _DEFAULT_DAILY_MAX_USD,
        )
        return _DEFAULT_DAILY_MAX_USD
    return parsed


_ATLAS_LLM_DAILY_MAX_USD = _load_daily_max_usd()
_LOGGER.info("Loaded ATLAS_LLM_DAILY_MAX_USD=%.2f", _ATLAS_LLM_DAILY_MAX_USD)


def _read_daily_spend() -> float:
    """Return accumulated spend today from the persistent spend file. Returns 0.0 if absent or stale."""
    if not _SPEND_FILE.exists():
        return 0.0
    try:
        with _SPEND_FILE.open("r", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_SH)
            try:
                data = json.load(fh)
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
        if data.get("date") != str(date.today()):
            return 0.0
        return float(data.get("accumulated_usd", 0.0))
    except Exception:  # noqa: BLE001
        return 0.0


def _update_daily_spend(usd_delta: float) -> None:
    """Add usd_delta to the persistent daily spend file, creating or resetting if needed."""
    today = str(date.today())
    try:
        # Open for read+write if file exists, else create read+write
        if _SPEND_FILE.exists():
            fh = _SPEND_FILE.open("r+", encoding="utf-8")
        else:
            fh = _SPEND_FILE.open("w+", encoding="utf-8")
        with fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                fh.seek(0)
                raw = fh.read()
                try:
                    data = json.loads(raw) if raw.strip() else {}
                except Exception:  # noqa: BLE001
                    data = {}
                if data.get("date") != today:
                    data = {"date": today, "accumulated_usd": 0.0, "call_count": 0}
                data["accumulated_usd"] = float(data.get("accumulated_usd", 0.0)) + usd_delta
                data["call_count"] = int(data.get("call_count", 0)) + 1
                fh.seek(0)
                fh.truncate()
                json.dump(data, fh, indent=2)
                fh.write("\n")
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.warning("Failed to update spend file: %s", exc)


def get_daily_spend_summary() -> dict:
    """Return today's persistent spend totals from the spend file."""
    if not _SPEND_FILE.exists():
        return {"date": str(date.today()), "accumulated_usd": 0.0, "call_count": 0}
    try:
        with _SPEND_FILE.open("r", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_SH)
            try:
                data = json.load(fh)
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
        if data.get("date") != str(date.today()):
            return {"date": str(date.today()), "accumulated_usd": 0.0, "call_count": 0}
        return data
    except Exception:  # noqa: BLE001
        return {"date": str(date.today()), "accumulated_usd": 0.0, "call_count": 0}


def _model_candidates() -> list[str]:
    override = (os.environ.get("ANTHROPIC_MODEL") or "").strip()
    if not override:
        return list(_FALLBACK_MODELS)

    ordered = [override]
    for model in _FALLBACK_MODELS:
        if model != override:
            ordered.append(model)
    return ordered


def _extract_text(response: Any) -> str:
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _parse_response_json(text: str) -> dict[str, Any]:
    payload = json.loads(_strip_code_fence(text))
    if not isinstance(payload, dict):
        raise ValueError("LLM response is not a JSON object")

    fires = bool(payload.get("fires", False))
    evidence_raw = payload.get("evidence", "")
    evidence = str(evidence_raw).strip() if evidence_raw is not None else ""

    suggested_fix_raw = payload.get("suggested_fix", None)
    if suggested_fix_raw is None:
        suggested_fix = None
    else:
        suggested_text = str(suggested_fix_raw).strip()
        suggested_fix = suggested_text if suggested_text else None

    return {
        "fires": fires,
        "evidence": evidence,
        "suggested_fix": suggested_fix,
    }


def _pricing_for_model(model: str) -> dict[str, float]:
    return _MODEL_PRICING_USD_PER_MTOKEN.get(model, _MODEL_PRICING_USD_PER_MTOKEN[_FALLBACK_MODELS[0]])


def _estimate_cost(tokens_in: int, tokens_out: int, model: str) -> float:
    pricing = _pricing_for_model(model)
    input_cost = (max(tokens_in, 0) / 1_000_000) * pricing["input"]
    output_cost = (max(tokens_out, 0) / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def _estimate_call_cost(input_tokens_estimate: int, model: str) -> float:
    pricing = _pricing_for_model(model)
    return (max(input_tokens_estimate, 0) / 1_000_000) * pricing["input"]


def get_cost_summary() -> dict[str, int | float]:
    return {
        "tokens_in": int(_cost_tracker["tokens_in"]),
        "tokens_out": int(_cost_tracker["tokens_out"]),
        "est_usd": float(_cost_tracker["est_usd"]),
        "max_usd": float(_ATLAS_LLM_MAX_USD),
    }


def evaluate_rule(system_prompt: str, user_content: str, rule_id: str) -> dict[str, Any]:
    models = _model_candidates()
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        result = {
            "fires": False,
            "evidence": "LLM error: ANTHROPIC_API_KEY not set",
            "suggested_fix": None,
            "model": models[0],
            "tokens_in": 0,
            "tokens_out": 0,
            "error": True,
            "cost_capped": False,
        }
        _LOGGER.info("rule_id=%s fires=%s error=%s model=%s", rule_id, False, True, result["model"])
        return result

    estimated_input_tokens = int((len(system_prompt) + len(user_content)) / 4)

    # Cross-process daily cap check (persistent file, covers all pipeline.py invocations today)
    daily_spend = _read_daily_spend()
    if daily_spend + _estimate_call_cost(estimated_input_tokens, models[0]) > _ATLAS_LLM_DAILY_MAX_USD:
        result = {
            "fires": False,
            "evidence": (
                f"Daily cost cap exceeded: ${daily_spend:.2f} accumulated today, "
                f"cap ${_ATLAS_LLM_DAILY_MAX_USD:.2f}"
            ),
            "suggested_fix": None,
            "model": models[0],
            "tokens_in": 0,
            "tokens_out": 0,
            "error": True,
            "cost_capped": True,
        }
        _LOGGER.info(
            "rule_id=%s fires=%s error=%s cost_capped=%s (daily) model=%s",
            rule_id, False, True, True, models[0],
        )
        return result

    client = Anthropic(api_key=api_key)
    last_error: Exception | None = None

    for model in models:
        projected_cost = float(_cost_tracker["est_usd"]) + _estimate_call_cost(estimated_input_tokens, model)
        if projected_cost > _ATLAS_LLM_MAX_USD:
            result = {
                "fires": False,
                "evidence": (
                    "Cost cap exceeded: "
                    f"${float(_cost_tracker['est_usd']):.2f} accumulated, cap ${_ATLAS_LLM_MAX_USD:.2f}"
                ),
                "suggested_fix": None,
                "model": model,
                "tokens_in": 0,
                "tokens_out": 0,
                "error": True,
                "cost_capped": True,
            }
            _LOGGER.info(
                "rule_id=%s fires=%s error=%s cost_capped=%s model=%s",
                rule_id,
                False,
                True,
                True,
                model,
            )
            return result

        try:
            response = client.messages.create(
                model=model,
                max_tokens=300,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            parsed = _parse_response_json(_extract_text(response))
            usage = getattr(response, "usage", None)
            tokens_in = int(getattr(usage, "input_tokens", 0) or 0)
            tokens_out = int(getattr(usage, "output_tokens", 0) or 0)
            call_est_usd = _estimate_cost(tokens_in, tokens_out, model)

            _cost_tracker["tokens_in"] = int(_cost_tracker["tokens_in"]) + tokens_in
            _cost_tracker["tokens_out"] = int(_cost_tracker["tokens_out"]) + tokens_out
            _cost_tracker["est_usd"] = float(_cost_tracker["est_usd"]) + call_est_usd
            _update_daily_spend(call_est_usd)

            result = {
                "fires": bool(parsed["fires"]),
                "evidence": str(parsed["evidence"]),
                "suggested_fix": parsed["suggested_fix"],
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "error": False,
                "cost_capped": False,
            }
            _LOGGER.info(
                "rule_id=%s fires=%s error=%s model=%s",
                rule_id,
                result["fires"],
                result["error"],
                model,
            )
            return result
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    message = f"LLM error: {last_error}" if last_error is not None else "LLM error: unknown error"
    model_name = models[0]
    result = {
        "fires": False,
        "evidence": message,
        "suggested_fix": None,
        "model": model_name,
        "tokens_in": 0,
        "tokens_out": 0,
        "error": True,
        "cost_capped": False,
    }
    _LOGGER.info("rule_id=%s fires=%s error=%s model=%s", rule_id, False, True, model_name)
    return result