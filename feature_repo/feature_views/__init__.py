"""All feature views, re-exported for ``feast apply`` discovery."""

from feature_repo.feature_views.merchant_features import merchant_features_v1
from feature_repo.feature_views.transaction_features import transaction_features_v1
from feature_repo.feature_views.user_features import user_features_v2
from feature_repo.feature_views.user_merchant_features import user_merchant_features_v1

ALL_FEATURE_VIEWS = [
    user_features_v2,
    merchant_features_v1,
    transaction_features_v1,
    user_merchant_features_v1,
]
