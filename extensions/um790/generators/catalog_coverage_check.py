from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from schemas.service import Service

NAME = "catalog_coverage_check"
INPUTS = ["service:*"]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Catalog Coverage Report.md"
]

_CATALOG_PATH = Path("/opt/stack/services/platform/service-catalog.json")
_SKIP_KEYS = {"$schema", "$status", "$fields"}


def generate(store: dict) -> dict[str, str]:
    service_store = store.get("service", {})
    entity_ids = {k for k, v in service_store.items() if isinstance(v, Service)}

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog_keys: set[str] = set()
    catalog_load_error: str | None = None

    if _CATALOG_PATH.exists():
        try:
            raw = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
            services_block = raw.get("services", {})
            catalog_keys = {k for k in services_block if k not in _SKIP_KEYS}
        except Exception as exc:
            catalog_load_error = str(exc)
    else:
        catalog_load_error = f"catalog not found at {_CATALOG_PATH}"

    catalog_only = sorted(catalog_keys - entity_ids)
    entity_only = sorted(entity_ids - catalog_keys)
    matched = sorted(catalog_keys & entity_ids)

    lines: list[str] = [
        "# Catalog Coverage Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"Atlas service entities: {len(entity_ids)}",
        f"service-catalog.json entries: {len(catalog_keys)}",
        "",
    ]

    if catalog_load_error:
        lines.extend([f"> ERROR loading catalog: {catalog_load_error}", ""])

    lines.extend([
        "---",
        "",
        "## Catalog-Only Services (in catalog.json, no atlas-store entity)",
        "",
        f"Count: {len(catalog_only)}",
        "",
        "_These services exist only in the fallback catalog. Add atlas-store entities to canonicalize them._",
        "",
    ])

    if catalog_only:
        lines.append("| Service Key |")
        lines.append("|-------------|")
        for key in catalog_only:
            lines.append(f"| `{key}` |")
    else:
        lines.append("_None — all catalog services have a matching entity._")

    lines.extend([
        "",
        "---",
        "",
        "## Entity-Only Services (atlas-store entity, not in catalog.json)",
        "",
        f"Count: {len(entity_only)}",
        "",
        "_These entities were canonicalized but never had a catalog.json entry, or were removed from it. This is the desired end state._",
        "",
    ])

    if entity_only:
        lines.append("| Entity ID |")
        lines.append("|-----------|")
        for eid in entity_only:
            lines.append(f"| `{eid}` |")
    else:
        lines.append("_None._")

    lines.extend([
        "",
        "---",
        "",
        "## Matched (in both)",
        "",
        f"Count: {len(matched)}",
        "",
    ])

    content = "\n".join(lines).rstrip() + "\n"
    return {OUTPUTS[0]: content}
