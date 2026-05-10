from __future__ import annotations

from schemas.service import Service
from schemas.vocabulary import Vocabulary

NAME = "service_catalog"
INPUTS = ["service:*"]
OUTPUTS = ["/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Service Catalog.md"]

HEADER = "AUTO-GENERATED from atlas-store/entities/services/*.yaml - do not hand-edit."


def _build_vocab_lookup(vocab_store: dict) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for vocab in vocab_store.values():
        if isinstance(vocab, Vocabulary):
            lookup[vocab.id] = {item.id: item.name for item in vocab.values}
    return lookup


def _resolve_vocab_name(lookup: dict[str, dict[str, str]], vocab_id: str, value_id: str) -> str:
    values = lookup.get(vocab_id, {})
    return values.get(value_id, value_id)


def generate(store: dict) -> dict[str, str]:
    service_store = store.get("service", {})
    services = [item for item in service_store.values() if isinstance(item, Service)]
    services.sort(key=lambda item: item.name.lower())

    vocab_lookup = _build_vocab_lookup(store.get("vocabulary", {}))
    lines = ["# Service Catalog", "", HEADER, ""]

    for service in services:
        service_type_name = _resolve_vocab_name(
            vocab_lookup,
            service.service_type.vocab_id,
            service.service_type.value_id,
        )
        lifecycle_name = _resolve_vocab_name(
            vocab_lookup,
            service.lifecycle.vocab_id,
            service.lifecycle.value_id,
        )
        port = str(service.port) if service.port is not None else "n/a"
        health = service.health_endpoint if service.health_endpoint else "n/a"
        remote = service.remote if service.remote else "n/a"
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
                f"- **Remote:** {remote}",
                f"- **Owned by:** `{service.owned_by.id}`",
                f"- **Depends on:** {depends}",
                f"- **Summary:** {summary}",
                "",
            ]
        )

    content = "\n".join(lines).rstrip() + "\n"
    return {OUTPUTS[0]: content}
