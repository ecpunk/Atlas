from __future__ import annotations

from collections import defaultdict

from schemas.project import Project
from schemas.task import Task

NAME = "open_tasks_rollup"
INPUTS = ["project:*", "task:*"]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Open Tasks Rollup (generated).md"
]


def _project_name_map(projects: list[Project]) -> dict[str, str]:
    return {project.id: project.name for project in projects}


def _render_task(task: Task) -> list[str]:
    lines = [
        f"- [{task.status}/{task.priority}] {task.title} (`{task.id}`)",
        f"  - Next: {task.next_action}",
        f"  - Closure: {task.closure_test}",
        f"  - Updated: {task.updated_at.isoformat()}",
    ]
    if task.blocked_on:
        lines.append(f"  - Blocked on: {task.blocked_on}")
    if task.owner_lane:
        lines.append(f"  - Owner lane: {task.owner_lane}")
    if task.due_date:
        lines.append(f"  - Due: {task.due_date}")
    return lines


def generate(store: dict) -> dict[str, str]:
    projects_store = store.get("project", {})
    tasks_store = store.get("task", {})

    projects = [item for item in projects_store.values() if isinstance(item, Project)]
    tasks = [item for item in tasks_store.values() if isinstance(item, Task)]

    open_states = {"open", "in_progress", "blocked"}
    open_tasks = [task for task in tasks if task.status in open_states]

    project_names = _project_name_map(projects)
    grouped: dict[str, list[Task]] = defaultdict(list)
    for task in open_tasks:
        grouped[task.project_id].append(task)

    lines: list[str] = [
        "# Open Tasks Rollup",
        "",
        "AUTO-GENERATED from atlas-store task entities. Do not hand-edit.",
        "",
        f"Total open tasks: {len(open_tasks)}",
        "",
    ]

    if not open_tasks:
        lines.extend(["(none)", ""])
    else:
        for project_id in sorted(grouped.keys()):
            project_tasks = sorted(grouped[project_id], key=lambda item: item.updated_at, reverse=True)
            project_name = project_names.get(project_id, project_id)
            lines.append(f"## {project_name} (`{project_id}`)")
            lines.append("")
            for task in project_tasks:
                lines.extend(_render_task(task))
            lines.append("")

    output_path = OUTPUTS[0]
    content = "\n".join(lines).rstrip() + "\n"
    return {output_path: content}
