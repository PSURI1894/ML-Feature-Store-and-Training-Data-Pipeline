"""Governance: sensitivity classification, RBAC, right-to-be-forgotten, audit."""

from feature_platform.governance.rbac import AccessDecision, can_read

__all__ = ["AccessDecision", "can_read"]
