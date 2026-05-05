"""Thin gRPC client used by model servers and for smoke tests."""

from __future__ import annotations

from typing import Any


class FeatureServiceClient:  # pragma: no cover - requires generated stubs
    def __init__(self, target: str = "localhost:50051") -> None:
        import grpc

        from services.serving_grpc import feature_service_pb2_grpc

        self._channel = grpc.insecure_channel(
            target, options=[("grpc.keepalive_time_ms", 30_000)]
        )
        self._stub = feature_service_pb2_grpc.FeatureServiceStub(self._channel)

    def get_online_features(
        self, feature_service: str, entities: list[dict[str, str]], context: dict[str, float] | None = None
    ) -> list[dict[str, Any]]:
        from services.serving_grpc import feature_service_pb2 as pb

        request = pb.GetOnlineFeaturesRequest(
            feature_service=feature_service,
            entities=[pb.EntityRow(join_keys=e) for e in entities],
            context=context or {},
        )
        resp = self._stub.GetOnlineFeatures(request, timeout=0.05)  # 50ms hard deadline
        return [
            {**dict(v.numeric), **dict(v.categorical), "_statuses": dict(v.statuses)}
            for v in resp.results
        ]

    def close(self) -> None:
        self._channel.close()
