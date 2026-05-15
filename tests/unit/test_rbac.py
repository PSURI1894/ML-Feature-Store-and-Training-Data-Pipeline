"""Tests for RBAC and right-to-be-forgotten."""

from __future__ import annotations

import fakeredis
import pytest

from feature_platform.common.exceptions import AccessDeniedError
from feature_platform.common.types import Sensitivity
from feature_platform.governance.rbac import can_read, enforce_read
from feature_platform.governance.rtbf import RightToBeForgotten
from feature_platform.offline.duckdb_store import DuckDBOfflineStore
from feature_platform.online.redis_store import RedisOnlineStore


def test_viewer_cannot_read_pii() -> None:
    assert not can_read("viewer", Sensitivity.PII).allowed


def test_ml_engineer_can_read_pii_and_must_audit() -> None:
    decision = can_read("ml-engineer", Sensitivity.PII)
    assert decision.allowed and decision.must_audit


def test_public_not_audited() -> None:
    assert not can_read("viewer", Sensitivity.PUBLIC).must_audit


def test_enforce_read_raises_for_denied() -> None:
    with pytest.raises(AccessDeniedError):
        enforce_read("viewer", Sensitivity.PII, principal="u@x.com", feature_view="user_features_v2")


def test_rtbf_deletes_online(tmp_path) -> None:
    online = RedisOnlineStore(client=fakeredis.FakeRedis())
    offline = DuckDBOfflineStore(root=tmp_path)
    online.write("user_features_v2", [({"entity_id": "u1"}, {"v": 1})])
    rtbf = RightToBeForgotten(online, offline, ["user_features_v2"])

    result = rtbf.erase("u1")
    assert result.completed
    assert online.read("user_features_v2", {"entity_id": "u1"}) is None
