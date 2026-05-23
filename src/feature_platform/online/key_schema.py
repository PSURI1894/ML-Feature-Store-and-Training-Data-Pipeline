"""Online key construction.

Online key = ``{feature_view}:{entity_id}``. For composite entities the join-key
values are concatenated with a separator.

Fix history
-----------
The original implementation joined composite keys with a bare ``|`` and did not
escape the separator inside values, so ``{"a": "x|y", "b": "z"}`` and
``{"a": "x", "b": "y|z"}`` produced the *same* entity id — a silent collision
that mixed two entities' features. We now escape the backslash and pipe
characters within each value before joining, making the encoding injective.
"""

from __future__ import annotations

from collections.abc import Mapping

COMPOSITE_SEPARATOR = "|"
_ESCAPE = "\\"


def _escape(value: str) -> str:
    """Escape the separator (and the escape char) so the join is reversible."""
    return value.replace(_ESCAPE, _ESCAPE + _ESCAPE).replace(
        COMPOSITE_SEPARATOR, _ESCAPE + COMPOSITE_SEPARATOR
    )


def entity_id(entity_keys: Mapping[str, str]) -> str:
    """Concatenate composite join-key values in sorted key order.

    Each value is escaped first so the separator inside a value can never be
    confused with the delimiter between values.
    """
    return COMPOSITE_SEPARATOR.join(_escape(str(entity_keys[k])) for k in sorted(entity_keys))


def online_key(feature_view: str, entity_keys: Mapping[str, str]) -> str:
    return f"{feature_view}:{entity_id(entity_keys)}"
