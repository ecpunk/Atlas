from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import TypedRef, validate_iso8601_timestamp


class Server(BaseModel):
    """Server entity model for Atlas machine and hosting metadata."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    hostname: str = Field(..., min_length=1)
    ip: str = Field(..., min_length=1)

    hardware: str = Field(..., min_length=1)
    cpu: Optional[str] = None
    ram_gib: Optional[float] = None
    storage: list[str] = Field(default_factory=list)
    gpu: Optional[str] = None

    os: Optional[str] = None

    ram_committed_gib: Optional[float] = None
    ram_alert_floor_gib: Optional[float] = None
    swap_gib: Optional[float] = None

    hosts: list[TypedRef] = Field(default_factory=list)

    source_of_truth_doc: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> "Server":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)
        return self