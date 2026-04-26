"""Online key construction.

Online key = ``{feature_view}:{entity_id}``. For composite entities the join-key
values are concatenated with a separator.

NOTE: this initial version joins composite keys with a bare ``|`` separator and
does not escape the separator inside individual key values. See
``fix/redis-composite-key-separator`` for the collision fix.
"""

from __future__ import annotations

from collections.abc import Mapping

COMPOSITE_SEPARATOR = "|"


def entity_id(entity_keys: Mapping[str, str]) -> str:
    """Concatenate composite join-key values in sorted key order."""
    return COMPOSITE_SEPARATOR.join(str(entity_keys[k]) for k in sorted(entity_keys))


def online_key(feature_view: str, entity_keys: Mapping[str, str]) -> str:
    return f"{feature_view}:{entity_id(entity_keys)}"
