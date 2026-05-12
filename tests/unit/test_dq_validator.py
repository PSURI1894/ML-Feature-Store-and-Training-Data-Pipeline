"""Tests for the DQ validator and inline expectations."""

from __future__ import annotations

import pandas as pd

from feature_platform.dq.expectations import Expectation
from feature_platform.dq.validator import validate_dataframe


def test_passes_when_all_expectations_met() -> None:
    df = pd.DataFrame({"entity_id": ["a", "b"], "txn_count_30d": [1, 5]})
    exps = [
        Expectation("entity_id", "not_null", {}),
        Expectation("txn_count_30d", "between", {"min": 0, "max": 10}),
    ]
    assert validate_dataframe(df, exps).passed


def test_fails_on_out_of_range() -> None:
    df = pd.DataFrame({"txn_count_30d": [1, 999]})
    result = validate_dataframe(df, [Expectation("txn_count_30d", "between", {"min": 0, "max": 10})])
    assert not result.passed
    assert "txn_count_30d" in result.failures[0]


def test_fail_fraction_tolerance() -> None:
    df = pd.DataFrame({"x": list(range(100)) + [10_000]})  # 1/101 outliers
    exp = Expectation("x", "between", {"min": 0, "max": 1000})
    assert validate_dataframe(df, [exp], fail_fraction=0.02).passed
    assert not validate_dataframe(df, [exp], fail_fraction=0.0).passed
