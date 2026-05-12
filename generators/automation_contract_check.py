from __future__ import annotations

import json
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

NAME = "automation_contract_check"
INPUTS = [
    "/opt/stack/services/automations/systemd/*.timer",
    "/opt/stack/services/automations/systemd/*.service",
    "/opt/stack/atlas-store/rules/automation_contract_policy.yaml",
]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Automation Contract Report.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/automation_contract_report.json",
]

SYSTEMD_DIR = Path("/opt/stack/services/automations/systemd")
STACK_ROOT = Path("/opt/stack/services")
POLICY_PATH = Path("/opt/stack/atlas-store/rules/automation_contract_policy.yaml")
CONTRACT_RULE_ID = "timer-service-runner-state-contract"
CONTRACT_RULE_NAME = "Scheduled job must map to service, runner, and state artifact"


def _parse_unit(path: Path) -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data.setdefault(key.strip(), []).append(value.strip())
    return data


def _resolve_stack_vars(text: str) -> str:
    return (
        text.replace("${STACK_ROOT}", str(STACK_ROOT))
        .replace("$STACK_ROOT", str(STACK_ROOT))
    )


def _load_policy() -> dict:
    defaults = {
        "contract_class": "state_required",
        "retirement_status": "active",
        "state_path_patterns": [
            "automations/state",
            "state.json",
            "state.csv",
            "state.log",
            "index_meta.json",
        ],
    }

    if not POLICY_PATH.exists():
        return {"defaults": defaults, "timers": {}}

    parsed = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(parsed, dict):
        return {"defaults": defaults, "timers": {}}

    policy_defaults = parsed.get("defaults")
    if isinstance(policy_defaults, dict):
        merged_defaults = dict(defaults)
        merged_defaults.update(policy_defaults)
    else:
        merged_defaults = defaults

    timers = parsed.get("timers")
    if not isinstance(timers, dict):
        timers = {}

    return {
        "defaults": merged_defaults,
        "timers": timers,
    }


def _timer_policy(policy: dict, timer_name: str) -> dict:
    merged = dict(policy.get("defaults") or {})
    timer_map = policy.get("timers") or {}
    timer_policy = timer_map.get(timer_name)
    if isinstance(timer_policy, dict):
        merged.update(timer_policy)
    return merged


def _systemctl_state(unit_name: str, mode: str) -> str:
    try:
        result = subprocess.run(
            ["systemctl", f"is-{mode}", unit_name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return "unknown"

    value = (result.stdout or result.stderr or "").strip()
    return value if value else "unknown"


def _extract_runner_path(exec_start: str, working_directory: Path | None) -> Path | None:
    resolved = _resolve_stack_vars(exec_start)
    try:
        tokens = shlex.split(resolved)
    except ValueError:
        tokens = resolved.split()

    if not tokens:
        return None

    python_bins = {"python", "python3", "/usr/bin/python", "/usr/bin/python3"}

    def _resolve_candidate(raw: str) -> Path:
        candidate = Path(raw)
        if candidate.is_absolute():
            return candidate
        if working_directory is not None:
            return working_directory / candidate
        return STACK_ROOT / candidate

    for idx, token in enumerate(tokens):
        token = token.lstrip("-")
        if token in python_bins and idx + 1 < len(tokens):
            return _resolve_candidate(tokens[idx + 1])
        if token.endswith((".py", ".sh")):
            return _resolve_candidate(token)
        if "/automations/" in token:
            return _resolve_candidate(token)

    return None


def _find_state_evidence(
    runner_path: Path,
    exec_start: str,
    working_directory: Path | None,
    state_patterns: list[str],
) -> str | None:
    if not runner_path.exists() or runner_path.suffix not in {".py", ".sh"}:
        return None

    content = runner_path.read_text(encoding="utf-8", errors="ignore")
    resolved_exec = _resolve_stack_vars(exec_start)

    for pattern in state_patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            continue
        needle = pattern.strip()
        if needle in content:
            return needle
        if needle in resolved_exec:
            return needle

        if working_directory is not None:
            candidate = Path(needle)
            if not candidate.is_absolute():
                candidate = working_directory / candidate
            if candidate.exists():
                return str(candidate)

    match = re.search(r"[^\s\"']*state\.(json|csv|log)[^\s\"']*", content)
    if match:
        return match.group(0)

    return None


def _evaluate_timer(timer_path: Path, policy: dict) -> dict[str, str]:
    timer_data = _parse_unit(timer_path)
    timer_name = timer_path.name
    known_timers = policy.get("timers") if isinstance(policy.get("timers"), dict) else {}
    if timer_name not in known_timers:
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Timer missing explicit policy entry in automation_contract_policy.yaml.",
            "evidence": f"policy_path={POLICY_PATH}",
        }

    timer_policy = _timer_policy(policy, timer_name)
    contract_class = str(timer_policy.get("contract_class", "state_required")).strip()
    retirement_status = str(timer_policy.get("retirement_status", "active")).strip().lower()
    retirement_note = str(timer_policy.get("retirement_note", "")).strip()
    superseded_by = str(timer_policy.get("superseded_by", "")).strip()
    timer_enabled = _systemctl_state(timer_name, "enabled")
    timer_active = _systemctl_state(timer_name, "active")

    state_patterns_raw = timer_policy.get("state_path_patterns", [])
    if isinstance(state_patterns_raw, list):
        state_patterns = [str(item) for item in state_patterns_raw]
    else:
        state_patterns = []

    if retirement_status in {"retired", "superseded"} and (
        timer_enabled == "enabled" or timer_active == "active"
    ):
        detail = f"Timer marked {retirement_status} but still enabled/active on host."
        hint = f"superseded_by={superseded_by}; note={retirement_note}" if (superseded_by or retirement_note) else ""
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": detail,
            "evidence": f"enabled={timer_enabled}; active={timer_active}; {hint}".strip("; "),
        }

    service_name = (timer_data.get("Unit") or [f"{timer_path.stem}.service"])[0]
    service_path = SYSTEMD_DIR / service_name
    if not service_path.exists():
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Timer unit does not map to an existing service file.",
            "evidence": f"Unit={service_name}; missing={service_path}",
        }

    service_data = _parse_unit(service_path)
    exec_start = (service_data.get("ExecStart") or [""])[0]
    working_directory_raw = (service_data.get("WorkingDirectory") or [""])[0]
    working_directory: Path | None = None
    if working_directory_raw:
        resolved_workdir = Path(_resolve_stack_vars(working_directory_raw))
        working_directory = resolved_workdir

    if not exec_start:
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Service has no ExecStart (unmapped runner).",
            "evidence": f"service={service_name}",
        }

    runner_path = _extract_runner_path(exec_start, working_directory)
    if runner_path is None:
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Could not resolve runner path from ExecStart.",
            "evidence": f"service={service_name}; ExecStart={exec_start}",
        }

    if not runner_path.exists():
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Resolved runner path does not exist.",
            "evidence": f"service={service_name}; runner={runner_path}",
        }

    if contract_class == "no_state_allowed":
        record = {
            "status": "pass",
            "timer": timer_name,
            "detail": "Timer is policy-classed as no_state_allowed and has valid service/runner mapping.",
            "evidence": f"service={service_name}; runner={runner_path}; class={contract_class}; retirement={retirement_status}",
        }
        if retirement_status == "candidate":
            record["status"] = "warn"
            record["detail"] = "Timer is a retirement candidate (policy-marked) and still active."
        return record

    state_evidence = _find_state_evidence(
        runner_path,
        exec_start,
        working_directory,
        state_patterns,
    )
    if state_evidence is None:
        return {
            "status": "fail",
            "timer": timer_name,
            "detail": "Runner is non-emitting (no state artifact reference found).",
            "evidence": f"service={service_name}; runner={runner_path}; class={contract_class}",
        }

    record = {
        "status": "pass",
        "timer": timer_name,
        "detail": "Timer maps cleanly to service, runner, and state artifact contract.",
        "evidence": f"service={service_name}; runner={runner_path}; state={state_evidence}; class={contract_class}; retirement={retirement_status}",
    }
    if retirement_status == "candidate":
        record["status"] = "warn"
        suffix = f" ({retirement_note})" if retirement_note else ""
        record["detail"] = f"Timer is a retirement candidate (policy-marked){suffix}."
    return record


def _render_markdown(records: list[dict[str, str]]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pass_count = sum(1 for r in records if r["status"] == "pass")
    fail_count = sum(1 for r in records if r["status"] == "fail")
    warn_count = sum(1 for r in records if r["status"] == "warn")
    outcome = "FAIL" if fail_count else ("WARN" if warn_count else "PASS")

    lines = [
        "# Automation Contract Report",
        "",
        "AUTO-GENERATED from systemd timer/service units and runner scripts. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"Timers scanned: {len(records)}",
        "",
        "## scheduled_job",
        "",
        f"### {CONTRACT_RULE_NAME} (`{CONTRACT_RULE_ID}`)",
        f"- Summary: {pass_count} pass, {fail_count} fail, {warn_count} warn, 0 manual",
        f"- Outcome: {outcome}",
        "- Suggested action: Add/update service mapping and state artifact emission for failed timers.",
        "",
        "| Outcome | Timer | Detail | Evidence |",
        "|---------|-------|--------|----------|",
    ]

    for record in sorted(records, key=lambda item: item["timer"]):
        lines.append(
            "| " + record["status"].upper() + " | " + record["timer"] + " | " + record["detail"] + " | " + record["evidence"].replace("|", "\\|") + " |"
        )

    lines.append("")
    return "\n".join(lines)


def generate(store: dict) -> dict[str, str]:
    _ = store
    policy = _load_policy()
    timer_paths = sorted(
        p for p in SYSTEMD_DIR.glob("*.timer")
        if p.name != "timer.template"
    )
    records = [_evaluate_timer(path, policy) for path in timer_paths]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule_id": CONTRACT_RULE_ID,
        "policy_path": str(POLICY_PATH),
        "records": records,
    }

    return {
        OUTPUTS[0]: _render_markdown(records),
        OUTPUTS[1]: json.dumps(payload, indent=2) + "\n",
    }