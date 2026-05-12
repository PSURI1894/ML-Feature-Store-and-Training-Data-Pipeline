# Catalog UI

A web portal so engineers can **discover** features instead of rebuilding them.

```bash
uvicorn services.catalog_ui.app:app --port 8050
```

## What it shows

- Every feature view with owner, team, sensitivity, tier, TTL, freshness SLA, and source contract.
- Per-view detail: the feature columns and the **models (feature services) that consume it** — so
  you can see impact before changing a view.
- Client-side filter for quick search.

## Data source

Reads the registry snapshot (`feature_platform.registry.sync.snapshot_from_repo`). It degrades
gracefully to an empty list if the registry can't be loaded, so the portal never hard-fails.

## Roadmap

- Freshness/drift status pulled live from Prometheus.
- Profiling (value distributions) per feature.
- "Request access" flow for `pii`/`financial` views tied to RBAC.
