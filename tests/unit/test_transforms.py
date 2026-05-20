"""Tests for the shared pure feature transforms."""

from __future__ import annotations

import math

from feature_platform.batch.transforms import (
    amount_zscore,
    chargeback_rate,
    is_cross_border,
    log1p_amount,
    velocity,
)


def test_amount_zscore() -> None:
    assert amount_zscore(15.0, 10.0, 5.0) == 1.0
    assert amount_zscore(10.0, 10.0, 0.0) == 0.0   # guard against /0


def test_chargeback_rate() -> None:
    assert chargeback_rate(2, 100) == 0.02
    assert chargeback_rate(0, 0) == 0.0


def test_log1p_amount_clamps_negative() -> None:
    assert log1p_amount(-5) == 0.0
    assert math.isclose(log1p_amount(math.e - 1), 1.0)


def test_is_cross_border() -> None:
    assert is_cross_border("US", "GB") == 1
    assert is_cross_border("US", "US") == 0
    assert is_cross_border(None, "US") == 0


def test_velocity() -> None:
    assert velocity(10, 300) == 2.0   # 10 txns / 5 min
    assert velocity(5, 0) == 0.0
