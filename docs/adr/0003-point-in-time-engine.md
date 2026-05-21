# ADR 0003: Point-in-time join engine

- Status: Accepted
- Date: 2026-04-24

## Context

Training-serving skew and inflated offline metrics traced back to future leakage in feature joins.

## Decision

Implement the as-of join as a per-entity **backward** merge (`feature_ts <= event_ts`) with an
optional TTL filter (`event_ts - feature_ts <= TTL`). Forbid any "latest value" API for training.
Lock the behaviour with an adversarial `tests/pit_correctness/` suite that injects future-dated rows.

## Consequences

- No code path can produce a training set with future leakage.
- The same engine runs locally (DuckDB/pandas) and is pushed down to BigQuery in prod.
- A subtle earlier bug (`direction="nearest"`) is permanently regression-tested
  (see `fix/pit-join-future-leakage`).
