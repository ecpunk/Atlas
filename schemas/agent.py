from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import VocabRef, validate_iso8601_timestamp


class TrustCalibrationEntry(BaseModel):
    """Reliability calibration entry for a task pattern."""

    task_pattern: str = Field(..., min_length=1)
    reliability: VocabRef
    notes: Optional[str] = None


class Agent(BaseModel):
    """Agent entity model for Atlas operator-managed AI agents."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    model_family: str = Field(..., min_length=1)
    interface: VocabRef

    primary_lane: VocabRef
    secondary_lanes: list[VocabRef] = Field(default_factory=list)

    can_read: list[str] = Field(default_factory=list)
    can_write: list[str] = Field(default_factory=list)
    can_execute: list[str] = Field(default_factory=list)

    trust_calibration: list[TrustCalibrationEntry] = Field(default_factory=list)

    session_duration_typical_minutes: Optional[int] = None
    known_failure_modes: list[str] = Field(default_factory=list)
    known_strengths: list[str] = Field(default_factory=list)
    telemetry_source: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> "Agent":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)
        return self