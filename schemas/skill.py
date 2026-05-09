from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import TypedRef, VocabRef, validate_iso8601_timestamp


class SkillPublishTarget(BaseModel):
    """Publish destination for generated SKILL.md content."""

    target_id: str = Field(..., min_length=1)
    output_path: str = Field(..., min_length=1)


class SkillFrontmatter(BaseModel):
    """Frontmatter emitted in generated SKILL.md files."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    context: Optional[str] = None


class Skill(BaseModel):
    """Skill entity model for reusable operator/agent skill definitions."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    context_mode: VocabRef
    publish_targets: list[SkillPublishTarget] = Field(default_factory=list)
    frontmatter: SkillFrontmatter
    body: str
    applies_when: Optional[str] = None
    related_skills: list[TypedRef] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_model(self) -> "Skill":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        if self.context_mode.vocab_id != "context_modes":
            raise ValueError("context_mode must reference vocab:context_modes:<value>")

        expected_frontmatter_context = (
            "fork" if self.context_mode.value_id == "fork" else None
        )
        if self.frontmatter.context != expected_frontmatter_context:
            raise ValueError(
                "frontmatter.context must be 'fork' when context_mode is fork, else null"
            )

        return self