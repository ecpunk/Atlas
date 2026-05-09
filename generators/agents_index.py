from __future__ import annotations

from schemas.agent import Agent
from schemas.conventions import VocabRef
from schemas.vocabulary import Vocabulary

NAME = "agents_index"
INPUTS = ["agent:*"]
OUTPUTS = ["/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Agents Index.md"]

HEADER = "AUTO-GENERATED from atlas-store/entities/agents/*.yaml - do not hand-edit."


def _build_vocab_display_map(vocab_store: dict) -> dict[tuple[str, str], str]:
    display_map: dict[tuple[str, str], str] = {}

    for vocab in vocab_store.values():
        if isinstance(vocab, Vocabulary):
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


def generate(store: dict) -> dict[str, str]:
    display_map = _build_vocab_display_map(store.get("vocabulary", {}))

    agent_store = store.get("agent", {})
    agents = [item for item in agent_store.values() if isinstance(item, Agent)]
    agents.sort(key=lambda item: item.id)

    sections = ["# Agents", "", HEADER, ""]
    sections.append("\n\n".join(_format_agent(agent, display_map) for agent in agents))
    content = "\n".join(sections).rstrip() + "\n"
    return {OUTPUTS[0]: content}
