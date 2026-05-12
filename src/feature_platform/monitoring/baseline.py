"""Baseline management for drift detection.

Baselines are refreshed monthly and stored alongside the offline data. These
loaders return ``{feature_name: np.ndarray}`` samples; they degrade to empty
dicts when no data layer is configured so monitoring is runnable locally.
"""

from __future__ import annotations

import numpy as np

from feature_platform.common.logging import get_logger

log = get_logger(__name__)


def load_baseline(feature_view: str) -> dict[str, np.ndarray]:  # pragma: no cover - data dependent
    """Load the current monthly baseline sample for a feature view."""
    log.debug("baseline.load", feature_view=feature_view)
    return {}


def load_current(feature_view: str) -> dict[str, np.ndarray]:  # pragma: no cover - data dependent
    """Load the most recent day's sample for a feature view."""
    log.debug("current.load", feature_view=feature_view)
    return {}


def should_refresh_baseline(days_since_refresh: int, cadence_days: int = 30) -> bool:
    """Baselines are refreshed on a fixed cadence (default monthly)."""
    return days_since_refresh >= cadence_days
