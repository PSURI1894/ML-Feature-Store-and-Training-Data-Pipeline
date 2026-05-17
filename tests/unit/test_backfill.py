"""Tests for the idempotent backfill runner."""

from __future__ import annotations

from feature_platform.backfill.runner import BackfillRequest, run_backfill
from feature_platform.backfill.state import InMemoryBackfillStore, RunStatus


def test_backfill_covers_all_partitions() -> None:
    calls: list[str] = []

    def compute(_fv: str, partition: str) -> int:
        calls.append(partition)
        return 10

    run = run_backfill(
        BackfillRequest("user_features_v2", "2026-04-01", "2026-04-05"), compute
    )
    assert run.status is RunStatus.COMPLETED
    assert len(calls) == 5            # inclusive 5 days
    assert run.rows_written == 50


def test_dry_run_does_not_compute() -> None:
    calls: list[str] = []
    run = run_backfill(
        BackfillRequest("user_features_v2", "2026-04-01", "2026-04-03", dry_run=True),
        lambda fv, p: calls.append(p) or 1,
    )
    assert calls == []
    assert run.status is RunStatus.PENDING


def test_completed_partitions_are_skipped_on_rerun() -> None:
    store = InMemoryBackfillStore()
    compute_calls: list[str] = []

    def compute(_fv: str, partition: str) -> int:
        compute_calls.append(partition)
        return 1

    req = BackfillRequest("user_features_v2", "2026-04-01", "2026-04-02")
    run_backfill(req, compute, store=store)
    first = len(compute_calls)
    run_backfill(req, compute, store=store)   # rerun
    assert len(compute_calls) == first        # nothing recomputed
