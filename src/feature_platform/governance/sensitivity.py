"""Sensitivity classification helpers.

Sensitivity drives both access control (who can read) and audit (what must be
logged). It is declared on every feature view via the ``sensitivity`` tag.
"""

from __future__ import annotations

from feature_platform.common.types import Sensitivity

# Roles permitted to read each sensitivity level (least-privilege).
READ_ROLES: dict[Sensitivity, frozenset[str]] = {
    Sensitivity.PUBLIC: frozenset({"viewer", "analyst", "ml-engineer", "admin"}),
    Sensitivity.FINANCIAL: frozenset({"analyst", "ml-engineer", "admin"}),
    Sensitivity.PII: frozenset({"ml-engineer", "admin"}),
}

# Sensitivities that require an audit log entry on every read.
AUDITED = frozenset({Sensitivity.FINANCIAL, Sensitivity.PII})


def parse(value: str) -> Sensitivity:
    return Sensitivity(value)


def requires_audit(sensitivity: Sensitivity) -> bool:
    return sensitivity in AUDITED
