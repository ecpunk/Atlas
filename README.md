# atlas-store

## Overview

atlas-store is the canonical definition store scaffold for Atlas Plan 001 first slice.

What it is today:
- Pydantic schemas for Project and Vocabulary entities
- One populated vocabulary instance: lifecycle_categories
- CLI validation tool for vocabularies and project entities
- CLI regeneration tool that emits a lifecycle payload for future knowledge-server integration

What it is not yet:
- A running service
- A write API
- Full generation pipeline integration across all downstream consumers

## Workflow

1. Edit YAML source of truth files.
2. Validate:

```bash
.venv/bin/python tools/validate.py
```

3. Regenerate lifecycle payload:

```bash
.venv/bin/python tools/regenerate_kb_buckets.py
```

4. Review output and commit.

## Adding a vocabulary value

1. Edit [vocabularies/lifecycle_categories.yaml](vocabularies/lifecycle_categories.yaml) and append a new item under values with all required fields.
2. Keep id stable and lowercase-hyphenated.
3. Run validation:

```bash
.venv/bin/python tools/validate.py --verbose
```

4. Regenerate payload:

```bash
.venv/bin/python tools/regenerate_kb_buckets.py
```

## Adding a project entity

1. Create a YAML file under [entities/projects](entities/projects) matching the Project schema.
2. Use typed references for relationships and vocab references for category/status.
3. Run validation:

```bash
.venv/bin/python tools/validate.py --verbose
```

## Validation

Current validation coverage:
- vocabularies/*.yaml -> Vocabulary schema
- entities/projects/*.yaml -> Project schema

Command:

```bash
.venv/bin/python tools/validate.py
```

Verbose mode:

```bash
.venv/bin/python tools/validate.py --verbose
```

## Regeneration

Regeneration currently emits a machine-readable lifecycle category payload.

Command:

```bash
.venv/bin/python tools/regenerate_kb_buckets.py
```

Optional write target:

```bash
.venv/bin/python tools/regenerate_kb_buckets.py --write /tmp/lifecycle_payload.json
```

Note: This tool does not modify knowledge-server source.

## Entity documentation

- [Skill](docs/skill-entity.md) - populated by Plan 003
- [Service](docs/service-entity.md) - populated by Plan 004
- [Server](docs/server-entity.md) - populated by Plan 005
- [Rule](docs/rule-entity.md) - populated by Plan 006
- [Agent](docs/agent-entity.md) - populated by Plan 007

## Not yet implemented

- Additional entity schemas (Service, Server, Rule, Agent)
- Write API
- Generation pipeline service
- Schema versioning and migrations
- Signals operational model wiring
- Agent operational model wiring
