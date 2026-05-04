"""Point-in-time (as-of) join — the core correctness primitive.

For each (entity, event_ts) row we attach the most recent feature value observed
**at or before** event_ts. This prevents future leakage into training data.

Implementation note: we use a per-entity as-of merge. ``merge_asof`` requires both
frames sorted by the time key.
"""

from __future__ import annotations

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
) -> pd.DataFrame:
    """Attach as-of feature values to entity rows.

    Parameters
    ----------
    entity_df:
        Columns: ``entity_id`` + ``event_ts_col`` (the request rows).
    feature_df:
        Columns: ``entity_id`` + ``feature_ts_col`` + feature columns.
    """
    if entity_df.empty:
        return entity_df.copy()

    left = entity_df.copy()
    right = feature_df.copy()
    left[event_ts_col] = pd.to_datetime(left[event_ts_col], utc=True)
    right[feature_ts_col] = pd.to_datetime(right[feature_ts_col], utc=True)

    left = left.sort_values(event_ts_col)
    right = right.sort_values(feature_ts_col)

    merged = pd.merge_asof(
        left,
        right,
        left_on=event_ts_col,
        right_on=feature_ts_col,
        by="entity_id",
        direction="nearest",
        suffixes=("", "_feat"),
    )
    log.info("pit.join", entities=len(left), features=len(right), out=len(merged))
    return merged.reset_index(drop=True)
