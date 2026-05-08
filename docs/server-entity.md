# Server Entity

## Schema reference

The Server entity model is defined in `schemas/server.py` as `Server`.

Fields:
- `id: str`
- `name: str`
- `hostname: str`
- `ip: str`
- `hardware: str`
- `cpu: str | None`
- `ram_gib: float | None`
- `storage: list[str]`
- `gpu: str | None`
- `os: str | None`
- `ram_committed_gib: float | None`
- `ram_alert_floor_gib: float | None`
- `swap_gib: float | None`
- `hosts: list[TypedRef]`
- `source_of_truth_doc: str | None`
- `created_at: datetime`
- `updated_at: datetime`

`hosts` uses typed references (`entity_type:id`) via `TypedRef` from `schemas/conventions.py`.

## File layout

- Schema: `schemas/server.py`
- Entities: `entities/servers/*.yaml`
- Worked example: `entities/servers/um790.yaml`
- Regenerator: `tools/regenerate_servers_index.py`

## Worked example

`entities/servers/um790.yaml` is the canonical example for this phase. It includes identity, hardware/software baseline, capacity summary fields, hosted service references, and source-of-truth path.

## How to add a server

1. Create a new YAML file at `entities/servers/<id>.yaml`.
2. Populate all required identity and timestamp fields.
3. Use `hosts` for typed service references (for example `service:knowledge-server-mcp`).
4. Use `ram_committed_gib` and `ram_alert_floor_gib` for static capacity budgeting only.
5. Validate with:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/validate.py
```

## Regeneration usage

Generate markdown to stdout:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_servers_index.py
```

Write markdown to a file:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_servers_index.py --write /path/to/servers.md
```

## Resolved open questions

- `source_of_truth_doc` is stored on the Server entity now; generated views may consume it in future plans.
- Live utilization signals (for example current RAM use and swap pressure) remain in signal entities, not Server static fields.
- Multi-host runtime spans are represented on Service relationships; Server keeps a host list for local visibility.

Last verified: 2026-05-08
