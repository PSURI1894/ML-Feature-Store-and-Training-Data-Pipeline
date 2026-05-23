"""Redis online store — the hot serving path.

Reads are pipelined for multi-entity requests so a single round trip serves a
whole feature service. Writes carry a TTL so stale features expire automatically.

Fix history: TTLs expiring just before a traffic peak caused cold reads. Added
``extend_ttl`` so the pre-warmer (``online/prewarm.py``) can refresh TTLs on
critical views ahead of known peaks without rewriting values.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import redis

from feature_platform.common.config import get_settings
from feature_platform.common.logging import get_logger
from feature_platform.common.metrics import ONLINE_READ_ERRORS, ONLINE_READ_LATENCY
from feature_platform.online.key_schema import online_key
from feature_platform.online.serialization import deserialize, serialize
from feature_platform.online.store import OnlineStore

log = get_logger(__name__)


class RedisOnlineStore(OnlineStore):
    def __init__(self, client: redis.Redis | None = None, default_ttl: int | None = None) -> None:
        settings = get_settings()
        self.client = client or redis.Redis(
            host=settings.redis_host, port=settings.redis_port, decode_responses=False
        )
        self.default_ttl = default_ttl or settings.redis_ttl_seconds

    def write(
        self,
        feature_view: str,
        rows: Sequence[tuple[Mapping[str, str], Mapping[str, Any]]],
        ttl_seconds: int | None = None,
    ) -> int:
        ttl = ttl_seconds or self.default_ttl
        pipe = self.client.pipeline(transaction=False)
        for entity_keys, values in rows:
            pipe.set(online_key(feature_view, entity_keys), serialize(dict(values)), ex=ttl)
        pipe.execute()
        return len(rows)

    def read(self, feature_view: str, entity_keys: Mapping[str, str]) -> dict[str, Any] | None:
        with ONLINE_READ_LATENCY.labels(feature_view, "redis").time():
            try:
                return deserialize(self.client.get(online_key(feature_view, entity_keys)))
            except redis.RedisError as exc:  # pragma: no cover - network
                ONLINE_READ_ERRORS.labels(feature_view, type(exc).__name__).inc()
                log.error("redis.read.error", fv=feature_view, error=str(exc))
                raise

    def read_many(
        self, feature_view: str, entity_keys_list: Sequence[Mapping[str, str]]
    ) -> list[dict[str, Any] | None]:
        if not entity_keys_list:
            return []
        keys = [online_key(feature_view, ek) for ek in entity_keys_list]
        with ONLINE_READ_LATENCY.labels(feature_view, "redis").time():
            blobs = self.client.mget(keys)
        return [deserialize(b) for b in blobs]

    def delete(self, feature_view: str, entity_keys: Mapping[str, str]) -> None:
        self.client.delete(online_key(feature_view, entity_keys))

    def extend_ttl(
        self, feature_view: str, entity_keys_list: Sequence[Mapping[str, str]], ttl_seconds: int
    ) -> int:
        """Refresh TTL on existing keys without rewriting values (pre-warming).

        Returns the number of keys whose TTL was extended (keys that had already
        expired are not resurrected — that's a materialize, not a pre-warm).
        """
        pipe = self.client.pipeline(transaction=False)
        keys = [online_key(feature_view, ek) for ek in entity_keys_list]
        for key in keys:
            pipe.expire(key, ttl_seconds)
        return sum(1 for ok in pipe.execute() if ok)
