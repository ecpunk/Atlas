# Rules

AUTO-GENERATED from atlas-store/entities/rules/*.yaml - do not hand-edit.

| Rule | Scope | Severity | Applies to | Check kind | Check definition | Fix tier | Enforcement |
|------|-------|----------|------------|------------|------------------|----------|-------------|
| Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`) | Instruction Layer | Error | `plan_document` | Section Present | `Plan must contain a section named exactly "Why this plan exists (Genesis
alignment)" or "Genesis Alignment Check" with no Yes answers` | Flag | Generation |
| Plan has Acceptance criteria section (`plan-has-acceptance-criteria`) | Instruction Layer | Error | `plan_document` | Section Present | `Plan must contain a section named exactly "Acceptance criteria" with at least
one checkbox` | Propose | Generation |
| Plan has required frontmatter (`plan-has-frontmatter`) | Instruction Layer | Error | `plan_document` | Frontmatter Field Present | `Plan must have these frontmatter keys: Status, Plan number, Phase,
Authored by, Recommended model, Surface, Run order` | Propose | Generation |
| Plan declares Genesis alignment (`plan-has-genesis-alignment`) | Instruction Layer | Warn | `plan_document` | Section Present | `Plan must contain a section named exactly "Why this plan exists (Genesis
alignment)" or "Genesis Alignment Check"` | Flag | Generation |
| Plan has Objective section (`plan-has-objective`) | Instruction Layer | Error | `plan_document` | Section Present | `Plan must contain a section named exactly "Objective"` | Propose | Generation |
| Plan has Phases section (`plan-has-phases`) | Instruction Layer | Error | `plan_document` | Section Present | `Plan must contain a section named exactly "Phases" with at least one numbered
subsection` | Propose | Generation |
| Plan has Source documents section (`plan-has-source-documents`) | Instruction Layer | Error | `plan_document` | Section Present | `Plan must contain a section named exactly "Source documents"` | Propose | Generation |
| Project must have category (`project-must-have-category`) | Project | Error | `project_entity` | Field Present | `category` | Flag | All |
| Project must have concept doc (`project-must-have-concept-doc`) | Project | Error | `project_entity` | Field Present | `concept_doc` | Flag | All |
| Project must have Drive folder (`project-must-have-gdrive-folder`) | Project | Error | `project_entity` | Field Present | `gdrive_folder` | Flag | All |
| Project must have lifecycle status (`project-must-have-status`) | Project | Error | `project_entity` | Field Present | `status` | Flag | All |
| Service must have deployment path (`service-must-have-deployment-path`) | Service | Error | `service_entity` | Field Present | `deployment_path` | Flag | All |
| Service must have host reference (`service-must-have-host-reference`) | Service | Error | `service_entity` | Field Present | `host` | Flag | All |
| Service must have owner (`service-must-have-owner`) | Service | Error | `service_entity` | Field Present | `owned_by` | Flag | All |
| Service should have source-of-truth doc (`service-should-have-source-of-truth-doc`) | Service | Warn | `service_entity` | Field Present | `source_of_truth_doc` | Flag | Scheduled Audit |

## Details

### Plan Genesis Alignment Check has no Yes answers (`plan-genesis-alignment-clean`)
**Description:** The Genesis Alignment Check section must exist and must not contain any affirmative "Yes" answers. A Yes answer means the plan author flagged a potential violation and should have stopped to reconsider before authoring.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Why this plan exists (Genesis alignment)" or "Genesis Alignment Check" with no Yes answers
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Flag the plan for operator review in the compliance report; do not auto-remediate.
**Authored by:** operator

### Plan has Acceptance criteria section (`plan-has-acceptance-criteria`)
**Description:** Plan documents must include Acceptance criteria with at least one checkbox so completion can be evaluated deterministically.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Acceptance criteria" with at least one checkbox
**Fix tier:** vocab:rule_fix_tiers:propose
**Fix action:** Add an "Acceptance criteria" section containing at least one markdown checkbox item.
**On violation:** Mark the plan as non-compliant in the compliance report and identify the missing section or checkbox structure.
**Authored by:** operator

### Plan has required frontmatter (`plan-has-frontmatter`)
**Description:** Plan documents must include required frontmatter keys to preserve consistent metadata for execution and reporting.
**Check kind:** vocab:rule_check_kinds:frontmatter_field_present
**Check definition:** Plan must have these frontmatter keys: Status, Plan number, Phase, Authored by, Recommended model, Surface, Run order
**Fix tier:** vocab:rule_fix_tiers:propose
**Fix action:** Add the missing frontmatter key-value pairs. See PLAN-TEMPLATE.md for the standard frontmatter block.
**On violation:** Mark the plan as non-compliant in the plan compliance report and surface missing frontmatter keys with remediation guidance.
**Authored by:** operator

### Plan declares Genesis alignment (`plan-has-genesis-alignment`)
**Description:** Plan documents must state their Genesis alignment to keep plan intent tied to Atlas architectural principles.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Why this plan exists (Genesis alignment)" or "Genesis Alignment Check"
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Flag the plan for operator review in the compliance report; do not auto-remediate.
**Authored by:** operator

### Plan has Objective section (`plan-has-objective`)
**Description:** Plan documents must include an Objective section that defines what successful execution produces.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Objective"
**Fix tier:** vocab:rule_fix_tiers:propose
**Fix action:** Add an "Objective" section that states success criteria in one focused paragraph.
**On violation:** Mark the plan as non-compliant in the compliance report and point to PLAN-TEMPLATE.md for the required section.
**Authored by:** operator

### Plan has Phases section (`plan-has-phases`)
**Description:** Plan documents must include a Phases section with numbered subsections to make execution sequencing explicit.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Phases" with at least one numbered subsection
**Fix tier:** vocab:rule_fix_tiers:propose
**Fix action:** Add a "Phases" section and include at least one numbered phase subsection.
**On violation:** Mark the plan as non-compliant in the compliance report and identify missing phase structure.
**Authored by:** operator

### Plan has Source documents section (`plan-has-source-documents`)
**Description:** Plan documents must include Source documents so execution is anchored to explicit authoritative inputs.
**Check kind:** vocab:rule_check_kinds:section_present
**Check definition:** Plan must contain a section named exactly "Source documents"
**Fix tier:** vocab:rule_fix_tiers:propose
**Fix action:** Add a "Source documents" section with explicit file paths used in the Implementation Gate.
**On violation:** Mark the plan as non-compliant in the compliance report and show the missing section.
**Authored by:** operator

### Project must have category (`project-must-have-category`)
**Description:** Every project entity must declare a lifecycle category. Projects without a category cannot be classified for views or audits.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** category
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block the write or generation; log error to validation summary; fire a signal of severity error.
**Authored by:** operator

### Project must have concept doc (`project-must-have-concept-doc`)
**Description:** Every project must declare a concept document path so planning and execution can anchor to a canonical specification.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** concept_doc
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the project until concept_doc is set; log an error in validation output.
**Authored by:** operator

### Project must have Drive folder (`project-must-have-gdrive-folder`)
**Description:** Every project must declare its Drive folder so Atlas can route humans and automations to the authoritative project location.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** gdrive_folder
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the project until gdrive_folder is set; log an error in validation output.
**Authored by:** operator

### Project must have lifecycle status (`project-must-have-status`)
**Description:** Every project must declare a lifecycle status to support prioritization, sequencing, and status-oriented views.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** status
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the project until status is set; log an error in validation output.
**Authored by:** operator

### Service must have deployment path (`service-must-have-deployment-path`)
**Description:** Every service must declare a deployment path so runtime ownership, operations, and incident handling can resolve to a concrete location.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** deployment_path
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the service until deployment_path is set; log an error in validation output.
**Authored by:** operator

### Service must have host reference (`service-must-have-host-reference`)
**Description:** Every service must reference a host so deployment responsibility and runtime triage can resolve to a concrete server.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** host
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the service until host is set; log an error in validation output.
**Authored by:** operator

### Service must have owner (`service-must-have-owner`)
**Description:** Every service must declare an owning project so accountability, change coordination, and escalation paths are explicit.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** owned_by
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Block writes and generation outputs for the service until owned_by is set; log an error in validation output.
**Authored by:** operator

### Service should have source-of-truth doc (`service-should-have-source-of-truth-doc`)
**Description:** Services should declare a source-of-truth document path so operators can resolve inventory, topology, and failure context quickly.
**Check kind:** vocab:rule_check_kinds:field_present
**Check definition:** source_of_truth_doc
**Fix tier:** vocab:rule_fix_tiers:flag
**Fix action:** n/a
**On violation:** Emit a warning during audits and generation; do not block writes, but surface remediation guidance in validation output.
**Authored by:** operator
