"""Time helpers. All timestamps in the platform are timezone-aware UTC.

Centralising this avoids the single most common cause of point-in-time bugs:
comparing a naive timestamp against a tz-aware one (or mixing local zones).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

UTC = timezone.utc

_DURATION_RE = re.compile(r"^(?P<value>\d+)(?P<unit>[smhdw])$")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def utcnow() -> datetime:
    """Timezone-aware current UTC time."""
    return datetime.now(tz=UTC)


def ensure_utc(ts: datetime) -> datetime:
    """Coerce a datetime to tz-aware UTC, assuming naive datetimes are already UTC."""
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC)


def parse_duration(spec: str) -> timedelta:
    """Parse a compact duration like ``'90d'``, ``'24h'``, ``'5m'`` into a timedelta."""
    match = _DURATION_RE.match(spec.strip())
    if not match:
        raise ValueError(f"invalid duration: {spec!r} (expected e.g. '24h', '7d')")
    return timedelta(seconds=int(match["value"]) * _UNIT_SECONDS[match["unit"]])


def event_date(ts: datetime) -> str:
    """Partition key (``YYYY-MM-DD``) derived from an event timestamp, in UTC."""
    return ensure_utc(ts).strftime("%Y-%m-%d")


def is_within_ttl(feature_ts: datetime, event_ts: datetime, ttl: timedelta) -> bool:
    """True iff ``feature_ts`` is usable as-of ``event_ts`` given a freshness ``ttl``.

    This encodes the two point-in-time constraints in one place:
    ``feature_ts <= event_ts`` (no leakage) and ``event_ts - feature_ts <= ttl`` (fresh).
    """
    feature_ts = ensure_utc(feature_ts)
    event_ts = ensure_utc(event_ts)
    return feature_ts <= event_ts and (event_ts - feature_ts) <= ttl
