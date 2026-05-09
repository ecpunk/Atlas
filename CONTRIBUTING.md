# Contributing to Atlas

## Bootstrap

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
3. Validate the framework:
   - `python tools/validate.py`

## Populate your own entities

Atlas expects your local stack data under `entities/`.

- Use `entities/projects/`, `entities/services/`, `entities/servers/`, `entities/skills/`, and `entities/agents/` for your own canonical entities.
- Start from the anonymized examples in `examples/`.
- Keep framework rules in `entities/rules/` and extend them for your environment as needed.

## Use the rule engine for plan authoring

- Plans should follow `PLAN-TEMPLATE.md`.
- Rule entities under `entities/rules/` define structural and semantic checks for plans and entities.
- Run generators and validators after plan changes to ensure compliance output remains consistent.

## Writing extensions

- Add substrate-specific behavior in `extensions/<your-substrate>/`.
- Keep core framework behavior in `schemas/`, `vocabularies/`, `generators/`, and `tools/` substrate-agnostic.
- See `extensions/um790/` for a complete reference extension structure.

## Public/private sync model

- Framework changes can be contributed here via pull request.
- Private operator entity data should remain local and never be committed upstream.
- Maintainers keep private and public trees aligned by cherry-picking framework commits only.
