from __future__ import annotations

"""drift_report.py — generate Drift Report.md from current coverage reports.

This generator uses drift_runner to collect DriftRecords from the three
coverage report files, then renders a summary markdown doc.

It does NOT execute remediation — that is the drift orchestrator's job.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

NAME = "drift_report"
INPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/KB Coverage Report.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Catalog Coverage Report.md",
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Output Integrity Report.md",
]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Drift Report.md",
]

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.drift import DriftRecord
from tools.drift_runner import collect_all


_TIER_LABEL = {
    "auto": "AUTO — will be deleted on next drift run",
    "propose": "PROPOSE — stub YAML written to staging/ for operator review",
    "flag": "FLAG — requires operator decision, no automatic action",
}

_KIND_LABEL = {
    "kb_orphan_dir": "KB orphan directory",
    "catalog_only_service": "Catalog-only service",
    "broken_concept_doc": "Broken concept_doc reference",
    "orphaned_output_file": "Orphaned output file",
    "task_missing_next_action": "Task coverage: missing next_action",
    "task_missing_open_work": "Task coverage: missing open canonical task",
    "task_tracking_gap": "Task coverage: missing next_action and open task",
}


def _render(records: list[DriftRecord]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    by_tier: dict[str, list[DriftRecord]] = {"auto": [], "propose": [], "flag": []}
    for r in records:
        by_tier[r.fix_tier].append(r)

    lines: list[str] = [
        "# Drift Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Generated at: {now}",
        f"Total drift records: {len(records)}  "
        f"(auto={len(by_tier['auto'])}, propose={len(by_tier['propose'])}, flag={len(by_tier['flag'])})",
        "",
        "---",
        "",
    ]

    for tier in ("auto", "propose", "flag"):
        tier_records = by_tier[tier]
        lines += [
            f"## {tier.upper()} ({len(tier_records)})",
            "",
            f"_{_TIER_LABEL[tier]}_",
            "",
        ]
        if not tier_records:
            lines += ["_None._", ""]
            continue

        # Group by kind
        by_kind: dict[str, list[DriftRecord]] = {}
        for r in tier_records:
            by_kind.setdefault(r.kind, []).append(r)

        for kind, kind_records in by_kind.items():
            kind_label = _KIND_LABEL.get(kind, kind)
            lines += [
                f"### {kind_label} ({len(kind_records)})",
                "",
                "| ID | Detail |",
                "|----|--------|",
            ]
            for r in kind_records:
                lines.append(f"| `{r.id}` | {r.detail} |")
            lines.append("")

    return "\n".join(lines)


def generate(store: dict) -> dict[str, str]:
    records = collect_all()
    content = _render(records)
    return {
        OUTPUTS[0]: content,
    }
