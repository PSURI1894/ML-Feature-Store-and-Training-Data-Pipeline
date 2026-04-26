"""Online store adapters (serving).

Low-latency KV reads keyed by ``{feature_view}:{entity_id}`` with a TTL. Redis is
the hot path (p99 < 10ms); DynamoDB is the cheaper cold path with a longer TTL.
"""

from feature_platform.online.store import OnlineStore

__all__ = ["OnlineStore"]
