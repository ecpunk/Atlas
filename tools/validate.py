#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.project import Project
from schemas.vocabulary import Vocabulary


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _schema_for_path(path: Path) -> Callable[[Any], Any] | None:
    parts = path.parts
    if "vocabularies" in parts:
        return Vocabulary.model_validate
    if "entities" in parts and "projects" in parts:
        return Project.model_validate
    return None


def _iter_yaml_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
        if p.is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Atlas YAML entities and vocabularies")
    parser.add_argument("--verbose", action="store_true", help="print parsed model on PASS")
    args = parser.parse_args()

    repo_root = REPO_ROOT
    targets = [repo_root / "vocabularies", repo_root / "entities"]

    has_failures = False

    for target in targets:
        if not target.exists():
            continue

        for yaml_path in _iter_yaml_files(target):
            rel = yaml_path.relative_to(repo_root)
            validator = _schema_for_path(yaml_path)
            if validator is None:
                print(f"PASS {rel} (no schema mapping; skipped)")
                continue

            try:
                data = _load_yaml(yaml_path)
                model = validator(data)
            except Exception as exc:
                has_failures = True
                print(f"FAIL {rel}: {exc}")
                continue

            print(f"PASS {rel}")
            if args.verbose:
                print(model)

    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
