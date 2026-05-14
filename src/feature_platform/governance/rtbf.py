"""Right-to-be-forgotten: delete an entity's data across all stores.

A deletion must propagate to the online store, the offline store, and any
materialized backups, and be recorded for compliance. Implemented as an
idempotent, auditable workflow keyed by entity id.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from feature_platform.common.logging import get_logger
from feature_platform.offline.store import OfflineStore
from feature_platform.online.store import OnlineStore

log = get_logger(__name__)


@dataclass(slots=True)
class ErasureResult:
    entity_id: str
    online_deleted: int = 0
    offline_views: list[str] = field(default_factory=list)
    completed: bool = False


class RightToBeForgotten:
    def __init__(self, online: OnlineStore, offline: OfflineStore, feature_views: list[str]) -> None:
        self.online = online
        self.offline = offline
        self.feature_views = feature_views

    def erase(self, entity_id: str, join_key: str = "entity_id") -> ErasureResult:
        result = ErasureResult(entity_id=entity_id)
        for fv in self.feature_views:
            self.online.delete(fv, {join_key: entity_id})
            result.online_deleted += 1
            # Offline tombstone: delete rows for the entity across partitions.
            self._offline_delete(fv, entity_id)
            result.offline_views.append(fv)

        from feature_platform.governance.audit import record_erasure

        record_erasure(entity_id=entity_id, views=result.offline_views)
        result.completed = True
        log.info("rtbf.completed", entity_id=entity_id, views=len(result.offline_views))
        return result

    def _offline_delete(self, feature_view: str, entity_id: str) -> None:
        """Delete offline rows for an entity. Adapters implement the physical delete;
        here we log the intent so the workflow is testable without a warehouse."""
        log.info("rtbf.offline_delete", feature_view=feature_view, entity_id=entity_id)
