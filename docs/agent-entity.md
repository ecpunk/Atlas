# Agent Entity

The Agent entity defines an operator-managed AI agent profile in Atlas: surface,
lane, declared capabilities, trust calibration by task pattern, and operating
constraints.

## Schema reference

- Schema model: `schemas/agent.py`
- Primary class: `Agent`
- Sub-model: `TrustCalibrationEntry`
- Supporting references:
	- `VocabRef` from `schemas/conventions.py`
	- Vocabulary model from `schemas/vocabulary.py`

## File layout

Agent support is split across schema, vocabularies, instances, and tooling:

```text
atlas-store/
	schemas/
		agent.py
	vocabularies/
		agent_interfaces.yaml
		agent_lanes.yaml
		reliability_levels.yaml
	entities/
		agents/
			copilot-cli-vscode.yaml
	tools/
		regenerate_agents_index.py
```

## Worked example

- Example entity: `entities/agents/copilot-cli-vscode.yaml`

This example captures the current VS Code Copilot runtime surface used in Atlas
execution with declared capabilities and calibrated trust patterns.

## Trust calibration model

`trust_calibration` is a list of structured entries, each describing one task
pattern and the current reliability assignment:

- `task_pattern`: free-text description of task class
- `reliability`: `vocab:reliability_levels:<value>`
- `notes`: optional calibration context

Reliability level operational meaning:

- `high`: autonomous use is acceptable with standard safeguards
- `medium`: propose-confirm before mutation
- `low`: surface-only, no autonomous mutation

This structure is intentionally flexible and will be refined after additional
real entries are collected.

## How to add an agent

1. Choose stable id (lowercase, hyphenated) and create `entities/agents/<id>.yaml`.
2. Populate all schema fields defined in `schemas/agent.py`.
3. Use vocabulary references for `interface`, lane fields, and reliability fields.
4. Set `created_at` and `updated_at` as ISO 8601 UTC timestamps.
5. Validate:
	 - `/opt/stack/atlas-store/.venv/bin/python tools/validate.py`
6. Regenerate index:
	 - `/opt/stack/atlas-store/.venv/bin/python tools/regenerate_agents_index.py`

## Regeneration usage

Generate markdown index to stdout:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_agents_index.py
```

Generate and write to a file:

```bash
/opt/stack/atlas-store/.venv/bin/python tools/regenerate_agents_index.py --write /tmp/agents-index.md
```

The regeneration tool resolves `VocabRef` values to display names by loading the
vocabulary files in `vocabularies/`.

## Resolved open questions

- Trust calibration stays list-of-objects for now, refined later after more data.
- Session relationship stays out of Agent entity; sessions are treated as signals.
- Agent entity authorship is operator-authored initially; agent proposals are
	future work with approval gating.

## Future work

- OTEL wiring: `telemetry_source` is a placeholder field only in this phase.
- Session signals: future phase should define session signal schema and linkage.
