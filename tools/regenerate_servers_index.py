#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.server import Server


HEADER = "AUTO-GENERATED from atlas-store/entities/servers/*.yaml -- do not hand-edit."


def _format_value(value: object | None) -> str:
    return "n/a" if value is None else str(value)


def _format_gib(value: float | None) -> str:
    if value is None:
        return "n/a"
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def _load_servers(entities_root: Path) -> list[Server]:
    servers: list[Server] = []
    for yaml_path in sorted(entities_root.glob("*.yaml")):
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        servers.append(Server.model_validate(data))
    return sorted(servers, key=lambda item: item.id)


def generate_markdown(servers: list[Server]) -> str:
    lines: list[str] = ["# Servers", "", HEADER, ""]

    for server in servers:
        committed = _format_gib(server.ram_committed_gib)
        source_doc = _format_value(server.source_of_truth_doc)
        os_value = _format_value(server.os)
        ram_value = _format_gib(server.ram_gib)

        lines.append(f"## {server.name} (`{server.id}`)")
        lines.append("")
        lines.append(f"- **Hostname:** `{server.hostname}` (`{server.ip}`)")
        lines.append(f"- **Hardware:** {server.hardware}")
        lines.append(f"- **OS:** {os_value}")
        lines.append(f"- **RAM:** {ram_value} GiB (committed: {committed})")
        lines.append(f"- **Hosts:** {len(server.hosts)} services")
        if server.hosts:
            for host_ref in server.hosts:
                lines.append(f"  - `{host_ref}`")
        else:
            lines.append("  - `n/a`")
        lines.append(f"- **Source of truth:** {source_doc}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate Atlas servers markdown index")
    parser.add_argument("--write", type=Path, default=None, help="optional output markdown path")
    args = parser.parse_args()

    servers_dir = REPO_ROOT / "entities" / "servers"
    servers = _load_servers(servers_dir)
    output = generate_markdown(servers)

    print(output, end="")

    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(output, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())