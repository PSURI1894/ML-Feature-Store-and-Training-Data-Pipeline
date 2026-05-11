"""Example: train a model on a point-in-time-correct dataset and log provenance.

    python examples/train_model_with_features.py

Builds the dataset via the training service, trains a tiny model, and records the
feature-view versions to MLflow so the run is auditable and reproducible.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from feature_platform.mlflow_integration.tracking import log_feature_metadata
from feature_platform.offline.duckdb_store import DuckDBOfflineStore
from feature_platform.training.dataset_builder import TrainingDataService
from feature_platform.training.entity_spec import TrainingDataRequest

UTC = timezone.utc


def main() -> None:
    store = DuckDBOfflineStore(root="data/train_example")
    base = datetime(2026, 5, 1, tzinfo=UTC)
    store.write(
        "user_features_v2",
        pd.DataFrame(
            [
                {"entity_id": "u1", "event_ts": base + timedelta(days=d),
                 "txn_count_30d": d, "created_ts": base + timedelta(days=d)}
                for d in range(30)
            ]
        ),
    )

    entity_df = pd.DataFrame(
        {"entity_id": ["u1"], "event_ts": [base + timedelta(days=20)], "label": [1]}
    )
    request = TrainingDataRequest(
        entity_df=entity_df,
        feature_views=["user_features_v2"],
        label_col="label",
        feature_view_versions={"user_features_v2": 2},
    )
    dataset = TrainingDataService(store).build(request)
    print(dataset.df.to_string(index=False))

    # ... fit a model here ...
    log_feature_metadata(
        dataset.feature_view_versions,
        feature_service="underwriting_v1",
        extra_tags={"algo": "xgboost", "rows": dataset.n_rows},
    )


if __name__ == "__main__":
    main()
