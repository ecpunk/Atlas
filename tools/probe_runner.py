#!/usr/bin/env python3
"""Atlas reality probes — compare canonical service entity state to actual running state.

For each non-retired service entity, runs probes against:
  - deployment_path  : filesystem exists check
  - systemd_unit     : systemctl is-active
  - port             : TCP connect on 127.0.0.1
  - health_endpoint  : HTTP GET status code

Returns a list of per-service drift reports.
"""
from __future__ import annotations

import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.store import load_store

SYSTEMD_TIMEOUT = 5   # seconds
PORT_TIMEOUT = 5       # seconds
HTTP_TIMEOUT = 10      # seconds

RETIRED_LIFECYCLE_ID = "retired"


def _probe_path(path: str) -> dict[str, Any]:
    exists = Path(path).exists()
    return {"type": "deployment_path", "expected": path, "actual": "exists" if exists else "missing", "pass": exists}


def _probe_systemd(unit: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", unit],
            capture_output=True,
            text=True,
            timeout=SYSTEMD_TIMEOUT,
            check=False,
        )
        state = result.stdout.strip() or result.stderr.strip() or "unknown"
    except subprocess.TimeoutExpired:
        state = "timeout"
    except FileNotFoundError:
        state = "systemctl-not-found"
    passed = state == "active"
    return {"type": "systemd_unit", "expected": "active", "actual": state, "pass": passed}


def _probe_port(port: int) -> dict[str, Any]:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=PORT_TIMEOUT):
            actual = "open"
            passed = True
    except (ConnectionRefusedError, OSError, socket.timeout):
        actual = "closed"
        passed = False
    return {"type": "port", "expected": f"open:{port}", "actual": actual, "pass": passed}


def _probe_http(url: str) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        scheme = urllib.parse.urlparse(url).scheme.lower()
        if scheme == "https":
            # Liveness probe only: allow self-signed/private certs to avoid false drift.
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT, context=ctx) as resp:
                status = resp.status
        else:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, OSError, TimeoutError):
        status = 0

    # 2xx/3xx = healthy; 4xx = server up but request was malformed (e.g. MCP streamable-http
    # rejects plain GET with 406) — treat as "alive"; 5xx or 0 = outage.
    SERVICE_DOWN_CODES = {0, 502, 503, 504}
    passed = status not in SERVICE_DOWN_CODES and status < 500
    actual = str(status) if status else "unreachable"
    return {"type": "health_endpoint", "expected": "not-5xx/unreachable", "actual": actual, "pass": passed}


def _lifecycle_id(service_dict: dict[str, Any]) -> str:
    """Extract lifecycle value_id from a service entity dict."""
    lifecycle = service_dict.get("lifecycle")
    if isinstance(lifecycle, dict):
        return lifecycle.get("value_id", "")
    if isinstance(lifecycle, str):
        # raw YAML form: "vocab:service_lifecycles:running"
        parts = lifecycle.split(":")
        return parts[-1] if parts else ""
    return ""


def run_probes(service_id: str = "") -> list[dict[str, Any]]:
    """Run probes for one service (if service_id given) or all non-retired services."""
    store = load_store(REPO_ROOT)
    services = store.get("service", {})

    if service_id:
        if service_id not in services:
            raise ValueError(f"Service '{service_id}' not found. Known ids: {sorted(services.keys())}")
        targets = {service_id: services[service_id]}
    else:
        targets = {sid: svc for sid, svc in services.items()
                   if _lifecycle_id(svc.model_dump()) != RETIRED_LIFECYCLE_ID}

    results: list[dict[str, Any]] = []

    for sid, svc in sorted(targets.items()):
        svc_dict = svc.model_dump()
        probes: list[dict[str, Any]] = []

        deployment_path = svc_dict.get("deployment_path")
        if deployment_path:
            probes.append(_probe_path(deployment_path))

        systemd_unit = svc_dict.get("systemd_unit")
        if systemd_unit:
            probes.append(_probe_systemd(systemd_unit))

        port = svc_dict.get("port")
        if port:
            probes.append(_probe_port(int(port)))

        health_endpoint = svc_dict.get("health_endpoint")
        if health_endpoint:
            if sid == "atlas-mcp":
                # Avoid self-probe deadlock: check_drift runs inside atlas-mcp.
                probes.append({
                    "type": "health_endpoint",
                    "expected": "not-5xx/unreachable",
                    "actual": "skipped-self-probe",
                    "pass": True,
                })
            else:
                probes.append(_probe_http(health_endpoint))

        drift = any(not p["pass"] for p in probes)
        results.append({
            "service_id": sid,
            "name": svc_dict.get("name", sid),
            "lifecycle": _lifecycle_id(svc_dict),
            "probes": probes,
            "drift": drift,
        })

    return results


if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(description="Run Atlas reality probes")
    parser.add_argument("--service", default="", help="probe a single service by id")
    args = parser.parse_args()

    try:
        results = run_probes(args.service)
        print(json.dumps(results, indent=2))
        drift_count = sum(1 for r in results if r["drift"])
        print(f"\n{len(results)} services probed. {drift_count} drifted.", file=sys.stderr)
        sys.exit(1 if drift_count else 0)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
