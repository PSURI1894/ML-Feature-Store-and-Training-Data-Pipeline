"""gRPC feature serving server.

    python -m services.serving_grpc.server

Generate stubs first with ``make proto``. The handler is intentionally thin: all
logic lives in ``FeatureResolver`` so it is unit-testable without gRPC.
"""

from __future__ import annotations

import time
from concurrent import futures

from feature_platform.common.logging import get_logger
from feature_platform.online.redis_store import RedisOnlineStore
from feature_platform.ondemand.executor import OnDemandExecutor
from feature_platform.serving.resolver import FeatureResolver

log = get_logger(__name__)

# Map feature service name -> feature views. In production this is read from the
# registry; hard-coded fallback keeps the server runnable standalone.
FEATURE_SERVICES = {
    "fraud_scoring_v3": [
        "user_features_v2",
        "merchant_features_v1",
        "transaction_features_v1",
        "user_merchant_features_v1",
    ],
    "underwriting_v1": ["user_features_v2", "merchant_features_v1"],
}


def make_resolver() -> FeatureResolver:
    return FeatureResolver(RedisOnlineStore(), OnDemandExecutor())


def serve(port: int = 50051, max_workers: int = 16) -> None:  # pragma: no cover - needs stubs
    import grpc

    from services.serving_grpc import feature_service_pb2_grpc  # generated

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[("grpc.max_concurrent_streams", 1000)],
    )
    feature_service_pb2_grpc.add_FeatureServiceServicer_to_server(
        FeatureServicer(make_resolver()), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    log.info("grpc.serving.started", port=port, workers=max_workers)
    server.wait_for_termination()


class FeatureServicer:  # pragma: no cover - requires generated stubs
    """Implements the generated FeatureServiceServicer interface."""

    def __init__(self, resolver: FeatureResolver) -> None:
        self.resolver = resolver

    def GetOnlineFeatures(self, request, context):  # noqa: N802 - gRPC naming
        from services.serving_grpc import feature_service_pb2 as pb

        views = FEATURE_SERVICES.get(request.feature_service, [])
        entities = [dict(e.join_keys) for e in request.entities]
        resolved = self.resolver.resolve_batch(views, entities, dict(request.context))

        results = []
        for r in resolved:
            fv = pb.FeatureVector()
            for k, v in r.values.items():
                if isinstance(v, (int, float)):
                    fv.numeric[k] = float(v)
                else:
                    fv.categorical[k] = str(v)
            for k, s in r.statuses.items():
                fv.statuses[k] = int(s)
            results.append(fv)
        return pb.GetOnlineFeaturesResponse(
            results=results, served_at_unix_ms=int(time.time() * 1000)
        )

    def HealthCheck(self, request, context):  # noqa: N802
        from services.serving_grpc import feature_service_pb2 as pb

        return pb.HealthCheckResponse(ok=True, version="0.1.0")


if __name__ == "__main__":
    serve()
