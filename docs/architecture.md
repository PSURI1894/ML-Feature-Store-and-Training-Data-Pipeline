# Architecture

This document is the canonical, in-depth description of the platform. The README has the summary;
this has the rationale and the edges.

## 1. Design principles

1. **Registry is the source of truth.** A feature that is not defined in `feature_repo/` cannot be
   served. Notebook features are migrated, not used directly.
2. **Write-once transformation.** The same transformation function feeds offline and online to
   prevent training–serving skew.
3. **Offline-first, then materialize.** Batch jobs write the offline store, then `feast materialize`
   copies recent values online with a TTL. This makes the offline store the system of record.
4. **Point-in-time by construction.** The training service can only build datasets via the as-of
   join; there is no API that returns "latest" values for training.
5. **Everything is tagged.** Owner, team, SLA, tier, and sensitivity are mandatory metadata.

## 2. Component responsibilities

| Component | Module | Responsibility |
|-----------|--------|----------------|
| Registry | `registry/` | Validate + sync feature definitions to Postgres via `feast apply` |
| Offline store | `offline/` | Read/write partitioned feature tables (BQ / Snowflake / Iceberg) |
| Online store | `online/` | Low-latency KV reads/writes (Redis / DynamoDB), key schema, TTL |
| Batch | `batch/` + `spark/` | Compute features from the warehouse on a schedule |
| Streaming | `streaming/` + `flink/` | Windowed features from Kafka; dual-write + snapshot |
| On-demand | `ondemand/` + `services/ondemand_api` | Request-time transforms over retrieved features |
| Training | `training/` | Point-in-time-correct dataset assembly |
| Serving | `serving/` + `services/serving_grpc` | Assemble online features for inference |
| Monitoring | `monitoring/` | Drift, freshness, null-rate, training-serving skew |
| Governance | `governance/` | Sensitivity, RBAC, right-to-be-forgotten, audit |
| Backfill | `backfill/` | Parameterized idempotent historical recompute |

## 3. Consistency model

Batch features are **offline-authoritative**: written to the offline store first, then materialized
online. Streaming features are **dual-written**: pushed online immediately for freshness and
snapshotted to the offline store periodically so training can reproduce them. A daily reconciliation
job (`monitoring/skew.py`) samples both stores and computes a skew score per feature; a non-trivial
skew is an incident, not a warning.

## 4. Failure domains

- **Online store outage** → serving falls back to the last-known materialized values where the model
  tolerates it; otherwise the request fails closed. See `docs/runbooks/online-store-outage.md`.
- **Stale features** → freshness gauge breaches SLA → alert. See `docs/runbooks/feature-staleness.md`.
- **Bad feature deploy** → blocked by CI validation; if it lands, pin previous `feature_view_versions`.

## 5. Multi-region

Online stores are regional (low-latency serving); the offline store is replicated so training is
portable across regions. Feature definitions are global (one registry).

See `docs/adr/` for the decisions behind these choices.
