"""Example: build a point-in-time-correct training dataset locally.

    python examples/build_training_dataset.py

Uses the DuckDB offline store with synthetic data so it runs with no external
services. Demonstrates the no-leakage guarantee end to end.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from feature_platform.offline.duckdb_store import DuckDBOfflineStore
from feature_platform.training.dataset_builder import TrainingDataService
from feature_platform.training.entity_spec import TrainingDataRequest

UTC = timezone.utc


def _seed(store: DuckDBOfflineStore) -> None:
    base = datetime(2026, 5, 1, tzinfo=UTC)
    rows = []
    for day in range(30):
        ts = base + timedelta(days=day)
        rows.append(
            {
                "entity_id": "u1",
                "event_ts": ts,
                "txn_count_30d": day,
                "txn_amount_avg_30d": 10.0 + day,
                "created_ts": ts,
            }
        )
    store.write("user_features_v2", pd.DataFrame(rows))


def main() -> None:
    store = DuckDBOfflineStore(root="data/example_offline")
    _seed(store)

    entity_df = pd.DataFrame(
        {
            "entity_id": ["u1", "u1"],
            "event_ts": [
                datetime(2026, 5, 10, tzinfo=UTC),
                datetime(2026, 5, 20, tzinfo=UTC),
            ],
            "label": [0, 1],
        }
    )

    request = TrainingDataRequest(
        entity_df=entity_df, feature_views=["user_features_v2"], label_col="label"
    )
    dataset = TrainingDataService(store).build(request)

    print(dataset.df.to_string(index=False))
    print("\nfeature_view_versions:", dataset.feature_view_versions)
    # As-of 2026-05-10 the txn_count_30d must be 9 (value written on day 9), never a future value.


if __name__ == "__main__":
    main()
