#!/usr/bin/env python3
"""Atlas MCP Read API — exposes the canonical entity store over streamable-http.

Port: 8105 (lan-only)
Auth: X-API-Key header
Transport: streamable-http at /mcp
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from tools.llm_client import get_llm_runtime_info, route_telegram_intent
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


def _validate_domain_tags(domain_tags: list[str] | None) -> list[str] | None:
    if domain_tags is None:
        return None

    if not isinstance(domain_tags, list):
        raise ValueError("domain_tags must be a list of lowercase strings")

    normalized: list[str] = []
    seen: set[str] = set()
    for tag in domain_tags:
        if not isinstance(tag, str):
            raise ValueError("domain_tags must be a list of lowercase strings")
        cleaned = tag.strip()
        if not cleaned:
            raise ValueError("domain_tags cannot contain empty strings")
        if cleaned != cleaned.lower():
            raise ValueError("domain_tags must be lowercase")
        if cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)

    return normalized


_TASK_STATUS_VALUES = {"open", "in_progress", "blocked", "resolved", "deferred"}
_TASK_PRIORITY_VALUES = {"critical", "high", "medium", "low"}


def _slugify_token(value: str, fallback: str = "task") -> str:
    token = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return token or fallback


def _resolve_project_id(project: str) -> str:
    store = _get_store()
    projects = store.get("project", {})
    if project in projects:
        return project

    matches = []
    needle = project.strip().lower()
    for project_id, model in projects.items():
        payload = _model_to_dict(model)
        if str(payload.get("name", "")).strip().lower() == needle:
            matches.append(project_id)

    if not matches:
        raise ValueError(f"Project '{project}' not found by id or exact name.")
    if len(matches) > 1:
        raise ValueError(f"Project name '{project}' is ambiguous. Matching ids: {sorted(matches)}")
    return matches[0]


def _next_task_id(project_id: str, title: str, source: str, source_request_id: str) -> str:
    tasks = _get_store().get("task", {})
    if source_request_id:
        stable_seed = f"{project_id}|{source}|{source_request_id}"
        stable_suffix = hashlib.sha1(stable_seed.encode("utf-8")).hexdigest()[:10]
        candidate = f"{project_id}-task-{stable_suffix}"
        if candidate not in tasks:
            return candidate

    title_token = _slugify_token(title, fallback="task")[:24]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    candidate = f"{project_id}-{title_token}-{stamp}"
    if candidate not in tasks:
        return candidate

    nonce = 2
    while f"{candidate}-{nonce}" in tasks:
        nonce += 1
    return f"{candidate}-{nonce}"


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
- create_kb_doc(path, content, confirm?, commit?): create docs/kb markdown via Atlas (single sanctioned write path)
- update_kb_doc(path, content, confirm?, commit?): update docs/kb markdown via Atlas (single sanctioned write path)
- check_drift(service_id?, force?): reality probes — reads cached result by default; force=True runs live

Write tools (propose-confirm pattern — preview first, then confirm=True to apply):
- add_project(id, name, summary, category, status, concept_doc, gdrive_folder?, domain_tags?): add new project (autonomous)
- update_project(id, confirm?, status?, category?, summary?, domain_tags?, ...): update project fields
- add_service(id, name, summary, service_type, lifecycle, deployment_path, ...): add new service (autonomous)
- update_service(id, confirm?, lifecycle?, port?, ...): update service fields
- retire_service(id, confirm?): set service lifecycle to retired
- add_task(project, title, next_action, closure_test, ...): add canonical task (autonomous)
- update_task(id, confirm?, status?, priority?, ...): update task fields

Task query tools:
- get_task(id): read one task
- list_tasks(project?, status?, priority?, limit?): list tasks with optional filters
- list_open_tasks(project?, limit?): list only open/in_progress/blocked tasks

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
def route_telegram_intent_tool(user_text: str, context_hint: str = "") -> dict[str, Any]:
    """Route a Telegram ops message into a structured intent using the Atlas LLM policy gate.

    Returns JSON with intent, side_effect, confidence, action/container/service/lines, and model usage metadata.
    """
    if not user_text.strip():
        return {
            "intent": "unknown",
            "side_effect": "none",
            "confidence": 0.0,
            "action": "",
            "container": "",
            "service": "",
            "lines": 50,
            "reason": "empty input",
            "error": True,
            "cost_capped": False,
        }
    return route_telegram_intent(user_text=user_text, context_hint=context_hint)


@mcp.tool()
def llm_cost_summary_tool() -> dict[str, Any]:
    """Return Atlas LLM runtime model and spend summary (daily + process run)."""
    return get_llm_runtime_info()


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
def list_tasks(project: str = "", status: str = "", priority: str = "", limit: int = 200) -> list[dict[str, Any]]:
    """List task entities. Optional filters: project (id or exact name), status, priority."""
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")
    if status and status not in _TASK_STATUS_VALUES:
        raise ValueError(f"status must be one of: {sorted(_TASK_STATUS_VALUES)}")
    if priority and priority not in _TASK_PRIORITY_VALUES:
        raise ValueError(f"priority must be one of: {sorted(_TASK_PRIORITY_VALUES)}")

    project_id = _resolve_project_id(project) if project else ""

    store = _get_store()
    tasks = store.get("task", {})
    result: list[dict[str, Any]] = []
    for task_id, task in sorted(tasks.items()):
        payload = _model_to_dict(task)
        if project_id and payload.get("project_id") != project_id:
            continue
        if status and payload.get("status") != status:
            continue
        if priority and payload.get("priority") != priority:
            continue

        result.append(
            {
                "id": task_id,
                "project_id": payload.get("project_id"),
                "title": payload.get("title"),
                "status": payload.get("status"),
                "priority": payload.get("priority"),
                "next_action": payload.get("next_action"),
                "updated_at": payload.get("updated_at"),
            }
        )
        if len(result) >= limit:
            break
    return result


@mcp.tool()
def list_open_tasks(project: str = "", limit: int = 200) -> list[dict[str, Any]]:
    """List open task entities (status in open, in_progress, blocked)."""
    open_states = {"open", "in_progress", "blocked"}
    tasks = list_tasks(project=project, status="", priority="", limit=1000)
    filtered = [task for task in tasks if task.get("status") in open_states]
    return filtered[:limit]


@mcp.tool()
def get_task(id: str) -> dict[str, Any]:
    """Return the full task entity for the given id."""
    store = _get_store()
    tasks = store.get("task", {})
    task = tasks.get(id)
    if task is None:
        ids = sorted(tasks.keys())
        raise ValueError(f"Task '{id}' not found. Known ids: {ids}")
    return _model_to_dict(task)


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
    gdrive_folder: str = "",
    code_repo: str = "",
    remote: str = "",
    domain_tags: list[str] | None = None,
) -> dict[str, Any]:
    """Add a new project entity to the Atlas store. Autonomous — writes and commits immediately.

    category: vocab value_id, e.g. 'current', 'live', 'blocked', 'defer', 'archive'
    status: vocab value_id, e.g. 'concept', 'active', 'paused', 'complete'
    concept_doc: path relative to services root, e.g. 'docs/kb/Projects/Foo/10-CONCEPT/FOO_CONCEPT.md'
    gdrive_folder: legacy Drive path metadata, optional; Drive retired as authoring surface 2026-05-09
    domain_tags: optional list of lowercase domain labels
    """
    store = _get_store()
    if id in store.get("project", {}):
        raise ValueError(f"Project '{id}' already exists. Use update_project to modify it.")

    validated_tags = _validate_domain_tags(domain_tags)
    now = _now_iso()
    data: dict[str, Any] = {
        "id": id,
        "name": name,
        "summary": summary,
        "category": f"vocab:lifecycle_categories:{category}",
        "status": f"vocab:project_statuses:{status}",
        "concept_doc": concept_doc,
        "created_at": now,
        "updated_at": now,
    }
    if gdrive_folder:
        data["gdrive_folder"] = gdrive_folder
    if code_repo:
        data["code_repo"] = code_repo
    if remote:
        data["remote"] = remote
    if validated_tags is not None:
        data["domain_tags"] = validated_tags

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
    domain_tags: list[str] | None = None,
) -> dict[str, Any]:
    """Update fields on an existing project entity.

    Returns a before/after preview when confirm=False (default). Call again with confirm=True to apply.
    Only non-empty scalar arguments are applied. status/category accept value_ids (e.g. 'active', 'current').
    domain_tags is applied when provided (including an empty list to clear tags).
    """
    store = _get_store()
    projects = store.get("project", {})
    if id not in projects:
        raise ValueError(f"Project '{id}' not found. Known ids: {sorted(projects.keys())}")

    rel_path = f"entities/projects/{id}.yaml"
    abs_path = REPO_ROOT / rel_path
    current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}

    validated_tags = _validate_domain_tags(domain_tags)
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
    if validated_tags is not None:
        after["domain_tags"] = validated_tags
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
    container_name: str = "",
    restartable: str = "",
    tier: str = "",
    expected_state: str = "",
    protected_high_use: str = "",
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
    if container_name:
        data["container_name"] = container_name
    if restartable:
        data["restartable"] = restartable.strip().lower() in {"1", "true", "yes", "on"}
    if tier:
        data["tier"] = tier
    if expected_state:
        data["expected_state"] = expected_state
    if protected_high_use:
        data["protected_high_use"] = protected_high_use.strip().lower() in {"1", "true", "yes", "on"}
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
    container_name: str = "",
    restartable: str = "",
    tier: str = "",
    expected_state: str = "",
    protected_high_use: str = "",
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
    if container_name:
        after["container_name"] = container_name
    if restartable:
        after["restartable"] = restartable.strip().lower() in {"1", "true", "yes", "on"}
    if tier:
        after["tier"] = tier
    if expected_state:
        after["expected_state"] = expected_state
    if protected_high_use:
        after["protected_high_use"] = protected_high_use.strip().lower() in {"1", "true", "yes", "on"}
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


@mcp.tool()
def add_task(
    project: str,
    title: str,
    next_action: str,
    closure_test: str,
    status: str = "open",
    priority: str = "medium",
    task_type: str = "general",
    why_now: str = "",
    owner_lane: str = "",
    blocked_on: str = "",
    blocked_by_task_ids: list[str] | None = None,
    source: str = "manual",
    source_ref: str = "",
    source_request_id: str = "",
    due_date: str = "",
    notes: str = "",
) -> dict[str, Any]:
    """Add a canonical task entity. Project can be id or exact project name."""
    if status not in _TASK_STATUS_VALUES:
        raise ValueError(f"status must be one of: {sorted(_TASK_STATUS_VALUES)}")
    if priority not in _TASK_PRIORITY_VALUES:
        raise ValueError(f"priority must be one of: {sorted(_TASK_PRIORITY_VALUES)}")

    project_id = _resolve_project_id(project)
    normalized_source = _slugify_token(source, fallback="manual")

    store = _get_store()
    tasks = store.get("task", {})
    if source_request_id:
        for existing_task in tasks.values():
            payload = _model_to_dict(existing_task)
            if (
                payload.get("project_id") == project_id
                and payload.get("source") == normalized_source
                and payload.get("source_request_id") == source_request_id
            ):
                return {
                    "ok": True,
                    "idempotent": True,
                    "task_id": payload.get("id"),
                    "project_id": project_id,
                    "task": payload,
                }

    task_id = _next_task_id(project_id, title, normalized_source, source_request_id)
    now = _now_iso()

    data: dict[str, Any] = {
        "id": task_id,
        "project_id": project_id,
        "title": title,
        "status": status,
        "priority": priority,
        "task_type": task_type,
        "next_action": next_action,
        "closure_test": closure_test,
        "source": normalized_source,
        "created_at": now,
        "updated_at": now,
    }
    if why_now:
        data["why_now"] = why_now
    if owner_lane:
        data["owner_lane"] = owner_lane
    if blocked_on:
        data["blocked_on"] = blocked_on
    if blocked_by_task_ids:
        data["blocked_by_task_ids"] = blocked_by_task_ids
    if source_ref:
        data["source_ref"] = source_ref
    if source_request_id:
        data["source_request_id"] = source_request_id
    if due_date:
        data["due_date"] = due_date
    if notes:
        data["notes"] = notes
    if status == "resolved":
        data["resolved_at"] = now

    result = _write_and_commit("tasks", task_id, data, f"feat: add task {task_id} via Atlas Write API")
    if "error" in result:
        return result
    return {
        "ok": True,
        "idempotent": False,
        "task_id": task_id,
        "project_id": project_id,
        **result,
    }


@mcp.tool()
def update_task(
    id: str,
    confirm: bool = False,
    status: str = "",
    priority: str = "",
    title: str = "",
    next_action: str = "",
    closure_test: str = "",
    owner_lane: str = "",
    blocked_on: str = "",
    notes: str = "",
    due_date: str = "",
) -> dict[str, Any]:
    """Update fields on an existing task entity via propose-confirm pattern."""
    store = _get_store()
    tasks = store.get("task", {})
    if id not in tasks:
        raise ValueError(f"Task '{id}' not found. Known ids: {sorted(tasks.keys())}")

    rel_path = f"entities/tasks/{id}.yaml"
    abs_path = REPO_ROOT / rel_path
    current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}
    after = dict(current_data)

    if status:
        if status not in _TASK_STATUS_VALUES:
            raise ValueError(f"status must be one of: {sorted(_TASK_STATUS_VALUES)}")
        after["status"] = status
    if priority:
        if priority not in _TASK_PRIORITY_VALUES:
            raise ValueError(f"priority must be one of: {sorted(_TASK_PRIORITY_VALUES)}")
        after["priority"] = priority
    if title:
        after["title"] = title
    if next_action:
        after["next_action"] = next_action
    if closure_test:
        after["closure_test"] = closure_test
    if owner_lane:
        after["owner_lane"] = owner_lane
    if blocked_on:
        after["blocked_on"] = blocked_on
    if notes:
        after["notes"] = notes
    if due_date:
        after["due_date"] = due_date

    effective_status = after.get("status", "open")
    if effective_status == "resolved":
        after["resolved_at"] = _now_iso()
    else:
        after.pop("resolved_at", None)

    after["updated_at"] = _now_iso()

    if not confirm:
        return {
            "action": "preview",
            "id": id,
            "before": current_data,
            "after": after,
            "note": "Call update_task(id=..., confirm=True, ...) with the same args to apply.",
        }

    return _write_and_commit("tasks", id, after, f"chore: update task {id} via Atlas Write API")


@mcp.tool()
def bootstrap_tasks_from_projects(project: str = "", confirm: bool = False, limit: int = 500) -> dict[str, Any]:
    """Backfill canonical tasks from project next_action and open_items fields.

    project: optional project id or exact name to scope bootstrap
    confirm: preview by default; set True to write tasks
    """
    if limit < 1 or limit > 2000:
        raise ValueError("limit must be between 1 and 2000")

    target_project_id = _resolve_project_id(project) if project else ""

    store = _get_store()
    projects = store.get("project", {})
    task_store = store.get("task", {})

    existing_refs: set[str] = set()
    for task_model in task_store.values():
        payload = _model_to_dict(task_model)
        source_ref = payload.get("source_ref")
        if isinstance(source_ref, str) and source_ref:
            existing_refs.add(source_ref)

    proposals: list[dict[str, Any]] = []
    for project_id, project_model in sorted(projects.items()):
        if target_project_id and project_id != target_project_id:
            continue

        payload = _model_to_dict(project_model)
        status_value = str(payload.get("status", {}).get("value_id", "")).strip()
        next_action = str(payload.get("next_action") or "").strip()
        open_items = payload.get("open_items", []) or []
        if next_action:
            source_ref = f"project:{project_id}:next_action"
            if source_ref not in existing_refs:
                proposals.append(
                    {
                        "project_id": project_id,
                        "title": f"Bootstrap next action for {project_id}",
                        "next_action": next_action,
                        "closure_test": "Execution evidence captured and project next_action updated.",
                        "priority": "medium",
                        "status": "open",
                        "task_type": "migration",
                        "source": "bootstrap",
                        "source_ref": source_ref,
                    }
                )

        for item in open_items:
            item_id = str(item.get("id") or "").strip()
            item_desc = str(item.get("description") or "").strip()
            if not item_id or not item_desc:
                continue
            source_ref = f"project:{project_id}:open_item:{item_id}"
            if source_ref in existing_refs:
                continue
            proposals.append(
                {
                    "project_id": project_id,
                    "title": f"Bootstrap open item {item_id}",
                    "next_action": item_desc,
                    "closure_test": "Open item resolved and removed from project.open_items.",
                    "priority": "high",
                    "status": "open",
                    "task_type": "migration",
                    "source": "bootstrap",
                    "source_ref": source_ref,
                }
            )

        # Seed a minimum tracking task when an active/in_progress project has
        # no canonical next_action and no open items to bootstrap from.
        if status_value in {"active", "in_progress"} and not next_action and not open_items:
            source_ref = f"project:{project_id}:task_tracking_gap"
            if source_ref not in existing_refs:
                proposals.append(
                    {
                        "project_id": project_id,
                        "title": f"Bootstrap tracking gap for {project_id}",
                        "next_action": (
                            "Define the immediate next action for this project and "
                            "decompose follow-on work into canonical tasks."
                        ),
                        "closure_test": (
                            "Project has a current next_action and at least one "
                            "maintained canonical task."
                        ),
                        "priority": "medium",
                        "status": "open",
                        "task_type": "tracking_gap",
                        "source": "bootstrap",
                        "source_ref": source_ref,
                    }
                )

        if len(proposals) >= limit:
            break

    preview = {
        "action": "preview" if not confirm else "apply",
        "count": len(proposals),
        "sample": proposals[:20],
    }
    if not confirm:
        preview["note"] = "Call bootstrap_tasks_from_projects(confirm=True) to apply."
        return preview

    created: list[str] = []
    errors: list[dict[str, Any]] = []
    for proposal in proposals:
        task_id = _next_task_id(
            proposal["project_id"],
            proposal["title"],
            proposal["source"],
            proposal["source_ref"],
        )
        now = _now_iso()
        data = {
            "id": task_id,
            "project_id": proposal["project_id"],
            "title": proposal["title"],
            "status": proposal["status"],
            "priority": proposal["priority"],
            "task_type": proposal["task_type"],
            "next_action": proposal["next_action"],
            "closure_test": proposal["closure_test"],
            "source": proposal["source"],
            "source_ref": proposal["source_ref"],
            "created_at": now,
            "updated_at": now,
        }
        result = _write_and_commit("tasks", task_id, data, f"feat: bootstrap task {task_id} via Atlas Write API")
        if "error" in result:
            errors.append({"task_id": task_id, "error": result["error"]})
        else:
            created.append(task_id)

    return {
        "action": "apply",
        "requested": len(proposals),
        "created": len(created),
        "failed": len(errors),
        "created_task_ids": created,
        "errors": errors,
    }


@mcp.tool()
def sync_project_next_actions_from_tasks(project: str = "", confirm: bool = False, limit: int = 200) -> dict[str, Any]:
    """Backfill empty project next_action values from canonical open tasks.

    Selects the most recently updated open task per project and copies its
    next_action into the project entity when project next_action is empty.
    """
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")

    target_project_id = _resolve_project_id(project) if project else ""
    store = _get_store()
    projects = store.get("project", {})
    tasks = store.get("task", {})

    open_states = {"open", "in_progress", "blocked"}
    tasks_by_project: dict[str, list[dict[str, Any]]] = {}
    for task_model in tasks.values():
        payload = _model_to_dict(task_model)
        if payload.get("status") not in open_states:
            continue
        project_id = str(payload.get("project_id") or "").strip()
        if not project_id:
            continue
        tasks_by_project.setdefault(project_id, []).append(payload)

    proposals: list[dict[str, str]] = []
    for project_id, project_model in sorted(projects.items()):
        if target_project_id and project_id != target_project_id:
            continue
        payload = _model_to_dict(project_model)
        status_value = str(payload.get("status", {}).get("value_id", "")).strip()
        if status_value not in {"active", "in_progress"}:
            continue

        current_next = str(payload.get("next_action") or "").strip()
        if current_next:
            continue

        project_tasks = tasks_by_project.get(project_id, [])
        if not project_tasks:
            continue

        project_tasks.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        chosen = project_tasks[0]
        chosen_next = str(chosen.get("next_action") or "").strip()
        if not chosen_next:
            continue

        proposals.append(
            {
                "project_id": project_id,
                "task_id": str(chosen.get("id") or ""),
                "next_action": chosen_next,
            }
        )
        if len(proposals) >= limit:
            break

    if not confirm:
        return {
            "action": "preview",
            "count": len(proposals),
            "sample": proposals[:20],
            "note": "Call sync_project_next_actions_from_tasks(confirm=True) to apply.",
        }

    updated: list[str] = []
    errors: list[dict[str, Any]] = []
    for proposal in proposals:
        project_id = proposal["project_id"]
        rel_path = f"entities/projects/{project_id}.yaml"
        abs_path = REPO_ROOT / rel_path
        current_data: dict[str, Any] = yaml.safe_load(abs_path.read_text(encoding="utf-8")) or {}
        current_data["next_action"] = proposal["next_action"]
        current_data["updated_at"] = _now_iso()
        result = _write_and_commit(
            "projects",
            project_id,
            current_data,
            f"chore: sync project next_action for {project_id} from task {proposal['task_id']}",
        )
        if "error" in result:
            errors.append({"project_id": project_id, "error": result["error"]})
        else:
            updated.append(project_id)

    return {
        "action": "apply",
        "requested": len(proposals),
        "updated": len(updated),
        "failed": len(errors),
        "updated_projects": updated,
        "errors": errors,
    }


DEFAULT_OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_KB_DOC_ROOT = Path("/opt/stack/services/docs/kb")
DEFAULT_KB_OUTPUT_DIR = DEFAULT_KB_DOC_ROOT / "Projects" / "Atlas" / "40-OUTPUT"
DEFAULT_SERVICES_REPO_ROOT = Path("/opt/stack/services")
KB_ROOT_ALLOWED_FILES = {
    "Start Here.md",
    "Standards.md",
    "Project Index.md",
    "The Latest.md",
    "System Log.md",
}


def _services_repo_root() -> Path:
    return Path(os.environ.get("ATLAS_SERVICES_REPO_ROOT", str(DEFAULT_SERVICES_REPO_ROOT))).resolve()


def _kb_doc_root() -> Path:
    return Path(os.environ.get("ATLAS_KB_DOC_ROOT", str(DEFAULT_KB_DOC_ROOT))).resolve()


def _is_kb_stage_name(stage_name: str) -> bool:
    return bool(re.match(r"^\d{2}-[A-Z0-9-]+$", stage_name))


def _resolve_kb_rel_path(path: str) -> tuple[Path, Path]:
    if not path or not path.strip():
        raise ValueError("Path is required")

    rel = Path(path.strip())
    if rel.is_absolute():
        raise ValueError("Absolute paths are not allowed")
    if any(part == ".." for part in rel.parts):
        raise ValueError("Path traversal is not allowed")

    root = _kb_doc_root()
    target = (root / rel).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise ValueError(f"Invalid doc path: {path!r}")
    return rel, target


def _is_allowed_kb_write(rel: Path) -> bool:
    if rel.suffix.lower() != ".md":
        return False

    parts = rel.parts
    if len(parts) == 1 and parts[0] in KB_ROOT_ALLOWED_FILES:
        return True

    if len(parts) < 4:
        return False
    if parts[0] != "Projects":
        return False
    if not _is_kb_stage_name(parts[2]):
        return False

    return True


def _sha256_text(content: str) -> str:
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=path.parent,
        prefix=".tmp-",
        suffix=".md",
    ) as tmp:
        tmp.write(content)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_name = tmp.name
    os.replace(temp_name, path)


def _git_commit_paths(repo_root: Path, rel_paths: list[str], message: str) -> dict[str, Any]:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "atlas-mcp",
        "GIT_COMMITTER_NAME": "atlas-mcp",
        "GIT_AUTHOR_EMAIL": "atlas-mcp@um790.local",
        "GIT_COMMITTER_EMAIL": "atlas-mcp@um790.local",
    }

    for rel_path in rel_paths:
        add = subprocess.run(
            ["git", "add", "-A", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if add.returncode != 0:
            return {"error": f"git add failed for {rel_path}: {add.stderr.strip() or add.stdout.strip()}"}

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if diff.returncode == 0:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "ok": True,
            "sha": head.stdout.strip() if head.returncode == 0 else "",
            "committed": False,
        }

    commit = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )
    if commit.returncode != 0:
        return {"error": f"git commit failed: {commit.stderr.strip() or commit.stdout.strip()}"}

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return {
        "ok": True,
        "sha": head.stdout.strip() if head.returncode == 0 else "",
        "committed": True,
    }


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
def create_kb_doc(path: str, content: str, confirm: bool = False, commit: bool = True) -> dict[str, Any]:
    """Create a markdown document under services/docs/kb/ via Atlas.

    Single sanctioned KB write path. Uses propose-confirm by default.
    Set confirm=True to apply the write.
    """
    rel, target = _resolve_kb_rel_path(path)
    if not _is_allowed_kb_write(rel):
        raise ValueError(
            "KB write path is not allowed by policy. "
            "Allowed: root canonical docs or Projects/<Project>/<NN-STAGE>/<file>.md"
        )

    exists = target.exists()
    after_hash = _sha256_text(content)

    if not confirm:
        return {
            "action": "preview",
            "operation": "create_kb_doc",
            "path": rel.as_posix(),
            "exists": exists,
            "after_hash": after_hash,
            "commit": commit,
            "note": "Call create_kb_doc(..., confirm=True) to apply.",
        }

    if exists:
        raise FileExistsError(f"KB doc already exists: {rel.as_posix()}")

    _atomic_write_text(target, content)
    file_hash = _sha256_file(target)

    commit_sha = ""
    committed = False
    if commit:
        repo_root = _services_repo_root()
        try:
            repo_rel = str(target.resolve().relative_to(repo_root.resolve()))
        except ValueError as exc:
            raise ValueError(f"KB doc path is outside repo root {repo_root}: {target}") from exc

        result = _git_commit_paths(repo_root, [repo_rel], f"docs: create {rel.as_posix()} via Atlas KB Write API")
        if "error" in result:
            return {
                "status": "error",
                "path": rel.as_posix(),
                "file_hash": file_hash,
                "commit_sha": "",
                "error": result["error"],
            }
        commit_sha = result.get("sha", "")
        committed = bool(result.get("committed", False))

    return {
        "status": "ok",
        "operation": "create_kb_doc",
        "path": rel.as_posix(),
        "file_hash": file_hash,
        "commit_sha": commit_sha,
        "committed": committed,
    }


@mcp.tool()
def update_kb_doc(path: str, content: str, confirm: bool = False, commit: bool = True) -> dict[str, Any]:
    """Update a markdown document under services/docs/kb/ via Atlas.

    Single sanctioned KB write path. Uses propose-confirm by default.
    Set confirm=True to apply the write.
    """
    rel, target = _resolve_kb_rel_path(path)
    if not _is_allowed_kb_write(rel):
        raise ValueError(
            "KB write path is not allowed by policy. "
            "Allowed: root canonical docs or Projects/<Project>/<NN-STAGE>/<file>.md"
        )

    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"KB doc not found: {rel.as_posix()}")

    before_hash = _sha256_file(target)
    after_hash = _sha256_text(content)

    if not confirm:
        return {
            "action": "preview",
            "operation": "update_kb_doc",
            "path": rel.as_posix(),
            "before_hash": before_hash,
            "after_hash": after_hash,
            "changed": before_hash != after_hash,
            "commit": commit,
            "note": "Call update_kb_doc(..., confirm=True) to apply.",
        }

    _atomic_write_text(target, content)
    file_hash = _sha256_file(target)

    commit_sha = ""
    committed = False
    if commit:
        repo_root = _services_repo_root()
        try:
            repo_rel = str(target.resolve().relative_to(repo_root.resolve()))
        except ValueError as exc:
            raise ValueError(f"KB doc path is outside repo root {repo_root}: {target}") from exc

        result = _git_commit_paths(repo_root, [repo_rel], f"docs: update {rel.as_posix()} via Atlas KB Write API")
        if "error" in result:
            return {
                "status": "error",
                "path": rel.as_posix(),
                "file_hash": file_hash,
                "commit_sha": "",
                "error": result["error"],
            }
        commit_sha = result.get("sha", "")
        committed = bool(result.get("committed", False))

    return {
        "status": "ok",
        "operation": "update_kb_doc",
        "path": rel.as_posix(),
        "file_hash": file_hash,
        "commit_sha": commit_sha,
        "committed": committed,
    }


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
