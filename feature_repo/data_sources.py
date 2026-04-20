"""Data sources backing feature views.

Each source declares the timestamp columns that make point-in-time correctness
possible: ``timestamp_field`` (event time, the as-of key) and ``created_timestamp_column``
(write time, used to break ties and audit late data).
"""

from __future__ import annotations

from feast import FileSource, KafkaSource, PushSource
from feast.data_format import JsonFormat

# --- Batch sources (warehouse-backed; FileSource locally, swapped for
#     BigQuerySource/SnowflakeSource via the prod profile) ---

user_features_source = FileSource(
    name="user_features_source",
    path="data/user_features.parquet",
    timestamp_field="event_ts",
    created_timestamp_column="created_ts",
    description="Daily user aggregates from the warehouse.",
)

merchant_features_source = FileSource(
    name="merchant_features_source",
    path="data/merchant_features.parquet",
    timestamp_field="event_ts",
    created_timestamp_column="created_ts",
)

transaction_features_source = FileSource(
    name="transaction_features_source",
    path="data/transaction_features.parquet",
    timestamp_field="event_ts",
    created_timestamp_column="created_ts",
)

user_merchant_source = FileSource(
    name="user_merchant_source",
    path="data/user_merchant_features.parquet",
    timestamp_field="event_ts",
    created_timestamp_column="created_ts",
)

# --- Streaming source (Flink/Spark push windowed features here) ---

transaction_events_stream = KafkaSource(
    name="transaction_events_stream",
    kafka_bootstrap_servers="localhost:9092",
    topic="transactions",
    timestamp_field="event_ts",
    batch_source=transaction_features_source,
    message_format=JsonFormat(
        schema_json="transaction_id string, user_id string, merchant_id string, "
        "amount double, event_ts timestamp"
    ),
)

# Push source for low-latency dual-writes from the streaming sink.
transaction_velocity_push = PushSource(
    name="transaction_velocity_push",
    batch_source=transaction_features_source,
)
