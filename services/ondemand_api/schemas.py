"""Request/response models for the on-demand API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OnDemandRequest(BaseModel):
    feature: str = Field(..., description="Registered on-demand feature name")
    context: dict[str, Any] = Field(
        ..., description="Request context + any retrieved online features"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feature": "amount_to_avg_ratio",
                    "context": {"amount": 250.0, "txn_amount_avg_30d": 50.0},
                }
            ]
        }
    }


class OnDemandResponse(BaseModel):
    feature: str
    values: dict[str, Any]
    compute_ms: float
