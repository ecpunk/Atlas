from __future__ import annotations

from dataclasses import dataclass
import importlib
import pkgutil
from types import ModuleType
from typing import Callable


GenerateFn = Callable[[dict], dict[str, str]]


@dataclass(frozen=True)
class GeneratorModule:
    name: str
    inputs: list[str]
    outputs: list[str]
    generate: GenerateFn
    module: ModuleType


def _load_generator(module_name: str) -> GeneratorModule:
    module = importlib.import_module(f"{__name__}.{module_name}")

    name = getattr(module, "NAME", None)
    inputs = getattr(module, "INPUTS", None)
    outputs = getattr(module, "OUTPUTS", None)
    generate = getattr(module, "generate", None)

    if not isinstance(name, str) or not name:
        raise ValueError(f"Generator module {module_name} is missing NAME")
    if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
        raise ValueError(f"Generator module {module_name} is missing INPUTS list[str]")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        raise ValueError(f"Generator module {module_name} is missing OUTPUTS list[str]")
    if not callable(generate):
        raise ValueError(f"Generator module {module_name} is missing callable generate(store)")

    return GeneratorModule(
        name=name,
        inputs=inputs,
        outputs=outputs,
        generate=generate,
        module=module,
    )


def discover_generators() -> dict[str, GeneratorModule]:
    discovered: dict[str, GeneratorModule] = {}

    for module_info in pkgutil.iter_modules(__path__):
        if module_info.name == "__init__" or module_info.name.startswith("_"):
            continue

        generator = _load_generator(module_info.name)
        discovered[generator.name] = generator

    return dict(sorted(discovered.items()))
