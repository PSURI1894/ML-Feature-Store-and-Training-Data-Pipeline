# ADR 0002: Offline store layout and engine

- Status: Accepted
- Date: 2026-04-20

## Context

The offline store is the system of record and the source for training joins. Training joins over
years of history were taking hours.

## Decision

- Partition offline tables by `event_date`, cluster by `entity_id`.
- Set `require_partition_filter = TRUE` to force pruning.
- Push the as-of join into the warehouse (BigQuery `QUALIFY ROW_NUMBER()`).
- Support BigQuery, Snowflake, and Iceberg behind one `OfflineStore` interface; DuckDB for local and
  for sampling very large joins before running them in full.

## Consequences

- Training joins prune to the requested date window — minutes, not hours.
- Iceberg's time-travel snapshots make a training set reproducible at a past instant.
- Cost is controlled via partition expiration + lifecycle to cold storage.
