from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import TypedRef, VocabRef, validate_iso8601_timestamp


class ServiceAuth(BaseModel):
    """Authentication configuration for a service endpoint."""

    mechanism: str  # e.g., "api_key", "oauth", "none"
    header: Optional[str] = None
    env_var: Optional[str] = None
    key_file: Optional[str] = None
    notes: Optional[str] = None


class Service(BaseModel):
    """Service entity model for Atlas runtime service metadata."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    service_type: VocabRef
    lifecycle: VocabRef

    host: TypedRef
    deployment_path: str = Field(..., min_length=1)
    port: Optional[int] = None
    health_endpoint: Optional[str] = None
    systemd_unit: Optional[str] = None
    network_binding: Optional[str] = None  # "localhost", "lan", "tailscale", "public"
    auth: Optional[ServiceAuth] = None
    remote: Optional[str] = None

    owned_by: TypedRef
    depends_on: list[TypedRef] = Field(default_factory=list)

    # Docker-specific operational metadata (applies to docker_container service_type)
    container_name: Optional[str] = None   # docker container name for health / restart ops
    restartable: Optional[bool] = None     # whether ops scripts may restart this container
    tier: Optional[str] = None            # operational tier: "critical", "standard", "optional"
    backup_unit: Optional[str] = None     # systemd unit name for backup job (e.g. "minecraft-backup-vanilla.service")

    last_health_check: Optional[datetime] = None
    last_health_status: Optional[VocabRef] = None

    failure_modes: list[str] = Field(default_factory=list)
    resource_budget_ram_mb: Optional[int] = Field(default=None, ge=0)

    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> "Service":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        if self.last_health_check is not None:
            self.last_health_check = validate_iso8601_timestamp(self.last_health_check)

        return self