# Home Assistant Integration Guidance

Resolve entity identity through integration metadata before coding against an entity id. Confirm platform provenance, inspect entity registry and config entries, and test target service calls directly before integrating automation logic.

## Why This Matters

Home Assistant often exposes multiple entities for one physical device. Platform-aware discovery prevents false assumptions, avoids brittle integrations, and reduces service-call failures caused by mismatched entities.
