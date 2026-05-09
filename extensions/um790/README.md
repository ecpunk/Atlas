# UM790 Extension

Substrate-specific Atlas extension for the UM790 home server stack.

## Scope
Provides generators, rules, and (future) detectors for resources hosted on UM790: systemd units, nginx vhosts, Docker Compose projects, the platform service catalog, and the knowledge-server MCP.

## Contract
Extensions are **additive only**. UM790 rules and generators add to core; they never override core behavior. If UM790 needs different behavior than core, it does so by adding a more specific rule, not by suppressing a core rule.

## What this extension owns
- `generators/kb_buckets.py` — knowledge-server VALID_STAGES
- `generators/service_catalog.py` — platform/service-catalog.json
- `generators/servers_index.py` — UM790 server inventory

## Future
- `rules/` — UM790-specific rules (port assignments, auth-gate patterns, FAILURE MODES requirements)
- `detectors/` — drift detectors that walk UM790 paths
- `probes/` — reality probes for systemd units, docker compose, nginx
