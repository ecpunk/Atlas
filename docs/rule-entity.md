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
| `applies_to` | `str` | v1 DSL expression, single-condition |
| `must_satisfy` | `str` | v1 DSL expression, single-condition |
| `enforcement_point` | `VocabRef` | Must reference `vocab:enforcement_points:<value>` |
| `on_violation` | `str` | Free text behavior (block, warn, log, signal) |
| `authored_by` | `str` | Rule author identifier |
| `created_at` | `datetime` | ISO 8601 UTC |
| `updated_at` | `datetime` | ISO 8601 UTC |

The model validates:
- Rule-specific vocabulary IDs for `scope`, `severity`, and `enforcement_point`
- Basic DSL shape for `applies_to` and `must_satisfy`
- Timestamp fields as datetimes

## File Layout

- `schemas/rule.py`
- `vocabularies/rule_scopes.yaml`
- `vocabularies/rule_severities.yaml`
- `vocabularies/enforcement_points.yaml`
- `entities/rules/project-must-have-category.yaml`
- `tools/regenerate_rules_doc.py`

## Worked Example

Reference rule:

- `entities/rules/project-must-have-category.yaml`

This rule enforces that every project has a lifecycle category.

## DSL Format (v1)

v1 uses a minimal single-condition DSL. It is stored as plain strings and is not
yet parsed/evaluated into executable logic.

Format:

`<entity_type> where <field_path> <op> [<value>]`

Supported operators:

| Operator | Value Required | Meaning |
|----------|----------------|---------|
| `equals` | yes | Field value equals provided value |
| `not_equals` | yes | Field value does not equal provided value |
| `contains` | yes | Field contains provided value |
| `is_null` | no | Field is null or missing |
| `is_not_null` | no | Field is present/non-null |

Examples:

- `project where id is_not_null`
- `project where category is_not_null`
- `service where service_type equals vocab:service_types:mcp_http`
- `server where name contains UM790`

Out of scope in v1:

- Logical composition (`and`, `or`, nested conditions)
- Rule composition (rules depending on other rules)
- Full parser/evaluator semantics beyond shape validation

## How To Add A Rule

1. Create `entities/rules/<rule-id>.yaml` using the Rule schema fields.
2. Use Rule vocab references:
	- `scope: vocab:rule_scopes:<value>`
	- `severity: vocab:rule_severities:<value>`
	- `enforcement_point: vocab:enforcement_points:<value>`
3. Set `applies_to` and `must_satisfy` using the v1 DSL format.
4. Run validation:

	```bash
	.venv/bin/python tools/validate.py
	```

5. Regenerate rules documentation summary:

	```bash
	.venv/bin/python tools/regenerate_rules_doc.py
	```

6. Optional: write generated summary to a file:

	```bash
	.venv/bin/python tools/regenerate_rules_doc.py --write /tmp/rules.md
	```

## Resolved Open Questions

- Query DSL: custom minimal DSL for v1 with one condition and fixed operators.
- Rule composition: deferred to a future plan.
- Standards principles vs guidance: not classified here; Rule entity represents
  structural assertions only.

## v1 Scope vs Future

In scope now:

- Rule schema and rule vocabularies
- Rule entity validation and reference resolution
- Markdown regeneration summary for rule catalog visibility

Future work:

- DSL parser and evaluator runtime
- Cross-rule composition and dependency semantics
- Mapping authored policy/guidance into machine-evaluable rule categories
