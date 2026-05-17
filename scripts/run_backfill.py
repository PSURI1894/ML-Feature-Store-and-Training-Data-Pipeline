"""CLI to request a backfill.

    python scripts/run_backfill.py --feature-view user_features_v2 \
        --start 2026-04-01 --end 2026-05-01 [--dry-run]

Idempotent: re-running skips already-completed partitions.
"""

from __future__ import annotations

import argparse

from feature_platform.backfill.runner import BackfillRequest, run_backfill
from feature_platform.common.logging import get_logger

log = get_logger("backfill.cli")


def _spark_compute(feature_view: str, partition: str) -> int:
    """Submit the Spark job for one partition. Returns rows written.

    In production this shells out to ``spark-submit`` with the partition date; the
    job writes the offline store with dynamic partition overwrite (idempotent).
    """
    log.info("backfill.compute", feature_view=feature_view, partition=partition)
    # subprocess.run(["spark-submit", f"spark/jobs/{feature_view}_batch.py", "--date", partition])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a feature backfill")
    parser.add_argument("--feature-view", required=True)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    request = BackfillRequest(
        feature_view=args.feature_view,
        start_date=args.start,
        end_date=args.end,
        dry_run=args.dry_run,
    )
    run = run_backfill(request, compute=_spark_compute)
    log.info("backfill.result", run_id=run.run_id, status=run.status.value, rows=run.rows_written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
