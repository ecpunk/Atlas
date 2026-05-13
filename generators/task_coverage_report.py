from __future__ import annotations

from collections import defaultdict

from schemas.project import Project
from schemas.task import Task

NAME = "task_coverage_report"
INPUTS = ["project:*", "task:*"]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Task Coverage Report.md"
]


def generate(store: dict) -> dict[str, str]:
    projects_store = store.get("project", {})
    tasks_store = store.get("task", {})

    projects = [item for item in projects_store.values() if isinstance(item, Project)]
    tasks = [item for item in tasks_store.values() if isinstance(item, Task)]

    open_states = {"open", "in_progress", "blocked"}
    open_task_count: dict[str, int] = defaultdict(int)
    for task in tasks:
        if task.status in open_states:
            open_task_count[task.project_id] += 1

    tracked = []
    for project in projects:
        status = project.status.value_id
        if status not in {"active", "in_progress"}:
            continue
        next_action = (project.next_action or "").strip()
        tracked.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "status": status,
                "has_next_action": bool(next_action),
                "open_task_count": int(open_task_count.get(project.id, 0)),
                "next_action": next_action,
            }
        )

    tracked.sort(key=lambda row: (row["status"], row["project_name"].lower()))

    missing_both = [row for row in tracked if not row["has_next_action"] and row["open_task_count"] == 0]
    missing_next = [row for row in tracked if not row["has_next_action"]]
    missing_open = [row for row in tracked if row["open_task_count"] == 0]

    lines: list[str] = [
        "# Task Coverage Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Tracked active/in_progress projects: {len(tracked)}",
        f"Missing next_action: {len(missing_next)}",
        f"Missing open canonical task: {len(missing_open)}",
        f"Missing both (gap): {len(missing_both)}",
        "",
        "## Coverage Table",
        "",
        "| Project | Status | next_action | open_tasks |",
        "|---|---|---|---|",
    ]

    for row in tracked:
        lines.append(
            f"| `{row['project_id']}` | {row['status']} | "
            f"{'yes' if row['has_next_action'] else 'no'} | {row['open_task_count']} |"
        )

    lines.extend(["", "## Missing Both (Priority Cleanup)", ""])
    if missing_both:
        for row in missing_both:
            lines.append(f"- `{row['project_id']}` ({row['status']})")
    else:
        lines.append("(none)")

    lines.append("")
    return {OUTPUTS[0]: "\n".join(lines).rstrip() + "\n"}
