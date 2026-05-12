"""Declarative expectations for feature columns.

A small, dependency-free expectation model that mirrors a subset of Great
Expectations so checks run inside batch/stream jobs without spinning up GE. The
full GE suite (great_expectations/) is used in CI and scheduled validation.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class Expectation:
    column: str
    kind: str            # not_null | between | in_set | unique
    params: dict

    def check(self, df: pd.DataFrame) -> tuple[bool, float]:
        """Return (passed, observed_fraction_failing)."""
        if self.column not in df.columns or df.empty:
            return False, 1.0
        col = df[self.column]
        n = len(col)
        if self.kind == "not_null":
            failing = int(col.isna().sum())
        elif self.kind == "between":
            lo, hi = self.params["min"], self.params["max"]
            failing = int(((col < lo) | (col > hi)).sum())
        elif self.kind == "in_set":
            failing = int((~col.isin(self.params["values"])).sum())
        elif self.kind == "unique":
            failing = int(n - col.nunique(dropna=True))
        else:
            raise ValueError(f"unknown expectation kind {self.kind!r}")
        return failing == 0, failing / n


USER_FEATURES_EXPECTATIONS = [
    Expectation("entity_id", "not_null", {}),
    Expectation("txn_count_30d", "between", {"min": 0, "max": 100_000}),
    Expectation("chargeback_rate_90d", "between", {"min": 0.0, "max": 1.0}),
    Expectation("home_country", "not_null", {}),
]
