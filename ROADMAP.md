# Atlas Roadmap

Where Atlas is, where it's going, and roughly in what order. Big picture only — each bullet may break into one or several plans when it's time.

Status legend: ✓ done · ◐ in progress · ◯ not started

---

## Phase 1 — Foundation

The substrate Atlas is built from. Almost complete.

- ✓ Canonical entity store with seven entity types (Project, Service, Server, Skill, Rule, Agent, Vocabulary)
- ✓ Schema validation, vocabularies, cross-entity references
- ✓ Generation pipeline with auto-discovery
- ✓ Core / extensions architectural boundary (substrate-agnostic vs substrate-specific)
- ✓ Rule engine — structural checks for plan documents
- ✓ Rule engine — structural checks for canonical entities
- ✓ Rule engine — semantic checks via LLM (plan-level Genesis alignment)
- ◯ Cost cap in LLM client (architectural fix, ~30 lines, no plan needed)

---

## Phase 2 — Release

Make Atlas visible and operationally safe before scaling its responsibility.

- ◯ Publish framework (without personal data) to `github.com/ecpunk/Atlas`
- ◯ License, contribution guidance, public-facing README polish
- ◯ Scheduled audit timer (systemd) — Atlas runs itself every N hours, regenerates reports
- ◯ Sync model documented for keeping public repo aligned with private working tree

---

## Phase 3 — Production deployment

Atlas becomes authoritative for real systems, one consumer at a time. Highest-value phase.

**Outbound: generators write to real consumer paths**
- ◯ Wire `service_catalog` → `/opt/stack/services/platform/service-catalog.json`
- ◯ Wire `kb_buckets` → knowledge-server VALID_STAGES source of truth
- ◯ Wire `project_index` → finalize cutover from staged to canonical Project Index.md (Plan 019 follow-through)
- ◯ Wire systemd unit definitions for project-as-service entities
- ◯ Wire nginx route declarations for service entities with public exposure
- ◯ Wire backup policy → backup script generation
- ◯ Wire monitoring / alerting config → from canonical service entities
- ◯ Wire agent context (Claude, Codex, Copilot) → regenerated from canonical store

Each is its own small plan. Pick by blast radius — narrowest first.

**Inbound: reality probes (drift detection vs deployed state)**
- ◯ Filesystem probes (deployment paths exist, configs match canonical)
- ◯ Process probes (systemd units active and matching declared state)
- ◯ Network probes (declared ports actually listening)
- ◯ Data integrity probes (backups ran on schedule, ZFS pools healthy, etc.)
- ◯ Reality compliance report alongside entity compliance report

**Self-repair**
- ◯ Propose-tier fixes — Atlas writes patches to a review folder, operator approves manually
- ◯ Auto-tier fixes (narrowly scoped, deterministic only) — Atlas applies and commits
- ◯ Fix-loop integration with audit timer — every cycle, audits surface gaps and repairs unambiguous ones

---

## Phase 4 — Agent integration

Agents stop scraping and start reading Atlas. Stop guessing and start proposing. This is the README's bet, made operational.

- ◯ Read API — MCP server exposing entities directly to agents
- ◯ Agent context generators write to Claude Desktop, Copilot, Codex skills/instructions paths
- ◯ Write API — structured way for agents to propose entity changes (entity diff → operator review → commit)
- ◯ Agents using Atlas as primary stack context (no more "let me check" stale-data sessions)
- ◯ Plan authoring via Atlas — new plans get drafted against current Rule entities, fail fast at the gate

---

## Phase 5 — Maturity

Things that aren't urgent now but become real as Atlas grows.

- ◯ Schema versioning + migration path (when entity schemas evolve, existing data migrates cleanly)
- ◯ Cross-entity referential integrity rules (beyond vocab refs — true relationship constraints)
- ◯ Rule library expansion — domain-specific rule packs (security, compliance, naming conventions)
- ◯ Semantic rule consensus / non-determinism resolution (multiple LLM runs, lower temperature, prompt caching)
- ◯ Additional substrate extensions if/when relevant (AWS, GCP, Kubernetes, bare-metal Linux at scale)
- ◯ Versioning, releases, changelog — Atlas as a product others might depend on
- ◯ Public examples / showcase demonstrating real stacks running on Atlas

---

## What "complete" looks like

Atlas reaches operational completion when:

1. Editing one entity propagates correctly to every downstream consumer in your stack
2. Atlas detects when reality drifts from canonical and either fixes it or surfaces it
3. Agents read canonical truth and propose changes through structured channels, never scraping
4. Standards live as Rule entities; changing a standard automatically audits the fleet
5. The system runs on a timer; you intervene only when something Atlas can't auto-resolve surfaces

Atlas reaches **architectural** completion well before all of Phase 5 is done. The above five points are achievable by end of Phase 4.

---

## Roughly in what order, near-term

1. Cost cap (today, no plan)
2. GitHub publish (one plan, ~20 min)
3. Scheduled audits (small ops task, ~15 min)
4. First generator wiring — `service_catalog` (one plan, narrow blast radius)
5. Second generator wiring — pick by what hurts most to keep hand-edited
6. Reality probes — first one (filesystem path existence, simplest probe shape)
7. Propose-tier self-repair on the easiest rule class

Steps 1-3 are mechanical and low-risk. Step 4 is the first real production milestone. Steps 5-7 each independently make Atlas more real.

---

## What's notably NOT in this roadmap

- Multi-operator / team features. Atlas is single-operator by design today; that's a much later question if it ever becomes one.
- A web UI. The interface is your editor + git + chat. Adding a UI is a different product.
- Hosted / SaaS Atlas. Not a goal. Atlas runs where your stack runs.
- Plugin marketplace, extension registry. Not relevant until there are external users with their own extensions to share.
