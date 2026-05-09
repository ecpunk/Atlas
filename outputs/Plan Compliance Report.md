# Plan Compliance Report

AUTO-GENERATED from atlas-store Rule entities. Do not hand-edit.

Generated at: 2026-05-09T17:31:41Z
Plans scanned: 25

## PLAN-001-schema-implementation-and-first-slice.md

- Summary: 2 pass, 5 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this scope, Source documents (read before starting), Acceptance criteria, Open questions (resolve before execution; Jon will fill in), Phase 0 — Discovery and decisions, Phase 1 — Repo bootstrap, Phase 2 — Schema implementation, Phase 3 — First vocabulary instance, Phase 4 — Validation tool and regeneration tool, Phase 5 — Validation gate and README, Constraints (do not violate), Reporting format, Hand-off to operator, End of plan
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number, Recommended model, Run order
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 001 — Atlas Schema Implementation and First Vertical Slice

**Status:** Ready for execution
**Phase:** 1.5 (bridges Phase 1 Schemas → Phase 2 Store)
**Authored by:** Claude (Opus 4.7), running as Plan agent
**Executor:** GitHub Copilot CLI (recommended: GPT-5.3-Codex on High, or Sonnet 4.6)
**Surface:** VS Code Agent mode on UM790 via Remote-SSH

---

## Objective

Stand up the `atlas-store` repository, implement Pydantic models for the two schema-detailed entities (`Project`, `Vocabulary`), populate `lifecycle_categories` as a fully-worked first vocabulary, and prove the pattern end-to-end with a single regeneration tool that produces a real consumable view from canonical YAML.
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this scope, Source documents (read before starting), Acceptance criteria, Open questions (resolve before execution; Jon will fill in), Phase 0 — Discovery and decisions, Phase 1 — Repo bootstrap, Phase 2 — Schema implementation, Phase 3 — First vocabulary instance, Phase 4 — Validation tool and regeneration tool, Phase 5 — Validation gate and README, Constraints (do not violate), Reporting format, Hand-off to operator, End of plan
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: FAIL
- Detail: Missing required section: Phases
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
Available sections: Objective, Why this scope, Source documents (read before starting), Acceptance criteria, Open questions (resolve before execution; Jon will fill in), Phase 0 — Discovery and decisions, Phase 1 — Repo bootstrap, Phase 2 — Schema implementation, Phase 3 — First vocabulary instance, Phase 4 — Validation tool and regeneration tool, Phase 5 — Validation gate and README, Constraints (do not violate), Reporting format, Hand-off to operator, End of plan
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: FAIL
- Detail: Missing required section: Source documents
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
Available sections: Objective, Why this scope, Source documents (read before starting), Acceptance criteria, Open questions (resolve before execution; Jon will fill in), Phase 0 — Discovery and decisions, Phase 1 — Repo bootstrap, Phase 2 — Schema implementation, Phase 3 — First vocabulary instance, Phase 4 — Validation tool and regeneration tool, Phase 5 — Validation gate and README, Constraints (do not violate), Reporting format, Hand-off to operator, End of plan
```

## PLAN-002-fan-out-prep.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Source documents, Implementation Gate, Acceptance criteria, Phases, Entity documentation, Constraints, Hard-stop conditions
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 002 — Fan-out Prep

**Status:** Ready for execution
**Phase:** Bridge between Plan 001 and parallel Plans 003-007
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Serial. Single VS Code conversation. Plans 003-007 cannot start until this completes.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Source documents, Implementation Gate, Acceptance criteria, Phases, Entity documentation, Constraints, Hard-stop conditions
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-003-skill-entity.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Skill is new — schema defined inline below, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 003 — Skill Entity

**Status:** Ready for execution
**Phase:** Parallel — runs after Plan 002 completes
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Independent. Runs in parallel with Plans 004, 005, 006, 007.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Skill is new — schema defined inline below, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-004-service-entity.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved (use these decisions), Implementation Gate, Service schema (from SCHEMAS.md sketch + resolved open questions), Supporting vocabularies, Worked example: `entities/services/knowledge-server-mcp.yaml`, Regeneration tool: `tools/regenerate_service_catalog.py`, <Service Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 004 — Service Entity

**Status:** Ready for execution
**Phase:** Parallel — runs after Plan 002 completes
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Independent. Runs in parallel with Plans 003, 005, 006, 007.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved (use these decisions), Implementation Gate, Service schema (from SCHEMAS.md sketch + resolved open questions), Supporting vocabularies, Worked example: `entities/services/knowledge-server-mcp.yaml`, Regeneration tool: `tools/regenerate_service_catalog.py`, <Service Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-005-server-entity.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Server schema (from SCHEMAS.md sketch + resolutions), Worked example: `entities/servers/um790.yaml`, Regeneration tool: `tools/regenerate_servers_index.py`, <Server Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 005 — Server Entity

**Status:** Ready for execution
**Phase:** Parallel — runs after Plan 002 completes
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Independent. Runs in parallel with Plans 003, 004, 006, 007.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Server schema (from SCHEMAS.md sketch + resolutions), Worked example: `entities/servers/um790.yaml`, Regeneration tool: `tools/regenerate_servers_index.py`, <Server Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-006-rule-entity.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Rule schema (from SCHEMAS.md sketch + resolutions), Supporting vocabularies, Worked example: `entities/rules/project-must-have-category.yaml`, Regeneration tool: `tools/regenerate_rules_doc.py`, Details, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 006 — Rule Entity

**Status:** Ready for execution
**Phase:** Parallel — runs after Plan 002 completes
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Independent. Runs in parallel with Plans 003, 004, 005, 007.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Rule schema (from SCHEMAS.md sketch + resolutions), Supporting vocabularies, Worked example: `entities/rules/project-must-have-category.yaml`, Regeneration tool: `tools/regenerate_rules_doc.py`, Details, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-007-agent-entity.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Agent schema (from SCHEMAS.md sketch + resolutions), Supporting vocabularies, Worked example: `entities/agents/copilot-cli-vscode.yaml`, Regeneration tool: `tools/regenerate_agents_index.py`, <Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 007 — Agent Entity

**Status:** Ready for execution
**Phase:** Parallel — runs after Plan 002 completes
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Independent. Runs in parallel with Plans 003, 004, 005, 006.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Open questions resolved, Implementation Gate, Agent schema (from SCHEMAS.md sketch + resolutions), Supporting vocabularies, Worked example: `entities/agents/copilot-cli-vscode.yaml`, Regeneration tool: `tools/regenerate_agents_index.py`, <Name> (`<id>`), Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-008-integration-check.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 008 — Integration Check

**Status:** Ready for execution
**Phase:** Closeout — runs after Plans 003-007 all complete
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** Sonnet 4.6 or GPT-5.3-Codex on Medium (no design work, pure verification)
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Serial. Single VS Code conversation. Runs after all five entity plans land.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-009-backfill-entities.md

- Summary: 4 pass, 3 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Entities to create, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: FAIL
- Detail: Missing frontmatter keys: Plan number
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
# Plan 009 — Backfill Missing Service and Project Entities

**Status:** Ready for execution
**Phase:** Closeout follow-up — clears all residual cross-reference warnings from Plan 008
**Authored by:** Claude (Opus 4.7)
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on Medium, or Sonnet 4.6
**Surface:** VS Code Agent mode, Default Approvals
**Run order:** Serial. Single VS Code conversation. No parallel cohort needed.

---

## Objective
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Why this exists, Entities to create, Source documents, Implementation Gate, Acceptance criteria, Phases, Constraints, Hard-stop conditions, Reporting format
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-010-backfill-projects.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-011-schemas-cleanup.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-012-skill-body-migration.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Revision note, Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Revision note, Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-013-pipeline-orchestrator.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Pipeline interface (this section is the spec), Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Pipeline interface (this section is the spec), Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-014-project-index-generator.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-016-retire-ad-hoc-tools.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-018-standards-decomposition.md

- Summary: 5 pass, 2 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: FAIL
- Detail: Missing required section: Why this plan exists (Genesis alignment) OR Genesis Alignment Check
- Suggested action: n/a
- Evidence:
```text
Available sections: Objective, Source documents, Acceptance criteria, Phases, Plan-specific notes
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-019-project-index-wire-up.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-020-workflow-status-vocabulary.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-021-backfill-projects.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-022-core-extensions-refactor.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-023-rule-engine-plan-authoring.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-024-rule-engine-entity-checks.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-025-rule-engine-semantic-checks.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-026-llm-cost-cap.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```

## PLAN-027-github-publish.md

- Summary: 7 pass, 0 fail, 0 warn, 0 manual

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
- Outcome: PASS
- Detail: Section "Acceptance criteria" is present.
- Suggested action: Add an "Acceptance criteria" section containing at least one markdown
checkbox item.

- Evidence:
```text
## Acceptance criteria
```

### Plan has required frontmatter (`plan-has-frontmatter`)
- Outcome: PASS
- Detail: All required frontmatter keys present.
- Suggested action: Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the
standard frontmatter block.

- Evidence:
```text
Present keys: Authored by, Phase, Plan number, Recommended model, Run order, Status, Surface
```

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
- Outcome: PASS
- Detail: Section "Why this plan exists (Genesis alignment)" is present.
- Suggested action: n/a
- Evidence:
```text
## Why this plan exists (Genesis alignment)
```

### Plan has Objective section (`plan-has-objective`)
- Outcome: PASS
- Detail: Section "Objective" is present.
- Suggested action: Add an "Objective" section that states success criteria in one focused paragraph.

- Evidence:
```text
## Objective
```

### Plan has Phases section (`plan-has-phases`)
- Outcome: PASS
- Detail: Section "Phases" is present.
- Suggested action: Add a "Phases" section and include at least one numbered phase subsection.

- Evidence:
```text
## Phases
```

### Plan has Source documents section (`plan-has-source-documents`)
- Outcome: PASS
- Detail: Section "Source documents" is present.
- Suggested action: Add a "Source documents" section with explicit file paths used in the
Implementation Gate.

- Evidence:
```text
## Source documents
```
