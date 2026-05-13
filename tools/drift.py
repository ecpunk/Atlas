from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FIX_TIER = Literal["auto", "propose", "flag"]

DRIFT_KINDS = Literal[
    "kb_orphan_dir",          # kb/Projects dir with no atlas-store entity
    "catalog_only_service",   # service in catalog.json with no atlas-store entity
    "broken_concept_doc",     # project entity concept_doc path does not exist on disk
    "orphaned_output_file",   # file in 40-OUTPUT/ not claimed by any generator
    "monitoring_baseline_gap",  # running service missing container_name or systemd_unit
    "monitoring_health_gap",    # running service has a port but no health_endpoint
    "monitoring_resource_budget_gap",  # running service missing resource_budget policy metadata
    "platform_probe_drift",  # atlas_probe_latest indicates runtime drift for a service
    "legacy_stage3_alert",   # legacy operator-kernel stage3 engine emitted failing alert state
    "task_missing_next_action",  # active/in_progress project has no next_action
    "task_missing_open_work",  # active/in_progress project has no open canonical task
    "task_tracking_gap",  # active/in_progress project missing both next_action and open canonical task
]


@dataclass
class DriftRecord:
    kind: str                         # one of DRIFT_KINDS
    entity_type: str                  # "project", "service", "output_file"
    id: str                           # kb dir name, catalog key, or filename
    detail: str                       # human-readable description
    fix_tier: FIX_TIER               # auto | propose | flag
    normalized_id: str = ""           # for kb orphans: the kebab-case normalized ID
    extra: dict = field(default_factory=dict)  # kind-specific context

    def __str__(self) -> str:
        return f"[{self.fix_tier.upper()}] {self.kind} / {self.entity_type} / {self.id}: {self.detail}"
