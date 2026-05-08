#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.rule import Rule
from schemas.vocabulary import Vocabulary

HEADER = "AUTO-GENERATED from atlas-store/entities/rules/*.yaml - do not hand-edit."


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping in {path}")
    return data


def _iter_rule_files(root: Path) -> Iterable[Path]:
    rules_dir = root / "entities" / "rules"
    if not rules_dir.exists():
        return []

    return sorted(
        p
        for p in rules_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}
    )


def _collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def _escape_table_cell(text: str) -> str:
    return text.replace("|", "\\|")


def _load_vocab_display_maps(root: Path) -> dict[str, dict[str, str]]:
    vocabularies_dir = root / "vocabularies"
    display_maps: dict[str, dict[str, str]] = {}

    for path in sorted(vocabularies_dir.glob("*.yaml")):
        vocab = Vocabulary.model_validate(_load_yaml(path))
        display_maps[vocab.id] = {value.id: value.name for value in vocab.values}

    return display_maps


def _resolve_vocab_value(
    display_maps: dict[str, dict[str, str]],
    vocab_id: str,
    value_id: str,
) -> str:
    values = display_maps.get(vocab_id)
    if values is None:
        raise ValueError(f"vocabulary file not found for '{vocab_id}'")

    value_name = values.get(value_id)
    if value_name is None:
        raise ValueError(f"vocabulary value '{value_id}' not found in '{vocab_id}'")

    return value_name


def generate_markdown(root: Path) -> str:
    display_maps = _load_vocab_display_maps(root)

    rules: list[Rule] = []
    for path in _iter_rule_files(root):
        rules.append(Rule.model_validate(_load_yaml(path)))

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

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate markdown summary for Atlas rule entities")
    parser.add_argument("--write", type=Path, default=None, help="optional output file path")
    args = parser.parse_args()

    output = generate_markdown(REPO_ROOT)
    print(output, end="")

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
