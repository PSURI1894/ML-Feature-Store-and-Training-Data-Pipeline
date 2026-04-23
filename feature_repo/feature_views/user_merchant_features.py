"""Composite-key feature view: user x merchant interaction history.

Demonstrates multi-entity join keys. The online store concatenates the keys with
a separator (see ``feature_platform.online.key_schema``); collisions are prevented
by escaping the separator inside individual keys.
"""

from __future__ import annotations

from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32, Int64

from feature_repo.data_sources import user_merchant_source
from feature_repo.entities import merchant, user
from feature_repo.tags import standard_tags

user_merchant_features_v1 = FeatureView(
    name="user_merchant_features_v1",
    entities=[user, merchant],  # composite key: (user_id, merchant_id)
    ttl=timedelta(days=90),
    schema=[
        Field(name="pair_txn_count_90d", dtype=Int64),
        Field(name="pair_amount_sum_90d", dtype=Float32),
        Field(name="pair_last_amount", dtype=Float32),
        Field(name="pair_is_first_txn", dtype=Int64),
    ],
    online=True,
    source=user_merchant_source,
    owner="parthsuri009@gmail.com",
    description="Interaction features between a specific user and merchant.",
    tags=standard_tags(
        owner="parthsuri009@gmail.com",
        team="risk",
        sensitivity="financial",
        tier="batch",
        sla_freshness="24h",
        source_contract="warehouse.transactions.v4",
    ),
)
