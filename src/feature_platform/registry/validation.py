"""Feature-definition validation — the gate that keeps the registry trustworthy.

Runs in three places with the same rules:
  * pre-commit hook (``--pre-commit``)
  * CI on feature_repo PRs (``--strict``, ``--check-compat``, ``--plan``)
  * the ``fp validate`` CLI command

Rules enforced
--------------
1. Naming: ``<snake_case>_v<int>``.
2. Mandatory tags: owner, team, sensitivity, tier, sla_freshness.
3. Sensitivity / tier come from the allowed enums.
4. TTL must be positive and >= declared SLA freshness.
5. Backward-incompatible schema changes require a version bump (compat check).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable

from feature_platform.common.exceptions import ValidationError
from feature_platform.common.logging import get_logger
from feature_platform.registry.models import FeatureViewRecord, RegistrySnapshot

log = get_logger(__name__)

_ALLOWED_SENSITIVITY = {"public", "financial", "pii"}
_ALLOWED_TIER = {"real-time", "near-real-time", "batch"}


def validate_record(fv: FeatureViewRecord) -> list[ValidationError]:
    """Return all validation errors for a single feature view (empty == valid)."""
    errors: list[ValidationError] = []

    if not fv.is_valid_name():
        errors.append(
            ValidationError(
                f"{fv.name!r} must match '<snake_case>_v<int>'", rule="naming"
            )
        )
    if not fv.owner or "@" not in fv.owner:
        errors.append(ValidationError(f"{fv.name}: owner must be an email", rule="owner"))
    if not fv.team:
        errors.append(ValidationError(f"{fv.name}: missing team tag", rule="team"))
    if fv.sensitivity not in _ALLOWED_SENSITIVITY:
        errors.append(
            ValidationError(
                f"{fv.name}: sensitivity {fv.sensitivity!r} not in {_ALLOWED_SENSITIVITY}",
                rule="sensitivity",
            )
        )
    if fv.tier not in _ALLOWED_TIER:
        errors.append(
            ValidationError(f"{fv.name}: tier {fv.tier!r} invalid", rule="tier")
        )
    if fv.ttl.total_seconds() <= 0:
        errors.append(ValidationError(f"{fv.name}: ttl must be positive", rule="ttl"))
    if fv.sla_freshness > fv.ttl:
        errors.append(
            ValidationError(
                f"{fv.name}: sla_freshness ({fv.sla_freshness}) exceeds ttl ({fv.ttl})",
                rule="sla_vs_ttl",
            )
        )
    return errors


def validate_snapshot(snapshot: RegistrySnapshot) -> list[ValidationError]:
    errors: list[ValidationError] = []
    seen: set[str] = set()
    for fv in snapshot.feature_views:
        errors.extend(validate_record(fv))
        if fv.name in seen:
            errors.append(ValidationError(f"duplicate feature view {fv.name}", rule="unique"))
        seen.add(fv.name)
    return errors


def check_compatibility(
    old: RegistrySnapshot, new: RegistrySnapshot
) -> list[ValidationError]:
    """Breaking changes (removed/renamed features) require a new version.

    If a feature view at the same version drops or renames a feature column, that
    is backward-incompatible and must instead be published as ``_v(n+1)``.
    """
    errors: list[ValidationError] = []
    for new_fv in new.feature_views:
        old_fv = old.by_name(new_fv.name)
        if old_fv is None:
            continue
        removed = set(old_fv.feature_names) - set(new_fv.feature_names)
        if removed:
            errors.append(
                ValidationError(
                    f"{new_fv.name}: removed features {sorted(removed)} without a version bump; "
                    f"publish {new_fv.base_name}_v{new_fv.version + 1} instead",
                    rule="compat",
                )
            )
    return errors


def load_repo_snapshot() -> RegistrySnapshot:
    """Import the feature repo and snapshot its definitions.

    Imported lazily so validation can run without a configured Feast store.
    """
    from feature_platform.registry.sync import snapshot_from_repo

    return snapshot_from_repo()


def validate_repo() -> list[ValidationError]:
    return validate_snapshot(load_repo_snapshot())


def _render_plan(snapshot: RegistrySnapshot) -> str:
    lines = ["| feature view | entities | owner | sensitivity | tier | sla |", "|---|---|---|---|---|---|"]
    for fv in snapshot.feature_views:
        lines.append(
            f"| `{fv.name}` | {', '.join(fv.entities)} | {fv.owner} | "
            f"{fv.sensitivity} | {fv.tier} | {fv.sla_freshness} |"
        )
    return "\n".join(lines)


def _print_errors(errors: Iterable[ValidationError]) -> None:
    for err in errors:
        log.error("validation.error", rule=err.rule, message=str(err))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate feature definitions")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--pre-commit", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--check-compat", metavar="GIT_REF")
    args = parser.parse_args(argv)

    snapshot = load_repo_snapshot()

    if args.plan:
        print(_render_plan(snapshot))
        return 0

    errors = validate_snapshot(snapshot)
    if args.check_compat:
        # In CI the baseline snapshot is materialised from the target ref; here we
        # rely on the sync layer to provide it.
        from feature_platform.registry.sync import snapshot_from_ref

        errors.extend(check_compatibility(snapshot_from_ref(args.check_compat), snapshot))

    _print_errors(errors)
    if errors:
        return 1
    log.info("validation.ok", feature_views=len(snapshot.feature_views))
    return 0


if __name__ == "__main__":
    sys.exit(main())
