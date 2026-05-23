"""Adversarial point-in-time correctness suite.

These tests inject future-dated feature rows and assert they never appear in the
joined output. They are the regression lock for the ``direction="nearest"``
leakage bug. Marked ``pit`` so ``make test-pit`` runs them in isolation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from feature_platform.training.point_in_time import point_in_time_join

UTC = timezone.utc
pytestmark = pytest.mark.pit


def _ts(day: int, hour: int = 0) -> datetime:
    return datetime(2026, 5, day, hour, tzinfo=UTC)


def test_future_value_is_never_selected() -> None:
    # A future feature row (day 11) is *closer* to the event (day 10) than the
    # past row (day 1). "nearest" would leak day 11; "backward" must pick day 1.
    entities = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(10)]})
    features = pd.DataFrame(
        {
            "entity_id": ["u1", "u1"],
            "event_ts": [_ts(1), _ts(11)],
            "txn_count_30d": [100, 999],
        }
    )
    out = point_in_time_join(entities, features)
    assert out.loc[0, "txn_count_30d"] == 100


def test_exact_timestamp_match_is_included() -> None:
    entities = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(10)]})
    features = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(10)], "v": [7]})
    assert point_in_time_join(entities, features).loc[0, "v"] == 7


def test_ttl_drops_stale_match() -> None:
    entities = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(30)]})
    features = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(1)], "v": [5]})
    out = point_in_time_join(entities, features, ttl=timedelta(days=7))
    assert pd.isna(out.loc[0, "v"])      # 29 days old > 7d TTL -> missing


def test_composite_key_no_leakage() -> None:
    entities = pd.DataFrame(
        {"entity_id": ["u1|m1", "u1|m2"], "event_ts": [_ts(10), _ts(10)]}
    )
    features = pd.DataFrame(
        {
            "entity_id": ["u1|m1", "u1|m1", "u1|m2"],
            "event_ts": [_ts(9), _ts(20), _ts(5)],   # day 20 is future for the event
            "v": [11, 999, 22],
        }
    )
    out = point_in_time_join(entities, features).sort_values("entity_id")
    assert out["v"].tolist() == [11, 22]


def test_no_match_yields_null() -> None:
    entities = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(1)]})
    features = pd.DataFrame({"entity_id": ["u1"], "event_ts": [_ts(5)], "v": [5]})
    out = point_in_time_join(entities, features)
    assert pd.isna(out.loc[0, "v"])      # only future data exists -> nothing as-of
