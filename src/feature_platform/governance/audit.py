"""Audit logging for sensitive access and erasures.

Audit events are structured and append-only. In production they are shipped to an
immutable store (e.g. BigQuery audit dataset / object lock); here they are emitted
as structured logs that a log pipeline can route.
"""

from __future__ import annotations

from feature_platform.common.logging import get_logger
from feature_platform.common.time_utils import utcnow
from feature_platform.common.types import Sensitivity

log = get_logger("audit")


def record_access(*, principal: str, feature_view: str, sensitivity: Sensitivity) -> None:
    log.info(
        "audit.access",
        principal=principal,
        feature_view=feature_view,
        sensitivity=sensitivity.value,
        ts=utcnow().isoformat(),
    )


def record_erasure(*, entity_id: str, views: list[str]) -> None:
    log.info(
        "audit.erasure",
        entity_id=entity_id,
        feature_views=views,
        ts=utcnow().isoformat(),
    )
