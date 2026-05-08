#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.skill import Skill, SkillPublishTarget


def _load_skill(path: Path) -> Skill:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Skill.model_validate(data)


def _select_target(skill: Skill, target_id: str | None) -> SkillPublishTarget:
    if not skill.publish_targets:
        raise ValueError("skill must declare at least one publish target")

    if target_id is None:
        return skill.publish_targets[0]

    for target in skill.publish_targets:
        if target.target_id == target_id:
            return target

    available = ", ".join(target.target_id for target in skill.publish_targets)
    raise ValueError(f"unknown target '{target_id}', available: {available}")


def _render_skill_md(skill: Skill) -> str:
    header = (
        f"# AUTO-GENERATED from atlas-store/entities/skills/{skill.id}.yaml "
        "\u2014 do not hand-edit"
    )

    frontmatter: dict[str, str] = {
        "name": skill.frontmatter.name,
        "description": skill.frontmatter.description,
    }
    if skill.frontmatter.context is not None:
        frontmatter["context"] = skill.frontmatter.context

    frontmatter_yaml = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        width=10000,
    ).rstrip()

    body = skill.body if skill.body.endswith("\n") else f"{skill.body}\n"
    return f"{header}\n---\n{frontmatter_yaml}\n---\n{body}"


def _resolve_output_path(output_path: str) -> Path:
    candidate = Path(output_path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate SKILL.md from a Skill entity YAML file")
    parser.add_argument("skill_yaml_path", type=Path, help="path to entities/skills/<id>.yaml")
    parser.add_argument("--target", default=None, help="publish target id (defaults to first publish target)")
    parser.add_argument("--write", action="store_true", help="write rendered SKILL.md to selected target output_path")
    args = parser.parse_args()

    skill_path = args.skill_yaml_path
    skill = _load_skill(skill_path)
    target = _select_target(skill, args.target)
    output = _render_skill_md(skill)

    print(output, end="")

    if args.write:
        output_path = _resolve_output_path(target.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())