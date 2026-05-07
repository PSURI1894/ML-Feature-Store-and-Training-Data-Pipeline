"""Freshness monitoring: alert when a view is staler than its SLA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from feature_platform.common.logging import get_logger
from feature_platform.common.metrics import FEATURE_FRESHNESS_SECONDS
from feature_platform.common.time_utils import ensure_utc, utcnow

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class FreshnessResult:
    feature_view: str
    age_seconds: float
    sla_seconds: float

    @property
    def breached(self) -> bool:
        return self.age_seconds > self.sla_seconds


def check_freshness(
    feature_view: str, latest_event_ts: datetime | None, sla: timedelta, now: datetime | None = None
) -> FreshnessResult:
    now = ensure_utc(now or utcnow())
    if latest_event_ts is None:
        age = float("inf")
    else:
        age = (now - ensure_utc(latest_event_ts)).total_seconds()
    if age != float("inf"):
        FEATURE_FRESHNESS_SECONDS.labels(feature_view).set(age)
    result = FreshnessResult(feature_view, age, sla.total_seconds())
    if result.breached:
        log.warning(
            "freshness.breach", feature_view=feature_view, age_s=age, sla_s=sla.total_seconds()
        )
    return result
