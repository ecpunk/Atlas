from __future__ import annotations

from schemas.server import Server

NAME = "servers_index"
INPUTS = ["server:*"]
OUTPUTS = ["/opt/stack/services/gdrive-projects/Projects/Current/Atlas/40-OUTPUT/Servers Index.md"]

HEADER = "AUTO-GENERATED from atlas-store/entities/servers/*.yaml -- do not hand-edit."


def _format_value(value: object | None) -> str:
    return "n/a" if value is None else str(value)


def _format_gib(value: float | None) -> str:
    if value is None:
        return "n/a"
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def generate(store: dict) -> dict[str, str]:
    server_store = store.get("server", {})
    servers = [item for item in server_store.values() if isinstance(item, Server)]
    servers.sort(key=lambda item: item.id)

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

    content = "\n".join(lines).rstrip() + "\n"
    return {"-": content}
