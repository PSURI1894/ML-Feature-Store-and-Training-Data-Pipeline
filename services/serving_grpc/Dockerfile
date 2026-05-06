# gRPC feature serving image. Stubs are generated at build time.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt grpcio-tools

COPY src ./src
COPY services ./services
RUN python -m grpc_tools.protoc -Iservices/serving_grpc/protos \
        --python_out=services/serving_grpc \
        --grpc_python_out=services/serving_grpc \
        services/serving_grpc/protos/feature_service.proto \
    && pip install --no-cache-dir -e .

EXPOSE 50051
CMD ["python", "-m", "services.serving_grpc.server"]
