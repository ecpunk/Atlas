from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import TypedRef, VocabRef, validate_iso8601_timestamp


class PhaseEntry(BaseModel):
    """A single phase in a project's build plan."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)  # e.g. "done", "partial", "not_started"
    notes: Optional[str] = None


class OpenItem(BaseModel):
    """A tracked open item against a project."""

    id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    created: Optional[str] = None  # ISO date string


class Project(BaseModel):
    """Project entity model for Atlas canonical project metadata."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    category: VocabRef
    status: VocabRef
    status_detail: Optional[str] = None

    last_done: Optional[str] = None
    next_action: Optional[str] = None
    key_decisions: list[str] = Field(default_factory=list)
    key_insights: list[str] = Field(default_factory=list)
    blocked_on: Optional[str] = None

    concept_doc: str | None = Field(None)
    gdrive_folder: Optional[str] = None
    code_repo: Optional[str] = None
    remote: Optional[str] = None
    local_paths: list[str] = Field(default_factory=list)

    depends_on: list[TypedRef] = Field(default_factory=list)
    unlocks: list[TypedRef] = Field(default_factory=list)
    related_projects: list[TypedRef] = Field(default_factory=list)
    related_services: list[TypedRef] = Field(default_factory=list)

    domain_tags: list[str] = Field(default_factory=list)

    phases: list[PhaseEntry] = Field(default_factory=list)
    open_items: list[OpenItem] = Field(default_factory=list)

    last_touched: Optional[str] = None
    last_session: Optional[str] = None
    expected_cadence: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> "Project":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        if self.last_touched is not None:
            self.last_touched = validate_iso8601_timestamp(self.last_touched)
        if self.last_session is not None:
            self.last_session = validate_iso8601_timestamp(self.last_session)

        return self
