"""Apache Iceberg offline store adapter.

Iceberg gives us hidden partitioning (``days(event_ts)``), schema evolution, and
time-travel snapshots — the latter is handy for reproducing a training set exactly
as the offline store looked at a past instant.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from feature_platform.common.config import get_settings
from feature_platform.common.logging import get_logger
from feature_platform.offline.store import OfflineStore, OfflineWriteResult

log = get_logger(__name__)


class IcebergOfflineStore(OfflineStore):
    def __init__(self, namespace: str = "feature_store") -> None:
        self.namespace = namespace
        self._catalog = None

    @property
    def catalog(self):  # pragma: no cover - requires a catalog
        if self._catalog is None:
            from pyiceberg.catalog import load_catalog

            settings = get_settings()
            self._catalog = load_catalog(
                "default",
                **{"uri": getattr(settings, "iceberg_catalog_uri", "thrift://localhost:9083")},
            )
        return self._catalog

    def _table_id(self, feature_view: str) -> str:
        return f"{self.namespace}.{feature_view}"

    def write(self, feature_view: str, df: pd.DataFrame) -> OfflineWriteResult:  # pragma: no cover
        import pyarrow as pa

        table = self.catalog.load_table(self._table_id(feature_view))
        # Upsert on identifier fields (entity_id, event_ts) for idempotency.
        table.upsert(pa.Table.from_pandas(df))
        log.info("iceberg.write", fv=feature_view, rows=len(df))
        return OfflineWriteResult(feature_view, len(df), ())

    def read_range(self, feature_view: str, start: datetime, end: datetime) -> pd.DataFrame:  # pragma: no cover
        table = self.catalog.load_table(self._table_id(feature_view))
        return (
            table.scan(row_filter=f"event_ts >= '{start}' AND event_ts < '{end}'")
            .to_pandas()
        )

    def point_in_time_query(  # pragma: no cover
        self, feature_view: str, entity_df: pd.DataFrame, *, event_ts_col: str = "event_ts"
    ) -> pd.DataFrame:
        # Scan the relevant window into Arrow, then do the as-of join in DuckDB.
        from feature_platform.training.point_in_time import point_in_time_join

        lo = entity_df[event_ts_col].min()
        hi = entity_df[event_ts_col].max()
        feats = self.read_range(feature_view, lo, hi)
        return point_in_time_join(entity_df, feats, event_ts_col=event_ts_col)

    def latest_event_ts(self, feature_view: str) -> datetime | None:  # pragma: no cover
        table = self.catalog.load_table(self._table_id(feature_view))
        df = table.scan(selected_fields=("event_ts",)).to_pandas()
        return None if df.empty else df["event_ts"].max()
