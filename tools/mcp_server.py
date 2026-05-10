#!/usr/bin/env python3
"""Atlas MCP Read API — exposes the canonical entity store over streamable-http.

Port: 8105 (lan-only)
Auth: X-API-Key header
Transport: streamable-http at /mcp
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from tools.store import Store, load_store

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8105
DEFAULT_MCP_PATH = "/mcp"
DEFAULT_API_KEY_FILE = REPO_ROOT / ".secrets" / "api_key.txt"

_store: Store | None = None


def _get_store() -> Store:
    global _store
    if _store is None:
        _store = load_store(REPO_ROOT)
    return _store


def _invalidate_store() -> None:
    global _store
    _store = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_commit(rel_path: str, message: str) -> dict[str, Any]:
    """Stage one file and commit it in REPO_ROOT. Returns {"ok": True} or {"error": ...}."""
    add = subprocess.run(
        ["git", "add", rel_path],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if add.returncode != 0:
        return {"error": f"git add failed: {add.stderr.strip() or add.stdout.strip()}"}

    commit = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=15,
        env={**os.environ, "GIT_AUTHOR_NAME": "atlas-mcp", "GIT_COMMITTER_NAME": "atlas-mcp",
             "GIT_AUTHOR_EMAIL": "atlas-mcp@um790.local", "GIT_COMMITTER_EMAIL": "atlas-mcp@um790.local"},
    )
    if commit.returncode != 0:
        return {"error": f"git commit failed: {commit.stderr.strip() or commit.stdout.strip()}"}
    return {"ok": True, "sha": commit.stdout.strip().split()[-1] if commit.stdout.strip() else ""}


def _write_and_commit(entity_dir: str, entity_id: str, data: dict[str, Any], message: str) -> dict[str, Any]:
    """Write entity YAML and commit. Validates schema via load_store after write."""
    rel_path = f"entities/{entity_dir}/{entity_id}.yaml"
    abs_path = REPO_ROOT / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True), encoding="utf-8")

    result = _git_commit(rel_path, message)
    _invalidate_store()
    # Trigger pipeline post-commit hook validation
    try:
        _get_store()
    except Exception as exc:
        return {"error": f"Entity written and committed but schema validation failed: {exc}"}
    return result


def _api_key() -> str:
    env_key = os.environ.get("ATLAS_MCP_API_KEY", "").strip()
    if env_key:
        return env_key
    key_file = Path(os.environ.get("ATLAS_MCP_API_KEY_FILE", str(DEFAULT_API_KEY_FILE)))
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    return ""


def _check_auth(provided_key: str) -> bool:
    expected = _api_key()
    if not expected:
        return True  # no key configured — open (local-only use)
    return provided_key == expected


def _model_to_dict(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    return obj


MCP_INSTRUCTIONS = """You are connected to the Atlas canonical entity store for the UM790 homelab.

Atlas is the single source of truth for stack definitions: projects, services, servers, agents, rules, and vocabularies.

Read tools:
- get_project(id): full project entity
- list_projects(category?, status?): filtered project list
- get_service(id): full service entity
- list_services(): all services with key fields
- get_server(id): server entity
- get_vocabulary(id): vocabulary with all values
- get_rule(id) / list_rules(scope?, severity?): rule entities
- get_agent(id) / list_agents(): agent definitions
- stack_summary(): entity counts — use this for orientation

Bridge / output tools:
- get_output(name): read a generated output file from atlas-store/outputs/ (e.g. "Service Catalog.md")
- get_kb_doc(name): read a knowledge base doc from services/docs/kb/ (e.g. "Start Here.md")
- check_drift(service_id?, force?): reality probes — reads cached result by default; force=True runs live

Write tools (propose-confirm pattern — preview first, then confirm=True to apply):
- add_project(id, name, summary, category, status, concept_doc, gdrive_folder): add new project (autonomous)
- update_project(id, confirm?, status?, category?, summary?, ...): update project fields
- add_service(id, name, summary, service_type, lifecycle, deployment_path, ...): add new service (autonomous)
- update_service(id, confirm?, lifecycle?, port?, ...): update service fields
- retire_service(id, confirm?): set service lifecycle to retired

Use stack_summary() first when you need an overview of what's in the store.
"""

mcp = FastMCP(
    "AtlasMCP",
    instructions=MCP_INSTRUCTIONS,
    host=os.environ.get("ATLAS_MCP_HOST", DEFAULT_HOST),
    port=int(os.environ.get("ATLAS_MCP_PORT", str(DEFAULT_PORT))),
    streamable_http_path=os.environ.get("ATLAS_MCP_PATH", DEFAULT_MCP_PATH),
)


@mcp.tool()
def stack_summary() -> dict[str, Any]:
    """Return counts of each entity type in the store. Use this for orientation."""
    store = _get_store()
    summary: dict[str, Any] = {}
    for kind, entities in store.items():
        summary[kind] = len(entities)
    return summary


@mcp.tool()
def list_projects(category: str = "", status: str = "") -> list[dict[str, Any]]:
    """List all projects. Optionally filter by category (e.g. 'current', 'live', 'blocked', 'defer', 'archive') or status."""
    store = _get_store()
    projects = store.get("project", {})
    result = []
    for pid, project in sorted(projects.items()):
        p = _model_to_dict(project)
        if category and p.get("category", {}).get("value_id") != category:
            continue
        if status and p.get("status", {}).get("value_id") != status:
            continue
        result.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "category": p.get("category", {}).get("value_id"),
            "status": p.get("status", {}).get("value_id"),
            "summary": p.get("summary", "").strip(),
        })
    return result


@mcp.tool()
def get_project(id: str) -> dict[str, Any]:
    """Return the full project entity for the given id."""
    store = _get_store()
    projects = store.get("project", {})
    project = projects.get(id)
    if project is None:
        ids = sorted(projects.keys())
        raise ValueError(f"Project '{id}' not found. Known ids: {ids}")
    return _model_to_dict(project)


@mcp.tool()
def list_services() -> list[dict[str, Any]]:
    """List all services with key operational fields."""
    store = _get_store()
    services = store.get("service", {})
    result = []
    for sid, service in sorted(services.items()):
        s = _model_to_dict(service)
        result.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "service_type": s.get("service_type", {}).get("value_id"),
            "lifecycle": s.get("lifecycle", {}).get("value_id"),
            "host": s.get("host", {}).get("id"),
            "port": s.get("port"),
            "health_endpoint": s.get("health_endpoint"),
        })
    return result


@mcp.tool()
def get_service(id: str) -> dict[str, Any]:
    """Return the full service entity for the given id."""
    store = _get_store()
    services = store.get("service", {})
    service = services.get(id)
    if service is None:
        ids = sorted(services.keys())
        raise ValueError(f"Service '{id}' not found. Known ids: {ids}")
    return _model_to_dict(service)


@mcp.tool()
def get_server(id: str) -> dict[str, Any]:
    """Return the full server entity for the given id."""
    store = _get_store()
    servers = store.get("server", {})
    server = servers.get(id)
    if server is None:
        ids = sorted(servers.keys())
        raise ValueError(f"Server '{id}' not found. Known ids: {ids}")
    return _model_to_dict(server)


@mcp.tool()
def get_vocabulary(id: str) -> dict[str, Any]:
    """Return a vocabulary with all its values. Example ids: lifecycle_categories, service_types, agent_lanes."""
    store = _get_store()
    vocabs = store.get("vocabulary", {})
    vocab = vocabs.get(id)
    if vocab is None:
        ids = sorted(vocabs.keys())
        raise ValueError(f"Vocabulary '{id}' not found. Known ids: {ids}")
    return _model_to_dict(vocab)


@mcp.tool()
def list_rules(scope: str = "", severity: str = "") -> list[dict[str, Any]]:
    """List rules. Optionally filter by scope or severity."""
    store = _get_store()
    rules = store.get("rule", {})
    result = []
    for rid, rule in sorted(rules.items()):
        r = _model_to_dict(rule)
        if scope and r.get("scope", {}).get("value_id") != scope:
            continue
        if severity and r.get("severity", {}).get("value_id") != severity:
            continue
        result.append({
            "id": r.get("id"),
            "scope": r.get("scope", {}).get("value_id"),
            "severity": r.get("severity", {}).get("value_id"),
            "applies_to": r.get("applies_to"),
            "must_satisfy": r.get("must_satisfy", "").strip(),
        })
    return result


@mcp.tool()
def get_rule(id: str) -> dict[str, Any]:
    """Return the full rule entity for the given id."""
    store = _get_store()
    rules = store.get("rule", {})
    rule = rules.get(id)
    if rule is None:
        ids = sorted(rules.keys())
        raise ValueError(f"Rule '{id}' not found. Known ids: {ids}")
    return _model_to_dict(rule)


@mcp.tool()
def list_agents() -> list[dict[str, Any]]:
    """List all agent entities with key capability fields."""
    store = _get_store()
    agents = store.get("agent", {})
    result = []
    for aid, agent in sorted(agents.items()):
        a = _model_to_dict(agent)
        result.append({
            "id": a.get("id"),
            "name": a.get("name"),
            "model_family": a.get("model_family"),
            "interface": a.get("interface", {}).get("value_id"),
            "primary_lane": a.get("primary_lane", {}).get("value_id"),
        })
    return result


@mcp.tool()
def get_agent(id: str) -> dict[str, Any]:
    """Return the full agent entity for the given id."""
    store = _get_store()
    agents = store.get("agent", {})
    agent = agents.get(id)
    if agent is None:
        ids = sorted(agents.keys())
        raise ValueError(f"Agent '{id}' not found. Known ids: {ids}")
    return _model_to_dict(agent)


# ---------------------------------------------------------------------------
# Write API
# ---------------------------------------------------------------------------

@mcp.tool()
def add_project(
    id: str,
    name: str,
    summary: str,
    category: str,
    status: str,
    concept_doc: str,
    gdrive_folder: str,
    code_repo: str = "",
    remote: str = "",
) -> dict[str, Any]:
    """Add a new project entity to the Atlas store. Autonomous — writes and commits immediately.

    category: vocab value_id, e.g. 'current', 'live', 'blocked', 'defer', 'archive'
    status: vocab value_id, e.g. 'concept', 'active', 'paused', 'complete'
    concept_doc: path relative to services root, e.g. 'docs/kb/Projects/Foo/10-CONCEPT/FOO_CONCEPT.md'
    gdrive_folder: gdrive path, e.g. "gdrive:Jon's Projects/Projects/Current/Foo/" (optional; Drive retired as authoring surface 2026-05-09)
    """
    store = _get_store()
    if id in store.get("project", {}):
        raise ValueError(f"Project '{id}' already exists. Use update_project to modify it.")

    now = _now_iso()
    data: dict[str, Any] = {
        "id": id,
        "name": name,
        "summary": summary,
        "category": f"vocab:lifecycle_categories:{category}",
        "status": f"vocab:project_statuses:{status}",
        "concept_doc": concept_doc,
        "gdrive_folder": gdrive_folder,
        "created_at": now,
        "updated_at": now,
    }
    if code_repo:
        data["code_repo"] = code_repo
    if remote:
        data["remote"] = remote

    return _write_and_commit("projects", id, data, f"feat: add project {id} via Atlas Write API")


@mcp.tool()
def update_project(
    id: str,
    confirm: bool = False,
    status: str = "",
    status_detail: str = "",
    category: str = "",
    summary: str = "",
    last_done: str = "",
    next_action: str = "",
    blocked_on: str = "",
    code_repo: str = "",
    remote: str = "",
) -> dict[str, Any]:
    """Update fields on an existing project entity.

    Returns a before/after preview when confirm=False (default). Call again with confirm=True to apply.
    Only non-empty arguments are applied. status/category accept value_ids (e.g. 'active', 'current').
    """
    store = _get_store()
    projects = store.get("project", {})
    if id not in projects:
        raise ValueError(f"Project '{id}' not found. Known ids: {sorted(projects.keys())}")

    rel_path = f"entities/projects/{id}.yaml"
    abs_path = REPO_ROOT / rel_path
    current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}

    after = dict(current_data)
    if status:
        after["status"] = f"vocab:project_statuses:{status}"
    if status_detail:
        after["status_detail"] = status_detail
    if category:
        after["category"] = f"vocab:lifecycle_categories:{category}"
    if summary:
        after["summary"] = summary
    if last_done:
        after["last_done"] = last_done
    if next_action:
        after["next_action"] = next_action
    if blocked_on:
        after["blocked_on"] = blocked_on
    if code_repo:
        after["code_repo"] = code_repo
    if remote:
        after["remote"] = remote
    after["updated_at"] = _now_iso()

    if not confirm:
        return {
            "action": "preview",
            "id": id,
            "before": current_data,
            "after": after,
            "note": "Call update_project(id=..., confirm=True, ...) with the same args to apply.",
        }

    return _write_and_commit("projects", id, after, f"chore: update project {id} via Atlas Write API")


@mcp.tool()
def add_service(
    id: str,
    name: str,
    summary: str,
    service_type: str,
    lifecycle: str,
    deployment_path: str,
    port: int = 0,
    host: str = "server:um790",
    owned_by: str = "",
    health_endpoint: str = "",
    systemd_unit: str = "",
    remote: str = "",
) -> dict[str, Any]:
    """Add a new service entity to the Atlas store. Autonomous — writes and commits immediately.

    service_type: vocab value_id, e.g. 'mcp_http', 'docker_compose', 'systemd', 'static'
    lifecycle: vocab value_id, e.g. 'running', 'stopped', 'retired', 'planned'
    host: TypedRef string, default 'server:um790'
    owned_by: TypedRef string, e.g. 'project:atlas' (optional)
    """
    store = _get_store()
    if id in store.get("service", {}):
        raise ValueError(f"Service '{id}' already exists. Use update_service to modify it.")

    now = _now_iso()
    data: dict[str, Any] = {
        "id": id,
        "name": name,
        "summary": summary,
        "service_type": f"vocab:service_types:{service_type}",
        "lifecycle": f"vocab:service_lifecycles:{lifecycle}",
        "host": host,
        "deployment_path": deployment_path,
        "owned_by": owned_by or f"project:{id}",
        "created_at": now,
        "updated_at": now,
    }
    if port:
        data["port"] = port
    if health_endpoint:
        data["health_endpoint"] = health_endpoint
    if systemd_unit:
        data["systemd_unit"] = systemd_unit
    if remote:
        data["remote"] = remote

    return _write_and_commit("services", id, data, f"feat: add service {id} via Atlas Write API")


@mcp.tool()
def update_service(
    id: str,
    confirm: bool = False,
    lifecycle: str = "",
    port: int = 0,
    health_endpoint: str = "",
    systemd_unit: str = "",
    source_of_truth_doc: str = "",
    summary: str = "",
    remote: str = "",
) -> dict[str, Any]:
    """Update fields on an existing service entity.

    Returns a before/after preview when confirm=False (default). Call again with confirm=True to apply.
    lifecycle accepts value_ids (e.g. 'running', 'stopped', 'retired').
    """
    store = _get_store()
    services = store.get("service", {})
    if id not in services:
        raise ValueError(f"Service '{id}' not found. Known ids: {sorted(services.keys())}")

    rel_path = f"entities/services/{id}.yaml"
    abs_path = REPO_ROOT / rel_path
    current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}

    after = dict(current_data)
    if lifecycle:
        after["lifecycle"] = f"vocab:service_lifecycles:{lifecycle}"
    if port:
        after["port"] = port
    if health_endpoint:
        after["health_endpoint"] = health_endpoint
    if systemd_unit:
        after["systemd_unit"] = systemd_unit
    if source_of_truth_doc:
        after["source_of_truth_doc"] = source_of_truth_doc
    if summary:
        after["summary"] = summary
    if remote:
        after["remote"] = remote
    after["updated_at"] = _now_iso()

    if not confirm:
        return {
            "action": "preview",
            "id": id,
            "before": current_data,
            "after": after,
            "note": "Call update_service(id=..., confirm=True, ...) with the same args to apply.",
        }

    return _write_and_commit("services", id, after, f"chore: update service {id} via Atlas Write API")


@mcp.tool()
def retire_service(id: str, confirm: bool = False) -> dict[str, Any]:
    """Set a service lifecycle to 'retired' in the Atlas store.

    Returns a preview when confirm=False (default). Call again with confirm=True to apply.
    """
    store = _get_store()
    services = store.get("service", {})
    if id not in services:
        raise ValueError(f"Service '{id}' not found. Known ids: {sorted(services.keys())}")

    rel_path = f"entities/services/{id}.yaml"
    abs_path = REPO_ROOT / rel_path
    current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}

    after = dict(current_data)
    after["lifecycle"] = "vocab:service_lifecycles:retired"
    after["updated_at"] = _now_iso()

    if not confirm:
        return {
            "action": "preview",
            "id": id,
            "current_lifecycle": current_data.get("lifecycle"),
            "new_lifecycle": "vocab:service_lifecycles:retired",
            "note": "Call retire_service(id=..., confirm=True) to apply.",
        }

    return _write_and_commit("services", id, after, f"chore: retire service {id} via Atlas Write API")


DEFAULT_OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_KB_DOC_ROOT = Path("/opt/stack/services/docs/kb")
DEFAULT_KB_OUTPUT_DIR = DEFAULT_KB_DOC_ROOT / "Projects" / "Atlas" / "40-OUTPUT"


@mcp.tool()
def get_output(name: str) -> str:
    """Read a generated output file from Atlas output directories.

    Pass the filename exactly as it appears (e.g. 'Service Catalog.md',
    'Rules.md', 'Project Index (generated).md'). Returns the file content.
    """
    legacy_outputs_dir = Path(os.environ.get("ATLAS_OUTPUT_DIR", str(DEFAULT_OUTPUTS_DIR))).resolve()
    kb_outputs_dir = Path(os.environ.get("ATLAS_KB_OUTPUT_DIR", str(DEFAULT_KB_OUTPUT_DIR))).resolve()

    search_roots = [kb_outputs_dir, legacy_outputs_dir]
    for root in search_roots:
        target = (root / name).resolve()
        # Guard against path traversal for each root.
        if not str(target).startswith(str(root)):
            raise ValueError(f"Invalid output name: {name!r}")
        if target.exists():
            return target.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"Output '{name}' not found. Searched: {kb_outputs_dir}, {legacy_outputs_dir}. "
        "Run the Atlas pipeline generation step to refresh outputs."
    )


@mcp.tool()
def get_kb_doc(name: str) -> str:
    """Read a knowledge base document from services/docs/kb/.

    Pass a relative path such as 'Start Here.md', 'Standards.md', or
    'Projects/atlas/10-CONCEPT/ATLAS_CONCEPT.md'. Returns the file content.
    """
    kb_root = Path(os.environ.get("ATLAS_KB_DOC_ROOT", str(DEFAULT_KB_DOC_ROOT)))
    target = (kb_root / name).resolve()
    # Guard against path traversal
    if not str(target).startswith(str(kb_root.resolve())):
        raise ValueError(f"Invalid doc name: {name!r}")
    if not target.exists():
        raise FileNotFoundError(
            f"KB doc '{name}' not found under {kb_root}. "
            "Run Track A3 migration to populate services/docs/kb/."
        )
    return target.read_text(encoding="utf-8")


@mcp.tool()
def check_drift(service_id: str = "", force: bool = False) -> list[dict[str, Any]]:
    """Run reality probes against running services and report drift.

    By default reads the cached probe result written by the atlas-probe systemd
    timer (automations/state/atlas_probe_latest.json). Set force=True to run
    live probes and refresh the cache.

    Returns a list of per-service probe results. Each result has:
    - service_id, name, lifecycle
    - probes: list of {type, expected, actual, pass}
    - drift: bool — True if any probe failed

    Pass service_id to filter to one service; omit for all non-retired services.
    """
    PROBE_CACHE = Path("/opt/stack/services/automations/state/atlas_probe_latest.json")

    if not force and PROBE_CACHE.exists() and not service_id:
        try:
            import json as _json
            return _json.loads(PROBE_CACHE.read_text(encoding="utf-8")).get("results", [])
        except Exception:
            pass  # fall through to live run

    import tools.probe_runner as _probe_runner  # local import avoids startup overhead
    results = _probe_runner.run_probes(service_id)

    # Update cache on live run (only when probing all services)
    if not service_id:
        try:
            import json as _json
            from datetime import datetime as _dt, timezone as _tz
            PROBE_CACHE.parent.mkdir(parents=True, exist_ok=True)
            PROBE_CACHE.write_text(
                _json.dumps({
                    "generated_at": _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "total": len(results),
                    "drifted": sum(1 for r in results if r["drift"]),
                    "results": results,
                }, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass  # cache write failure is non-fatal

    return results


if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response
    from starlette.routing import Route

    expected_api_key = _api_key()

    class ApiKeyMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if request.method == "OPTIONS":
                return await call_next(request)
            if request.url.path.startswith("/.well-known/"):
                return await call_next(request)
            client_host = request.client.host if request.client else ""
            if client_host in ("127.0.0.1", "::1"):
                return await call_next(request)
            if not expected_api_key:
                return await call_next(request)  # no key configured — open
            provided = request.headers.get("x-api-key", "")
            if provided != expected_api_key:
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
            return await call_next(request)

    async def services_rest(request: Request) -> JSONResponse:
        """GET /services — returns all service entities as a JSON object keyed by id.

        Intended for machine consumers (e.g. catalog.py) that need structured
        data without navigating the MCP streamable-http protocol.
        """
        import json as _json
        from datetime import datetime as _dt
        store = _get_store()
        services = store.get("service", {})
        result: dict[str, Any] = {}
        for sid, service in sorted(services.items()):
            s = _model_to_dict(service)
            result[sid] = s

        def _default(obj: Any) -> Any:
            if isinstance(obj, _dt):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return Response(
            content=_json.dumps(result, default=_default),
            media_type="application/json",
        )

    host = os.environ.get("ATLAS_MCP_HOST", DEFAULT_HOST)
    port = int(os.environ.get("ATLAS_MCP_PORT", str(DEFAULT_PORT)))

    async def oauth_resource_metadata(request: Request) -> JSONResponse:
        base = str(request.base_url).rstrip("/")
        return JSONResponse({"resource": base, "authorization_servers": []})

    app = mcp.streamable_http_app()
    app.routes.insert(0, Route("/.well-known/oauth-protected-resource", oauth_resource_metadata, methods=["GET"]))
    app.routes.insert(0, Route("/services", services_rest, methods=["GET"]))
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "accept",
            "content-type",
            "mcp-protocol-version",
            "mcp-session-id",
            "last-event-id",
            "x-api-key",
        ],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
    )

    uvicorn.run(app, host=host, port=port)
