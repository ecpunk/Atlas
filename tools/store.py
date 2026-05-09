"""Shared store loader — used by pipeline.py and mcp_server.py."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

from pydantic import BaseModel

from schemas.vocabulary import Vocabulary


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
    """Load all vocabularies and entities from the store root into a typed dict."""
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
