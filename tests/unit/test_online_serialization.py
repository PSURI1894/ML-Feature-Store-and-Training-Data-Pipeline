"""Tests for online serialization and Redis store behaviour (fakeredis)."""

from __future__ import annotations

import fakeredis
import pytest

from feature_platform.online.redis_store import RedisOnlineStore
from feature_platform.online.serialization import deserialize, serialize


def test_serialize_roundtrip() -> None:
    features = {"txn_count_30d": 12, "amount_avg": 4.5, "country": "US", "flag": True}
    assert deserialize(serialize(features)) == features


def test_deserialize_none_is_none() -> None:
    assert deserialize(None) is None
    assert deserialize(b"") is None


def test_unsupported_version_raises() -> None:
    blob = bytes([99]) + b"garbage"
    with pytest.raises(ValueError, match="schema version"):
        deserialize(blob)


@pytest.fixture()
def store() -> RedisOnlineStore:
    return RedisOnlineStore(client=fakeredis.FakeRedis(), default_ttl=3600)


def test_write_read_roundtrip(store: RedisOnlineStore) -> None:
    store.write("user_features_v2", [({"user_id": "u1"}, {"txn_count_30d": 7})])
    assert store.read("user_features_v2", {"user_id": "u1"}) == {"txn_count_30d": 7}


def test_read_missing_returns_none(store: RedisOnlineStore) -> None:
    assert store.read("user_features_v2", {"user_id": "ghost"}) is None


def test_read_many_preserves_order(store: RedisOnlineStore) -> None:
    store.write(
        "user_features_v2",
        [({"user_id": "u1"}, {"v": 1}), ({"user_id": "u3"}, {"v": 3})],
    )
    result = store.read_many(
        "user_features_v2",
        [{"user_id": "u1"}, {"user_id": "u2"}, {"user_id": "u3"}],
    )
    assert result == [{"v": 1}, None, {"v": 3}]


def test_delete_removes_key(store: RedisOnlineStore) -> None:
    store.write("user_features_v2", [({"user_id": "u1"}, {"v": 1})])
    store.delete("user_features_v2", {"user_id": "u1"})
    assert store.read("user_features_v2", {"user_id": "u1"}) is None
