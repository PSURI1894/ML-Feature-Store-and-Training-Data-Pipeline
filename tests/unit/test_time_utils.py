"""Tests for time helpers (the source of most PIT bugs if wrong)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from feature_platform.common.time_utils import (
    ensure_utc,
    event_date,
    is_within_ttl,
    parse_duration,
)


def test_ensure_utc_makes_naive_aware() -> None:
    naive = datetime(2026, 5, 1, 12, 0, 0)
    assert ensure_utc(naive).tzinfo is timezone.utc


@pytest.mark.parametrize(
    "spec,seconds",
    [("30s", 30), ("5m", 300), ("24h", 86_400), ("7d", 604_800), ("2w", 1_209_600)],
)
def test_parse_duration(spec: str, seconds: int) -> None:
    assert parse_duration(spec) == timedelta(seconds=seconds)


def test_parse_duration_invalid() -> None:
    with pytest.raises(ValueError, match="invalid duration"):
        parse_duration("soon")


def test_event_date_is_utc() -> None:
    ts = datetime(2026, 5, 1, 23, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    # 23:30 +05:30 == 18:00 UTC -> same date in UTC
    assert event_date(ts) == "2026-05-01"


def test_is_within_ttl() -> None:
    event = datetime(2026, 5, 10, tzinfo=timezone.utc)
    fresh = datetime(2026, 5, 9, tzinfo=timezone.utc)
    stale = datetime(2026, 4, 1, tzinfo=timezone.utc)
    future = datetime(2026, 5, 11, tzinfo=timezone.utc)
    assert is_within_ttl(fresh, event, timedelta(days=7))
    assert not is_within_ttl(stale, event, timedelta(days=7))
    assert not is_within_ttl(future, event, timedelta(days=7))  # no leakage
