"""On-demand transform service (FastAPI).

    uvicorn services.ondemand_api.main:app --reload

Computes on-demand features at request time. Co-located with model servers to
keep added latency negligible.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app

from feature_platform.common.exceptions import FeatureNotFoundError
from feature_platform.common.logging import get_logger
from feature_platform.ondemand.executor import OnDemandExecutor
from services.ondemand_api.schemas import OnDemandRequest, OnDemandResponse

log = get_logger(__name__)
app = FastAPI(title="On-Demand Feature Service", version="0.1.0")
app.mount("/metrics", make_asgi_app())

_executor = OnDemandExecutor()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/compute", response_model=OnDemandResponse)
def compute(req: OnDemandRequest) -> OnDemandResponse:
    start = time.perf_counter()
    try:
        values = _executor.compute(req.feature, req.context)
    except FeatureNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    elapsed = (time.perf_counter() - start) * 1000
    return OnDemandResponse(feature=req.feature, values=values, compute_ms=round(elapsed, 3))
