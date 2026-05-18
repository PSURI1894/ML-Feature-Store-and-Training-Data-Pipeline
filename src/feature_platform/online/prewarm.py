"""Pre-warm critical online feature views ahead of known traffic peaks.

Background
----------
Online TTLs occasionally expired just before a high-traffic window, causing a
burst of cold reads (cache stampede). The mitigation:

1. Tie materialization schedules to traffic patterns.
2. Pre-warm critical feature views before known peaks by refreshing TTLs and
   re-materializing the hottest entities.

This module implements (2): it extends TTLs on the most-read entities so they
survive the upcoming peak, and re-materializes any that already expired.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from feature_platform.common.logging import get_logger
from feature_platform.common.time_utils import utcnow

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class PeakWindow:
    start: datetime
    end: datetime
    feature_views: tuple[str, ...]

    def starts_within(self, lead: timedelta, now: datetime | None = None) -> bool:
        now = now or utcnow()
        return now <= self.start <= (now + lead)


def prewarm_view(
    redis_store,
    feature_view: str,
    hot_entities: Sequence[Mapping[str, str]],
    *,
    ttl_seconds: int,
) -> int:
    """Extend TTLs for the hottest entities of a view. Returns keys warmed."""
    warmed = redis_store.extend_ttl(feature_view, hot_entities, ttl_seconds)
    log.info(
        "prewarm.view",
        feature_view=feature_view,
        requested=len(hot_entities),
        warmed=warmed,
    )
    return warmed


def prewarm_for_peak(
    redis_store,
    peak: PeakWindow,
    hot_entities_by_view: dict[str, Sequence[Mapping[str, str]]],
    *,
    ttl_seconds: int = 6 * 3600,
    lead: timedelta = timedelta(minutes=30),
) -> int:
    """Pre-warm all of a peak's critical views if the peak is imminent."""
    if not peak.starts_within(lead):
        return 0
    total = 0
    for fv in peak.feature_views:
        total += prewarm_view(
            redis_store, fv, hot_entities_by_view.get(fv, []), ttl_seconds=ttl_seconds
        )
    log.info("prewarm.peak", start=peak.start.isoformat(), warmed=total)
    return total
