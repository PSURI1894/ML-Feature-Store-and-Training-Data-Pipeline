# On-demand feature service image.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY services ./services
RUN pip install --no-cache-dir -e .

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/healthz').status==200 else 1)"

CMD ["uvicorn", "services.ondemand_api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
