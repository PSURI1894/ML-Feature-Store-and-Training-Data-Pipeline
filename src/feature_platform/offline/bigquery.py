"""BigQuery offline store adapter.

Tables are partitioned by ``event_date`` and clustered by ``entity_id``. The
as-of join is pushed down to BigQuery as a windowed query so the warehouse does
the heavy lifting and only the result set leaves the warehouse.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from feature_platform.common.config import get_settings
from feature_platform.common.logging import get_logger
from feature_platform.offline.partitioning import add_partition_column, prune_predicate
from feature_platform.offline.store import OfflineStore, OfflineWriteResult

log = get_logger(__name__)


class BigQueryOfflineStore(OfflineStore):
    def __init__(self, project: str | None = None, dataset: str | None = None) -> None:
        settings = get_settings()
        self.project = project or settings.bigquery_project
        self.dataset = dataset or settings.bigquery_dataset
        self._client = None  # lazy; avoids importing google-cloud in unit tests

    @property
    def client(self):  # pragma: no cover - requires GCP creds
        if self._client is None:
            from google.cloud import bigquery

            self._client = bigquery.Client(project=self.project)
        return self._client

    def _table(self, feature_view: str) -> str:
        return f"`{self.project}.{self.dataset}.{feature_view}`"

    def write(self, feature_view: str, df: pd.DataFrame) -> OfflineWriteResult:  # pragma: no cover
        df = add_partition_column(df)
        # MERGE for idempotency on (entity_id, event_ts).
        self.client.load_table_from_dataframe(
            df, f"{self.project}.{self.dataset}.{feature_view}_staging"
        ).result()
        self.client.query(self._merge_sql(feature_view)).result()
        parts = tuple(sorted(df["event_date"].unique().tolist()))
        return OfflineWriteResult(feature_view, len(df), parts)

    def _merge_sql(self, fv: str) -> str:
        return f"""
        MERGE {self._table(fv)} T
        USING {self._table(fv + '_staging')} S
        ON T.entity_id = S.entity_id AND T.event_ts = S.event_ts
        WHEN MATCHED AND S.created_ts > T.created_ts THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT ROW
        """

    def read_range(self, feature_view: str, start: datetime, end: datetime) -> pd.DataFrame:  # pragma: no cover
        sql = (
            f"SELECT * FROM {self._table(feature_view)} "
            f"WHERE {prune_predicate(start, end)} AND event_ts >= @start AND event_ts < @end"
        )
        return self.client.query(sql).to_dataframe()

    def point_in_time_query(  # pragma: no cover - requires BQ
        self, feature_view: str, entity_df: pd.DataFrame, *, event_ts_col: str = "event_ts"
    ) -> pd.DataFrame:
        entity_table = f"{self.project}.{self.dataset}._pit_entities"
        self.client.load_table_from_dataframe(entity_df, entity_table).result()
        sql = f"""
        SELECT e.*, f.* EXCEPT(entity_id, event_ts, created_ts, event_date)
        FROM `{entity_table}` e
        LEFT JOIN {self._table(feature_view)} f
          ON e.entity_id = f.entity_id
         AND f.event_ts <= e.{event_ts_col}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY e.entity_id, e.{event_ts_col} ORDER BY f.event_ts DESC
        ) = 1
        """
        log.info("bq.pit_query", fv=feature_view, rows=len(entity_df))
        return self.client.query(sql).to_dataframe()

    def latest_event_ts(self, feature_view: str) -> datetime | None:  # pragma: no cover
        row = list(
            self.client.query(f"SELECT max(event_ts) ts FROM {self._table(feature_view)}")
        )
        return row[0]["ts"] if row else None
