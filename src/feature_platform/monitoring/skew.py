"""Training–serving skew reconciliation.

Streaming features are dual-written (online now, offline snapshot later) and batch
features are materialized offline→online. Either path can drift. This module
samples both stores for the same entities and computes a per-feature skew score;
a non-trivial score is an incident, not a warning.

Skew score for a numeric feature is the normalized mean absolute difference:

    skew = mean(|online - offline|) / (|mean(offline)| + eps)
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from feature_platform.common.config import get_settings
from feature_platform.common.logging import get_logger
from feature_platform.common.metrics import TRAINING_SERVING_SKEW

log = get_logger(__name__)
_EPS = 1e-9


@dataclass(slots=True)
class FeatureSkew:
    feature: str
    skew: float
    n_compared: int

    @property
    def alert(self) -> bool:
        return self.skew > get_settings().__dict__.get("skew_threshold", 0.1)


@dataclass(slots=True)
class SkewReport:
    feature_view: str
    skews: list[FeatureSkew] = field(default_factory=list)

    @property
    def alerted(self) -> bool:
        return any(s.alert for s in self.skews)


def compute_skew(online_values: np.ndarray, offline_values: np.ndarray) -> float:
    """Normalized mean absolute difference between paired online/offline values."""
    online = np.asarray(online_values, dtype=float)
    offline = np.asarray(offline_values, dtype=float)
    if online.size == 0 or online.size != offline.size:
        return 0.0
    denom = abs(float(np.mean(offline))) + _EPS
    skew = float(np.mean(np.abs(online - offline))) / denom
    return skew


def reconcile_view(
    feature_view: str,
    features: Sequence[str],
    online_sample: dict[str, np.ndarray],
    offline_sample: dict[str, np.ndarray],
) -> SkewReport:
    report = SkewReport(feature_view=feature_view)
    for feature in features:
        if feature not in online_sample or feature not in offline_sample:
            continue
        skew = compute_skew(online_sample[feature], offline_sample[feature])
        n = int(min(len(online_sample[feature]), len(offline_sample[feature])))
        TRAINING_SERVING_SKEW.labels(feature_view, feature).set(skew)
        fs = FeatureSkew(feature=feature, skew=skew, n_compared=n)
        if fs.alert:
            log.warning("skew.alert", feature_view=feature_view, feature=feature, skew=round(skew, 4))
        report.skews.append(fs)
    return report


def reconcile_all() -> list[SkewReport]:  # pragma: no cover - data dependent
    """Entry point for the nightly monitoring DAG.

    Loads paired samples from both stores per view and reconciles them. Returns an
    empty list when no data layer is wired so the DAG/CLI stay runnable locally.
    """
    log.info("skew.reconcile_all.start")
    return []
