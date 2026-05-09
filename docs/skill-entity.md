# Skill Entity

The Skill entity defines reusable skill metadata in Atlas so SKILL.md artifacts are generated from a single canonical YAML source. Each skill records display metadata, invocation context mode, publish targets, and the markdown body that becomes the generated skill content.

## Schema Reference

Schema module: `schemas/skill.py` (`Skill`, `SkillPublishTarget`, `SkillFrontmatter`)

Fields:

- `id`: Stable skill identifier (for example `jon-woodall-writing-style`).
- `name`: Human-readable display name.
- `version`: Skill version string (semver recommended).
- `summary`: One-line summary for quick listings.
- `description`: Longer descriptive text.
- `context_mode`: Vocabulary reference to `vocab:context_modes:<value>`.
- `publish_targets`: List of output targets with `target_id` and `output_path`.
- `frontmatter`: Frontmatter values emitted in generated SKILL.md files.
- `body`: Markdown body content emitted after frontmatter.
- `applies_when`: Optional natural-language trigger condition.
- `related_skills`: Optional typed references (`skill:<id>`) to related skills.
- `created_at`: ISO 8601 UTC creation timestamp.
- `updated_at`: ISO 8601 UTC update timestamp.

## File Layout

- Skill schema: `schemas/skill.py`
- Skill entities: `entities/skills/<id>.yaml`
- Context mode vocabulary: `vocabularies/context_modes.yaml`
- Regeneration tool: `tools/regenerate_skill_md.py`

Worked example: `entities/skills/jon-woodall-writing-style.yaml`

## Add A New Skill

1. Create `entities/skills/<id>.yaml` using the `Skill` schema fields.
2. Validate definitions:
	- `.venv/bin/python tools/validate.py`
3. Regenerate SKILL.md output for the desired target path:
	- `.venv/bin/python tools/regenerate_skill_md.py entities/skills/<id>.yaml --target <target-id> --write`

## Regeneration Usage

Render to stdout using the first publish target:

```bash
.venv/bin/python tools/regenerate_skill_md.py entities/skills/jon-woodall-writing-style.yaml
```

Render to stdout for a specific target:

```bash
.venv/bin/python tools/regenerate_skill_md.py entities/skills/jon-woodall-writing-style.yaml --target claude-desktop
```

Write generated output to selected target path:

```bash
.venv/bin/python tools/regenerate_skill_md.py entities/skills/jon-woodall-writing-style.yaml --target copilot-vscode --write
```

## Future Work

Actual migration of existing `jon-*` skill body content is deferred to a later plan. The worked example currently uses placeholder body text for schema and generator validation.
