"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

UTC = timezone.utc


@pytest.fixture()
def fake_redis():
    import fakeredis

    return fakeredis.FakeRedis()


@pytest.fixture()
def online_store(fake_redis):
    from feature_platform.online.redis_store import RedisOnlineStore

    return RedisOnlineStore(client=fake_redis, default_ttl=3600)


@pytest.fixture()
def offline_store(tmp_path):
    from feature_platform.offline.duckdb_store import DuckDBOfflineStore

    return DuckDBOfflineStore(root=tmp_path / "offline")


@pytest.fixture()
def user_feature_frame() -> pd.DataFrame:
    base = datetime(2026, 5, 1, tzinfo=UTC)
    return pd.DataFrame(
        [
            {
                "entity_id": "u1",
                "event_ts": base.replace(day=1 + d),
                "txn_count_30d": d,
                "txn_amount_avg_30d": 10.0 + d,
                "created_ts": base.replace(day=1 + d),
            }
            for d in range(10)
        ]
    )
