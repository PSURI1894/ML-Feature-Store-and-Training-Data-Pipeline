"""Idempotent backfill runner.

Walks the requested date range day by day, skipping partitions already completed
(idempotency / resume), recomputing each, and recording progress. The actual
compute is delegated to a callable so the same runner drives Spark in prod and a
pure function in tests.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from feature_platform.backfill.state import (
    BackfillRun,
    InMemoryBackfillStore,
    RunStatus,
)
from feature_platform.common.logging import get_logger
from feature_platform.offline.partitioning import partition_range

log = get_logger(__name__)

# (feature_view, partition_date) -> rows_written
ComputeFn = Callable[[str, str], int]


@dataclass(frozen=True, slots=True)
class BackfillRequest:
    feature_view: str
    start_date: str   # YYYY-MM-DD
    end_date: str     # YYYY-MM-DD
    dry_run: bool = False


def run_backfill(
    request: BackfillRequest,
    compute: ComputeFn,
    store: InMemoryBackfillStore | None = None,
) -> BackfillRun:
    from datetime import datetime, timezone

    store = store or InMemoryBackfillStore()
    run = BackfillRun(
        feature_view=request.feature_view,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    store.save(run)

    lo = datetime.fromisoformat(request.start_date).replace(tzinfo=timezone.utc)
    hi = datetime.fromisoformat(request.end_date).replace(tzinfo=timezone.utc)
    partitions = partition_range(lo, hi)
    log.info(
        "backfill.start",
        run_id=run.run_id,
        feature_view=request.feature_view,
        partitions=len(partitions),
        dry_run=request.dry_run,
    )

    if request.dry_run:
        log.info("backfill.dry_run", partitions=partitions)
        run.mark(RunStatus.PENDING)
        return run

    run.mark(RunStatus.RUNNING)
    try:
        for partition in partitions:
            if store.is_partition_done(request.feature_view, partition):
                log.info("backfill.skip", partition=partition)
                continue
            rows = compute(request.feature_view, partition)
            run.complete_partition(partition, rows)
            store.save(run)
        run.mark(RunStatus.COMPLETED)
    except Exception:  # noqa: BLE001
        run.mark(RunStatus.FAILED)
        store.save(run)
        log.error("backfill.failed", run_id=run.run_id)
        raise
    log.info("backfill.done", run_id=run.run_id, rows=run.rows_written)
    return run
