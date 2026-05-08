"""Tests for drift statistics (PSI / KS)."""

from __future__ import annotations

import numpy as np

from feature_platform.monitoring.drift import evaluate_feature, psi
from feature_platform.monitoring.null_rate import compute_null_rates


def test_psi_zero_for_identical_distributions() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=10_000)
    assert psi(x, x) < 0.01


def test_psi_large_for_shifted_distribution() -> None:
    rng = np.random.default_rng(0)
    base = rng.normal(0, 1, 10_000)
    shifted = rng.normal(3, 1, 10_000)
    assert psi(base, shifted) > 0.2


def test_evaluate_feature_alerts_on_shift() -> None:
    rng = np.random.default_rng(1)
    base = rng.normal(0, 1, 5_000)
    shifted = rng.normal(2, 1, 5_000)
    result = evaluate_feature("amount", base, shifted)
    assert result.alert is True


def test_evaluate_feature_no_alert_when_stable() -> None:
    rng = np.random.default_rng(2)
    base = rng.normal(0, 1, 5_000)
    similar = rng.normal(0, 1, 5_000)
    result = evaluate_feature("amount", base, similar)
    assert result.alert is False


def test_null_rate_flags_high_nulls() -> None:
    import pandas as pd

    df = pd.DataFrame({"entity_id": ["a", "b", "c", "d"], "f": [1, None, None, None]})
    results = compute_null_rates(df, threshold=0.5)
    f = next(r for r in results if r.feature == "f")
    assert f.breached
