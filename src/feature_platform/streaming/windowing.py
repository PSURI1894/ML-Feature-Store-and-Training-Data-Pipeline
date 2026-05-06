"""Time-windowed aggregation primitives for streaming features.

Kept engine-agnostic and pure so they're unit-testable without a running Flink
cluster and reusable by the near-real-time Spark Structured Streaming tier.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from feature_platform.common.time_utils import ensure_utc


@dataclass(slots=True)
class SlidingCountWindow:
    """Sliding window over event timestamps; emits count + sum within `width`."""

    width: timedelta
    _events: deque[tuple[datetime, float]] = field(default_factory=deque)

    def add(self, ts: datetime, value: float = 1.0) -> None:
        self._events.append((ensure_utc(ts), value))

    def _evict(self, now: datetime) -> None:
        cutoff = ensure_utc(now) - self.width
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def count(self, now: datetime) -> int:
        self._evict(now)
        return len(self._events)

    def sum(self, now: datetime) -> float:
        self._evict(now)
        return sum(v for _, v in self._events)

    def velocity_per_min(self, now: datetime) -> float:
        seconds = self.width.total_seconds()
        return self.count(now) / (seconds / 60.0) if seconds else 0.0
