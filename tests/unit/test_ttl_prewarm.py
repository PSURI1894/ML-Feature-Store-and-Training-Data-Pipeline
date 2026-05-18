"""Tests for TTL pre-warming ahead of traffic peaks."""

from __future__ import annotations

from datetime import timedelta

import fakeredis

from feature_platform.common.time_utils import utcnow
from feature_platform.online.prewarm import PeakWindow, prewarm_for_peak, prewarm_view
from feature_platform.online.redis_store import RedisOnlineStore


def _store() -> RedisOnlineStore:
    return RedisOnlineStore(client=fakeredis.FakeRedis(), default_ttl=60)


def test_extend_ttl_keeps_key_alive() -> None:
    store = _store()
    store.write("user_features_v2", [({"entity_id": "u1"}, {"v": 1})], ttl_seconds=60)
    warmed = store.extend_ttl("user_features_v2", [{"entity_id": "u1"}], ttl_seconds=3600)
    assert warmed == 1
    assert store.client.ttl(b"user_features_v2:u1") > 60


def test_extend_ttl_does_not_resurrect_missing_keys() -> None:
    store = _store()
    warmed = store.extend_ttl("user_features_v2", [{"entity_id": "ghost"}], ttl_seconds=3600)
    assert warmed == 0


def test_prewarm_only_when_peak_imminent() -> None:
    store = _store()
    store.write("user_features_v2", [({"entity_id": "u1"}, {"v": 1})])
    far_peak = PeakWindow(
        start=utcnow() + timedelta(hours=5), end=utcnow() + timedelta(hours=6),
        feature_views=("user_features_v2",),
    )
    assert prewarm_for_peak(store, far_peak, {"user_features_v2": [{"entity_id": "u1"}]}) == 0

    soon_peak = PeakWindow(
        start=utcnow() + timedelta(minutes=10), end=utcnow() + timedelta(hours=1),
        feature_views=("user_features_v2",),
    )
    assert prewarm_for_peak(store, soon_peak, {"user_features_v2": [{"entity_id": "u1"}]}) == 1


def test_prewarm_view_reports_count() -> None:
    store = _store()
    store.write("user_features_v2", [({"entity_id": "u1"}, {"v": 1}), ({"entity_id": "u2"}, {"v": 2})])
    assert prewarm_view(store, "user_features_v2", [{"entity_id": "u1"}, {"entity_id": "u2"}], ttl_seconds=600) == 2
