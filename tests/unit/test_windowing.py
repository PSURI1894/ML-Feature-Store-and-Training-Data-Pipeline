"""Tests for streaming windowing primitives."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from feature_platform.streaming.windowing import SlidingCountWindow

UTC = timezone.utc


def _t(minute: int) -> datetime:
    return datetime(2026, 5, 1, 12, minute, tzinfo=UTC)


def test_counts_within_window() -> None:
    w = SlidingCountWindow(width=timedelta(minutes=5))
    for m in range(0, 6):
        w.add(_t(m), value=float(m))
    # at 12:05, events from 12:00..12:05 are within the 5-min window
    assert w.count(_t(5)) == 6
    assert w.sum(_t(5)) == sum(range(6))


def test_evicts_old_events() -> None:
    w = SlidingCountWindow(width=timedelta(minutes=5))
    w.add(_t(0))
    w.add(_t(1))
    # at 12:10 both events are older than 5 minutes -> evicted
    assert w.count(_t(10)) == 0


def test_velocity_per_min() -> None:
    w = SlidingCountWindow(width=timedelta(minutes=5))
    for m in range(5):
        w.add(_t(m))
    assert w.velocity_per_min(_t(4)) == 1.0   # 5 events / 5 min
