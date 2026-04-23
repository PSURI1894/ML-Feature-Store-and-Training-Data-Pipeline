"""Feature services — named bundles of features that a model consumes.

A model pins a feature service (and through it, feature-view versions). This is
the contract surface between the platform and a model.
"""

from __future__ import annotations

from feast import FeatureService

from feature_repo.feature_views.merchant_features import merchant_features_v1
from feature_repo.feature_views.transaction_features import transaction_features_v1
from feature_repo.feature_views.user_features import user_features_v2
from feature_repo.feature_views.user_merchant_features import user_merchant_features_v1

# Real-time fraud scoring model.
fraud_scoring_v3 = FeatureService(
    name="fraud_scoring_v3",
    features=[
        user_features_v2,
        merchant_features_v1,
        transaction_features_v1,
        user_merchant_features_v1,
    ],
    owner="parthsuri009@gmail.com",
    tags={"model": "fraud_scoring", "stage": "production"},
)

# Lightweight underwriting model — user + merchant only.
underwriting_v1 = FeatureService(
    name="underwriting_v1",
    features=[user_features_v2, merchant_features_v1],
    owner="parthsuri009@gmail.com",
    tags={"model": "underwriting", "stage": "staging"},
)

ALL_FEATURE_SERVICES = [fraud_scoring_v3, underwriting_v1]
