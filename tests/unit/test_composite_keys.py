"""Regression tests for composite online-key collisions."""

from __future__ import annotations

from feature_platform.online.key_schema import entity_id, online_key


def test_simple_key() -> None:
    assert online_key("user_features_v2", {"user_id": "u1"}) == "user_features_v2:u1"


def test_composite_key_sorted_order() -> None:
    key = online_key("user_merchant_features_v1", {"user_id": "u1", "merchant_id": "m9"})
    # sorted by key name: merchant_id then user_id
    assert key == "user_merchant_features_v1:m9|u1"


def test_separator_in_value_does_not_collide() -> None:
    # The classic bug: these two distinct entities must not map to the same id.
    a = entity_id({"a": "x|y", "b": "z"})
    b = entity_id({"a": "x", "b": "y|z"})
    assert a != b


def test_escape_is_injective_for_backslash() -> None:
    a = entity_id({"a": "x\\", "b": "y"})
    b = entity_id({"a": "x", "b": "\\y"})
    assert a != b


def test_roundtrip_distinct_pairs() -> None:
    seen = {
        entity_id({"a": v1, "b": v2})
        for v1 in ("p", "p|q", "p\\q")
        for v2 in ("r", "r|s")
    }
    # 3 x 2 distinct inputs must yield 6 distinct ids (no collisions).
    assert len(seen) == 6
