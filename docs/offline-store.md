# Offline Store

The offline store is the **system of record** for feature values and the source for training data.

## Adapters

| Adapter | Module | Use |
|---------|--------|-----|
| DuckDB | `offline/duckdb_store.py` | local/dev; fast PIT over Parquet samples |
| BigQuery | `offline/bigquery.py` | prod; push-down as-of join |
| Iceberg | `offline/iceberg.py` | prod; hidden partitioning + time-travel |
| Snowflake | (profile swap) | prod alternative |

All adapters implement `OfflineStore` (`offline/store.py`).

## Layout & performance

- **Partition** by `event_date`, **cluster** by `entity_id`.
- `require_partition_filter = TRUE` forces every query to prune partitions — a guardrail against
  accidental full-history scans.
- The as-of join is **pushed down** to the warehouse (BigQuery `QUALIFY ROW_NUMBER()`), so only the
  result leaves the warehouse.
- For very large joins, sample with DuckDB first (`offline/duckdb_store.py`) to validate, then run
  the full BigQuery job.

## Idempotency

Writes upsert on `(entity_id, event_ts)` keeping the row with the greatest `created_ts`. This makes
backfills safe to re-run.

## Cost controls

- 3-year partition expiration; lifecycle older partitions to cold storage.
- Cluster keys keep PIT joins cheap.
- Monitor `$/feature_view/month` (see `docs/monitoring.md`).
