"""Feature data quality via Great Expectations + lightweight inline checks."""

from feature_platform.dq.validator import DQResult, validate_dataframe

__all__ = ["DQResult", "validate_dataframe"]
