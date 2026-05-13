from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import validate_iso8601_timestamp

_TASK_STATUSES = {"open", "in_progress", "blocked", "resolved", "deferred"}
_TASK_PRIORITIES = {"critical", "high", "medium", "low"}


class Task(BaseModel):
    """Canonical task entity for Atlas task tracking."""

    id: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)

    status: str = Field(default="open")
    priority: str = Field(default="medium")
    task_type: str = Field(default="general", min_length=1)

    next_action: str = Field(..., min_length=1)
    closure_test: str = Field(..., min_length=1)

    why_now: Optional[str] = None
    owner_lane: Optional[str] = None
    blocked_on: Optional[str] = None
    blocked_by_task_ids: list[str] = Field(default_factory=list)

    source: str = Field(default="manual", min_length=1)
    source_ref: Optional[str] = None
    source_request_id: Optional[str] = None

    notes: Optional[str] = None
    due_date: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_task(self) -> "Task":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)
        if self.resolved_at is not None:
            self.resolved_at = validate_iso8601_timestamp(self.resolved_at)

        if self.status not in _TASK_STATUSES:
            raise ValueError(f"status must be one of: {sorted(_TASK_STATUSES)}")
        if self.priority not in _TASK_PRIORITIES:
            raise ValueError(f"priority must be one of: {sorted(_TASK_PRIORITIES)}")

        if self.status == "resolved" and self.resolved_at is None:
            raise ValueError("resolved tasks must include resolved_at")
        if self.status != "resolved" and self.resolved_at is not None:
            raise ValueError("resolved_at can only be set when status='resolved'")

        return self
