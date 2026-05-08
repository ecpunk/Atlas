from __future__ import annotations

import yaml

from schemas.skill import Skill, SkillPublishTarget

NAME = "skill_md"
INPUTS = ["skill:*"]
OUTPUTS = ["-"]


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


def generate(store: dict) -> dict[str, str]:
    skill_store = store.get("skill", {})
    skills = [item for item in skill_store.values() if isinstance(item, Skill)]
    skills.sort(key=lambda item: item.id)

    chunks: list[str] = []
    for skill in skills:
        for target in skill.publish_targets:
            rendered = _render_skill_md(skill)
            chunks.append(f"--- skill_md:{skill.id}:{target.target_id} ---\n{rendered}")

    content = "\n\n".join(chunks)
    if content:
        content += "\n"

    return {"-": content}
