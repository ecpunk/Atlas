# Atlas

**A single source of truth for the systems you build.**

Define your projects, services, and the rules that govern them as canonical entities. Generate every downstream artifact — configs, documentation, context for AI agents — from them. Edit one entity, regenerate, every consumer updates.

---

## The problem

Every system you've ever worked on encoded the same fact in many places.

The list of services lives in a deployment config, in a load balancer, in three READMEs, in your team's onboarding doc, and in the context you've taught your AI assistant. They drift. You change one. The others stay wrong. Documentation becomes fiction. Configurations contradict each other. The AI agent gives confidently wrong answers because it learned from the part that's already stale.

This is normal. Every stack accumulates this. The question is how long you can hold the contradictions in your head before something important breaks.

---

## The approach

Atlas treats every fact you care about as a canonical entity — Project, Service, Server, Skill, Rule, Agent, Vocabulary — stored as schema-validated YAML in a Git repository. A generation pipeline emits all the artifacts your tools and humans and agents consume.

Take any service in your stack. In a typical setup, its port number lives in a deployment manifest, its routing in a load balancer config, its description in three different READMEs, its existence in your AI assistant's context as some scraped paragraph that may or may not still be accurate. Atlas defines that service as one entity. Generators emit the rest. Renaming, retiring, or reconfiguring it becomes a single-entity edit plus regeneration. Every consumer updates. Including the agents.

---

## What it isn't

Not a deploy tool. It doesn't push containers, manage cloud state, or replace the tools that move bits around. It's the source-of-truth layer those tools — and your agents, and your docs — read *from*. It also isn't a runtime. There's no Atlas service running. Just a Git repo, a Python pipeline, and YAML.

---

## Why now

Modern stacks have an emerging requirement that older ones didn't: AI agents need shared context. You can give an agent good answers by handing it your stack's truth, or you can let it scrape and guess. Atlas exists because the second option doesn't scale and the first option requires a single source of truth that doesn't currently exist as a category.

The bet is that this category becomes obvious in a few years — that every serious stack ends up with something like this, the same way every serious stack ended up with version control and configuration management. Atlas is one early implementation of that pattern.

---

## How Atlas fits into your workflow

Most descriptions of tools like this start by telling you to learn a new file format and run a new command. Atlas doesn't, because that's not where it sits.

**You don't change how you work.** If you're already collaborating with AI agents to manage your stack — talking to them, asking them to make changes, reviewing what they did — Atlas slots underneath that. You stay in conversation. The agent does the rest.

Without Atlas, those conversations have a hole in them. You ask the agent to retire a service. It edits a deployment config, maybe updates a README, probably forgets the architecture diagram, and definitely doesn't update the context the *next* agent session will start with. The next time you talk to an agent about that service, it's working from stale information. You re-explain.

The hole goes the other direction too. You ask an agent to spin up a new service. Did it remember to register the service in the catalog? Set up backups? Configure alerting? Add it to the documentation index? Match your naming conventions? Use the right base image? Each of those is a standard you'd hope it remembered. Each is a standard that quietly gets dropped under pressure. By the time you notice, the new service is live and missing things, and finding all of them is its own project.

And the hole gets deeper as your standards evolve. You tighten a security policy. You raise the backup retention bar. You decide every service now needs structured failure-mode documentation. Without Atlas, that's a fleet-wide migration — find every service, check it, fix what doesn't comply, hope you found them all. The new standard sits in a doc somewhere; the existing fleet still reflects yesterday's standard; the gap widens until something breaks. With Atlas, you update the rule. The next pipeline run audits every service against the new standard, applies the fix where it's unambiguous, and surfaces the rest for review. Standards stop being aspirations written in markdown — they become structure that propagates.

With Atlas, all three gaps close. Retiring a service: update the canonical entity, the pipeline regenerates every consumer, the next session starts current. Creating a service: the rules that govern "what a service must have" are entities the agent reads and applies — backups configured, alerting wired, documentation registered, conventions checked, not because the agent remembered but because the structure made forgetting impossible. Changing a standard: edit the rule, regenerate, the fleet converges.

The human stays in conversation. The agent goes from "edit five files and hope you didn't miss anything" to "update one entity and let the pipeline propagate." Standards stop being aspirational checklists and become structural requirements that get applied by default. Your stack and your agent's understanding of your stack don't drift apart, because they're rendered from the same source.

This is the actual bet: **AI-collaborative work scales when humans and agents share canonical truth, when standards live as structure rather than memory, and when changing the structure propagates without manual fan-out.** Atlas is the substrate that makes all three real.

---

## Architecture

Atlas is composed of four named layers, each doing one thing.

**The canonical store** holds your stack as data. Projects, services, servers, skills, agents, vocabularies — each is a YAML entity with a schema that gets validated. Stored in a Git repository, so every state of your system is a commit and every change is a diff. This is the substrate of truth.

**The generation pipeline** reads entities and emits artifacts. Configs, documentation, agent context, dashboards — anything downstream that needs to know what's in your stack. Generators are pluggable; you write one for each consumer that needs a view of your data. Edit an entity, regenerate, every consumer updates.

**The rule engine** holds your standards as data. Backup policy, security policy, naming conventions, what-a-service-must-have — each is a Rule entity. Rules are referenceable by generators (so new services get scaffolded against current standards) and by drift detection (so the existing fleet gets audited against current standards). Change a rule once; the change propagates.

**Drift detection and self-repair** close the loop between canonical and reality. Drift detection runs as part of the pipeline, comparing what your entities say against what's actually deployed, documented, and configured. For unambiguous gaps, self-repair applies the fix automatically. For ambiguous ones, it surfaces the gap for review. The fleet converges on the standard rather than diverging from it.

These four layers split across two boundaries.

**Core** is substrate-agnostic: schemas, vocabularies, entities, validation, the pipeline orchestrator, and generators that produce universal artifacts. The canonical store and rule engine live here.

**Extensions** are substrate-specific: generators and rules that target a particular environment. An AWS extension generates CloudFormation and reads state via boto3. A Kubernetes extension emits manifests and reads cluster state. A bare-metal extension generates systemd units and reads from `/etc`. Each plugs into the same pipeline.

**Additive contract**: extensions add to core; they never override. A substrate that needs different behavior does so by adding a more specific rule, not by suppressing a core one. This keeps the substrate-agnostic guarantee real.

---

## Who this is for

Atlas is for the operator running real infrastructure — the homelab person with too many services, the small team accumulating config sprawl, the SRE drowning in standards-evolution-tracking, the developer who's noticed they're spending too much time re-explaining their stack to AI agents. Anyone whose stack has accumulated more places-where-state-lives than they can hold in their head.

If you have three services, you don't need this. If you're an enterprise platform team, you have larger tools. Atlas sits in the middle: one operator or a small team running real infrastructure, working alongside AI agents, tired of chasing the same fact across five files.

---

## Implementation status

Atlas is being built in layers. The boundary between what works today and what's coming is clear:

**Working today:**

- Canonical store: seven entity types, full schema validation, substantive entity coverage
- Generation pipeline: orchestrator with auto-discovery across core and extensions
- Rule engine foundation: Rule entities exist as a first-class type; generators can reference them
- One reference extension demonstrating the substrate boundary

**In active development:**

- Drift detection: the audit half of the loop — comparing canonical to reality
- Self-repair: the convergence half — applying unambiguous fixes, surfacing ambiguous ones

**Designed, not yet built:**

- Read API: an MCP server exposing entities to agents directly, so agents don't have to read YAML
- Write API: a structured way for agents to propose entity changes without going through plans

The design anticipates each. The substrate boundary established in the architecture means each can be added without rearchitecture.

---

## How Atlas is built

Every change to Atlas itself originates from a written plan that passes a five-question structural integrity check before execution. Execution is by an AI coding agent working against the plan's acceptance criteria. Every commit traces back to a plan. Every plan traces back to first-principles design documents.

This isn't ceremony — it's how AI-collaborative work gets made auditable. The plans are short. The check is fast. The result is a codebase where the design intent is inspectable and where large refactors don't accumulate quiet drift.

This discipline is also a working demonstration of the broader bet. A codebase that's collaboratively built by humans and agents needs canonical structure for both to share. Atlas is built using the same pattern Atlas exists to enable.

---

## Why YAML + Python + Git

Boring on purpose. Atlas stores its own state in plain text files in a Git repository. No database, no service to deploy, no migration story. If you can read YAML and run Python, you can read Atlas's state. If the pipeline breaks, every entity is still a flat file you can `grep`. The substrate of truth has to be more durable than any tool that reads it.
