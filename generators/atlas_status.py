from __future__ import annotations

from pathlib import Path

from schemas.project import Project

NAME = "atlas_status"
INPUTS = ["project:atlas"]
OUTPUTS = [
    "/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Atlas Status.md"
]

_STATUS_SYMBOL = {
    "done": "✓",
    "partial": "◐",
    "not_started": "◯",
}

_STATUS_LABEL = {
    "done": "Done",
    "partial": "Partial",
    "not_started": "Not started",
}


def generate(store: dict) -> dict[str, str]:
    project_store = store.get("project", {})
    atlas = project_store.get("atlas")
    if not isinstance(atlas, Project):
        raise ValueError("atlas project entity not found in store")

    lines: list[str] = [
        "# Atlas — Working State",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "Source: `get_project('atlas')` or `entities/projects/atlas.yaml`.",
        "",
    ]

    # Current focus
    if atlas.next_action:
        lines += ["## Next Action", "", atlas.next_action, ""]

    if atlas.last_done:
        lines += ["## Last Done", "", atlas.last_done, ""]

    # Phase status table
    if atlas.phases:
        lines += [
            "## Phase Status",
            "",
            "| Phase | Name | Status | Notes |",
            "|---|---|---|---|",
        ]
        for phase in atlas.phases:
            symbol = _STATUS_SYMBOL.get(phase.status, phase.status)
            label = _STATUS_LABEL.get(phase.status, phase.status)
            notes = phase.notes.replace("\n", " ").strip() if phase.notes else ""
            lines.append(f"| {phase.id} | {phase.name} | {symbol} {label} | {notes} |")
        lines.append("")

    # Open items
    if atlas.open_items:
        lines += ["## Open Items", ""]
        for item in atlas.open_items:
            created = f" *(opened {item.created})*" if item.created else ""
            lines.append(f"{item.id}. {item.description}{created}")
        lines.append("")
    else:
        lines += ["## Open Items", "", "None.", ""]

    content = "\n".join(lines).rstrip() + "\n"

    output_path = OUTPUTS[0]
    return {output_path: content}
