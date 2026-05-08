from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from .conventions import VocabRef, validate_iso8601_timestamp

_DSL_PATTERN = re.compile(
    r"^([a-z_][a-z0-9_]*)\s+where\s+([a-z_][a-z0-9_.]*)\s+"
    r"(equals|not_equals|is_null|is_not_null|contains)(?:\s+(.+))?$"
)


class Rule(BaseModel):
    """Rule entity model for Atlas structural assertions."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

    scope: VocabRef
    severity: VocabRef

    applies_to: str = Field(..., min_length=1)
    must_satisfy: str = Field(..., min_length=1)

    enforcement_point: VocabRef
    on_violation: str = Field(..., min_length=1)

    authored_by: str = Field(..., min_length=1)

    created_at: datetime
    updated_at: datetime

    @field_validator("applies_to", "must_satisfy")
    @classmethod
    def validate_dsl_expression(cls, value: str) -> str:
        expr = value.strip()
        match = _DSL_PATTERN.fullmatch(expr)
        if match is None:
            raise ValueError(
                "DSL expression must match '<entity_type> where <field_path> <op> [<value>]'"
            )

        op = match.group(3)
        rhs = match.group(4)

        if op in {"is_null", "is_not_null"}:
            if rhs is not None:
                raise ValueError(f"operator '{op}' must not include a value")
            return expr

        if rhs is None or not rhs.strip():
            raise ValueError(f"operator '{op}' requires a value")

        return expr

    @model_validator(mode="after")
    def validate_model(self) -> "Rule":
        self.created_at = validate_iso8601_timestamp(self.created_at)
        self.updated_at = validate_iso8601_timestamp(self.updated_at)

        if self.scope.vocab_id != "rule_scopes":
            raise ValueError("scope must reference vocab:rule_scopes:<value>")

        if self.severity.vocab_id != "rule_severities":
            raise ValueError("severity must reference vocab:rule_severities:<value>")

        if self.enforcement_point.vocab_id != "enforcement_points":
            raise ValueError("enforcement_point must reference vocab:enforcement_points:<value>")

        return self
