from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NAME = "project_state_deltas"
INPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Plan Compliance Report.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Entity Compliance Report.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Automation Contract Report.md",
    "/opt/stack/services/automations/state/atlas_probe_latest.json",
    "/opt/stack/atlas-store/entities/projects/atlas.yaml",
]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Project State Deltas.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/project_state_deltas.json",
]

_PLAN_REPORT = Path(INPUTS[0])
_ENTITY_REPORT = Path(INPUTS[1])
_AUTOMATION_CONTRACT_REPORT = Path(INPUTS[2])
_DRIFT_CACHE = Path(INPUTS[3])


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_fail_rules(report_path: Path) -> dict[str, dict[str, str]]:
    """Parse report markdown and return failing rules keyed by rule id."""
    failing: dict[str, dict[str, str]] = {}
    if not report_path.exists():
        return failing

    lines = report_path.read_text(encoding="utf-8").splitlines()
    current_rule_id = ""
    current_rule_name = ""

    for line in lines:
        header_match = re.match(r"^###\s+(.+?)\s+\(`([^`]+)`\)\s*$", line)
        if header_match:
            current_rule_name = header_match.group(1).strip()
            current_rule_id = header_match.group(2).strip()
            continue

        if current_rule_id and line.strip() == "- Outcome: FAIL":
            failing[current_rule_id] = {
                "rule_id": current_rule_id,
                "rule_name": current_rule_name,
            }
            continue

        if current_rule_id:
            summary_match = re.match(r"^- Summary:\s*(\d+)\s+pass,\s*(\d+)\s+fail,", line.strip())
            if summary_match and int(summary_match.group(2)) > 0:
                failing[current_rule_id] = {
                    "rule_id": current_rule_id,
                    "rule_name": current_rule_name,
                }

    return failing


def _parse_drift_records(cache_path: Path) -> list[dict[str, str]]:
    if not cache_path.exists():
        return []
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    records: list[dict[str, str]] = []
    for result in payload.get("results", []):
        if not result.get("drift"):
            continue
        service_id = str(result.get("service_id", "")).strip()
        if not service_id:
            continue
        name = str(result.get("name", service_id)).strip()
        records.append({
            "service_id": service_id,
            "name": name,
        })
    return records


def _build_signals() -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []

    for info in _parse_fail_rules(_PLAN_REPORT).values():
        signals.append(
            {
                "signal_id": f"plan:{info['rule_id']}",
                "kind": "plan_rule_failure",
                "description": f"Plan compliance has failing rule `{info['rule_id']}` ({info['rule_name']}).",
                "source": str(_PLAN_REPORT),
            }
        )

    for info in _parse_fail_rules(_ENTITY_REPORT).values():
        signals.append(
            {
                "signal_id": f"entity:{info['rule_id']}",
                "kind": "entity_rule_failure",
                "description": f"Entity compliance has failing rule `{info['rule_id']}` ({info['rule_name']}).",
                "source": str(_ENTITY_REPORT),
            }
        )

    for info in _parse_fail_rules(_AUTOMATION_CONTRACT_REPORT).values():
        signals.append(
            {
                "signal_id": f"automation:{info['rule_id']}",
                "kind": "automation_contract_failure",
                "description": f"Automation contract report has failing rule `{info['rule_id']}` ({info['rule_name']}).",
                "source": str(_AUTOMATION_CONTRACT_REPORT),
            }
        )

    for drift in _parse_drift_records(_DRIFT_CACHE):
        signals.append(
            {
                "signal_id": f"drift:{drift['service_id']}",
                "kind": "service_drift",
                "description": f"Service drift detected for `{drift['service_id']}` ({drift['name']}).",
                "source": str(_DRIFT_CACHE),
            }
        )

    return sorted(signals, key=lambda item: item["signal_id"])


def _auto_item_from_signal(signal: dict[str, str], created: str) -> dict[str, str]:
    return {
        "id": f"auto:{signal['signal_id']}",
        "description": signal["description"],
        "created": created,
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Project State Deltas",
        "",
        "AUTO-GENERATED from compliance outputs and drift state. Do not hand-edit.",
        "",
        f"Generated at: {summary['generated_at']}",
        f"Signal count: {summary['signal_count']}",
        f"Delta summary: create={len(summary['create'])}, update={len(summary['update'])}, close={len(summary['close'])}",
        "",
    ]

    lines.append("## Signals")
    lines.append("")
    if not summary["signals"]:
        lines.extend(["_No active signals detected._", ""])
    else:
        for signal in summary["signals"]:
            lines.append(f"- `{signal['signal_id']}` — {signal['description']}")
        lines.append("")

    lines.append("## Canonical Deltas")
    lines.append("")

    for label, key in (("Create", "create"), ("Update", "update"), ("Close", "close")):
        lines.append(f"### {label}")
        lines.append("")
        if not summary[key]:
            lines.append("_None._")
            lines.append("")
            continue
        for item in summary[key]:
            lines.append(f"- `{item['id']}` — {item['description']}")
        lines.append("")

    lines.append("## Proposed Open Items")
    lines.append("")
    for item in summary["proposed_open_items"]:
        lines.append(f"- `{item['id']}` — {item['description']}")

    lines.append("")
    return "\n".join(lines)


def generate(store: dict) -> dict[str, str]:
    project_store = store.get("project", {})
    atlas = project_store.get("atlas")
    if atlas is None:
        raise ValueError("Atlas project entity not found in store")

    existing_items = [
        {
            "id": str(item.id),
            "description": str(item.description),
            "created": item.created,
        }
        for item in getattr(atlas, "open_items", [])
    ]

    manual_items = [item for item in existing_items if not item["id"].startswith("auto:")]
    existing_auto = {item["id"]: item for item in existing_items if item["id"].startswith("auto:")}

    created = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    signals = _build_signals()
    desired_auto = {_auto_item_from_signal(signal, created)["id"]: _auto_item_from_signal(signal, created) for signal in signals}

    create: list[dict[str, str]] = []
    update: list[dict[str, str]] = []
    close: list[dict[str, str]] = []

    for item_id, desired in sorted(desired_auto.items()):
        existing = existing_auto.get(item_id)
        if existing is None:
            create.append(desired)
            continue
        if existing.get("description") != desired.get("description"):
            update.append(desired)

    for item_id, existing in sorted(existing_auto.items()):
        if item_id not in desired_auto:
            close.append(existing)

    proposed_open_items = manual_items + [desired_auto[item_id] for item_id in sorted(desired_auto)]

    summary: dict[str, Any] = {
        "generated_at": _now_iso(),
        "signal_count": len(signals),
        "signals": signals,
        "create": create,
        "update": update,
        "close": close,
        "proposed_open_items": proposed_open_items,
    }

    return {
        OUTPUTS[0]: _render_markdown(summary),
        OUTPUTS[1]: json.dumps(summary, indent=2) + "\n",
    }
