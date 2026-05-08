from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from .conventions import validate_iso8601_timestamp


class VocabularyValue(BaseModel):
    """Single value entry in a controlled vocabulary."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    semantics: str = Field(..., min_length=1)
    physical_location: Optional[str] = None
    deprecated: bool = False
    deprecated_reason: Optional[str] = None


class Vocabulary(BaseModel):
    """Vocabulary definition containing constrained allowed values."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    purpose: str = Field(..., min_length=1)
    values: list[VocabularyValue] = Field(default_factory=list)
    extension_policy: Literal["open", "closed"]
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_model(self) -> "Vocabulary":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        ids = [value.id for value in self.values]
        duplicates = sorted({value_id for value_id in ids if ids.count(value_id) > 1})
        if duplicates:
            dupes = ", ".join(duplicates)
            raise ValueError(f"duplicate vocabulary value id(s): {dupes}")

        return self
