"""Entities — the things features are attached to.

Join keys are the columns used to look features up. Composite features (e.g.
user x merchant) join on multiple keys; the online store concatenates them.
"""

from __future__ import annotations

from feast import Entity, ValueType

user = Entity(
    name="user",
    join_keys=["user_id"],
    value_type=ValueType.STRING,
    description="An end user / account holder.",
    tags={"team": "growth", "domain": "identity"},
)

merchant = Entity(
    name="merchant",
    join_keys=["merchant_id"],
    value_type=ValueType.STRING,
    description="A merchant accepting payments.",
    tags={"team": "risk", "domain": "merchant"},
)

transaction = Entity(
    name="transaction",
    join_keys=["transaction_id"],
    value_type=ValueType.STRING,
    description="A single payment transaction.",
    tags={"team": "risk", "domain": "payments"},
)

ALL_ENTITIES = [user, merchant, transaction]
