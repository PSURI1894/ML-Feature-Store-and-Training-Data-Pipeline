"""Periodic offline snapshots of streaming features.

Online streaming values are ephemeral (TTL). To keep training reproducible, we
periodically append the current streaming feature values to the offline store
with their event_ts, so a point-in-time join can recover them later.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from feature_platform.common.logging import get_logger
from feature_platform.common.time_utils import utcnow
from feature_platform.offline.store import OfflineStore

log = get_logger(__name__)


class OfflineSnapshotter:
    def __init__(self, offline: OfflineStore, feature_view: str) -> None:
        self.offline = offline
        self.feature_view = feature_view
        self._buffer: list[dict] = []

    def stage(self, entity_id: str, features: dict, event_ts: datetime | None = None) -> None:
        ts = event_ts or utcnow()
        self._buffer.append({"entity_id": entity_id, "event_ts": ts, "created_ts": utcnow(), **features})

    def flush(self) -> int:
        if not self._buffer:
            return 0
        df = pd.DataFrame(self._buffer)
        result = self.offline.write(self.feature_view, df)
        log.info("stream.snapshot.flush", feature_view=self.feature_view, rows=result.rows_written)
        self._buffer.clear()
        return result.rows_written
