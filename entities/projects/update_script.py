#!/usr/bin/env python3
"""Update concept_doc fields in atlas-store project entities after gdrive migration."""

import sys
from pathlib import Path

ENTITIES_DIR = Path("/opt/stack/atlas-store/entities/projects")
KB_ROOT = "docs/kb/Projects"

# Map: entity filename → concept_doc path (relative to services repo root)
UPDATES = {
    "ai-hvac-balancer.yaml":            f"{KB_ROOT}/AI HVAC Balancer/10-CONCEPT/AI_HVAC_BALANCER_CONCEPT.md",
    "aws-starter.yaml":                 f"{KB_ROOT}/AWS Starter/10-CONCEPT/AWS_STARTER_CONCEPT.md",
    "build-and-design-navigator.yaml":  f"{KB_ROOT}/Build & Design Navigator/10-CONCEPT/BUILD_AND_DESIGN_NAVIGATOR_CONCEPT.md",
    "code-intelligence-mcp.yaml":       f"{KB_ROOT}/Code Intelligence MCP/10-CONCEPT/CODE_INTELLIGENCE_MCP_CONCEPT.md",
    "development-framework.yaml":       f"{KB_ROOT}/Development Framework/10-CONCEPT/DEVELOPMENT_FRAMEWORK_CONCEPT.md",
    "family-meal-planner.yaml":         f"{KB_ROOT}/Family Meal Planner/10-CONCEPT/FAMILY_MEAL_PLANNER_CONCEPT.md",
    "gmail-triage.yaml":                f"{KB_ROOT}/Gmail Triage/10-CONCEPT/GMAIL_TRIAGE_CONCEPT.md",
    "health-investigation.yaml":        f"{KB_ROOT}/Health Investigation/10-CONCEPT/HEALTH_INVESTIGATION_CONCEPT.md",
    "home-assistant.yaml":              f"{KB_ROOT}/Home Assistant/10-CONCEPT/HOME_ASSISTANT_CONCEPT.md",
    "home-command-tablet.yaml":         f"{KB_ROOT}/Home Command Tablet/10-CONCEPT/HOME_COMMAND_TABLET_CONCEPT.md",
    "knowledge-base-cleanup.yaml":      f"{KB_ROOT}/Knowledge Base Cleanup/10-CONCEPT/KNOWLEDGE_BASE_CLEANUP_CONCEPT.md",
    "knowledge-server.yaml":            f"{KB_ROOT}/UM790-Knowledge-Server/10-CONCEPT/concept.md",
    "nas-build.yaml":                   f"{KB_ROOT}/NAS Build/10-CONCEPT/NAS_BUILD_CONCEPT.md",
    "pat-patent.yaml":                  f"{KB_ROOT}/PAT Patent/10-CONCEPT/PAT_PATENT_CONCEPT.md",
    "personal-ai-layer.yaml":           f"{KB_ROOT}/Personal AI Layer/10-CONCEPT/PERSONAL_AI_LAYER_CONCEPT.md",
    "serveiq.yaml":                     f"{KB_ROOT}/ServeIQ/10-CONCEPT/SERVEIQ_CONCEPT.md",
    "stargate-archive.yaml":            f"{KB_ROOT}/Stargate Archive/10-CONCEPT/STARGATE_ARCHIVE_CONCEPT.md",
    "storefront.yaml":                  f"{KB_ROOT}/Storefront/10-CONCEPT/STOREFRONT_CONCEPT.md",
    "the-engine.yaml":                  f"{KB_ROOT}/The Engine/10-CONCEPT/THE_ENGINE_SPEC.md",
    "thought-substrate.yaml":           f"{KB_ROOT}/Thought Substrate/10-CONCEPT/THOUGHT_SUBSTRATE_CONCEPT.md",
}

# Verify all target files exist in the services docs/kb
SERVICES_ROOT = Path("/opt/stack/services")
errors = []
for fname, path in UPDATES.items():
    full = SERVICES_ROOT / path
    if not full.exists():
        errors.append(f"  MISSING TARGET: {path}")

if errors:
    print("ERROR - target concept doc files missing:")
    for e in errors:
        print(e)
    sys.exit(1)

print("All target files verified on disk.")

# Now update each entity YAML
updated = 0
already_set = 0
failed = []

for fname, new_path in UPDATES.items():
    entity_file = ENTITIES_DIR / fname
    if not entity_file.exists():
        failed.append(f"  ENTITY NOT FOUND: {fname}")
        continue
    
    content = entity_file.read_text()
    lines = content.split('\n')
    
    # Check if concept_doc field already exists
    existing_idx = None
    status_idx = None
    for i, line in enumerate(lines):
        if line.startswith('concept_doc:'):
            existing_idx = i
        if line.startswith('status:'):
            status_idx = i
    
    if existing_idx is not None:
        # Replace existing concept_doc line
        old_val = lines[existing_idx]
        lines[existing_idx] = f"concept_doc: {new_path}"
        if old_val == lines[existing_idx]:
            print(f"  UNCHANGED: {fname} (already correct)")
            already_set += 1
            continue
        print(f"  UPDATED:  {fname}")
        print(f"    OLD: {old_val}")
        print(f"    NEW: concept_doc: {new_path}")
    elif status_idx is not None:
        # Insert concept_doc after status line
        lines.insert(status_idx + 1, f"concept_doc: {new_path}")
        print(f"  INSERTED: {fname} → {new_path}")
    else:
        failed.append(f"  NO status: line in {fname} — skipping")
        continue
    
    entity_file.write_text('\n'.join(lines))
    updated += 1

print(f"\nSummary: {updated} updated, {already_set} already correct, {len(failed)} failed")
if failed:
    for f in failed:
        print(f)
