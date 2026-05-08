#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import BaseModel

from schemas.conventions import TypedRef, VocabRef
from schemas.project import Project
from schemas.vocabulary import Vocabulary


@dataclass
class LoadedDocument:
    path: Path
    kind: str
    model: BaseModel


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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


def _iter_yaml_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.suffix.lower() in {".yaml", ".yml"}
        if p.is_file()
    )


def _iter_refs(obj: Any) -> tuple[list[TypedRef], list[VocabRef]]:
    typed: list[TypedRef] = []
    vocab: list[VocabRef] = []

    def walk(value: Any) -> None:
        if isinstance(value, TypedRef):
            typed.append(value)
            return
        if isinstance(value, VocabRef):
            vocab.append(value)
            return
        if isinstance(value, BaseModel):
            for field_value in value.__dict__.values():
                walk(field_value)
            return
        if isinstance(value, dict):
            for field_value in value.values():
                walk(field_value)
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                walk(item)

    walk(obj)
    return typed, vocab


def _validate_references(loaded_docs: list[LoadedDocument], repo_root: Path) -> tuple[int, int]:
    warnings = 0
    failures = 0

    entity_refs: set[str] = set()
    vocab_values: dict[str, set[str]] = {}

    for doc in loaded_docs:
        if doc.kind == "vocabulary" and isinstance(doc.model, Vocabulary):
            vocab_values[doc.model.id] = {item.id for item in doc.model.values}
            continue

        model_id = getattr(doc.model, "id", None)
        if isinstance(model_id, str) and model_id:
            entity_refs.add(f"{doc.kind}:{model_id}")

    for doc in loaded_docs:
        typed_refs, vocab_refs = _iter_refs(doc.model)
        rel = doc.path.relative_to(repo_root)

        for typed_ref in typed_refs:
            rendered = str(typed_ref)
            if rendered not in entity_refs:
                warnings += 1
                print(f"WARN: unresolved reference {rendered} in {rel}")

        for vocab_ref in vocab_refs:
            values = vocab_values.get(vocab_ref.vocab_id)
            if values is None or vocab_ref.value_id not in values:
                failures += 1
                print(f"FAIL {rel}: unresolved vocabulary reference {vocab_ref}")

    return warnings, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Atlas YAML entities and vocabularies")
    parser.add_argument("--verbose", action="store_true", help="print parsed model on PASS")
    args = parser.parse_args()

    repo_root = REPO_ROOT
    validated = 0
    passed = 0
    warnings = 0
    failed = 0

    loaded_docs: list[LoadedDocument] = []

    vocab_root = repo_root / "vocabularies"
    if vocab_root.exists():
        for yaml_path in _iter_yaml_files(vocab_root):
            validated += 1
            rel = yaml_path.relative_to(repo_root)
            try:
                data = _load_yaml(yaml_path)
                model = Vocabulary.model_validate(data)
            except Exception as exc:
                failed += 1
                print(f"FAIL {rel}: {exc}")
                continue

            loaded_docs.append(LoadedDocument(path=yaml_path, kind="vocabulary", model=model))
            passed += 1
            print(f"PASS {rel}")
            if args.verbose:
                print(model)

    entities_root = repo_root / "entities"
    if entities_root.exists():
        for entity_dir in sorted(p for p in entities_root.iterdir() if p.is_dir()):
            yaml_files = _iter_yaml_files(entity_dir)
            if not yaml_files:
                continue

            entity_dir_name = entity_dir.name
            entity_kind = entity_dir_name[:-1] if entity_dir_name.endswith("s") else entity_dir_name
            validator = _schema_for_entity_dir(entity_dir_name)

            if validator is None:
                warnings += 1
                print(
                    f"WARN: no schema module for entities/{entity_dir_name}/, "
                    f"skipping ({len(yaml_files)} files)"
                )
                validated += len(yaml_files)
                continue

            for yaml_path in yaml_files:
                validated += 1
                rel = yaml_path.relative_to(repo_root)
                try:
                    data = _load_yaml(yaml_path)
                    model = validator(data)
                except Exception as exc:
                    failed += 1
                    print(f"FAIL {rel}: {exc}")
                    continue

                loaded_docs.append(LoadedDocument(path=yaml_path, kind=entity_kind, model=model))
                passed += 1
                print(f"PASS {rel}")
                if args.verbose:
                    print(model)

    ref_warnings, ref_failures = _validate_references(loaded_docs, repo_root)
    warnings += ref_warnings
    failed += ref_failures

    print(f"Validated {validated} files: {passed} PASSED, {warnings} WARNINGS, {failed} FAILED")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
