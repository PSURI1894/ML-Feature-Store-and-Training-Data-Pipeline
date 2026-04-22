"""Tests for feature-definition validation rules."""

from __future__ import annotations

from datetime import timedelta

import pytest

from feature_platform.registry.models import FeatureViewRecord, RegistrySnapshot
from feature_platform.registry.validation import (
    check_compatibility,
    validate_record,
    validate_snapshot,
)


def _record(**overrides) -> FeatureViewRecord:
    base = dict(
        name="user_features_v2",
        version=2,
        entities=("user",),
        feature_names=("a", "b"),
        owner="eng@example.com",
        team="growth",
        sensitivity="financial",
        tier="batch",
        ttl=timedelta(days=90),
        sla_freshness=timedelta(hours=24),
        online=True,
    )
    base.update(overrides)
    return FeatureViewRecord(**base)


def test_valid_record_has_no_errors() -> None:
    assert validate_record(_record()) == []


@pytest.mark.parametrize(
    "overrides,rule",
    [
        ({"name": "BadName"}, "naming"),
        ({"name": "no_version"}, "naming"),
        ({"owner": "not-an-email"}, "owner"),
        ({"team": ""}, "team"),
        ({"sensitivity": "secret"}, "sensitivity"),
        ({"tier": "warp-speed"}, "tier"),
        ({"ttl": timedelta(0)}, "ttl"),
        ({"sla_freshness": timedelta(days=365)}, "sla_vs_ttl"),
    ],
)
def test_invalid_records(overrides: dict, rule: str) -> None:
    errors = validate_record(_record(**overrides))
    assert any(e.rule == rule for e in errors), f"expected rule {rule}, got {errors}"


def test_duplicate_names_flagged() -> None:
    snap = RegistrySnapshot(feature_views=[_record(), _record()])
    assert any(e.rule == "unique" for e in validate_snapshot(snap))


def test_removing_feature_requires_version_bump() -> None:
    old = RegistrySnapshot(feature_views=[_record(feature_names=("a", "b", "c"))])
    new = RegistrySnapshot(feature_views=[_record(feature_names=("a", "b"))])
    errors = check_compatibility(old, new)
    assert any(e.rule == "compat" for e in errors)
