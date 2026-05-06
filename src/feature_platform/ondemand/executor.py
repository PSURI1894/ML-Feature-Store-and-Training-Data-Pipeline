"""Lightweight on-demand feature execution.

A decorator registers a pure function as an on-demand transform. The executor
runs it at request time over a merged dict of request context + retrieved online
features. Kept independent of Feast so it can run inside the gRPC serving path.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from feature_platform.common.exceptions import FeatureNotFoundError
from feature_platform.common.logging import get_logger

log = get_logger(__name__)

TransformFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class OnDemandFeature:
    name: str
    fn: TransformFn
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


_REGISTRY: dict[str, OnDemandFeature] = {}


def on_demand(*, name: str, inputs: tuple[str, ...], outputs: tuple[str, ...]) -> Callable[[TransformFn], TransformFn]:
    def decorator(fn: TransformFn) -> TransformFn:
        _REGISTRY[name] = OnDemandFeature(name=name, fn=fn, inputs=inputs, outputs=outputs)
        return fn

    return decorator


class OnDemandExecutor:
    def __init__(self, registry: dict[str, OnDemandFeature] | None = None) -> None:
        self.registry = registry or _REGISTRY

    def compute(self, name: str, context: dict[str, Any]) -> dict[str, Any]:
        odf = self.registry.get(name)
        if odf is None:
            raise FeatureNotFoundError(f"on-demand feature {name!r} not registered")
        missing = [c for c in odf.inputs if c not in context]
        if missing:
            raise FeatureNotFoundError(f"{name}: missing inputs {missing}")
        result = odf.fn(context)
        return {k: result[k] for k in odf.outputs if k in result}


@on_demand(
    name="amount_to_avg_ratio",
    inputs=("amount", "txn_amount_avg_30d"),
    outputs=("amount_to_avg_ratio",),
)
def _amount_to_avg_ratio(ctx: dict[str, Any]) -> dict[str, Any]:
    avg = ctx.get("txn_amount_avg_30d") or 0.0
    return {"amount_to_avg_ratio": (ctx["amount"] / avg) if avg else 0.0}
