#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.service import Service
from schemas.vocabulary import Vocabulary

HEADER = "AUTO-GENERATED from atlas-store/entities/services/*.yaml - do not hand-edit."


def _load_services(repo_root: Path) -> list[Service]:
    services_root = repo_root / "entities" / "services"
    services: list[Service] = []

    for path in sorted(services_root.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        services.append(Service.model_validate(data))

    return services


def _load_vocab_lookup(repo_root: Path, vocab_id: str, cache: dict[str, dict[str, str]]) -> dict[str, str]:
    cached = cache.get(vocab_id)
    if cached is not None:
        return cached

    vocab_path = repo_root / "vocabularies" / f"{vocab_id}.yaml"
    data = yaml.safe_load(vocab_path.read_text(encoding="utf-8"))
    vocab = Vocabulary.model_validate(data)
    lookup = {item.id: item.name for item in vocab.values}
    cache[vocab_id] = lookup
    return lookup


def _resolve_vocab_name(repo_root: Path, vocab_id: str, value_id: str, cache: dict[str, dict[str, str]]) -> str:
    lookup = _load_vocab_lookup(repo_root, vocab_id, cache)
    return lookup.get(value_id, value_id)


def generate_markdown(repo_root: Path) -> str:
    services = sorted(_load_services(repo_root), key=lambda item: item.name.lower())
    vocab_cache: dict[str, dict[str, str]] = {}

    lines = ["# Service Catalog", "", HEADER, ""]

    for service in services:
        service_type_name = _resolve_vocab_name(
            repo_root,
            service.service_type.vocab_id,
            service.service_type.value_id,
            vocab_cache,
        )
        lifecycle_name = _resolve_vocab_name(
            repo_root,
            service.lifecycle.vocab_id,
            service.lifecycle.value_id,
            vocab_cache,
        )
        port = str(service.port) if service.port is not None else "n/a"
        health = service.health_endpoint if service.health_endpoint else "n/a"
        depends = ", ".join(ref.id for ref in service.depends_on) if service.depends_on else "none"
        summary = " ".join(service.summary.split())

        lines.extend(
            [
                f"## {service.name} (`{service.id}`)",
                "",
                f"- **Type:** {service_type_name}",
                f"- **Lifecycle:** {lifecycle_name}",
                f"- **Host:** `{service.host.id}`",
                f"- **Port:** {port}",
                f"- **Health:** {health}",
                f"- **Owned by:** `{service.owned_by.id}`",
                f"- **Depends on:** {depends}",
                f"- **Summary:** {summary}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate Atlas service catalog markdown")
    parser.add_argument("--write", type=Path, default=None, help="optional output file path")
    args = parser.parse_args()

    output = generate_markdown(REPO_ROOT)
    print(output, end="")

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())