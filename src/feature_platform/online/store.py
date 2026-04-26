"""Online store interface."""

from __future__ import annotations

import abc
from collections.abc import Mapping, Sequence
from typing import Any


class OnlineStore(abc.ABC):
    @abc.abstractmethod
    def write(
        self,
        feature_view: str,
        rows: Sequence[tuple[Mapping[str, str], Mapping[str, Any]]],
        ttl_seconds: int | None = None,
    ) -> int:
        """Write feature rows. Each row is (entity_keys, feature_values). Returns
        the number of keys written."""

    @abc.abstractmethod
    def read(
        self, feature_view: str, entity_keys: Mapping[str, str]
    ) -> dict[str, Any] | None:
        """Read one entity's features for a view (None if absent/expired)."""

    @abc.abstractmethod
    def read_many(
        self, feature_view: str, entity_keys_list: Sequence[Mapping[str, str]]
    ) -> list[dict[str, Any] | None]:
        """Batched multi-entity read (pipelined / BatchGetItem)."""

    @abc.abstractmethod
    def delete(self, feature_view: str, entity_keys: Mapping[str, str]) -> None:
        """Delete one entity's features (used by right-to-be-forgotten)."""
