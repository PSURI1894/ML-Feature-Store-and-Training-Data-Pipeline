"""Merchant-level batch features used by risk/fraud models."""

from __future__ import annotations

from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32, Int64

from feature_repo.data_sources import merchant_features_source
from feature_repo.entities import merchant
from feature_repo.tags import standard_tags

merchant_features_v1 = FeatureView(
    name="merchant_features_v1",
    entities=[merchant],
    ttl=timedelta(days=180),
    schema=[
        Field(name="merchant_age_days", dtype=Int64),
        Field(name="avg_ticket_size", dtype=Float32),
        Field(name="refund_rate_30d", dtype=Float32),
        Field(name="dispute_rate_90d", dtype=Float32),
        Field(name="mcc_risk_score", dtype=Float32),
    ],
    online=True,
    source=merchant_features_source,
    owner="parthsuri009@gmail.com",
    tags=standard_tags(
        owner="parthsuri009@gmail.com",
        team="risk",
        sensitivity="financial",
        tier="batch",
        sla_freshness="24h",
        source_contract="warehouse.merchants.v2",
    ),
)
