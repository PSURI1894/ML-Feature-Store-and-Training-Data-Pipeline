"""Role-based access control for reading sensitive feature views."""

from __future__ import annotations

from dataclasses import dataclass

from feature_platform.common.exceptions import AccessDeniedError
from feature_platform.common.types import Sensitivity
from feature_platform.governance.sensitivity import READ_ROLES, requires_audit


@dataclass(frozen=True, slots=True)
class AccessDecision:
    allowed: bool
    reason: str
    must_audit: bool


def can_read(role: str, sensitivity: Sensitivity) -> AccessDecision:
    """Decide whether ``role`` may read a view of the given sensitivity."""
    allowed = role in READ_ROLES.get(sensitivity, frozenset())
    reason = "ok" if allowed else f"role {role!r} cannot read {sensitivity.value} features"
    return AccessDecision(allowed=allowed, reason=reason, must_audit=requires_audit(sensitivity))


def enforce_read(role: str, sensitivity: Sensitivity, *, principal: str, feature_view: str) -> None:
    """Raise AccessDeniedError if not permitted; emit audit on sensitive reads."""
    decision = can_read(role, sensitivity)
    if not decision.allowed:
        raise AccessDeniedError(decision.reason)
    if decision.must_audit:
        from feature_platform.governance.audit import record_access

        record_access(principal=principal, feature_view=feature_view, sensitivity=sensitivity)
