from __future__ import annotations

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

_FALLBACK_MODELS = ("claude-sonnet-4-6", "claude-sonnet-4-5")

_LOGGER = logging.getLogger("atlas.llm_client")
if not _LOGGER.handlers:
    _HANDLER = logging.StreamHandler(sys.stderr)
    _HANDLER.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    _LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.INFO)


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


def evaluate_rule(system_prompt: str, user_content: str, rule_id: str) -> dict[str, Any]:
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        result = {
            "fires": False,
            "evidence": "LLM error: ANTHROPIC_API_KEY not set",
            "suggested_fix": None,
            "model": _model_candidates()[0],
            "tokens_in": 0,
            "tokens_out": 0,
            "error": True,
        }
        _LOGGER.info("rule_id=%s fires=%s error=%s model=%s", rule_id, False, True, result["model"])
        return result

    client = Anthropic(api_key=api_key)
    last_error: Exception | None = None

    for model in _model_candidates():
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

            result = {
                "fires": bool(parsed["fires"]),
                "evidence": str(parsed["evidence"]),
                "suggested_fix": parsed["suggested_fix"],
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "error": False,
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
    model_name = _model_candidates()[0]
    result = {
        "fires": False,
        "evidence": message,
        "suggested_fix": None,
        "model": model_name,
        "tokens_in": 0,
        "tokens_out": 0,
        "error": True,
    }
    _LOGGER.info("rule_id=%s fires=%s error=%s model=%s", rule_id, False, True, model_name)
    return result