"""DuckDB offline store — the local/dev default and the engine used for fast
point-in-time joins over Parquet samples before promoting to BigQuery.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from feature_platform.common.logging import get_logger
from feature_platform.offline.partitioning import add_partition_column
from feature_platform.offline.store import OfflineStore, OfflineWriteResult

log = get_logger(__name__)


class DuckDBOfflineStore(OfflineStore):
    def __init__(self, root: str | Path = "data/offline") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, feature_view: str) -> Path:
        return self.root / f"{feature_view}.parquet"

    def write(self, feature_view: str, df: pd.DataFrame) -> OfflineWriteResult:
        df = add_partition_column(df)
        path = self._path(feature_view)
        if path.exists():
            existing = pd.read_parquet(path)
            df = pd.concat([existing, df], ignore_index=True)
            # Idempotency: keep the latest created_ts per (entity_id, event_ts).
            sort_col = "created_ts" if "created_ts" in df.columns else "event_ts"
            df = (
                df.sort_values(sort_col)
                .drop_duplicates(["entity_id", "event_ts"], keep="last")
                .reset_index(drop=True)
            )
        df.to_parquet(path, index=False)
        parts = tuple(sorted(df["event_date"].unique().tolist()))
        log.info("offline.write", fv=feature_view, rows=len(df), partitions=len(parts))
        return OfflineWriteResult(feature_view, len(df), parts)

    def read_range(
        self, feature_view: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        path = self._path(feature_view)
        if not path.exists():
            return pd.DataFrame()
        con = duckdb.connect()
        return con.execute(
            "SELECT * FROM read_parquet(?) WHERE event_ts >= ? AND event_ts < ?",
            [str(path), start, end],
        ).df()

    def point_in_time_query(
        self, feature_view: str, entity_df: pd.DataFrame, *, event_ts_col: str = "event_ts"
    ) -> pd.DataFrame:
        from feature_platform.training.point_in_time import point_in_time_join

        feats = pd.read_parquet(self._path(feature_view))
        return point_in_time_join(entity_df, feats, event_ts_col=event_ts_col)

    def latest_event_ts(self, feature_view: str) -> datetime | None:
        path = self._path(feature_view)
        if not path.exists():
            return None
        con = duckdb.connect()
        row = con.execute(
            "SELECT max(event_ts) FROM read_parquet(?)", [str(path)]
        ).fetchone()
        return row[0] if row and row[0] is not None else None
