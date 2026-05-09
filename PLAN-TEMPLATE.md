# Atlas Plan Template

Canonical scaffolding for Atlas plans. New plans reference this document for standard sections rather than duplicating them. The result: plans are short, focused on the variation, and consistent.

---

## Plan frontmatter (every plan)

```
**Status:** Ready for execution / In progress / Complete
**Plan number:** NNN
**Phase:** What build-phase concern this addresses
**Authored by:** Claude (Opus 4.7) or Codex
**Executor:** GitHub Copilot CLI / VS Code Agent on UM790
**Recommended model:** GPT-5.3-Codex on Medium/High, or Sonnet 4.6
**Surface:** VS Code Agent mode, Autopilot (default) or Default Approvals (when explicitly noted)
**Run order:** Serial / Parallel with Plans NNN-NNN
```

---

## Genesis Alignment Check (run before authoring any plan)

Atlas exists to dissolve the identity-vs-location anti-pattern across the stack (`30-CONTEXT/GENESIS.md`). Plans that work against the architecture multiply the disease they're meant to cure. Before specifying any plan, the author runs through these five checks. If the answer to any is "yes," stop and reconsider before specifying.

1. **Does this plan create a new place where stack state is encoded outside the canonical store?**
   *Genesis Leap 8.* Denormalization is the disease Atlas treats. New entity types are fine if they normalize existing scattered facts. New status / issue / finding / report entities that mirror what already exists in audit output, log files, or scripts are not — they create a new copy of the same fact.

2. **Does this plan ingest audit, monitoring, or diagnostic output as authoritative entities?**
   *Genesis Leap 1.* Audits are the diagnosis, not the cure. Audit output is a thermometer measuring the gap between reality and canonical entities. The cure is the canonical entity the audit is checking against, not a mirror of the audit's findings inside Atlas.

3. **Does this plan add a one-time analysis artifact that won't be regenerated from canonical data?**
   *Genesis Leap 9.* Every human-readable artifact in Atlas is a generated view. Consolidation analyses, overlap matrices, snapshot reports, audit reports — if it can't be re-emitted from `atlas-store` plus a generator, it shouldn't be a plan deliverable. It's a one-shot file that will be wrong by next week.

4. **Does this plan address a symptom of identity-vs-location at the surface, instead of the canonical entity underneath?**
   *Genesis Leap 4.* Five overlapping scripts is identity-vs-location at the function layer. The fix is not "consolidate the five scripts" — it's "define the canonical entity those scripts each fragment-encode, then the scripts become wrappers around a generated output and retire naturally." Symptom-fixing plans add work without reducing fan-out.

5. **Does this plan rely on a Genesis appendix inference as if it were a settled conclusion?**
   *Genesis Appendix.* Four claims are explicitly flagged as inferences worth re-auditing: identity-vs-location is systemic; the five existing files can be fully replaced by generated views; substrate is a peer system; conversations should be first-class artifacts. Plans that assume these are facts — without the Phase 1 schema work or evidence that should ground them — are running ahead of the architecture.

If any answer is yes, the author should either reframe the plan against the canonical-store + generated-views model, or surface the specific tension to the operator before proceeding. This check applies to plans authored by Claude AND plans authored by Codex from the template.

---

## Required plan-specific sections

Every plan must contain:

1. **Objective** — one paragraph describing what success looks like
2. **Source documents** — explicit paths Codex reads during Implementation Gate
3. **Acceptance criteria** — checkbox list, each verifiable by command or file inspection
4. **Phases** — numbered, with explicit acceptance per phase

Optional sections, when warranted:
- **Why this exists** (only if non-obvious from Objective)
- **Schema definitions inline** (only when introducing genuinely new entities not in SCHEMAS.md)
- **Plan-specific constraints** (only when overriding Standard Constraints below)

---

## Standard Implementation Gate

Every plan begins with this gate. Codex executes it before any writes.

> Read the source documents listed in this plan. Confirm in one paragraph what will be done and what shape the changes will take. Identify any contradiction between the plan and the actual repository state. Then proceed.
>
> If a source document is missing or unparseable, hard-stop with the specific gap. Do not improvise.

---

## Standard Constraints

Apply to every plan unless the plan explicitly overrides:

- Use atlas-store venv: `/opt/stack/atlas-store/.venv/bin/python`. Never `python3` or system Python.
- Discovery-first: one deterministic attempt + one bounded fallback per question. After both, hard-stop.
- No new dependencies beyond `pydantic` and `pyyaml` unless the plan explicitly authorizes
- No knowledge-server modification unless the plan is specifically about that service
- Use explicit-path `git add <path>` for every commit. Never `git add -A` or `git add .`
- Use `git log --oneline -n N` (optionally with `--grep`) for status reporting. Never `git status` to drive the report.
- Pattern-match existing entity YAML and Pydantic style. Do not invent new structures.
- Do not modify SCHEMAS.md, ATLAS_CONCEPT.md, GENESIS.md, or any plan document
- Do not touch anything outside `/opt/stack/atlas-store/` or the Atlas Drive folder

---

## Standard Hard-Stop Conditions

Stop execution and report verbatim if any of these occur. Do not retry or improvise.

- `validate.py` reports a FAIL (not WARN) on any file the plan created
- A single command stalls more than 60 seconds (likely FUSE on `/mnt/gdrive`)
- Drive API rate limit appears in rclone logs
- Discovery surfaces something that contradicts the plan
- An operation requires more than one retry to succeed
- More than three trivial corrections become necessary — that's a signal a future plan is warranted

For routine scenarios not on this list, consult `OPERATING-MODE.md` for the pre-approved decision before stopping. Most scenarios already have answers there.

---

## Standard Commit Cadence

- **Per-phase commits** when phases produce semantically distinct artifacts (e.g., schemas → vocabularies → tools)
- **Per-batch commits** when a phase produces N similar artifacts (e.g., 10 entity instances = 1 commit)
- **Never per-file commits** for batch work
- **Always use explicit-path** `git add <path1> <path2> ...`

---

## Standard Reporting Format

Every plan ends with this report block, posted both in chat and written to Drive.

```
PLAN NNN COMPLETE
Started: <iso8601 UTC, captured at first action>
Finished: <iso8601 UTC, captured at last commit>
Duration: <h:m:s>

Done:
- <one bullet per significant accomplishment>

Files created/modified:
- <full path per file>

Commits:
- <hash> <commit message>

Validation:
- Files: <total>
- Passed: <count>
- Warnings: <count>
- Failed: <count>

Issues encountered:
- <list, or "none">

Recommended next plan:
- <one line, or "no further plan; close cohort">
```

Write to: `/opt/stack/services/gdrive-projects/Projects/Current/Atlas/20-DESIGN/STATUS-<YYYY-MM-DD>-plan-<NNN>-<short-name>.md`

---

## Operator Touchpoints

The operator (Jon) is invoked when, and only when:

- An architectural decision crosses system boundaries
- A genuinely novel pattern is needed (not extending existing)
- A Standard Hard-Stop Condition fires
- The plan's source documents contain contradictions that can't be resolved by reading

The operator is NOT invoked when:

- Untracked files from parallel plans appear → consult `OPERATING-MODE.md`
- Validation produces warnings (not failures) → consult `OPERATING-MODE.md`
- A specific MCP server is unreachable → consult `OPERATING-MODE.md`
- Sequencing through phases of an already-approved plan
- Choosing between two equivalent implementations of the same spec

---

## Authoring Conventions for New Plans

When writing a plan that follows this template:

- Run the Genesis Alignment Check above first, before specifying anything
- Reference standard sections rather than duplicating: "See `PLAN-TEMPLATE.md` § Standard Constraints"
- Include only the variation specific to this plan
- Aim for 300–600 words. If a plan is longer than 800 words, it probably contains material that belongs in `SCHEMAS.md` or in a separate plan
- Always cross-reference `OPERATING-MODE.md` once at the top: "Consults `OPERATING-MODE.md` for standard scenario decisions"
