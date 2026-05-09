#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# When set, any output path under GDRIVE_OUTPUT_PREFIX is rewritten to
# $ATLAS_OUTPUT_DIR/<filename>. Allows migrating outputs off the FUSE mount
# without modifying individual generator modules.
GDRIVE_OUTPUT_PREFIX = "/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/"


def _rewrite_output_path(output_path: str) -> str:
    """Rewrite a gdrive 40-OUTPUT path to ATLAS_OUTPUT_DIR if the env var is set."""
    atlas_output_dir = os.environ.get("ATLAS_OUTPUT_DIR", "").strip()
    if not atlas_output_dir:
        return output_path
    if output_path.startswith(GDRIVE_OUTPUT_PREFIX):
        filename = output_path[len(GDRIVE_OUTPUT_PREFIX):]
        return str(Path(atlas_output_dir) / filename)
    return output_path
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pydantic import BaseModel

from tools.store import Store, _iter_yaml_files, _load_yaml, _schema_for_entity_dir, load_store

GenerateFn = Callable[[dict], dict[str, str]]


@dataclass(frozen=True)
class GeneratorModule:
    name: str
    inputs: list[str]
    outputs: list[str]
    generate: GenerateFn
    module: ModuleType
    source: str
    module_path: Path
    requires_llm: bool = False



def _iter_generator_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []

    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file()
        if p.suffix == ".py"
        if p.name != "__init__.py"
        if not p.name.startswith("_")
    )


def _load_generator_from_path(module_key: str, module_path: Path, source: str) -> GeneratorModule:
    spec = importlib.util.spec_from_file_location(module_key, module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Unable to load generator module: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    name = getattr(module, "NAME", None)
    inputs = getattr(module, "INPUTS", None)
    outputs = getattr(module, "OUTPUTS", None)
    generate = getattr(module, "generate", None)
    requires_llm = bool(getattr(module, "REQUIRES_LLM", False))

    if not isinstance(name, str) or not name:
        raise ValueError(f"Generator module {module_path} is missing NAME")
    if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
        raise ValueError(f"Generator module {module_path} is missing INPUTS list[str]")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        raise ValueError(f"Generator module {module_path} is missing OUTPUTS list[str]")
    if not callable(generate):
        raise ValueError(f"Generator module {module_path} is missing callable generate(store)")

    return GeneratorModule(
        name=name,
        inputs=inputs,
        outputs=outputs,
        generate=generate,
        module=module,
        source=source,
        module_path=module_path,
        requires_llm=requires_llm,
    )


def discover_generators(repo_root: Path) -> dict[str, GeneratorModule]:
    discovered: dict[str, GeneratorModule] = {}

    core_dir = repo_root / "generators"
    for module_path in _iter_generator_files(core_dir):
        module_key = f"atlas_core_generator_{module_path.stem}"
        generator = _load_generator_from_path(module_key, module_path, "core")
        if generator.name in discovered:
            other = discovered[generator.name]
            raise ValueError(
                f"Duplicate generator NAME '{generator.name}' in {module_path} and {other.module_path}"
            )
        discovered[generator.name] = generator

    extensions_root = repo_root / "extensions"
    if extensions_root.exists() and extensions_root.is_dir():
        for extension_dir in sorted(p for p in extensions_root.iterdir() if p.is_dir()):
            generator_dir = extension_dir / "generators"
            source = f"extension:{extension_dir.name}"
            for module_path in _iter_generator_files(generator_dir):
                module_key = f"atlas_{extension_dir.name}_generator_{module_path.stem}"
                generator = _load_generator_from_path(module_key, module_path, source)
                if generator.name in discovered:
                    other = discovered[generator.name]
                    raise ValueError(
                        f"Duplicate generator NAME '{generator.name}' in {module_path} and {other.module_path}"
                    )
                discovered[generator.name] = generator

    return dict(sorted(discovered.items()))



def main() -> int:
    parser = argparse.ArgumentParser(description="Run Atlas generation pipeline")
    parser.add_argument("--list", action="store_true", help="list discovered generators and exit")
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
        "--allow-llm",
        action="store_true",
        help="explicitly authorize LLM API calls; required when running LLM-enabled generators",
    )
    parser.add_argument(
        "--show-content",
        action="store_true",
        help="print generated content for each output",
    )
    args = parser.parse_args()

    try:
        store = load_store(REPO_ROOT)
        generators = discover_generators(REPO_ROOT)

        if args.list:
            print("Discovered generators:")
            for name, generator in generators.items():
                print(f"- {name} [{generator.source}] ({generator.module_path})")
            return 0

        selected_names = args.generator if args.generator else list(generators.keys())
        missing = [name for name in selected_names if name not in generators]
        if missing:
            print(f"ERROR: unknown generator(s): {', '.join(missing)}", file=sys.stderr)
            return 1

        # LLM gate: fail fast if any selected generator requires LLM and --allow-llm was not passed
        if not args.allow_llm:
            llm_generators = [
                name for name in selected_names if generators[name].requires_llm
            ]
            if llm_generators:
                print(
                    f"ERROR: generator(s) {', '.join(llm_generators)} require LLM API calls. "
                    "Pass --allow-llm to authorize. This flag prevents accidental spend.",
                    file=sys.stderr,
                )
                return 1

        collected: list[tuple[str, str, str, str]] = []
        for name in selected_names:
            generator = generators[name]
            outputs = generator.generate(store)
            if not isinstance(outputs, dict):
                raise ValueError(f"Generator {name} returned non-dict outputs")

            for output_path, content in outputs.items():
                if not isinstance(output_path, str) or not isinstance(content, str):
                    raise ValueError(f"Generator {name} produced non-string output mapping")
                collected.append((name, generator.source, _rewrite_output_path(output_path), content))

        if args.write:
            for _, _, output_path, content in collected:
                if output_path == "-":
                    continue
                target = Path(output_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                print(f"wrote: {output_path}")
            return 0

        print("Generated outputs summary:")
        for generator_name, generator_source, output_path, content in collected:
            print(f"({generator_name} [{generator_source}], {output_path}, {len(content)})")

        if args.show_content:
            for generator_name, generator_source, output_path, content in collected:
                print(f"\n--- {generator_name} [{generator_source}] -> {output_path} ---")
                print(content, end="" if content.endswith("\n") else "\n")

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
