"""Custom Airflow operators wrapping platform actions.

Thin wrappers so DAGs read declaratively and the same logic is reachable from the
CLI and tests.
"""

from __future__ import annotations

from typing import Any

from airflow.models import BaseOperator


class FeastApplyOperator(BaseOperator):
    """Sync feature definitions to the registry (``feast apply``)."""

    def execute(self, context: Any) -> None:  # noqa: D401
        from feature_platform.registry.sync import apply

        apply()


class MaterializeOperator(BaseOperator):
    """Materialize a window offline -> online."""

    def __init__(self, *, lookback_days: int = 1, feature_views: list[str] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.lookback_days = lookback_days
        self.feature_views = feature_views

    def execute(self, context: Any) -> int:
        from datetime import timedelta

        from feature_platform.batch.runner import materialize_recent
        from feature_platform.common.time_utils import utcnow

        end = utcnow()
        return materialize_recent(
            start=end - timedelta(days=self.lookback_days),
            end=end,
            feature_views=self.feature_views,
        )
