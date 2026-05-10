from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

NAME = "orphaned_output_check"
INPUTS = []
OUTPUTS = [
    "/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT/Output Integrity Report.md"
]

_OUTPUT_DIR = Path("/opt/stack/services/docs/kb/Projects/Atlas/40-OUTPUT")
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Match lines like:  "/opt/stack/services/docs/kb/..."  (double-quoted path strings)
_OUTPUTS_LINE_RE = re.compile(r'"(/[^"]+)"')


def _iter_generator_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix == ".py" and p.name != "__init__.py" and not p.name.startswith("_")
    )


def _collect_all_outputs(repo_root: Path) -> dict[str, list[str]]:
    """Parse OUTPUTS[] statically from generator source files — no imports."""
    result: dict[str, list[str]] = {}

    def _parse(module_path: Path) -> tuple[str, list[str]]:
        text = module_path.read_text(encoding="utf-8")

        name_match = re.search(r'^NAME\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
        name = name_match.group(1) if name_match else module_path.stem

        outputs_match = re.search(r'^OUTPUTS\s*=\s*\[([^\]]*)\]', text, re.MULTILINE | re.DOTALL)
        outputs: list[str] = []
        if outputs_match:
            outputs = _OUTPUTS_LINE_RE.findall(outputs_match.group(1))

        return name, outputs

    for module_path in _iter_generator_files(repo_root / "generators"):
        name, outputs = _parse(module_path)
        result[name] = outputs

    extensions_root = repo_root / "extensions"
    if extensions_root.exists():
        for ext_dir in sorted(p for p in extensions_root.iterdir() if p.is_dir()):
            for module_path in _iter_generator_files(ext_dir / "generators"):
                name, outputs = _parse(module_path)
                result[name] = outputs

    return result


def generate(store: dict) -> dict[str, str]:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_outputs = _collect_all_outputs(_REPO_ROOT)

    claimed_paths: set[str] = set()
    for outputs in all_outputs.values():
        for path in outputs:
            claimed_paths.add(str(Path(path).resolve()))

    present_files: list[Path] = sorted(_OUTPUT_DIR.iterdir()) if _OUTPUT_DIR.exists() else []

    orphaned: list[str] = []
    claimed_present: list[str] = []
    for f in present_files:
        if str(f.resolve()) in claimed_paths:
            claimed_present.append(f.name)
        else:
            orphaned.append(f.name)

    lines: list[str] = [
        "# Output Integrity Report",
        "",
        "AUTO-GENERATED from atlas-store. Do not hand-edit.",
        "",
        f"Generated at: {generated_at}",
        f"Generators scanned: {len(all_outputs)}",
        f"Files in 40-OUTPUT/: {len(present_files)}",
        f"Claimed by a generator: {len(claimed_present)}",
        f"Orphaned (no generator claims them): {len(orphaned)}",
        "",
        "---",
        "",
        "## Orphaned Output Files",
        "",
        "_Files in 40-OUTPUT/ not listed in any generator's OUTPUTS[]. May be stale from renamed or retired generators._",
        "",
        f"Count: {len(orphaned)}",
        "",
    ]

    if orphaned:
        lines.append("| File |")
        lines.append("|------|")
        for name in orphaned:
            lines.append(f"| `{name}` |")
    else:
        lines.append("_None — all output files are claimed by an active generator._")

    lines.extend([
        "",
        "---",
        "",
        "## Generator Output Map (reference)",
        "",
        "| Generator | Outputs |",
        "|-----------|---------|",
    ])
    for gen_name, outputs in sorted(all_outputs.items()):
        for out in outputs:
            lines.append(f"| `{gen_name}` | `{Path(out).name}` |")

    lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    return {OUTPUTS[0]: content}
