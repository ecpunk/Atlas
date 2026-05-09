# Service Catalog

AUTO-GENERATED from atlas-store/entities/services/*.yaml - do not hand-edit.

## Atlas MCP (`atlas-mcp`)

- **Type:** MCP over HTTP
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8105
- **Health:** http://127.0.0.1:8105/mcp
- **Owned by:** `atlas`
- **Depends on:** none
- **Summary:** MCP server exposing the Atlas canonical entity store. 16 tools: 11 read (get/list for projects, services, servers, agents, rules, vocabularies, stack_summary) and 5 write (add_project, update_project, add_service, update_service, retire_service). Write tools use propose-confirm pattern.

## Gmail Triage (`gmail-triage`)

- **Type:** Docker Container
- **Lifecycle:** Maintained
- **Host:** `um790`
- **Port:** 8093
- **Health:** http://127.0.0.1:8093/
- **Owned by:** `gmail-triage`
- **Depends on:** none
- **Summary:** Gmail processing workflow with batch run mode and a companion dashboard UI.

## Home Assistant (`home-assistant`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8123
- **Health:** http://127.0.0.1:8123/
- **Owned by:** `home-assistant`
- **Depends on:** none
- **Summary:** Home Assistant runtime providing local home automation orchestration and UI.

## Home Command Tablet API (`home-command-tablet`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8094
- **Health:** http://127.0.0.1:8094/
- **Owned by:** `home-command-tablet`
- **Depends on:** none
- **Summary:** Home Command API runtime used by tablet-facing home command workflows.

## rclone Google Drive Mount (`rclone-gdrive`)

- **Type:** systemd Unit
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** n/a
- **Health:** n/a
- **Owned by:** `knowledge-server`
- **Depends on:** none
- **Summary:** Systemd-managed rclone mount that presents Google Drive content at /mnt/gdrive for local knowledge workflows.

## Remodel Tracker API (`remodel-tracker`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8090
- **Health:** http://127.0.0.1:8090/api/v1
- **Owned by:** `remodel-tracker`
- **Depends on:** none
- **Summary:** Remodel Tracker primary application service backing renovation workflows and MCP integration.

## ServeIQ Demo (`serveiq-demo`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8098
- **Health:** http://127.0.0.1:8098/
- **Owned by:** `serveiq-demo`
- **Depends on:** none
- **Summary:** Demo ServeIQ runtime exposing a separate public/demo instance.

## ServeIQ Main (`serveiq-main`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8097
- **Health:** http://127.0.0.1:8097/
- **Owned by:** `serveiq-main`
- **Depends on:** none
- **Summary:** Primary ServeIQ application runtime serving the main environment.

## Thought Substrate MCP (`thought-substrate`)

- **Type:** MCP over HTTP
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8099
- **Health:** http://127.0.0.1:8099/mcp
- **Owned by:** `thought-substrate`
- **Depends on:** none
- **Summary:** Semantic retrieval and capture service used for workspace-aware context discovery and indexing.

## Turdcraft Minecraft Server (`turdcraft`)

- **Type:** Docker Container
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 25565
- **Health:** n/a
- **Owned by:** `turdcraft`
- **Depends on:** none
- **Summary:** Java Minecraft server runtime for the Turdcraft world hosted on UM790.

## UM790 Knowledge Server MCP (`knowledge-server-mcp`)

- **Type:** MCP over HTTP
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8092
- **Health:** http://127.0.0.1:8092/mcp
- **Owned by:** `knowledge-server`
- **Depends on:** rclone-gdrive
- **Summary:** MCP service that provides read and write access to the markdown knowledge base so cross-agent workflows can discover, retrieve, and update project docs.

## UM790 Ops MCP (`um790-ops-mcp`)

- **Type:** MCP over HTTP
- **Lifecycle:** Running
- **Host:** `um790`
- **Port:** 8103
- **Health:** http://127.0.0.1:8103/mcp
- **Owned by:** `um790-ops-mcp`
- **Depends on:** none
- **Summary:** MCP service providing local operations tooling: shell execution, docker lifecycle management, service health, logs. Intended as the permanent home for ops tools migrated out of knowledge-server as part of the pre-Atlas compensation retirement track.
