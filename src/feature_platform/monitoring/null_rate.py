"""Null-rate monitoring: a spike in nulls usually means an upstream contract break."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class NullRateResult:
    feature: str
    null_rate: float
    threshold: float

    @property
    def breached(self) -> bool:
        return self.null_rate > self.threshold


def compute_null_rates(df: pd.DataFrame, threshold: float = 0.05) -> list[NullRateResult]:
    """Per-column null fraction; flag columns above ``threshold``."""
    reserved = {"entity_id", "event_ts", "created_ts", "event_date"}
    results: list[NullRateResult] = []
    n = len(df)
    if n == 0:
        return results
    for col in df.columns:
        if col in reserved:
            continue
        rate = float(df[col].isna().sum()) / n
        results.append(NullRateResult(feature=col, null_rate=rate, threshold=threshold))
    return results
