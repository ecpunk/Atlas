from __future__ import annotations

"""monitoring_coverage_check.py — score each running service entity for monitoring maturity.

Coverage dimensions (v1):
  container_name    — required for docker_container services
  systemd_unit      — required for systemd_unit services
  health_endpoint   — required for services with a port (network-reachable)
  restartable       — must be explicitly set (not None) for docker services
  resource_budget   — resource_budget_ram_mb should be set
  tier              — operational tier declared for docker services

Each dimension is scored independently. Services with ANY baseline gap
(container_name or systemd_unit missing) are surfaced as coverage gaps.
"""

from datetime import datetime, timezone
from pathlib import Path

from schemas.service import Service

NAME = "monitoring_coverage_check"
INPUTS = ["service:*"]
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Monitoring Coverage Report.md",
]

# service_type values that are Docker-based
_DOCKER_TYPES = {"docker_container"}
# service_type values that are systemd-managed (non-docker)
_SYSTEMD_TYPES = {"systemd_unit", "mcp_http", "mcp_stdio", "fastapi"}
# service_type values that are network-exposed (must have health_endpoint if port set)
_NETWORK_TYPES = {"docker_container", "mcp_http", "fastapi", "nginx_vhost"}

_ACTIVE_LIFECYCLES = {"running", "degraded"}


def _type_id(service: Service) -> str:
    return service.service_type.ref.split(":")[-1] if service.service_type else ""


def _lifecycle_id(service: Service) -> str:
    return service.lifecycle.ref.split(":")[-1] if service.lifecycle else ""


def _score(service: Service) -> dict:
    """Return per-dimension coverage result for a service."""
    stype = _type_id(service)
    dims: dict[str, bool | None] = {}  # None = not applicable

    # container_name — required for docker services
    if stype in _DOCKER_TYPES:
        dims["container_name"] = bool(service.container_name)
    else:
        dims["container_name"] = None

    # systemd_unit — required for pure systemd services
    if stype in _SYSTEMD_TYPES:
        dims["systemd_unit"] = bool(service.systemd_unit)
    else:
        dims["systemd_unit"] = None

    # health_endpoint — required if service has a port AND is network-exposed
    if service.port and stype in _NETWORK_TYPES:
        dims["health_endpoint"] = bool(service.health_endpoint)
    else:
        dims["health_endpoint"] = None

    # restartable — must be explicitly set (not None) for docker services
    if stype in _DOCKER_TYPES:
        dims["restartable"] = service.restartable is not None
    else:
        dims["restartable"] = None

    # resource_budget — expected for all active services (warn, not baseline)
    dims["resource_budget"] = service.resource_budget_ram_mb is not None

    # tier — expected for docker services
    if stype in _DOCKER_TYPES:
        dims["tier"] = bool(service.tier)
    else:
        dims["tier"] = None

    applicable = {k: v for k, v in dims.items() if v is not None}
    passed = sum(1 for v in applicable.values() if v)
    total = len(applicable)

    # Baseline gap: missing container_name or systemd_unit
    baseline_gap = (
        (dims["container_name"] is False)
        or (dims["systemd_unit"] is False)
    )

    # Health gap: has a port but no health_endpoint
    health_gap = dims["health_endpoint"] is False

    gaps = [k for k, v in applicable.items() if not v]

    return {
        "dims": dims,
        "passed": passed,
        "total": total,
        "gaps": gaps,
        "baseline_gap": baseline_gap,
        "health_gap": health_gap,
        "score_pct": int(100 * passed / total) if total else 100,
    }


def _bar(pct: int) -> str:
    filled = pct // 10
    return "█" * filled + "░" * (10 - filled)


def generate(store: dict) -> dict[str, str]:
    service_store: dict[str, Service] = store.get("service", {})

    active = {
        sid: svc
        for sid, svc in service_store.items()
        if _lifecycle_id(svc) in _ACTIVE_LIFECYCLES
    }

    scores = {sid: _score(svc) for sid, svc in active.items()}

    # Sort: baseline gaps first, then by score ascending
    ordered = sorted(
        active.keys(),
        key=lambda sid: (not scores[sid]["baseline_gap"], scores[sid]["score_pct"]),
    )

    baseline_gaps = [sid for sid in ordered if scores[sid]["baseline_gap"]]
    health_gaps = [sid for sid in ordered if scores[sid]["health_gap"] and not scores[sid]["baseline_gap"]]
    full_coverage = [sid for sid in ordered if not scores[sid]["baseline_gap"] and not scores[sid]["health_gap"]]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines: list[str] = [
        "# Monitoring Coverage Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Generated at: {now}",
        f"Active services (running + degraded): {len(active)}",
        f"Baseline gaps: {len(baseline_gaps)}",
        f"Health endpoint gaps: {len(health_gaps)}",
        f"Full coverage: {len(full_coverage)}",
        "",
        "---",
        "",
        "## Coverage Dimensions",
        "",
        "| Dimension | Applies to | Required? |",
        "|-----------|-----------|-----------|",
        "| `container_name` | docker_container | **Baseline** |",
        "| `systemd_unit` | systemd_unit, mcp_http, mcp_stdio, fastapi | **Baseline** |",
        "| `health_endpoint` | any service with a `port` | **Health** |",
        "| `restartable` | docker_container | Warn |",
        "| `resource_budget` | all | Warn |",
        "| `tier` | docker_container | Warn |",
        "",
        "---",
        "",
        "## Baseline Gaps (missing container_name or systemd_unit)",
        "",
        f"Count: {len(baseline_gaps)}",
        "",
    ]

    if not baseline_gaps:
        lines += ["_None — all active services have baseline coverage._", ""]
    else:
        lines += [
            "| Service | Type | Missing |",
            "|---------|------|---------|",
        ]
        for sid in baseline_gaps:
            svc = active[sid]
            s = scores[sid]
            missing = ", ".join(f"`{g}`" for g in s["gaps"])
            lines.append(f"| `{sid}` | {_type_id(svc)} | {missing} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Health Endpoint Gaps (has port, no health_endpoint)",
        "",
        f"Count: {len(health_gaps)}",
        "",
    ]

    if not health_gaps:
        lines += ["_None._", ""]
    else:
        lines += [
            "| Service | Port | Missing |",
            "|---------|------|---------|",
        ]
        for sid in health_gaps:
            svc = active[sid]
            s = scores[sid]
            missing = ", ".join(f"`{g}`" for g in s["gaps"])
            lines.append(f"| `{sid}` | {svc.port} | {missing} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Full Coverage Scorecard",
        "",
        "| Service | Type | Score | Gaps |",
        "|---------|------|-------|------|",
    ]

    for sid in ordered:
        svc = active[sid]
        s = scores[sid]
        bar = _bar(s["score_pct"])
        gap_str = ", ".join(f"`{g}`" for g in s["gaps"]) if s["gaps"] else "_none_"
        lines.append(f"| `{sid}` | {_type_id(svc)} | {bar} {s['score_pct']}% | {gap_str} |")

    lines.append("")

    return {OUTPUTS[0]: "\n".join(lines)}
