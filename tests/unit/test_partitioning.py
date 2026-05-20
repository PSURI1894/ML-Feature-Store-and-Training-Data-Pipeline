"""Tests for offline partitioning helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from feature_platform.offline.partitioning import (
    add_partition_column,
    partition_range,
    prune_predicate,
)

UTC = timezone.utc


def test_add_partition_column() -> None:
    df = pd.DataFrame({"event_ts": [datetime(2026, 5, 1, 23, tzinfo=UTC)]})
    out = add_partition_column(df)
    assert out.loc[0, "event_date"] == "2026-05-01"


def test_partition_range_inclusive() -> None:
    parts = partition_range(datetime(2026, 5, 1, tzinfo=UTC), datetime(2026, 5, 4, tzinfo=UTC))
    assert parts == ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"]


def test_prune_predicate() -> None:
    pred = prune_predicate(datetime(2026, 5, 1, tzinfo=UTC), datetime(2026, 5, 2, tzinfo=UTC))
    assert "event_date BETWEEN DATE '2026-05-01' AND DATE '2026-05-02'" == pred
