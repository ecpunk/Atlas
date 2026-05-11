# Atlas

Atlas is a canonical, agent-facing control plane for the systems you operate.
Agents, operators, automations, and dashboards read state, propose changes,
and act through a single typed (for now) surface -- governed by rules, validated against
schemas, and reconciled by a drift loop you do not have to write.

## The Problem Atlas Solves

Modern agent runtimes can call any tool, edit any file, and run any command.
What they cannot do is know whether the action is correct for your system,
consistent with prior decisions, or already known to be wrong. That context
has to live somewhere.

Most stacks scatter it. Some of the truth lives in configs, some in a wiki,
some in a teammate's head, some in a status page that was accurate last
Tuesday. When an agent -- or a human -- needs to answer "what services exist,
what rules govern them, and what is currently drifting" they get a different
answer from every source. The cost is not just confusion. It is unsafe
automation, because the executor has no ground truth to check itself against.

Atlas is where that context lives. One canonical home per fact, machine-
readable, schema-validated, and reachable through the same interface no
matter who is asking.

## How It Works

Four layers, each doing one job.

**Canonical store.** Typed YAML entities for the things you operate --
projects, services, servers, rules, agents, skills. Schemas enforce shape.
Vocabularies enforce values. Every fact has one home; nothing is hand-edited
into two places.

**Generation pipeline.** Generators read canonical entities and produce
operator-readable views -- service catalogs, project indexes, status reports,
compliance summaries. Generated views are never edited by hand. If a view is
wrong, the entity is wrong, or the generator is wrong, and you fix the cause.

**Rule engine.** Rules are entities too. They are enforced at validation
time (schema and reference checks) and at generation time (compliance and
plan checks). Adding a rule is a YAML change, not a code change. Rules catch
drift before it ships and catch bad edits regardless of who made them.

**Drift loop.** A scheduled reconciler compares intended state against
observed state, classifies the gap, and routes it: auto-remediate for safe
cleanup, propose for operator triage, flag for review. The loop runs on a
timer. Findings land back in the canonical store and surface through the
same interface as everything else.

## Architecture

```text
+-----------------------------------------------------------------------+
| Operators | Agents | Automations | UIs                                |
+-----------------------------------------------------------------------+
                                  |
                          same typed surface
                          same rules apply
                                  v
+-----------------------------------------------------------------------+
| Atlas MCP (read | propose | act | check)                              |
+-----------------------------------------------------------------------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
        v                         v                         v
+-------------------+   +----------------------+   +----------------------+
| Canonical Store   |-->| Generation Pipeline  |-->| Operator Views       |
| (typed YAML)      |   | (generators)         |   | (catalogs, indexes,  |
|                   |   |                      |   | reports)             |
| projects          |   | no hand-edits to     |   +----------------------+
| services          |   | generated views      |              ^
| servers           |   +----------------------+              |
| rules             |              ^                          |
| agents            |              |                          |
| skills            |      +-------+--------+                 |
| vocabularies      |      | Rule Engine    |                 |
+---------+---------+      | validation-time|                 |
          |                | + generation-  |                 |
          |                | time checks    |                 |
          |                +----------------+                 |
          |                                                   |
          +------------> +----------------------+ ------------+
                        | Drift Loop            |
                        | observe | classify    |
                        | auto | propose | flag |
                        +----------------------+
```

## The Agnostic Surface

Atlas does not care who is asking.

A human operator running a CLI, an agent in a Claude or Copilot session, a
dashboard polling for state, an automation reconciling drift -- all hit the
same typed surface with the same rules applied. The contract is the schema,
not the caller. Agents do not get a privileged shortcut, and they do not get
a weakened path. The rules that catch a careless human edit catch a confused
agent edit. The validation that protects a script protects a chat session.

This is the property that makes Atlas safe to wire into agent workflows.
The runtime executing the action is interchangeable. The system that decides
whether the action is allowed is not.

## What You Get If You Pull This Repo

Operational today:

- Canonical YAML store with schema and reference validation
- Generation pipeline producing operator-readable views and machine outputs
- Rule engine with entity and plan rule families
- Scheduled drift loop with auto, propose, and flag tiers
- MCP server exposing read and write tools for agent integration

Partial or in progress:

- Full provenance and loop-prevention metadata on operational signals
- Escalation calibration and daily operator briefing
- A handful of Layer-3 operational capabilities described in the concept doc

Atlas runs against a private operator stack here. Extension generators and
operator-specific entities are not part of the public framework. See
[PUBLIC.md](PUBLIC.md) for the mirror policy.

## Getting Started

```bash
git clone <this repo>
cd atlas-store
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Validate canonical entities and references
.venv/bin/python tools/validate.py

# Preview the full generation pipeline
.venv/bin/python tools/pipeline.py --dry-run

# Run the MCP server (default: 0.0.0.0:8105/mcp)
.venv/bin/python tools/mcp_server.py
```

The pipeline has additional flags for running a single generator, writing
outputs, and opting into LLM-enabled generators. Run `tools/pipeline.py
--help` for the surface, or `tools/pipeline.py --list` to see what is wired
up in your checkout.

## Repository Layout

- `schemas/` - Pydantic schemas for entities and conventions
- `vocabularies/` - Canonical vocabulary sets
- `entities/` - Canonical entity records (projects, services, rules, etc.)
- `generators/` - Core generators
- `extensions/` - Operator-specific generators and policies
- `tools/` - Validation, pipeline, drift, remediation, MCP server
- `staging/` - Propose-tier drift stubs awaiting triage

## License And Mirror

This repository is the working store. The public framework mirror lives at
[github.com/ecpunk/Atlas](https://github.com/ecpunk/Atlas) and excludes
operator-personal entity data. See [PUBLIC.md](PUBLIC.md) for what is and
is not mirrored.
