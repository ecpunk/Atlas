from __future__ import annotations

from schemas.rule import Rule
from schemas.vocabulary import Vocabulary

NAME = "rules_doc"
INPUTS = ["rule:*"]
OUTPUTS = ["-"]

HEADER = "AUTO-GENERATED from atlas-store/entities/rules/*.yaml - do not hand-edit."


def _collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def _escape_table_cell(text: str) -> str:
    return text.replace("|", "\\|")


def _build_vocab_display_maps(vocab_store: dict) -> dict[str, dict[str, str]]:
    display_maps: dict[str, dict[str, str]] = {}

    for vocab in vocab_store.values():
        if isinstance(vocab, Vocabulary):
            display_maps[vocab.id] = {value.id: value.name for value in vocab.values}

    return display_maps


def _resolve_vocab_value(display_maps: dict[str, dict[str, str]], vocab_id: str, value_id: str) -> str:
    values = display_maps.get(vocab_id)
    if values is None:
        raise ValueError(f"vocabulary file not found for '{vocab_id}'")

    value_name = values.get(value_id)
    if value_name is None:
        raise ValueError(f"vocabulary value '{value_id}' not found in '{vocab_id}'")

    return value_name


def generate(store: dict) -> dict[str, str]:
    display_maps = _build_vocab_display_maps(store.get("vocabulary", {}))

    rule_store = store.get("rule", {})
    rules = [item for item in rule_store.values() if isinstance(item, Rule)]
    rules.sort(key=lambda item: item.id)

    lines: list[str] = [
        "# Rules",
        "",
        HEADER,
        "",
        "| Rule | Scope | Severity | Applies to | Must satisfy | Enforcement |",
        "|------|-------|----------|------------|--------------|-------------|",
    ]

    for rule in rules:
        scope_name = _resolve_vocab_value(display_maps, rule.scope.vocab_id, rule.scope.value_id)
        severity_name = _resolve_vocab_value(display_maps, rule.severity.vocab_id, rule.severity.value_id)
        enforcement_name = _resolve_vocab_value(
            display_maps,
            rule.enforcement_point.vocab_id,
            rule.enforcement_point.value_id,
        )

        rule_name = _escape_table_cell(f"{rule.name} (`{rule.id}`)")
        applies_to = _escape_table_cell(rule.applies_to)
        must_satisfy = _escape_table_cell(rule.must_satisfy)

        lines.append(
            "| "
            f"{rule_name} | {scope_name} | {severity_name} | "
            f"`{applies_to}` | `{must_satisfy}` | {enforcement_name} |"
        )

    lines.extend(["", "## Details", ""])

    for rule in rules:
        lines.extend(
            [
                f"### {rule.name} (`{rule.id}`)",
                f"**Description:** {_collapse_whitespace(rule.description)}",
                f"**On violation:** {_collapse_whitespace(rule.on_violation)}",
                f"**Authored by:** {_collapse_whitespace(rule.authored_by)}",
                "",
            ]
        )

    content = "\n".join(lines).rstrip() + "\n"
    return {"-": content}
