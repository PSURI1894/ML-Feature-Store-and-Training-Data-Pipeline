-- Offline feature store DDL (BigQuery dialect; analogous for Snowflake/Iceberg).
-- Partitioned by event_date and clustered by entity_id so point-in-time joins
-- prune partitions and cluster-skip instead of full scans.

CREATE SCHEMA IF NOT EXISTS feature_store;

CREATE TABLE IF NOT EXISTS feature_store.user_features_v2 (
    entity_id            STRING    NOT NULL,   -- user_id
    event_ts             TIMESTAMP NOT NULL,   -- event time (as-of key)
    account_age_days     INT64,
    txn_count_30d        INT64,
    txn_amount_sum_30d   FLOAT64,
    txn_amount_avg_30d   FLOAT64,
    distinct_merchants_30d INT64,
    chargeback_rate_90d  FLOAT64,
    home_country         STRING,
    created_ts           TIMESTAMP NOT NULL,   -- write time (tie-break / late-data audit)
    event_date           DATE      NOT NULL    -- partition key (derived from event_ts)
)
PARTITION BY event_date
CLUSTER BY entity_id
OPTIONS (
    description = "User-level batch features (v2). Partition by event_date, cluster by entity_id.",
    partition_expiration_days = 1095,           -- 3y retention; lifecycle to cold after
    require_partition_filter = TRUE             -- force partition pruning on every query
);

-- Composite-key view: identifier is (user_id, merchant_id) stored as a single
-- entity_id column produced by the key schema (user_id|merchant_id).
CREATE TABLE IF NOT EXISTS feature_store.user_merchant_features_v1 (
    entity_id            STRING    NOT NULL,   -- "{user_id}|{merchant_id}"
    event_ts             TIMESTAMP NOT NULL,
    pair_txn_count_90d   INT64,
    pair_amount_sum_90d  FLOAT64,
    pair_last_amount     FLOAT64,
    pair_is_first_txn    INT64,
    created_ts           TIMESTAMP NOT NULL,
    event_date           DATE      NOT NULL
)
PARTITION BY event_date
CLUSTER BY entity_id
OPTIONS (require_partition_filter = TRUE);
