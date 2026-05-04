"""Basic happy-path tests for the point-in-time join.

The adversarial future-leakage suite lives in tests/pit_correctness/ (added with
the leakage fix). These cover the common case where all features precede events.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from feature_platform.training.point_in_time import point_in_time_join

UTC = timezone.utc


def _ts(day: int) -> datetime:
    return datetime(2026, 5, day, tzinfo=UTC)


def test_attaches_most_recent_past_value() -> None:
    entities = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(10)]})
    features = pd.DataFrame(
        {
            "entity_id": ["u1", "u1", "u1"],
            "event_ts": [_ts(1), _ts(5), _ts(9)],
            "txn_count_30d": [1, 5, 9],
        }
    )
    out = point_in_time_join(entities, features)
    assert out.loc[0, "txn_count_30d"] == 9


def test_empty_entities_returns_empty() -> None:
    out = point_in_time_join(
        pd.DataFrame(columns=["entity_id", "event_ts"]),
        pd.DataFrame(columns=["entity_id", "event_ts", "f"]),
    )
    assert out.empty


def test_per_entity_isolation() -> None:
    entities = pd.DataFrame({"entity_id": ["u1", "u2"], "event_ts": [_ts(10), _ts(10)]})
    features = pd.DataFrame(
        {"entity_id": ["u1", "u2"], "event_ts": [_ts(9), _ts(8)], "v": [91, 82]}
    )
    out = point_in_time_join(entities, features).sort_values("entity_id")
    assert out["v"].tolist() == [91, 82]
