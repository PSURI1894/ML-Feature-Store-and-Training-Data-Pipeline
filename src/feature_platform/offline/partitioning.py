"""Partition + clustering helpers shared by all offline adapters.

Partition pruning is the single biggest cost lever on the offline store: a
training join restricted to ``event_date`` between the min and max requested
event timestamps scans days, not years.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from feature_platform.common.time_utils import ensure_utc

PARTITION_COL = "event_date"
CLUSTER_COL = "entity_id"


def add_partition_column(df: pd.DataFrame, ts_col: str = "event_ts") -> pd.DataFrame:
    """Derive the ``event_date`` partition column from the event timestamp."""
    out = df.copy()
    out[PARTITION_COL] = pd.to_datetime(out[ts_col], utc=True).dt.strftime("%Y-%m-%d")
    return out


def partition_range(start: datetime, end: datetime) -> list[str]:
    """Inclusive list of ``YYYY-MM-DD`` partitions covering [start, end]."""
    start_d = ensure_utc(start).date()
    end_d = ensure_utc(end).date()
    days = (end_d - start_d).days
    return [(start_d + timedelta(days=i)).isoformat() for i in range(days + 1)]


def prune_predicate(start: datetime, end: datetime) -> str:
    """SQL predicate that lets the engine prune partitions for a time range."""
    lo = ensure_utc(start).strftime("%Y-%m-%d")
    hi = ensure_utc(end).strftime("%Y-%m-%d")
    return f"{PARTITION_COL} BETWEEN DATE '{lo}' AND DATE '{hi}'"
