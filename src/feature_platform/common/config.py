"""Centralised, environment-driven configuration using pydantic-settings.

Every service and job reads from the same ``Settings`` object so that local,
staging and prod differ only by environment variables — never by code path.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PROD = "prod"


class OfflineStoreKind(str, Enum):
    DUCKDB = "duckdb"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    ICEBERG = "iceberg"


class OnlineStoreKind(str, Enum):
    REDIS = "redis"
    DYNAMODB = "dynamodb"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="", extra="ignore", case_sensitive=False
    )

    env: Environment = Field(default=Environment.LOCAL, alias="FP_ENV")
    log_level: str = Field(default="INFO", alias="FP_LOG_LEVEL")
    log_json: bool = Field(default=False, alias="FP_LOG_JSON")

    # Stores
    offline_store: OfflineStoreKind = Field(default=OfflineStoreKind.DUCKDB)
    online_store: OnlineStoreKind = Field(default=OnlineStoreKind.REDIS)

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl_seconds: int = 86_400

    bigquery_project: str | None = None
    bigquery_dataset: str = "feature_store"

    kafka_bootstrap_servers: str = "localhost:9092"
    registry_db_url: str = "postgresql://feast:feast@localhost:5432/registry"
    mlflow_tracking_uri: str = "http://localhost:5000"

    # Drift thresholds
    drift_ks_pvalue_threshold: float = 0.05
    drift_psi_threshold: float = 0.2

    @property
    def is_prod(self) -> bool:
        return self.env is Environment.PROD


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide cached settings instance."""
    return Settings()
