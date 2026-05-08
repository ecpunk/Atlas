from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from schemas.project import Project
from schemas.vocabulary import Vocabulary

NAME = "project_index"
INPUTS = ["project:*"]
OUTPUTS = [
    "/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Project Index (generated).md"
]


def _flatten_summary(summary: str) -> str:
    return " ".join(summary.split())


def _render_project(project: Project) -> list[str]:
    drive_folder = project.gdrive_folder if project.gdrive_folder else "n/a"
    code_repo = project.code_repo if project.code_repo else "n/a"
    domain_tags = ", ".join(project.domain_tags) if project.domain_tags else "n/a"

    return [
        f"### {project.name} (`{project.id}`)",
        f"- **Category:** {project.category}",
        f"- **Status:** {project.status}",
        f"- **Domain tags:** {domain_tags}",
        f"- **Summary:** {_flatten_summary(project.summary)}",
        f"- **Drive folder:** {drive_folder}",
        f"- **Code repo:** {code_repo}",
        "",
    ]


def generate(store: dict) -> dict[str, str]:
    vocab_store = store.get("vocabulary", {})
    lifecycle = vocab_store.get("lifecycle_categories")
    if not isinstance(lifecycle, Vocabulary):
        raise ValueError("Missing vocabulary:lifecycle_categories in store")

    project_store = store.get("project", {})
    projects = [item for item in project_store.values() if isinstance(item, Project)]

    projects_by_category: dict[str, list[Project]] = defaultdict(list)
    for project in projects:
        projects_by_category[project.category.value_id].append(project)

    lines: list[str] = [
        "# Project Index",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
    ]

    for category in lifecycle.values:
        category_id = category.id
        category_name = category.name

        lines.append(f"## {category_name}")
        lines.append("")

        section_projects = sorted(
            projects_by_category.get(category_id, []),
            key=lambda item: item.name.lower(),
        )

        if not section_projects:
            lines.append("(none)")
            lines.append("")
            continue

        for project in section_projects:
            lines.extend(_render_project(project))

    content = "\n".join(lines).rstrip() + "\n"

    output_path = OUTPUTS[0]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return {output_path: content}
