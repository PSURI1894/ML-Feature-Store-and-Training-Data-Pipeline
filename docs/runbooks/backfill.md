# Runbook: Backfill

When to backfill: a new feature view, a corrected transform, or recovering from missed batch runs.

## Steps

1. **Plan (dry run):**
   ```bash
   python scripts/run_backfill.py --feature-view user_features_v2 \
     --start 2026-04-01 --end 2026-05-01 --dry-run
   ```
2. **Execute** (or trigger `.github/workflows/backfill.yml` with `dry_run=false`). The runner skips
   partitions already completed (`backfill_partitions`).
3. **Verify** row counts in `backfill_runs`, then spot-check the offline store.
4. **Materialize** the backfilled window to the online store if it must serve.

## Safety

- Idempotent: re-running is safe (dynamic partition overwrite + completed-partition skip).
- Large ranges run as Spark jobs with day-level chunking; validate on a DuckDB sample first.
- Every run is audited (requester, status, rows).
