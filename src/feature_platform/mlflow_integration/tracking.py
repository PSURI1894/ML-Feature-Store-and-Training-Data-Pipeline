"""Record the feature provenance of every training run.

Logging ``feature_view_versions`` (and, where available, an offline snapshot id)
as MLflow params/tags makes a model's features auditable and its training set
reproducible months later.
"""

from __future__ import annotations

from typing import Any

from feature_platform.common.logging import get_logger

log = get_logger(__name__)

FEATURE_VERSIONS_TAG = "feature_view_versions"
FEATURE_SERVICE_TAG = "feature_service"


def log_feature_metadata(
    feature_view_versions: dict[str, int],
    *,
    feature_service: str | None = None,
    offline_snapshot_id: str | None = None,
    extra_tags: dict[str, Any] | None = None,
) -> None:
    """Attach feature provenance to the active MLflow run.

    No-ops with a warning if MLflow isn't installed/active so training code stays
    runnable in environments without a tracking server.
    """
    try:
        import mlflow
    except ImportError:  # pragma: no cover
        log.warning("mlflow.not_installed")
        return

    for fv, version in feature_view_versions.items():
        mlflow.log_param(f"fv.{fv}", version)
    mlflow.set_tag(FEATURE_VERSIONS_TAG, ",".join(f"{k}:v{v}" for k, v in feature_view_versions.items()))
    if feature_service:
        mlflow.set_tag(FEATURE_SERVICE_TAG, feature_service)
    if offline_snapshot_id:
        mlflow.set_tag("offline_snapshot_id", offline_snapshot_id)
    for k, v in (extra_tags or {}).items():
        mlflow.set_tag(k, v)
    log.info("mlflow.feature_metadata.logged", feature_views=list(feature_view_versions))
