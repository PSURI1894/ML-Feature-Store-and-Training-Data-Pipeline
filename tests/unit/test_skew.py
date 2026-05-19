"""Tests for training-serving skew reconciliation."""

from __future__ import annotations

import numpy as np

from feature_platform.monitoring.skew import compute_skew, reconcile_view


def test_zero_skew_for_identical_values() -> None:
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert compute_skew(x, x) == 0.0


def test_skew_grows_with_divergence() -> None:
    offline = np.array([10.0, 10.0, 10.0])
    online = np.array([12.0, 12.0, 12.0])
    assert compute_skew(online, offline) > 0.15


def test_mismatched_lengths_return_zero() -> None:
    assert compute_skew(np.array([1.0]), np.array([1.0, 2.0])) == 0.0


def test_reconcile_view_flags_divergent_feature() -> None:
    report = reconcile_view(
        "user_features_v2",
        ["txn_count_30d"],
        online_sample={"txn_count_30d": np.array([100.0, 100.0])},
        offline_sample={"txn_count_30d": np.array([10.0, 10.0])},
    )
    assert report.alerted
    assert report.skews[0].n_compared == 2
