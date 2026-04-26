"""Compact serialization for online feature structs.

msgpack keeps values small (latency + memory) and preserves numeric types better
than JSON. A 1-byte schema version prefix lets us evolve the encoding without a
flag-day migration.
"""

from __future__ import annotations

from typing import Any

import msgpack

SCHEMA_VERSION = 1
_PREFIX = bytes([SCHEMA_VERSION])


def serialize(features: dict[str, Any]) -> bytes:
    """Serialize a feature struct to ``version-prefix || msgpack`` bytes."""
    return _PREFIX + msgpack.packb(features, use_bin_type=True)


def deserialize(blob: bytes | None) -> dict[str, Any] | None:
    """Inverse of :func:`serialize`. Returns None for missing keys."""
    if not blob:
        return None
    version = blob[0]
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported online value schema version {version}")
    return msgpack.unpackb(blob[1:], raw=False)
