"""Feature resolver — assemble an online feature vector for a request.

Pulls stored features from the online store (batched), runs any on-demand
transforms over request context + retrieved values, and tags each feature with a
status (present / missing / stale). This is the core called by the gRPC server.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from feature_platform.common.logging import get_logger
from feature_platform.online.store import OnlineStore

log = get_logger(__name__)


class FeatureStatus(IntEnum):
    PRESENT = 1
    MISSING = 2
    STALE = 3


@dataclass(slots=True)
class ResolvedFeatures:
    values: dict[str, Any] = field(default_factory=dict)
    statuses: dict[str, FeatureStatus] = field(default_factory=dict)


class FeatureResolver:
    def __init__(self, online: OnlineStore, on_demand_executor: Any | None = None) -> None:
        self.online = online
        self.on_demand = on_demand_executor

    def resolve(
        self,
        feature_views: Sequence[str],
        entity_keys: Mapping[str, str],
        context: Mapping[str, Any] | None = None,
    ) -> ResolvedFeatures:
        resolved = ResolvedFeatures()
        for fv in feature_views:
            row = self.online.read(fv, entity_keys)
            if row is None:
                resolved.statuses[fv] = FeatureStatus.MISSING
                continue
            for name, value in row.items():
                resolved.values[name] = value
                resolved.statuses[name] = FeatureStatus.PRESENT

        if self.on_demand and context:
            merged = {**resolved.values, **context}
            for feature_name in context.get("_on_demand", []):  # type: ignore[union-attr]
                try:
                    out = self.on_demand.compute(feature_name, merged)
                    resolved.values.update(out)
                    for k in out:
                        resolved.statuses[k] = FeatureStatus.PRESENT
                except Exception as exc:  # noqa: BLE001 - serve-best-effort
                    log.warning("resolve.on_demand_failed", feature=feature_name, error=str(exc))
        return resolved

    def resolve_batch(
        self,
        feature_views: Sequence[str],
        entity_keys_list: Sequence[Mapping[str, str]],
        context: Mapping[str, Any] | None = None,
    ) -> list[ResolvedFeatures]:
        return [self.resolve(feature_views, ek, context) for ek in entity_keys_list]
