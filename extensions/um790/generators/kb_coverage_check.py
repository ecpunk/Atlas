from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from schemas.project import Project

NAME = "kb_coverage_check"
INPUTS = ["project:*"]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/KB Coverage Report.md"
]

_KB_PROJECTS_ROOT = Path("/opt/stack/services/docs/kb/Projects")
_SERVICES_ROOT = Path("/opt/stack/services")

_SKIP_DIRS = {"Atlas"}


def _dir_to_id(name: str) -> str:
    """Normalize a kb/Projects directory name to a project entity ID.

    Examples:
      "AI HVAC Balancer"           -> "ai-hvac-balancer"
      "Build & Design Navigator"   -> "build-and-design-navigator"
      "Code Intelligence MCP (Archive)" -> "code-intelligence-mcp-archive"
      "UM790-Knowledge-Server"     -> "um790-knowledge-server"
    """
    normalized = name.lower()
    normalized = normalized.replace("&", "and")
    normalized = re.sub(r"[()[\]{}]", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return normalized


def generate(store: dict) -> dict[str, str]:
    project_store = store.get("project", {})
    projects = {k: v for k, v in project_store.items() if isinstance(v, Project)}
    entity_ids = set(projects.keys())

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Direction 1: kb/Projects dirs with no entity ---
    orphan_dirs: list[tuple[str, str]] = []  # (dir_name, normalized_id)
    matched_dirs: list[tuple[str, str]] = []

    if _KB_PROJECTS_ROOT.exists():
        for dir_path in sorted(_KB_PROJECTS_ROOT.iterdir()):
            if not dir_path.is_dir():
                continue
            if dir_path.name in _SKIP_DIRS:
                continue
            normalized = _dir_to_id(dir_path.name)
            if normalized in entity_ids:
                matched_dirs.append((dir_path.name, normalized))
            else:
                orphan_dirs.append((dir_path.name, normalized))

    # --- Direction 2: entities with concept_doc that doesn't exist on disk ---
    broken_refs: list[tuple[str, str]] = []  # (entity_id, concept_doc path)
    valid_refs: list[tuple[str, str]] = []

    for entity_id, project in sorted(projects.items()):
        if not project.concept_doc:
            continue
        doc_path = _SERVICES_ROOT / project.concept_doc
        if doc_path.exists():
            valid_refs.append((entity_id, project.concept_doc))
        else:
            broken_refs.append((entity_id, project.concept_doc))

    # --- Render ---
    lines: list[str] = [
        "# KB Coverage Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"KB project dirs scanned: {len(orphan_dirs) + len(matched_dirs)}",
        f"Project entities scanned: {len(projects)}",
        "",
        "---",
        "",
        "## Orphan Directories (kb/Projects dir with no atlas-store entity)",
        "",
        f"Count: {len(orphan_dirs)}",
        "",
    ]

    if orphan_dirs:
        lines.append("| Directory | Normalized ID (no match) |")
        lines.append("|-----------|--------------------------|")
        for dir_name, norm_id in orphan_dirs:
            lines.append(f"| {dir_name} | `{norm_id}` |")
    else:
        lines.append("_None — all kb/Projects directories have a matching entity._")

    lines.extend([
        "",
        "---",
        "",
        "## Broken concept_doc References (entity points to missing file)",
        "",
        f"Count: {len(broken_refs)}",
        "",
    ])

    if broken_refs:
        lines.append("| Entity ID | concept_doc path |")
        lines.append("|-----------|-----------------|")
        for entity_id, doc_path in broken_refs:
            lines.append(f"| `{entity_id}` | `{doc_path}` |")
    else:
        lines.append("_None — all concept_doc paths resolve to existing files._")

    lines.extend([
        "",
        "---",
        "",
        "## Matched (reference only)",
        "",
        f"Dirs matched to entities: {len(matched_dirs)}",
        f"Entities with valid concept_doc: {len(valid_refs)}",
        "",
    ])

    content = "\n".join(lines).rstrip() + "\n"
    return {OUTPUTS[0]: content}
