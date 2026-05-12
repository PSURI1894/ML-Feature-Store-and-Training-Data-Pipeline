"""MLflow integration: tie training runs to the exact features they used."""

from feature_platform.mlflow_integration.tracking import log_feature_metadata

__all__ = ["log_feature_metadata"]
