#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.agent import Agent
from schemas.conventions import VocabRef
from schemas.vocabulary import Vocabulary

HEADER = "AUTO-GENERATED from atlas-store/entities/agents/*.yaml - do not hand-edit."


def _iter_yaml_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
    )


def _load_vocab_display_map(vocab_root: Path) -> dict[tuple[str, str], str]:
    display_map: dict[tuple[str, str], str] = {}

    for vocab_path in _iter_yaml_files(vocab_root):
        data = yaml.safe_load(vocab_path.read_text(encoding="utf-8"))
        vocab = Vocabulary.model_validate(data)
        for value in vocab.values:
            display_map[(vocab.id, value.id)] = value.name

    return display_map


def _display_vocab(ref: VocabRef, display_map: dict[tuple[str, str], str]) -> str:
    display = display_map.get((ref.vocab_id, ref.value_id))
    return display if display is not None else str(ref)


def _display_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _format_agent(agent: Agent, display_map: dict[tuple[str, str], str]) -> str:
    lines: list[str] = []
    lines.append(f"## {agent.name} (`{agent.id}`)")
    lines.append("")
    lines.append(f"- **Model family:** {agent.model_family}")
    lines.append(f"- **Interface:** {_display_vocab(agent.interface, display_map)}")
    lines.append(f"- **Primary lane:** {_display_vocab(agent.primary_lane, display_map)}")
    secondary = [_display_vocab(ref, display_map) for ref in agent.secondary_lanes]
    lines.append(f"- **Secondary lanes:** {_display_list(secondary)}")
    lines.append(f"- **Can read:** {_display_list(agent.can_read)}")
    lines.append(f"- **Can write:** {_display_list(agent.can_write)}")
    lines.append(f"- **Can execute:** {_display_list(agent.can_execute)}")
    lines.append("")
    lines.append("### Trust calibration")
    lines.append("")
    lines.append("| Task pattern | Reliability | Notes |")
    lines.append("|--------------|-------------|-------|")
    for entry in agent.trust_calibration:
        reliability = _display_vocab(entry.reliability, display_map)
        notes = entry.notes if entry.notes else "-"
        lines.append(f"| {entry.task_pattern} | {reliability} | {notes} |")
    lines.append("")
    lines.append("### Known failure modes")
    for mode in agent.known_failure_modes:
        lines.append(f"- {mode}")
    if not agent.known_failure_modes:
        lines.append("- none")
    lines.append("")
    lines.append("### Known strengths")
    for strength in agent.known_strengths:
        lines.append(f"- {strength}")
    if not agent.known_strengths:
        lines.append("- none")

    return "\n".join(lines)


def generate_agents_index(repo_root: Path) -> str:
    entities_root = repo_root / "entities" / "agents"
    vocab_root = repo_root / "vocabularies"
    display_map = _load_vocab_display_map(vocab_root)

    agents: list[Agent] = []
    for entity_path in _iter_yaml_files(entities_root):
        data = yaml.safe_load(entity_path.read_text(encoding="utf-8"))
        agents.append(Agent.model_validate(data))

    agents.sort(key=lambda item: item.id)

    sections = ["# Agents", "", HEADER, ""]
    sections.append("\n\n".join(_format_agent(agent, display_map) for agent in agents))
    return "\n".join(sections).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate markdown index for Atlas agent entities")
    parser.add_argument("--write", type=Path, default=None, help="optional output file path")
    args = parser.parse_args()

    output = generate_agents_index(REPO_ROOT)
    print(output, end="")

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())