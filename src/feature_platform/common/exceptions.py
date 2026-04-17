"""Typed exception hierarchy for the feature platform.

A single base (``FeaturePlatformError``) makes it easy for services to catch
platform-originated failures and map them to gRPC/HTTP status codes without
swallowing unrelated bugs.
"""

from __future__ import annotations


class FeaturePlatformError(Exception):
    """Base class for all platform errors."""


class RegistryError(FeaturePlatformError):
    """Raised when a feature definition is invalid or the registry is inconsistent."""


class ValidationError(RegistryError):
    """A feature view failed a governance/schema validation rule."""

    def __init__(self, message: str, *, rule: str | None = None) -> None:
        super().__init__(message)
        self.rule = rule


class FeatureNotFoundError(FeaturePlatformError):
    """Requested feature view / feature does not exist in the registry."""


class OnlineStoreError(FeaturePlatformError):
    """Online store read/write failure."""


class OfflineStoreError(FeaturePlatformError):
    """Offline store query/write failure."""


class PointInTimeError(FeaturePlatformError):
    """Point-in-time join invariant was violated (e.g. future leakage detected)."""


class FreshnessSLAViolation(FeaturePlatformError):
    """A feature view is staler than its declared SLA."""


class AccessDeniedError(FeaturePlatformError):
    """RBAC denied access to a sensitive feature view."""
