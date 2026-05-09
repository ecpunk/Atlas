from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


def validate_iso8601_timestamp(value: datetime) -> datetime:
    """Validate a parsed ISO 8601 timestamp value."""
    if not isinstance(value, datetime):
        raise TypeError("timestamp must be a datetime")
    return value


class TypedRef(BaseModel):
    """Typed reference in the form entity_type:id."""

    entity_type: str = Field(..., min_length=1)
    id: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parse_typed_ref(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            parts = value.split(":", 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError("typed reference must be in the form entity_type:id")
            return {"entity_type": parts[0], "id": parts[1]}
        raise TypeError("typed reference must be a string or mapping")

    def __str__(self) -> str:
        return f"{self.entity_type}:{self.id}"


class VocabRef(BaseModel):
    """Vocabulary reference in the form vocab:vocab_id:value_id."""

    vocab_id: str = Field(..., min_length=1)
    value_id: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def parse_vocab_ref(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            parts = value.split(":")
            if len(parts) != 3 or parts[0] != "vocab" or not parts[1] or not parts[2]:
                raise ValueError("vocabulary reference must be in the form vocab:vocab_id:value_id")
            return {"vocab_id": parts[1], "value_id": parts[2]}
        raise TypeError("vocabulary reference must be a string or mapping")

    def __str__(self) -> str:
        return f"vocab:{self.vocab_id}:{self.value_id}"


class Provenance(BaseModel):
    """Signal provenance metadata for origin and propagation state."""

    origin: str = Field(..., min_length=1)
    timestamp: datetime
    status: VocabRef
    hold_down_until: Optional[datetime] = None
    hop_count: int = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_timestamps(self) -> "Provenance":
        self.timestamp = validate_iso8601_timestamp(self.timestamp)
        if self.hold_down_until is not None:
            self.hold_down_until = validate_iso8601_timestamp(self.hold_down_until)
        return self
