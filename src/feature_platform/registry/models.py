"""Platform-side records mirrored from Feast objects.

We snapshot the Feast registry into plain records so the catalog UI, validation
and compatibility checks don't depend on the Feast SDK's internal types.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import timedelta

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*_v\d+$")


@dataclass(frozen=True, slots=True)
class FeatureViewRecord:
    name: str
    version: int
    entities: tuple[str, ...]
    feature_names: tuple[str, ...]
    owner: str
    team: str
    sensitivity: str
    tier: str
    ttl: timedelta
    sla_freshness: timedelta
    online: bool
    source_contract: str | None = None
    deprecated: bool = False
    sunset_date: str | None = None

    @property
    def base_name(self) -> str:
        """Name without the version suffix, e.g. ``user_features``."""
        return re.sub(r"_v\d+$", "", self.name)

    def is_valid_name(self) -> bool:
        return bool(NAME_RE.match(self.name))


@dataclass(slots=True)
class RegistrySnapshot:
    """An immutable view of the registry at a point in time."""

    feature_views: list[FeatureViewRecord] = field(default_factory=list)

    def by_name(self, name: str) -> FeatureViewRecord | None:
        return next((fv for fv in self.feature_views if fv.name == name), None)

    def versions_of(self, base_name: str) -> list[FeatureViewRecord]:
        return sorted(
            (fv for fv in self.feature_views if fv.base_name == base_name),
            key=lambda fv: fv.version,
        )

    def sensitive_views(self) -> list[FeatureViewRecord]:
        return [fv for fv in self.feature_views if fv.sensitivity in {"pii", "financial"}]
