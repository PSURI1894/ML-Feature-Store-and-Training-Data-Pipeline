"""Register models with their feature contract.

A model version is only promotable to Production if its run recorded the
feature-view versions it was trained on — this is the audit gate that links the
model registry to the feature registry.
"""

from __future__ import annotations

from feature_platform.common.logging import get_logger
from feature_platform.mlflow_integration.tracking import FEATURE_VERSIONS_TAG

log = get_logger(__name__)


def register_model(model_uri: str, name: str, *, stage: str = "Staging") -> str | None:
    try:
        import mlflow
    except ImportError:  # pragma: no cover
        log.warning("mlflow.not_installed")
        return None

    result = mlflow.register_model(model_uri, name)
    log.info("mlflow.model.registered", name=name, version=result.version)
    return result.version


def assert_feature_provenance(run_id: str) -> None:
    """Raise if a run lacks feature-version provenance (blocks promotion)."""
    import mlflow

    run = mlflow.get_run(run_id)
    if FEATURE_VERSIONS_TAG not in run.data.tags:
        raise ValueError(
            f"run {run_id} has no {FEATURE_VERSIONS_TAG} tag; "
            "cannot promote a model without feature provenance"
        )
