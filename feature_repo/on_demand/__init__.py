"""On-demand feature views — computed at request time from context + retrieved features."""

from feature_repo.on_demand.transaction_ratios import transaction_ratios

ALL_ON_DEMAND_VIEWS = [transaction_ratios]
