# Rule Entity

Rule entities define structural assertions that Atlas expects to hold across store data.
Violations describe invalid state and are surfaced according to severity and enforcement point.

## Schema Reference

Implementation: `schemas/rule.py`

Fields:

| Field | Type | Notes |
|------|------|-------|
| `id` | `str` | Stable lowercase-hyphenated rule ID |
| `name` | `str` | Human-readable display name |
| `description` | `str` | What the rule asserts and why |
| `scope` | `VocabRef` | Must reference `vocab:rule_scopes:<value>` |
| `severity` | `VocabRef` | Must reference `vocab:rule_severities:<value>` |
| `applies_to` | `str` | Target artifact/entity class (for example `plan_document`) |
| `check_kind` | `VocabRef` | Must reference `vocab:rule_check_kinds:<value>` |
| `check_definition` | `str` | Check-specific definition text (keys, section names, thresholds) |
| `fix_tier` | `VocabRef` | Must reference `vocab:rule_fix_tiers:<value>` |
| `fix_action` | `str \| null` | Required for `auto`/`propose`; null for `flag` |
| `enforcement_point` | `VocabRef` | Must reference `vocab:enforcement_points:<value>` |
| `on_violation` | `str` | Free text behavior (block, warn, log, signal) |
| `authored_by` | `str` | Rule author identifier |
| `created_at` | `datetime` | ISO 8601 UTC |
| `updated_at` | `datetime` | ISO 8601 UTC |

The model validates:
- Rule-specific vocabulary IDs for `scope`, `severity`, `check_kind`, `fix_tier`, and `enforcement_point`
- `fix_action` nullability by fix tier (`flag` => null, `auto`/`propose` => required)
- Timestamp fields as datetimes

## File Layout

- `schemas/rule.py`
- `vocabularies/rule_scopes.yaml`
- `vocabularies/rule_severities.yaml`
- `vocabularies/rule_check_kinds.yaml`
- `vocabularies/rule_fix_tiers.yaml`
- `vocabularies/enforcement_points.yaml`
- `entities/rules/project-must-have-category.yaml`
- `generators/rules_doc.py`

## Worked Example

Reference rule:

- `entities/rules/project-must-have-category.yaml`

This rule enforces that every project has a lifecycle category.

## Check Kinds (v1)

`check_kind` selects how the consuming generator evaluates `check_definition`.

- `section_present`
- `frontmatter_field_present`
- `length_warning`
- `template_reference_present`
- `manual`

## How To Add A Rule

1. Create `entities/rules/<rule-id>.yaml` using the Rule schema fields.
2. Use Rule vocab references:
	- `scope: vocab:rule_scopes:<value>`
	- `severity: vocab:rule_severities:<value>`
	- `check_kind: vocab:rule_check_kinds:<value>`
	- `fix_tier: vocab:rule_fix_tiers:<value>`
	- `enforcement_point: vocab:enforcement_points:<value>`
3. Set `applies_to`, `check_definition`, and `fix_action` (or null for `flag`).
4. Run validation:

	```bash
	.venv/bin/python tools/validate.py
	```

5. Regenerate rules documentation summary:

	```bash
	.venv/bin/python tools/pipeline.py --generator rules_doc
	```

6. Optional: include `--show-content` to print generated markdown in terminal output.

## Resolved Open Questions

- Check execution model: check-kind + check-definition, with manual checks supported.
- Rule composition: deferred to a future plan.
- Standards principles vs guidance: not classified here; Rule entity represents
  structural assertions only.

## v1 Scope vs Future

In scope now:

- Rule schema and rule vocabularies
- Rule entity validation and reference resolution
- Markdown regeneration summary for rule catalog visibility

Future work:

- Additional check kinds for semantic checks
- Cross-rule composition and dependency semantics
- Mapping authored policy/guidance into machine-evaluable rule categories
