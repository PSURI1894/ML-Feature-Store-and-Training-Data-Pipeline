"""Specification of a training-data request.

A request is a set of feature views/services plus the entity rows
``(entity_id, event_ts[, label])`` to enrich. Validation here fails fast before
we touch the (expensive) offline store.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class TrainingDataRequest:
    entity_df: pd.DataFrame
    feature_views: list[str]
    label_col: str | None = None
    event_ts_col: str = "event_ts"
    feature_view_versions: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = {"entity_id", self.event_ts_col} - set(self.entity_df.columns)
        if missing:
            raise ValueError(f"entity_df missing required columns: {sorted(missing)}")
        if self.label_col and self.label_col not in self.entity_df.columns:
            raise ValueError(f"label_col {self.label_col!r} not in entity_df")
        if not self.feature_views:
            raise ValueError("at least one feature view is required")

    @property
    def time_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        ts = pd.to_datetime(self.entity_df[self.event_ts_col], utc=True)
        return ts.min(), ts.max()
