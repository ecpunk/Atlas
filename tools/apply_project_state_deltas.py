#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DELTA_PATH = Path("/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/project_state_deltas.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Atlas project state deltas to project open_items")
    parser.add_argument("--project-id", default="atlas", help="Project entity id (default: atlas)")
    parser.add_argument("--delta-file", default=str(DEFAULT_DELTA_PATH), help="Delta JSON path")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Default is preview only.")
    args = parser.parse_args()

    delta_path = Path(args.delta_file)
    if not delta_path.exists():
        raise FileNotFoundError(f"Delta file not found: {delta_path}")

    rel_entity = Path("entities") / "projects" / f"{args.project_id}.yaml"
    entity_path = REPO_ROOT / rel_entity
    if not entity_path.exists():
        raise FileNotFoundError(f"Project entity not found: {entity_path}")

    delta = _load_json(delta_path)
    project = _load_yaml(entity_path)

    before_open_items = project.get("open_items") or []
    proposed_open_items = delta.get("proposed_open_items") or []

    print(
        "Delta summary:",
        f"create={len(delta.get('create') or [])}",
        f"update={len(delta.get('update') or [])}",
        f"close={len(delta.get('close') or [])}",
    )
    print(f"Open items before: {len(before_open_items)}")
    print(f"Open items after:  {len(proposed_open_items)}")

    if not args.apply:
        print("Preview only. Re-run with --apply to persist changes.")
        return 0

    project["open_items"] = proposed_open_items
    project["updated_at"] = _now_iso()
    _write_yaml(entity_path, project)
    print(f"Applied deltas to {entity_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
