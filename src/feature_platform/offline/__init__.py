"""Offline store adapters (training / batch).

The offline store is the **system of record** for feature values. It is
partitioned by ``event_date`` and clustered by ``entity_id`` so point-in-time
joins prune partitions instead of scanning history.
"""

from feature_platform.offline.store import OfflineStore, OfflineWriteResult

__all__ = ["OfflineStore", "OfflineWriteResult"]
