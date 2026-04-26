"""DynamoDB online store — the cheaper cold path with a longer TTL.

Cold/low-traffic feature views live here to keep Redis memory for hot features.
DynamoDB's native TTL attribute expires items server-side.
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from typing import Any

from feature_platform.common.config import get_settings
from feature_platform.online.key_schema import online_key
from feature_platform.online.serialization import deserialize, serialize
from feature_platform.online.store import OnlineStore


class DynamoDBOnlineStore(OnlineStore):
    def __init__(self, table_name: str | None = None, default_ttl: int = 7 * 86_400) -> None:
        settings = get_settings()
        self.table_name = table_name or "feature_store_online"
        self.default_ttl = default_ttl
        self.region = getattr(settings, "dynamodb_region", "us-east-1")
        self._table = None

    @property
    def table(self):  # pragma: no cover - requires AWS
        if self._table is None:
            import boto3

            self._table = boto3.resource("dynamodb", region_name=self.region).Table(
                self.table_name
            )
        return self._table

    def write(  # pragma: no cover - requires AWS
        self,
        feature_view: str,
        rows: Sequence[tuple[Mapping[str, str], Mapping[str, Any]]],
        ttl_seconds: int | None = None,
    ) -> int:
        ttl = ttl_seconds or self.default_ttl
        expires = int(time.time()) + ttl
        with self.table.batch_writer() as batch:
            for entity_keys, values in rows:
                batch.put_item(
                    Item={
                        "pk": online_key(feature_view, entity_keys),
                        "value": serialize(dict(values)),
                        "expires_at": expires,
                    }
                )
        return len(rows)

    def read(self, feature_view: str, entity_keys: Mapping[str, str]) -> dict[str, Any] | None:  # pragma: no cover
        resp = self.table.get_item(Key={"pk": online_key(feature_view, entity_keys)})
        item = resp.get("Item")
        return deserialize(item["value"].value) if item else None

    def read_many(  # pragma: no cover
        self, feature_view: str, entity_keys_list: Sequence[Mapping[str, str]]
    ) -> list[dict[str, Any] | None]:
        return [self.read(feature_view, ek) for ek in entity_keys_list]

    def delete(self, feature_view: str, entity_keys: Mapping[str, str]) -> None:  # pragma: no cover
        self.table.delete_item(Key={"pk": online_key(feature_view, entity_keys)})
