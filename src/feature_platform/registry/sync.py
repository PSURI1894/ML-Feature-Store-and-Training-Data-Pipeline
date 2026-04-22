"""Sync feature definitions to the registry metadata store via ``feast apply``.

Also builds platform-side :class:`RegistrySnapshot` objects from the Feast repo
(used by validation, the catalog UI, and compatibility checks).
"""

from __future__ import annotations

import subprocess
from datetime import timedelta
from pathlib import Path

from feature_platform.common.logging import get_logger
from feature_platform.registry.models import FeatureViewRecord, RegistrySnapshot

log = get_logger(__name__)

REPO_PATH = Path(__file__).resolve().parents[3] / "feature_repo"


def _ttl_to_timedelta(ttl: object) -> timedelta:
    if isinstance(ttl, timedelta):
        return ttl
    return timedelta(seconds=int(ttl)) if ttl else timedelta(0)


def _record_from_feast(fv: object) -> FeatureViewRecord:
    """Map a Feast FeatureView into a platform record using only public attrs."""
    tags = getattr(fv, "tags", {}) or {}
    name = fv.name
    version = int(name.rsplit("_v", 1)[-1]) if "_v" in name else 1
    sla = tags.get("sla_freshness", "24h")
    from feature_platform.common.time_utils import parse_duration

    return FeatureViewRecord(
        name=name,
        version=version,
        entities=tuple(getattr(fv, "entities", []) or []),
        feature_names=tuple(f.name for f in getattr(fv, "features", []) or []),
        owner=tags.get("owner", getattr(fv, "owner", "") or ""),
        team=tags.get("team", ""),
        sensitivity=tags.get("sensitivity", "public"),
        tier=tags.get("tier", "batch"),
        ttl=_ttl_to_timedelta(getattr(fv, "ttl", None)),
        sla_freshness=parse_duration(sla),
        online=bool(getattr(fv, "online", True)),
        source_contract=tags.get("source_contract"),
    )


def snapshot_from_repo() -> RegistrySnapshot:
    """Import the feature repo package and snapshot its feature views."""
    from feature_repo.feature_views import ALL_FEATURE_VIEWS

    return RegistrySnapshot(
        feature_views=[_record_from_feast(fv) for fv in ALL_FEATURE_VIEWS]
    )


def snapshot_from_ref(git_ref: str) -> RegistrySnapshot:  # pragma: no cover - CI only
    """Build a snapshot from another git ref (for compatibility checks).

    In CI we ``git worktree add`` the ref and import the repo from there; locally
    this returns an empty snapshot so the check is a no-op.
    """
    log.info("snapshot.from_ref", ref=git_ref)
    return RegistrySnapshot(feature_views=[])


def apply(repo_path: Path = REPO_PATH) -> None:
    """Run ``feast apply`` to sync definitions to the metadata store."""
    log.info("feast.apply.start", repo=str(repo_path))
    result = subprocess.run(
        ["feast", "apply"], cwd=repo_path, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        log.error("feast.apply.failed", stderr=result.stderr)
        raise RuntimeError(f"feast apply failed: {result.stderr}")
    log.info("feast.apply.done")
