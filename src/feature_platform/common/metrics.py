"""Prometheus metric definitions shared across services.

Naming follows the Prometheus convention ``<namespace>_<subsystem>_<unit>``.
Keeping every metric here prevents duplicate-registration errors and gives a
single inventory of what we measure.
"""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

NAMESPACE = "feature_platform"

# ---- Online serving ----
ONLINE_READ_LATENCY = Histogram(
    "online_read_latency_seconds",
    "Latency of online feature reads",
    labelnames=("feature_view", "online_store"),
    namespace=NAMESPACE,
    buckets=(0.0005, 0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1),
)
ONLINE_READ_ERRORS = Counter(
    "online_read_errors_total",
    "Online read errors",
    labelnames=("feature_view", "reason"),
    namespace=NAMESPACE,
)

# ---- Materialization / batch ----
MATERIALIZE_ROWS = Counter(
    "materialize_rows_total",
    "Rows materialized offline->online",
    labelnames=("feature_view",),
    namespace=NAMESPACE,
)

# ---- Freshness & drift ----
FEATURE_FRESHNESS_SECONDS = Gauge(
    "feature_freshness_seconds",
    "Seconds since the newest feature value for a view",
    labelnames=("feature_view",),
    namespace=NAMESPACE,
)
FEATURE_DRIFT_PSI = Gauge(
    "feature_drift_psi",
    "Population Stability Index vs. baseline",
    labelnames=("feature_view", "feature"),
    namespace=NAMESPACE,
)
TRAINING_SERVING_SKEW = Gauge(
    "training_serving_skew",
    "Skew score between offline and online feature values",
    labelnames=("feature_view", "feature"),
    namespace=NAMESPACE,
)
