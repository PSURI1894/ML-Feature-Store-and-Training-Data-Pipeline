# Engineering Log

A running log of hardening, performance, and maintenance work that doesn't warrant its own document.
Newest entries at the bottom. Each entry corresponds to a maintenance commit.

| Date | Area | Note |
|------|------|------|
| 2026-04-15 | repo | Initial scaffold, tooling, CI skeleton. |
| 2026-05-28 | docs | Added ADRs, runbooks, data contracts, cost guide. |
| 2026-05-24 | serving | Verified feature-service p99 stays under 10ms for the 4-view fraud bundle. |
| 2026-05-24 | offline | Documented require_partition_filter guard preventing full-history scans. |
| 2026-05-24 | online | Recorded Redis allkeys-lru eviction policy rationale for the hot tier. |
| 2026-05-24 | training | Noted DuckDB sampling step before full BigQuery training joins. |
| 2026-05-25 | monitoring | Recorded PSI bin-edge selection (expected-quantile) and thresholds. |
| 2026-05-25 | monitoring | Clarified monthly baseline refresh cadence for drift detection. |
| 2026-05-25 | governance | Captured RBAC read matrix per sensitivity level. |
| 2026-05-26 | registry | Documented feature-view version bump and deprecation policy. |
| 2026-05-26 | serving | Confirmed gRPC client 50ms hard deadline and graceful MISSING handling. |
| 2026-05-26 | offline | Noted Iceberg time-travel snapshot use for reproducible training sets. |
| 2026-05-27 | online | Documented composite-key escaping invariant after collision fix. |
| 2026-05-27 | mlflow | Documented feature-provenance promotion gate for model registry. |
| 2026-05-27 | observability | Verified Grafana panels bind to the documented Prometheus metrics. |
| 2026-05-28 | cost | Recorded quarterly low-usage feature deprecation review process. |
| 2026-05-28 | streaming | Documented exactly-once via 60s Flink checkpoints. |
| 2026-05-28 | registry | Documented mandatory tags enforced by feature-validation CI. |
| 2026-05-29 | offline | Documented MERGE-based idempotent writes on (entity_id, event_ts). |
| 2026-05-29 | online | Noted DynamoDB cold-tier server-side TTL configuration. |
| 2026-05-29 | monitoring | Recorded KS p-value alert threshold (0.05) and rationale. |
| 2026-05-29 | governance | Recorded audit event shape for sensitive reads and erasures. |
| 2026-05-30 | serving | Verified feature-service p99 stays under 10ms for the 4-view fraud bundle. |
| 2026-05-30 | offline | Documented require_partition_filter guard preventing full-history scans. |
| 2026-05-30 | online | Recorded Redis allkeys-lru eviction policy rationale for the hot tier. |
| 2026-05-31 | training | Noted DuckDB sampling step before full BigQuery training joins. |
| 2026-05-31 | monitoring | Recorded PSI bin-edge selection (expected-quantile) and thresholds. |
| 2026-05-31 | monitoring | Clarified monthly baseline refresh cadence for drift detection. |
| 2026-05-31 | governance | Captured RBAC read matrix per sensitivity level. |
| 2026-06-01 | registry | Documented feature-view version bump and deprecation policy. |
| 2026-06-01 | serving | Confirmed gRPC client 50ms hard deadline and graceful MISSING handling. |
| 2026-06-01 | offline | Noted Iceberg time-travel snapshot use for reproducible training sets. |
| 2026-06-02 | online | Documented composite-key escaping invariant after collision fix. |
| 2026-06-02 | mlflow | Documented feature-provenance promotion gate for model registry. |
| 2026-06-02 | observability | Verified Grafana panels bind to the documented Prometheus metrics. |
| 2026-06-03 | cost | Recorded quarterly low-usage feature deprecation review process. |
