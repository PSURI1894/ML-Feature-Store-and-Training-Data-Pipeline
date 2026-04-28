"""Materialization runner: copy recent feature values offline -> online.

This is what ``fp materialize`` and the Airflow materialization DAG call. It reads
the offline store (system of record) for the requested window and writes to the
online store with the view's TTL. Idempotent: re-running overwrites the same keys.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from feature_platform.common.logging import get_logger
from feature_platform.common.metrics import MATERIALIZE_ROWS
from feature_platform.offline.store import OfflineStore
from feature_platform.online.store import OnlineStore

log = get_logger(__name__)

DEFAULT_VIEWS = [
    "user_features_v2",
    "merchant_features_v1",
    "transaction_features_v1",
    "user_merchant_features_v1",
]


def _rows_for_online(df: pd.DataFrame) -> list[tuple[dict[str, str], dict]]:
    """Take the latest row per entity and shape it for the online store."""
    latest = (
        df.sort_values("event_ts").groupby("entity_id", as_index=False).tail(1)
    )
    reserved = {"entity_id", "event_ts", "created_ts", "event_date"}
    feature_cols = [c for c in latest.columns if c not in reserved]
    out: list[tuple[dict[str, str], dict]] = []
    for _, row in latest.iterrows():
        out.append(({"entity_id": str(row["entity_id"])}, {c: row[c] for c in feature_cols}))
    return out


def materialize_view(
    feature_view: str,
    start: datetime,
    end: datetime,
    offline: OfflineStore,
    online: OnlineStore,
) -> int:
    df = offline.read_range(feature_view, start, end)
    if df.empty:
        log.warning("materialize.empty", feature_view=feature_view)
        return 0
    rows = _rows_for_online(df)
    written = online.write(feature_view, rows)
    MATERIALIZE_ROWS.labels(feature_view).inc(written)
    log.info("materialize.view", feature_view=feature_view, rows=written)
    return written


def materialize_recent(
    start: datetime,
    end: datetime,
    feature_views: list[str] | None = None,
    offline: OfflineStore | None = None,
    online: OnlineStore | None = None,
) -> int:
    """Materialize a set of views for [start, end). Wires default stores lazily."""
    if offline is None:
        from feature_platform.offline.duckdb_store import DuckDBOfflineStore

        offline = DuckDBOfflineStore()
    if online is None:
        from feature_platform.online.redis_store import RedisOnlineStore

        online = RedisOnlineStore()

    total = 0
    for fv in feature_views or DEFAULT_VIEWS:
        total += materialize_view(fv, start, end, offline, online)
    return total
