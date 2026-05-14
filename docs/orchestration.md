# Orchestration

Airflow schedules the platform's recurring work. (Dagster is a drop-in alternative; the same
library functions are called either way.)

## DAGs

| DAG | Schedule | Does |
|-----|----------|------|
| `batch_features` | daily 02:00 UTC | Spark compute → DQ gate → offline store → trigger materialize |
| `materialization` | every 4h (+ pre-peak) | offline → online with TTL |
| `feature_monitoring` | nightly 03:30 UTC | drift, freshness, null-rate, skew |

## Principles

- **Idempotent tasks** keyed by logical date → safe re-runs and backfills.
- **Thin DAGs, fat library** — operators call `feature_platform.*` functions, also reachable from
  the CLI and unit tests (`plugins/feast_operators.py`).
- **DQ gate** — a batch that fails expectations is not materialized.
- **Traffic-aware materialization** — extra runs pre-warm critical views before known peaks.
