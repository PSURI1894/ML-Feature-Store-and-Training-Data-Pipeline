"""Build a wide, point-in-time-correct training dataset from a request.

Joins every requested feature view onto the entity rows with an as-of join, then
returns a single wide frame ``entity_id, event_ts, feature_1..N[, label]`` ready
for model training. The set of (feature_view -> version) used is returned so the
caller can pin it to the MLflow run.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from feature_platform.common.logging import get_logger
from feature_platform.offline.store import OfflineStore
from feature_platform.training.entity_spec import TrainingDataRequest
from feature_platform.training.point_in_time import point_in_time_join

log = get_logger(__name__)


@dataclass(slots=True)
class TrainingDataset:
    df: pd.DataFrame
    feature_view_versions: dict[str, int]

    @property
    def n_rows(self) -> int:
        return len(self.df)


class TrainingDataService:
    def __init__(self, offline_store: OfflineStore) -> None:
        self.offline = offline_store

    def build(self, request: TrainingDataRequest) -> TrainingDataset:
        result = request.entity_df.copy()
        start, end = request.time_range
        versions: dict[str, int] = {}

        for fv in request.feature_views:
            features = self.offline.read_range(fv, start.to_pydatetime(), end.to_pydatetime())
            if features.empty:
                log.warning("training.no_features", feature_view=fv)
                continue
            enriched = point_in_time_join(
                result[["entity_id", request.event_ts_col]],
                features,
                event_ts_col=request.event_ts_col,
            )
            feature_cols = [
                c for c in enriched.columns
                if c not in {"entity_id", request.event_ts_col, "created_ts", "event_date"}
            ]
            result = result.merge(
                enriched[["entity_id", request.event_ts_col, *feature_cols]],
                on=["entity_id", request.event_ts_col],
                how="left",
            )
            versions[fv] = request.feature_view_versions.get(fv, 1)

        log.info("training.built", rows=len(result), feature_views=list(versions))
        return TrainingDataset(df=result, feature_view_versions=versions)
