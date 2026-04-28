"""User-level batch features.

Versioned: ``user_features_v2`` is the current view. v1 is deprecated (see the
deprecation note); models still pinned to v1 read from the frozen definition.
"""

from __future__ import annotations

from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32, Int64, String

from feature_repo.data_sources import user_features_source
from feature_repo.entities import user
from feature_repo.tags import standard_tags

user_features_v2 = FeatureView(
    name="user_features_v2",
    entities=[user],
    ttl=timedelta(days=90),
    schema=[
        Field(name="account_age_days", dtype=Int64),
        Field(name="txn_count_30d", dtype=Int64),
        Field(name="txn_amount_sum_30d", dtype=Float32),
        Field(name="txn_amount_avg_30d", dtype=Float32),
        Field(name="distinct_merchants_30d", dtype=Int64),
        Field(name="chargeback_rate_90d", dtype=Float32),
        Field(name="home_country", dtype=String),
    ],
    online=True,
    source=user_features_source,
    owner="parthsuri009@gmail.com",
    description="Rolling user activity + risk aggregates.",
    tags=standard_tags(
        owner="parthsuri009@gmail.com",
        team="growth",
        sensitivity="financial",
        tier="batch",
        sla_freshness="24h",
        source_contract="warehouse.users.v3",
    ),
)
