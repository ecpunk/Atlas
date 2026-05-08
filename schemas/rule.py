from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .conventions import VocabRef, validate_iso8601_timestamp


class Rule(BaseModel):
    """Rule entity model for Atlas structural assertions."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

    scope: VocabRef
    severity: VocabRef

    applies_to: str = Field(..., min_length=1)
    check_kind: VocabRef
    check_definition: str = Field(..., min_length=1)
    fix_tier: VocabRef
    fix_action: Optional[str] = None

    enforcement_point: VocabRef
    on_violation: str = Field(..., min_length=1)

    authored_by: str = Field(..., min_length=1)

    created_at: datetime
    updated_at: datetime

    @field_validator("applies_to", "check_definition")
    @classmethod
    def normalize_non_empty_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be empty")
        return normalized

    @model_validator(mode="after")
    def validate_model(self) -> "Rule":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        if self.scope.vocab_id != "rule_scopes":
            raise ValueError("scope must reference vocab:rule_scopes:<value>")

        if self.severity.vocab_id != "rule_severities":
            raise ValueError("severity must reference vocab:rule_severities:<value>")

        if self.check_kind.vocab_id != "rule_check_kinds":
            raise ValueError("check_kind must reference vocab:rule_check_kinds:<value>")

        if self.fix_tier.vocab_id != "rule_fix_tiers":
            raise ValueError("fix_tier must reference vocab:rule_fix_tiers:<value>")

        if self.enforcement_point.vocab_id != "enforcement_points":
            raise ValueError("enforcement_point must reference vocab:enforcement_points:<value>")

        if self.fix_tier.value_id == "flag" and self.fix_action is not None:
            raise ValueError("fix_action must be null when fix_tier is vocab:rule_fix_tiers:flag")

        if self.fix_tier.value_id in {"auto", "propose"}:
            if self.fix_action is None or not self.fix_action.strip():
                raise ValueError("fix_action is required when fix_tier is auto or propose")

        return self
