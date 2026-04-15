.DEFAULT_GOAL := help
SHELL := /bin/bash
PY := python

.PHONY: help install dev fmt lint type test test-pit cov proto feast-apply \
        materialize up down monitor backfill clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime deps
	$(PY) -m pip install -e .

dev: ## Install dev + engine deps and pre-commit hooks
	$(PY) -m pip install -e ".[dev,spark,flink]"
	pre-commit install

fmt: ## Auto-format
	ruff check --fix src tests
	black src tests

lint: ## Lint
	ruff check src tests
	black --check src tests

type: ## Static type-check
	mypy src

test: ## Run unit tests
	pytest -m "not integration"

test-pit: ## Run point-in-time correctness suite
	pytest -m pit -v

cov: ## Coverage report
	pytest --cov-report=html && echo "open htmlcov/index.html"

proto: ## Regenerate gRPC stubs
	$(PY) -m grpc_tools.protoc -Iservices/serving_grpc/protos \
		--python_out=services/serving_grpc \
		--grpc_python_out=services/serving_grpc \
		services/serving_grpc/protos/feature_service.proto

feast-apply: ## Sync feature definitions to the registry
	cd feature_repo && feast apply

materialize: ## Materialize offline -> online (last 1 day)
	$(PY) -m feature_platform.cli materialize --since 1d

up: ## Start local stack (redis, kafka, postgres, mlflow)
	docker compose up -d

down: ## Tear down local stack
	docker compose down -v

monitor: ## Run nightly feature monitor
	$(PY) -m feature_platform.cli monitor --all

backfill: ## Run a backfill (FV=..., START=..., END=...)
	$(PY) scripts/run_backfill.py --feature-view $(FV) --start $(START) --end $(END)

clean: ## Remove caches and build artifacts
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
