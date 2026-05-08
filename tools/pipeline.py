#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import BaseModel

from schemas.vocabulary import Vocabulary
from tools.generators import discover_generators


Store = dict[str, dict[str, BaseModel]]


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _iter_yaml_files(root: Path) -> list[Path]:
    if not root.exists():
        return []

    return sorted(
        p
        for p in root.rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
        if p.is_file()
    )


def _schema_for_entity_dir(entity_dir_name: str) -> Callable[[Any], BaseModel] | None:
    singular = entity_dir_name[:-1] if entity_dir_name.endswith("s") else entity_dir_name
    module_name = f"schemas.{singular}"
    class_name = singular.capitalize()

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            return None
        raise

    schema_cls = getattr(module, class_name, None)
    if schema_cls is None or not hasattr(schema_cls, "model_validate"):
        return None

    return schema_cls.model_validate


def load_store(repo_root: Path) -> Store:
    store: Store = {"vocabulary": {}}

    vocab_root = repo_root / "vocabularies"
    for yaml_path in _iter_yaml_files(vocab_root):
        model = Vocabulary.model_validate(_load_yaml(yaml_path))
        store["vocabulary"][model.id] = model

    entities_root = repo_root / "entities"
    if entities_root.exists():
        for entity_dir in sorted(p for p in entities_root.iterdir() if p.is_dir()):
            entity_dir_name = entity_dir.name
            kind = entity_dir_name[:-1] if entity_dir_name.endswith("s") else entity_dir_name

            validator = _schema_for_entity_dir(entity_dir_name)
            if validator is None:
                print(
                    f"WARN: no schema module for entities/{entity_dir_name}/, skipping",
                    file=sys.stderr,
                )
                continue

            kind_store = store.setdefault(kind, {})
            for yaml_path in _iter_yaml_files(entity_dir):
                model = validator(_load_yaml(yaml_path))
                model_id = getattr(model, "id", None)
                if not isinstance(model_id, str) or not model_id:
                    raise ValueError(f"Entity file missing string id: {yaml_path}")
                kind_store[model_id] = model

    return store


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Atlas generation pipeline")
    parser.add_argument(
        "--generator",
        action="append",
        default=[],
        help="generator name to run (repeatable); default runs all",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--write", action="store_true", help="write outputs to target paths")
    mode_group.add_argument("--dry-run", action="store_true", help="explicit alias for no-write mode")
    parser.add_argument(
        "--show-content",
        action="store_true",
        help="print generated content for each output",
    )
    args = parser.parse_args()

    try:
        store = load_store(REPO_ROOT)
        generators = discover_generators()

        selected_names = args.generator if args.generator else list(generators.keys())
        missing = [name for name in selected_names if name not in generators]
        if missing:
            print(f"ERROR: unknown generator(s): {', '.join(missing)}", file=sys.stderr)
            return 1

        collected: list[tuple[str, str, str]] = []
        for name in selected_names:
            generator = generators[name]
            outputs = generator.generate(store)
            if not isinstance(outputs, dict):
                raise ValueError(f"Generator {name} returned non-dict outputs")

            for output_path, content in outputs.items():
                if not isinstance(output_path, str) or not isinstance(content, str):
                    raise ValueError(f"Generator {name} produced non-string output mapping")
                collected.append((name, output_path, content))

        if args.write:
            for _, output_path, content in collected:
                if output_path == "-":
                    continue
                target = Path(output_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            return 0

        print("Generated outputs summary:")
        for generator_name, output_path, content in collected:
            print(f"({generator_name}, {output_path}, {len(content)})")

        if args.show_content:
            for generator_name, output_path, content in collected:
                print(f"\n--- {generator_name} -> {output_path} ---")
                print(content, end="" if content.endswith("\n") else "\n")

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
