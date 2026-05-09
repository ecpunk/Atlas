# Service Entity

## Schema reference

The Service entity model is defined in `schemas/service.py` as `Service`.

Fields:
- `id: str`
- `name: str`
- `summary: str`
- `service_type: VocabRef`
- `lifecycle: VocabRef`
- `host: TypedRef`
- `deployment_path: str`
- `port: int | None`
- `health_endpoint: str | None`
- `systemd_unit: str | None`
- `owned_by: TypedRef`
- `depends_on: list[TypedRef]`
- `last_health_check: datetime | None`
- `last_health_status: VocabRef | None`
- `failure_modes: list[str]`
- `source_of_truth_doc: str | None`
- `resource_budget_ram_mb: int | None`
- `created_at: datetime`
- `updated_at: datetime`

`TypedRef` fields use `entity_type:id` values (for example `server:um790`).
`VocabRef` fields use `vocab:vocab_id:value_id` values (for example `vocab:service_types:mcp_http`).

## File layout

- Schema: `schemas/service.py`
- Entities: `entities/services/*.yaml`
- Worked example: `entities/services/knowledge-server-mcp.yaml`
- Vocabularies:
  - `vocabularies/service_types.yaml`
  - `vocabularies/service_lifecycles.yaml`
  - `vocabularies/health_statuses.yaml`
- Regenerator: `tools/regenerate_service_catalog.py`

## Worked example

`entities/services/knowledge-server-mcp.yaml` is the canonical example for this phase.
It shows service identity, lifecycle and type vocab references, host/project typed references,
dependency references, health tracking fields, failure mode labels, and source-of-truth linkage.

## How to add a service

1. Create a new file at `entities/services/<id>.yaml`.
2. Populate required identity and timestamp fields (`id`, `name`, `summary`, `created_at`, `updated_at`).
3. Set constrained fields using vocabulary references:
	- `service_type` -> `vocab:service_types:<value>`
	- `lifecycle` -> `vocab:service_lifecycles:<value>`
	- `last_health_status` -> `vocab:health_statuses:<value>` (optional)
4. Set relationship fields using typed references:
	- `host` -> `server:<id>`
	- `owned_by` -> `project:<id>`
	- `depends_on` -> list of typed refs like `service:<id>`
5. Record service-specific failure modes in `failure_modes` as short labels.
6. Validate all documents:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/validate.py
```

## Regeneration usage

Generate service catalog markdown to stdout:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_service_catalog.py
```

Write service catalog markdown to a file:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_service_catalog.py --write /path/to/service-catalog.md
```

## Resolved open questions

- Project ownership is one-to-many: a Service has exactly one `owned_by` project reference, and a project may own many services.
- FAILURE_MODES are modeled directly on the Service entity as `failure_modes: list[str]`.
- Resource budget is declared on the Service entity as `resource_budget_ram_mb`; enforcement remains in the operational layer.
- Existing `platform/service-catalog.json` is not changed in this plan; generated catalog output from entities is the forward path.

Last verified: 2026-05-08
