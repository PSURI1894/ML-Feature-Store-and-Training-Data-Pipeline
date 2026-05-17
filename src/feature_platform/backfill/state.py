"""Backfill run state tracking.

Each backfill is recorded in a ``backfill_runs`` table so progress survives
restarts, partial runs are resumable, and duplicate runs are detected. Day-level
chunking lets a large backfill resume from the last completed partition.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from feature_platform.common.time_utils import utcnow


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class BackfillRun:
    feature_view: str
    start_date: str
    end_date: str
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: RunStatus = RunStatus.PENDING
    completed_partitions: list[str] = field(default_factory=list)
    rows_written: int = 0
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def mark(self, status: RunStatus) -> None:
        self.status = status
        self.updated_at = utcnow()

    def complete_partition(self, partition: str, rows: int) -> None:
        if partition not in self.completed_partitions:
            self.completed_partitions.append(partition)
            self.rows_written += rows
            self.updated_at = utcnow()


class InMemoryBackfillStore:
    """Default store for tests/local; prod uses the SQL table in backfill_runs.sql."""

    def __init__(self) -> None:
        self._runs: dict[str, BackfillRun] = {}

    def save(self, run: BackfillRun) -> None:
        self._runs[run.run_id] = run

    def get(self, run_id: str) -> BackfillRun | None:
        return self._runs.get(run_id)

    def is_partition_done(self, feature_view: str, partition: str) -> bool:
        return any(
            partition in r.completed_partitions
            for r in self._runs.values()
            if r.feature_view == feature_view and r.status == RunStatus.COMPLETED
        )
