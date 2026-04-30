"""Sink that dual-writes streaming features to the online store.

Streaming features are written online immediately (for freshness) and buffered
for periodic offline snapshots (for training consistency) — see offline_snapshot.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from feature_platform.common.logging import get_logger
from feature_platform.online.store import OnlineStore

log = get_logger(__name__)


class OnlineFeatureSink:
    def __init__(self, online: OnlineStore, feature_view: str, ttl_seconds: int = 3600) -> None:
        self.online = online
        self.feature_view = feature_view
        self.ttl_seconds = ttl_seconds
        self._written = 0

    def emit(self, entity_keys: Mapping[str, str], features: Mapping[str, Any]) -> None:
        self.online.write(
            self.feature_view, [(dict(entity_keys), dict(features))], ttl_seconds=self.ttl_seconds
        )
        self._written += 1
        if self._written % 1000 == 0:
            log.info("stream.sink.progress", feature_view=self.feature_view, written=self._written)

    @property
    def written(self) -> int:
        return self._written
