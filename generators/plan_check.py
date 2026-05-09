from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

import yaml

from schemas.rule import Rule
from tools.llm_client import evaluate_rule

NAME = "plan_check"
INPUTS = ["rule:*"]
OUTPUTS = [
    "/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Plan Compliance Report.md"
]

_PLAN_ROOT = Path("/opt/stack/services/gdrive-projects/Projects/Current/Atlas/20-DESIGN")
_PLAN_PATTERN = "PLAN-*.md"


CheckResult = tuple[str, str, str]


def _load_plan_paths() -> list[Path]:
    paths = sorted(p for p in _PLAN_ROOT.glob(_PLAN_PATTERN) if p.name != "PLAN-TEMPLATE.md")
    return [path for path in paths if path.is_file()]


def _extract_yaml_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}

    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}

    raw = text[4:end]
    try:
        loaded = yaml.safe_load(raw)
    except Exception:
        return {}

    return loaded if isinstance(loaded, dict) else {}


def _extract_markdown_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    data: dict[str, str] = {}

    for line in lines[:40]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped == "---":
            break

        match = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", stripped)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            data[key] = value

    return data


def _extract_level2_sections(lines: list[str]) -> list[tuple[str, int, int]]:
    headings: list[tuple[str, int]] = []

    for idx, line in enumerate(lines):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.append((match.group(1).strip(), idx))

    sections: list[tuple[str, int, int]] = []
    for idx, (title, start) in enumerate(headings):
        end = headings[idx + 1][1] if idx + 1 < len(headings) else len(lines)
        sections.append((title, start, end))

    return sections


def _normalize_space(text: str) -> str:
    return " ".join(text.split())


def _find_section(lines: list[str], section_name: str) -> tuple[int, int] | None:
    normalized_target = _normalize_space(section_name)
    for title, start, end in _extract_level2_sections(lines):
        if _normalize_space(title) == normalized_target:
            return start, end
    return None


def _quoted_values(text: str) -> list[str]:
    values = []
    for item in re.findall(r'"([^"]+)"', text):
        normalized = _normalize_space(item)
        if normalized:
            values.append(normalized)
    return values


def _required_frontmatter_keys(check_definition: str) -> list[str]:
    tail = check_definition
    lower = check_definition.lower()
    key_anchor = "keys:"
    idx = lower.find(key_anchor)
    if idx >= 0:
        tail = check_definition[idx + len(key_anchor) :]

    compact = " ".join(tail.split())
    return [item.strip() for item in compact.split(",") if item.strip()]


def _top_excerpt(text: str, line_count: int = 14) -> str:
    return "\n".join(text.splitlines()[:line_count]).strip()


def _parse_check(rule: Rule, plan_text: str, lines: list[str]) -> CheckResult:
    kind = rule.check_kind.value_id

    if kind == "manual":
        return (
            "manual",
            "Requires human judgment.",
            "manual check; no deterministic evidence",
        )

    if kind == "frontmatter_field_present":
        required_keys = _required_frontmatter_keys(rule.check_definition)
        yaml_meta = _extract_yaml_frontmatter(plan_text)
        md_meta = _extract_markdown_frontmatter(plan_text)

        key_map: dict[str, object] = {}
        key_map.update(yaml_meta)
        if not key_map:
            key_map.update(md_meta)

        present_lower = {str(key).strip().lower() for key in key_map.keys()}
        missing = [key for key in required_keys if key.lower() not in present_lower]

        if missing:
            detail = "Missing frontmatter keys: " + ", ".join(missing)
            evidence = _top_excerpt(plan_text)
            return ("fail", detail, evidence)

        evidence = "Present keys: " + ", ".join(sorted(key_map.keys()))
        return ("pass", "All required frontmatter keys present.", evidence)

    if kind == "section_present":
        expected_sections = _quoted_values(rule.check_definition)
        if not expected_sections:
            expected_sections = [rule.check_definition.strip()]

        matched: str | None = None
        matched_bounds: tuple[int, int] | None = None
        for candidate in expected_sections:
            bounds = _find_section(lines, candidate)
            if bounds is not None:
                matched = candidate
                matched_bounds = bounds
                break

        if matched is None or matched_bounds is None:
            detail = "Missing required section: " + " OR ".join(expected_sections)
            evidence = "Available sections: " + ", ".join(title for title, _, _ in _extract_level2_sections(lines))
            return ("fail", detail, evidence)

        lower_definition = rule.check_definition.lower()
        section_lines = lines[matched_bounds[0] : matched_bounds[1]]
        section_text = "\n".join(section_lines)

        if "at least one checkbox" in lower_definition:
            if re.search(r"(?m)^\s*-\s*\[[ xX]\]\s+", section_text) is None:
                return ("fail", "Section exists but has no checkbox items.", section_text.strip())

        if "at least one numbered subsection" in lower_definition:
            has_numbered_subsection = re.search(r"(?m)^###\s+Phase\s+\d+\b", section_text) is not None
            has_numbered_list = re.search(r"(?m)^\s*\d+\.\s+", section_text) is not None
            if not (has_numbered_subsection or has_numbered_list):
                return ("fail", "Section exists but has no numbered subsection.", section_text.strip())

        evidence = lines[matched_bounds[0]].strip()
        return ("pass", f'Section "{matched}" is present.', evidence)

    if kind == "length_warning":
        threshold_match = re.search(r"(\d+)", rule.check_definition)
        threshold = int(threshold_match.group(1)) if threshold_match else 600
        word_count = len(re.findall(r"\b\w+\b", plan_text))

        if word_count > threshold:
            detail = f"Word count {word_count} exceeds threshold {threshold}."
            evidence = f"Word count: {word_count}"
            return ("warn", detail, evidence)

        detail = f"Word count {word_count} within threshold {threshold}."
        return ("pass", detail, f"Word count: {word_count}")

    if kind == "template_reference_present":
        refs = _quoted_values(rule.check_definition)
        required = refs[0] if refs else rule.check_definition.strip()

        if required and required not in plan_text:
            detail = f"Required reference not found: {required}"
            evidence = _top_excerpt(plan_text)
            return ("fail", detail, evidence)

        return ("pass", "Required reference is present.", required)

    if kind == "llm_evaluated":
        llm_result = evaluate_rule(
            system_prompt=rule.check_definition,
            user_content=plan_text,
            rule_id=rule.id,
        )

        model = str(llm_result.get("model", "unknown"))
        tokens_in = int(llm_result.get("tokens_in", 0) or 0)
        tokens_out = int(llm_result.get("tokens_out", 0) or 0)
        evidence_text = str(llm_result.get("evidence", "")).strip() or "(none)"
        suggested_fix = llm_result.get("suggested_fix")
        evidence = f"model={model}; tokens_in={tokens_in}; tokens_out={tokens_out}\n{evidence_text}"

        if bool(llm_result.get("error", False)):
            return ("warn", "LLM evaluation error.", evidence)

        if bool(llm_result.get("fires", False)):
            detail = "LLM flagged potential Genesis alignment violation."
            if isinstance(suggested_fix, str) and suggested_fix.strip():
                detail += " Suggested fix: " + suggested_fix.strip()
            return ("fail", detail, evidence)

        detail = "LLM check passed."
        if isinstance(suggested_fix, str) and suggested_fix.strip():
            detail += " Suggested fix: " + suggested_fix.strip()
        return ("pass", detail, evidence)

    return (
        "fail",
        f"Unsupported check_kind: {kind}",
        f"Rule check_kind vocab value is not implemented: {kind}",
    )


def _render_report(results: dict[str, list[tuple[Rule, CheckResult]]]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    llm_models: set[str] = set()

    for _, plan_results in results.items():
        for rule, result in plan_results:
            if rule.check_kind.value_id != "llm_evaluated":
                continue
            evidence = result[2]
            model_match = re.search(r"model=([^;\n]+)", evidence)
            if model_match:
                llm_models.add(model_match.group(1).strip())

    lines: list[str] = [
        "# Plan Compliance Report",
        "",
        "AUTO-GENERATED from atlas-store Rule entities. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"Plans scanned: {len(results)}",
    ]

    if llm_models:
        lines.extend(
            [
                "- Note: LLM-evaluated outcomes are non-deterministic and reflect a single run.",
                f"- LLM models observed: {', '.join(sorted(llm_models))}",
            ]
        )

    lines.append("")

    for plan_name, plan_results in results.items():
        pass_count = sum(1 for _, item in plan_results if item[0] == "pass")
        fail_count = sum(1 for _, item in plan_results if item[0] == "fail")
        warn_count = sum(1 for _, item in plan_results if item[0] == "warn")
        manual_count = sum(1 for _, item in plan_results if item[0] == "manual")

        lines.extend(
            [
                f"## {plan_name}",
                "",
                f"- Summary: {pass_count} pass, {fail_count} fail, {warn_count} warn, {manual_count} manual",
                "",
            ]
        )

        for rule, result in plan_results:
            status, detail, evidence = result
            action = rule.fix_action if rule.fix_action else "n/a"
            lines.extend(
                [
                    f"### {rule.name} (`{rule.id}`)",
                    f"- Outcome: {status.upper()}",
                    f"- Detail: {detail}",
                    f"- Suggested action: {action}",
                    "- Evidence:",
                    "```text",
                    evidence if evidence else "(none)",
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def generate(store: dict) -> dict[str, str]:
    rule_store = store.get("rule", {})
    rules = [item for item in rule_store.values() if isinstance(item, Rule)]
    plan_rules = sorted(
        [rule for rule in rules if rule.applies_to == "plan_document"],
        key=lambda item: item.id,
    )

    plans = _load_plan_paths()
    results: dict[str, list[tuple[Rule, CheckResult]]] = {}

    for plan_path in plans:
        plan_text = plan_path.read_text(encoding="utf-8")
        lines = plan_text.splitlines()

        plan_results: list[tuple[Rule, CheckResult]] = []
        for rule in plan_rules:
            parsed = _parse_check(rule, plan_text, lines)
            plan_results.append((rule, parsed))

        results[plan_path.name] = plan_results

    content = _render_report(results)
    output_path = OUTPUTS[0]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return {output_path: content}
