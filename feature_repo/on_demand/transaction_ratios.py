"""On-demand feature view: ratios that need request-time context.

These can't be precomputed because they depend on the *current* transaction
amount passed in the inference request, combined with stored user aggregates.
The same pure transforms back this view and the batch pipeline.
"""

from __future__ import annotations

import pandas as pd
from feast import Field
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float64

from feature_repo.feature_views.transaction_features import transaction_features_v1
from feature_repo.feature_views.user_features import user_features_v2


@on_demand_feature_view(
    sources=[user_features_v2, transaction_features_v1],
    schema=[
        Field(name="amount_to_avg_ratio", dtype=Float64),
        Field(name="amount_to_sum_ratio", dtype=Float64),
    ],
)
def transaction_ratios(inputs: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    avg = inputs["txn_amount_avg_30d"].replace(0, pd.NA)
    total = inputs["txn_amount_sum_30d"].replace(0, pd.NA)
    out["amount_to_avg_ratio"] = (inputs["amount"] / avg).fillna(0.0)
    out["amount_to_sum_ratio"] = (inputs["amount"] / total).fillna(0.0)
    return out
