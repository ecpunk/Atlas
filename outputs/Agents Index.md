# Agents

AUTO-GENERATED from atlas-store/entities/agents/*.yaml - do not hand-edit.

## GitHub Copilot CLI in VS Code (`copilot-cli-vscode`)

- **Model family:** gpt-5.3-codex
- **Interface:** VS Code Extension
- **Primary lane:** Implementation
- **Secondary lanes:** Discovery
- **Can read:** um790_filesystem, gdrive_files_via_fuse_mount, code_repo, web
- **Can write:** um790_filesystem, code_repo, gdrive_files_via_fuse_mount
- **Can execute:** shell_via_remote_ssh, docker, systemd_via_sudo, mcp_servers

### Trust calibration

| Task pattern | Reliability | Notes |
|--------------|-------------|-------|
| discovery and read-only investigation | High | validated 2026-05-04 with knowledge-server diagnosis |
| mechanical implementation against detailed plan | High | validated Plan 001 execution 2026-05-08 |
| open-ended diagnostic prompts | High | beats prescriptive checklists |
| architectural reasoning under uncertainty | Medium | prefer Opus 4.7 tier for novel architecture; Codex sufficient for extending validated patterns |

### Known failure modes
- silent timeout on FUSE-mount read stalls
- over-engineering when prompts are prescriptive
- assumes implementation when prompts are ambiguous (mitigated by Implementation Gate pattern)

### Known strengths
- discovery-first when prompted to investigate before acting
- accurate hard-stop reporting on real failures
- clean git commit hygiene with descriptive messages
