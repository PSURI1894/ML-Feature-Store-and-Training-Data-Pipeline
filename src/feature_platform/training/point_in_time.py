"""Point-in-time (as-of) join — the core correctness primitive.

For each (entity, event_ts) row we attach the most recent feature value observed
**at or before** event_ts (and, optionally, within a freshness TTL). This prevents
future leakage into training data.

Fix history
-----------
The original implementation used ``merge_asof(direction="nearest")``, which could
attach a feature value observed *after* the event — leaking the future. The
correct direction is ``backward``; we additionally drop matches older than the
view TTL so offline values match what the online store would have served.
See tests/pit_correctness/test_no_future_leakage.py.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from feature_platform.common.logging import get_logger

log = get_logger(__name__)

_RESERVED = {"entity_id", "event_ts", "created_ts", "event_date"}


def point_in_time_join(
    entity_df: pd.DataFrame,
    feature_df: pd.DataFrame,
    *,
    event_ts_col: str = "event_ts",
    feature_ts_col: str = "event_ts",
    ttl: timedelta | None = None,
) -> pd.DataFrame:
    """Attach as-of feature values to entity rows (no future leakage).

    Parameters
    ----------
    entity_df:
        Columns: ``entity_id`` + ``event_ts_col`` (the request rows).
    feature_df:
        Columns: ``entity_id`` + ``feature_ts_col`` + feature columns.
    ttl:
        If given, matches where ``event_ts - feature_ts > ttl`` are treated as
        missing (the feature would have been stale at serving time).
    """
    if entity_df.empty:
        return entity_df.copy()

    left = entity_df.copy()
    right = feature_df.copy()
    left[event_ts_col] = pd.to_datetime(left[event_ts_col], utc=True)
    right[feature_ts_col] = pd.to_datetime(right[feature_ts_col], utc=True)

    # merge_asof requires both frames globally sorted by the time key.
    left = left.sort_values(event_ts_col).reset_index(drop=True)
    right = right.sort_values(feature_ts_col).reset_index(drop=True)

    # Track the matched feature timestamp so we can enforce the TTL afterwards.
    right["_feature_ts"] = right[feature_ts_col]

    merged = pd.merge_asof(
        left,
        right,
        left_on=event_ts_col,
        right_on=feature_ts_col,
        by="entity_id",
        direction="backward",   # the fix: only values at-or-before the event
        suffixes=("", "_feat"),
    )

    feature_cols = [c for c in right.columns if c not in _RESERVED and c != "_feature_ts"]
    if ttl is not None and "_feature_ts" in merged.columns:
        too_old = (merged[event_ts_col] - merged["_feature_ts"]) > ttl
        merged.loc[too_old, feature_cols] = pd.NA

    merged = merged.drop(columns=[c for c in ("_feature_ts",) if c in merged.columns])
    log.info("pit.join", entities=len(left), features=len(right), out=len(merged), ttl=str(ttl))
    return merged.reset_index(drop=True)
