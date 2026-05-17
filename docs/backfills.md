# Backfills

Recompute historical feature values safely and resumably.

## Request

```bash
python scripts/run_backfill.py --feature-view user_features_v2 \
  --start 2026-04-01 --end 2026-05-01            # add --dry-run to preview
```

Or via the audited GitHub Action (`.github/workflows/backfill.yml`).

## Guarantees

- **Idempotent** — partitions already completed are skipped (`backfill_partitions` table). Re-runs
  are safe; the Spark job uses dynamic partition overwrite.
- **Resumable** — progress is recorded per day, so a failed run resumes from the last good partition.
- **Audited** — every run is a row in `backfill_runs` with requester, status, and row counts.

## Schema

`infra/sql/backfill_runs.sql`: `backfill_runs` (one per request) + `backfill_partitions` (per day).

## Large backfills

Run as a Spark job with day-level chunking. For very wide joins, validate on a DuckDB sample first
(`training/duckdb_sampler.py`), then run the full warehouse job.
