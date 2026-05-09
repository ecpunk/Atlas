from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from schemas.conventions import TypedRef, VocabRef
from schemas.rule import Rule
from schemas.vocabulary import Vocabulary

NAME = "entity_check"
REQUIRES_LLM = True
INPUTS = ["rule:*"]
OUTPUTS = [
    "/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Entity Compliance Report.md"
]

_ENTITY_SUFFIX = "_entity"
_MISSING = object()

CheckResult = tuple[str, str, str]
RuleOutcome = tuple[str, str, str, str]


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _render_value(value: Any) -> str:
    if value is _MISSING:
        return "missing"
    if value is None:
        return "null"
    if isinstance(value, (VocabRef, TypedRef)):
        return str(value)
    if isinstance(value, BaseModel):
        return yaml.safe_dump(value.model_dump(mode="json"), sort_keys=False).strip()
    if isinstance(value, (list, tuple, set)):
        rendered = ", ".join(_render_value(item) for item in value)
        return f"[{rendered}]"
    if isinstance(value, dict):
        return yaml.safe_dump(value, sort_keys=False).strip()
    return str(value)


def _normalize_for_compare(value: Any) -> Any:
    if isinstance(value, (VocabRef, TypedRef)):
        return str(value)
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_normalize_for_compare(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_normalize_for_compare(item) for item in value)
    if isinstance(value, set):
        return {_normalize_for_compare(item) for item in value}
    if isinstance(value, dict):
        return {key: _normalize_for_compare(item) for key, item in value.items()}
    return value


def _parse_definition(raw: str) -> Any:
    try:
        parsed = yaml.safe_load(raw)
    except Exception:
        return raw.strip()

    if parsed is None:
        return raw.strip()
    return parsed


def _extract_field_name(raw: str) -> str:
    parsed = _parse_definition(raw)

    if isinstance(parsed, str):
        field = parsed.strip()
        if field:
            return field
        raise ValueError("check_definition must specify a field name")

    if isinstance(parsed, dict):
        field = parsed.get("field")
        if isinstance(field, str) and field.strip():
            return field.strip()

    raise ValueError("check_definition must be a field name string or mapping with field")


def _parse_field_value_definition(raw: str) -> tuple[str, Any, str]:
    parsed = _parse_definition(raw)

    if isinstance(parsed, dict):
        field = parsed.get("field")
        if not isinstance(field, str) or not field.strip():
            raise ValueError("field_value check_definition requires a non-empty field")

        mode_raw = parsed.get("mode", "equals")
        mode = str(mode_raw).strip().lower().replace(" ", "_")
        if mode not in {"equals", "contains"}:
            raise ValueError(f"Unsupported field_value mode: {mode}")

        if "value" not in parsed:
            raise ValueError("field_value check_definition requires a value")

        return field.strip(), parsed.get("value"), mode

    if isinstance(parsed, str):
        text = parsed.strip()
        if not text:
            raise ValueError("field_value check_definition must not be empty")

        if " contains " in text:
            field, expected_raw = text.split(" contains ", 1)
            mode = "contains"
        elif "==" in text:
            field, expected_raw = text.split("==", 1)
            mode = "equals"
        elif "=" in text:
            field, expected_raw = text.split("=", 1)
            mode = "equals"
        else:
            raise ValueError("field_value string definition must use contains, ==, or =")

        field = field.strip()
        expected_raw = expected_raw.strip()
        if not field:
            raise ValueError("field_value definition is missing field")
        if not expected_raw:
            raise ValueError("field_value definition is missing expected value")

        try:
            expected = yaml.safe_load(expected_raw)
        except Exception:
            expected = expected_raw

        return field, expected, mode

    raise ValueError("field_value check_definition must be a string or mapping")


def _resolve_vocab_ref(value: Any) -> VocabRef | None:
    if isinstance(value, VocabRef):
        return value
    if isinstance(value, str):
        try:
            return VocabRef.model_validate(value)
        except Exception:
            return None
    return None


def _entity_store_key(applies_to: str) -> str:
    if applies_to.endswith(_ENTITY_SUFFIX):
        return applies_to[: -len(_ENTITY_SUFFIX)]
    return applies_to


def _check_field_present(entity: BaseModel, check_definition: str) -> CheckResult:
    field = _extract_field_name(check_definition)
    value = getattr(entity, field, _MISSING)

    if value is _MISSING:
        return (
            "fail",
            f"Field '{field}' not found on entity.",
            f"{field}=missing",
        )

    if _is_blank(value):
        return (
            "fail",
            f"Field '{field}' is empty.",
            f"{field}={_render_value(value)}",
        )

    return (
        "pass",
        f"Field '{field}' is present.",
        f"{field}={_render_value(value)}",
    )


def _check_field_value(entity: BaseModel, check_definition: str) -> CheckResult:
    field, expected, mode = _parse_field_value_definition(check_definition)
    value = getattr(entity, field, _MISSING)

    if value is _MISSING:
        return (
            "fail",
            f"Field '{field}' not found on entity.",
            f"{field}=missing",
        )

    if _is_blank(value):
        return (
            "fail",
            f"Field '{field}' is empty.",
            f"{field}={_render_value(value)}",
        )

    actual_norm = _normalize_for_compare(value)
    expected_norm = _normalize_for_compare(expected)

    if mode == "contains":
        if isinstance(value, str):
            matched = str(expected) in value
        elif isinstance(value, (list, tuple, set)):
            matched = any(_normalize_for_compare(item) == expected_norm for item in value)
        else:
            matched = False
    else:
        matched = actual_norm == expected_norm

    detail = (
        f"Field '{field}' matches expected value."
        if matched
        else f"Field '{field}' does not match expected value."
    )
    expected_text = _render_value(expected)
    evidence = f"actual={_render_value(value)}; expected={expected_text}; mode={mode}"
    return ("pass" if matched else "fail", detail, evidence)


def _check_vocab_ref_valid(
    entity: BaseModel,
    check_definition: str,
    vocab_store: dict[str, Any],
) -> CheckResult:
    field = _extract_field_name(check_definition)
    value = getattr(entity, field, _MISSING)

    if value is _MISSING:
        return (
            "fail",
            f"Field '{field}' not found on entity.",
            f"{field}=missing",
        )

    if _is_blank(value):
        return (
            "fail",
            f"Field '{field}' is empty.",
            f"{field}={_render_value(value)}",
        )

    ref = _resolve_vocab_ref(value)
    if ref is None:
        return (
            "fail",
            f"Field '{field}' is not a valid vocabulary reference.",
            f"{field}={_render_value(value)}",
        )

    vocab = vocab_store.get(ref.vocab_id)
    if not isinstance(vocab, Vocabulary):
        return (
            "fail",
            f"Vocabulary '{ref.vocab_id}' not found.",
            f"{field}={ref}",
        )

    exists = any(item.id == ref.value_id for item in vocab.values)
    if not exists:
        return (
            "fail",
            f"Vocabulary value '{ref.value_id}' not found in '{ref.vocab_id}'.",
            f"{field}={ref}",
        )

    return (
        "pass",
        f"Field '{field}' resolves to an existing vocabulary value.",
        f"{field}={ref}",
    )


def _evaluate_rule(rule: Rule, entity: BaseModel, vocab_store: dict[str, Any]) -> CheckResult:
    kind = rule.check_kind.value_id

    if kind == "field_present":
        return _check_field_present(entity, rule.check_definition)
    if kind == "field_value":
        return _check_field_value(entity, rule.check_definition)
    if kind == "vocab_ref_valid":
        return _check_vocab_ref_valid(entity, rule.check_definition, vocab_store)

    return (
        "fail",
        f"Unsupported check_kind for entity_check: {kind}",
        f"check_kind={kind}",
    )


def _escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def _render_report(results: dict[str, list[tuple[Rule, list[RuleOutcome]]]]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entity_type_count = len(results)
    rule_count = sum(len(group) for group in results.values())

    lines: list[str] = [
        "# Entity Compliance Report",
        "",
        "AUTO-GENERATED from atlas-store Rule entities. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"Entity types scanned: {entity_type_count}",
        f"Rules applied: {rule_count}",
        "",
    ]

    for applies_to in sorted(results):
        lines.extend([f"## {applies_to}", ""])

        for rule, outcomes in results[applies_to]:
            pass_count = sum(1 for status, _, _, _ in outcomes if status == "pass")
            fail_count = sum(1 for status, _, _, _ in outcomes if status == "fail")
            action = rule.fix_action if rule.fix_action else "n/a"

            lines.extend(
                [
                    f"### {rule.name} (`{rule.id}`)",
                    f"- Summary: {pass_count} pass, {fail_count} fail",
                    f"- Suggested action: {action}",
                    "",
                ]
            )

            lines.append("| Outcome | Entity | Detail | Evidence |")
            lines.append("|---------|--------|--------|----------|")

            if not outcomes:
                lines.append("| n/a | n/a | no entities loaded for rule scope | n/a |")
                lines.append("")
                continue

            for status, entity_id, detail, evidence in outcomes:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            _escape_cell(status.upper()),
                            _escape_cell(entity_id),
                            _escape_cell(detail),
                            _escape_cell(evidence),
                        ]
                    )
                    + " |"
                )

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate(store: dict) -> dict[str, str]:
    rule_store = store.get("rule", {})
    rules = [item for item in rule_store.values() if isinstance(item, Rule)]
    entity_rules = sorted(
        [rule for rule in rules if rule.applies_to.endswith(_ENTITY_SUFFIX)],
        key=lambda item: (item.applies_to, item.id),
    )

    vocab_store = store.get("vocabulary", {})
    results: dict[str, list[tuple[Rule, list[RuleOutcome]]]] = {}

    for rule in entity_rules:
        entity_key = _entity_store_key(rule.applies_to)
        entity_store = store.get(entity_key, {})
        entities = [item for item in entity_store.values() if isinstance(item, BaseModel)]
        entities.sort(key=lambda item: getattr(item, "id", ""))

        outcomes: list[RuleOutcome] = []
        for entity in entities:
            status, detail, evidence = _evaluate_rule(rule, entity, vocab_store)
            entity_id = getattr(entity, "id", "(missing-id)")
            outcomes.append((status, str(entity_id), detail, evidence))

        results.setdefault(rule.applies_to, []).append((rule, outcomes))

    content = _render_report(results)
    output_path = OUTPUTS[0]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return {output_path: content}