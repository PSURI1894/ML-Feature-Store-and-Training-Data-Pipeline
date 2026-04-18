"""Lightweight domain types used across modules.

These are deliberately plain dataclasses / enums (not Feast objects) so that the
platform's internal contracts don't break every time the Feast SDK changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class Sensitivity(str, Enum):
    """Data sensitivity classification driving RBAC and audit."""

    PUBLIC = "public"
    FINANCIAL = "financial"
    PII = "pii"


class FeatureTier(str, Enum):
    """Cost/latency tier — defaults to BATCH unless justified."""

    REAL_TIME = "real-time"        # Flink
    NEAR_REAL_TIME = "near-real-time"  # Spark structured streaming (5-min)
    BATCH = "batch"               # Spark daily/hourly


class ValueType(str, Enum):
    INT64 = "int64"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BOOL = "bool"
    TIMESTAMP = "timestamp"


@dataclass(frozen=True, slots=True)
class EntityRef:
    name: str
    join_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    name: str
    dtype: ValueType
    description: str = ""


@dataclass(slots=True)
class FeatureViewMeta:
    """Platform-side metadata mirrored from a Feast FeatureView definition."""

    name: str
    version: int
    entities: tuple[str, ...]
    features: tuple[FeatureSpec, ...]
    owner: str
    team: str
    ttl: timedelta
    tier: FeatureTier = FeatureTier.BATCH
    sensitivity: Sensitivity = Sensitivity.PUBLIC
    sla_freshness: timedelta = field(default_factory=lambda: timedelta(hours=24))
    online: bool = True
    offline: bool = True
    source_contract: str | None = None

    @property
    def qualified_name(self) -> str:
        return f"{self.name}_v{self.version}"


@dataclass(frozen=True, slots=True)
class EntityRow:
    """A single (entity, event_ts) request row for point-in-time retrieval."""

    keys: dict[str, str]
    event_ts: datetime
