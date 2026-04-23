"""Transaction-level features. Some are streaming (velocity) and pushed online."""

from __future__ import annotations

from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32, Int64

from feature_repo.data_sources import transaction_features_source
from feature_repo.entities import transaction
from feature_repo.tags import standard_tags

transaction_features_v1 = FeatureView(
    name="transaction_features_v1",
    entities=[transaction],
    ttl=timedelta(days=30),
    schema=[
        Field(name="amount", dtype=Float32),
        Field(name="amount_zscore_user_30d", dtype=Float32),
        Field(name="seconds_since_prev_txn", dtype=Int64),
        Field(name="is_cross_border", dtype=Int64),
    ],
    online=True,
    source=transaction_features_source,
    owner="parthsuri009@gmail.com",
    tags=standard_tags(
        owner="parthsuri009@gmail.com",
        team="risk",
        sensitivity="financial",
        tier="near-real-time",
        sla_freshness="5m",
        source_contract="warehouse.transactions.v4",
    ),
)
