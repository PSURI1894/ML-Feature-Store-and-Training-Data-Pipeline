"""Feature catalog web portal (FastAPI + Jinja2).

    uvicorn services.catalog_ui.app:app --reload --port 8050

Lists every feature view with owner, team, sensitivity, freshness SLA, tier, and
the models (feature services) that consume it. Reads from the registry snapshot.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from feature_platform.common.logging import get_logger

log = get_logger(__name__)

_HERE = Path(__file__).parent
app = FastAPI(title="Feature Catalog", version="0.1.0")
app.mount("/static", StaticFiles(directory=_HERE / "static"), name="static")
templates = Jinja2Templates(directory=str(_HERE / "templates"))


def _snapshot():
    """Load the registry snapshot; empty on failure so the UI still renders."""
    try:
        from feature_platform.registry.sync import snapshot_from_repo

        return snapshot_from_repo()
    except Exception as exc:  # noqa: BLE001 - UI must not hard-fail
        log.warning("catalog.snapshot_failed", error=str(exc))
        from feature_platform.registry.models import RegistrySnapshot

        return RegistrySnapshot(feature_views=[])


def _consumers(feature_view: str) -> list[str]:
    """Which feature services (models) consume a view."""
    try:
        from feature_repo.feature_services import ALL_FEATURE_SERVICES

        return [
            fs.name
            for fs in ALL_FEATURE_SERVICES
            if any(getattr(v, "name", "") == feature_view for v in fs.features)
        ]
    except Exception:  # noqa: BLE001
        return []


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    snapshot = _snapshot()
    return templates.TemplateResponse(
        "index.html", {"request": request, "feature_views": snapshot.feature_views}
    )


@app.get("/feature-view/{name}", response_class=HTMLResponse)
def feature_view_detail(request: Request, name: str) -> HTMLResponse:
    snapshot = _snapshot()
    fv = snapshot.by_name(name)
    if fv is None:
        raise HTTPException(status_code=404, detail=f"unknown feature view {name}")
    return templates.TemplateResponse(
        "feature_view.html",
        {"request": request, "fv": fv, "consumers": _consumers(name)},
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
