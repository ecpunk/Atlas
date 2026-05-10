# Public mirror

The Atlas framework is published publicly at https://github.com/ecpunk/Atlas.

The public repo contains framework files only — schemas, vocabularies, generators, tools, framework rules, the reference UM790 extension structure, and example entities. It does NOT contain operator-personal data (Project, Service, Server, Skill, Agent entities live only in this private working copy).

Sync model: framework changes (schema additions, generator updates, new framework rules) get cherry-picked into atlas-public manually and pushed. Entity data never syncs.

## Sync workflow

Use this workflow for each public framework update.

1. Make and validate framework change in `/opt/stack/atlas-store`.
2. Identify the atlas-store commit(s) containing framework-only changes.
3. Cherry-pick those commit(s) into `/opt/stack/atlas-public`.
4. Resolve any merge drift only within framework files.
5. Run validation in atlas-public before push.
6. Push atlas-public `main` to `origin`.
7. Record sync result (commit IDs and date) in project status/session note.

## Guardrails

1. Never copy `entities/projects`, `entities/services`, `entities/servers`, `entities/skills`, or `entities/agents` from private store into atlas-public.
2. Public mirror includes schemas, vocabularies, generators, tools, framework rules, extension scaffolding, and examples only.
3. If a commit mixes framework and operator data, split it before sync.

## Quick checks

```bash
git -C /opt/stack/atlas-public status -sb
git -C /opt/stack/atlas-public remote -v
git -C /opt/stack/atlas-public branch --show-current
python /opt/stack/atlas-public/tools/validate.py
```
