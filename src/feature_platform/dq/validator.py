"""Run expectations over a feature frame and summarise pass/fail.

Used as a gate in batch jobs: features that fail hard expectations are not
written to the online store, preventing a bad batch from corrupting serving.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import pandas as pd

from feature_platform.common.logging import get_logger
from feature_platform.dq.expectations import Expectation

log = get_logger(__name__)


@dataclass(slots=True)
class DQResult:
    passed: bool = True
    failures: list[str] = field(default_factory=list)
    details: dict[str, float] = field(default_factory=dict)


def validate_dataframe(
    df: pd.DataFrame, expectations: Sequence[Expectation], *, fail_fraction: float = 0.0
) -> DQResult:
    """Evaluate expectations. ``fail_fraction`` tolerates a small fraction of
    violations (e.g. 0.01) before failing the check."""
    result = DQResult()
    for exp in expectations:
        ok, frac_failing = exp.check(df)
        result.details[f"{exp.column}:{exp.kind}"] = frac_failing
        if not ok and frac_failing > fail_fraction:
            result.passed = False
            result.failures.append(
                f"{exp.column} {exp.kind}: {frac_failing:.2%} rows violate"
            )
    if not result.passed:
        log.warning("dq.failed", failures=result.failures)
    return result
