"""Pure feature transformations — the single source of truth for feature logic.

These functions are framework-agnostic (operate on plain values / small frames)
so the *same* logic is reachable from Spark (batch), Flink (streaming) and the
on-demand service. This is how training–serving skew is prevented.
"""

from __future__ import annotations

import math


def amount_zscore(amount: float, mean: float, std: float) -> float:
    """Z-score of a transaction amount vs. the user's rolling distribution."""
    if std <= 0:
        return 0.0
    return (amount - mean) / std


def chargeback_rate(chargebacks: int, txns: int) -> float:
    """Chargebacks per transaction over a window (0 when no txns)."""
    return chargebacks / txns if txns > 0 else 0.0


def log1p_amount(amount: float) -> float:
    """Stable log transform used by several models; clamps negatives to 0."""
    return math.log1p(max(amount, 0.0))


def is_cross_border(user_country: str | None, merchant_country: str | None) -> int:
    if not user_country or not merchant_country:
        return 0
    return int(user_country != merchant_country)


def velocity(count_window: int, window_seconds: int) -> float:
    """Transactions per minute within a window."""
    if window_seconds <= 0:
        return 0.0
    return count_window / (window_seconds / 60.0)
