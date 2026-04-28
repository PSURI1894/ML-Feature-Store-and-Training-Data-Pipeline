"""Offline store interface.

Concrete adapters (BigQuery, Snowflake, Iceberg, DuckDB) implement this so the
training service and batch jobs are storage-agnostic.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True, slots=True)
class OfflineWriteResult:
    feature_view: str
    rows_written: int
    partitions_touched: tuple[str, ...]


class OfflineStore(abc.ABC):
    """Abstract offline store."""

    @abc.abstractmethod
    def write(self, feature_view: str, df: pd.DataFrame) -> OfflineWriteResult:
        """Write/append feature rows. Implementations MUST be idempotent per
        (entity_id, event_ts) so backfills can be re-run safely."""

    @abc.abstractmethod
    def read_range(
        self, feature_view: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Read feature rows whose ``event_ts`` falls in [start, end)."""

    @abc.abstractmethod
    def point_in_time_query(
        self,
        feature_view: str,
        entity_df: pd.DataFrame,
        *,
        event_ts_col: str = "event_ts",
    ) -> pd.DataFrame:
        """Push the as-of join into the warehouse where possible (BQ/Snowflake).

        ``entity_df`` has entity join keys + an event-timestamp column. Returns the
        entity rows enriched with the most recent feature values as-of each event.
        """

    @abc.abstractmethod
    def latest_event_ts(self, feature_view: str) -> datetime | None:
        """Newest ``event_ts`` present — used for freshness monitoring."""

    def healthcheck(self) -> bool:  # pragma: no cover - trivial default
        return True
