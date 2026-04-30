"""PyFlink streaming job: per-user transaction velocity features.

Consumes the ``transactions`` Kafka topic, computes sliding-window velocity and
amount aggregates per user with event-time + watermarks, and dual-writes the
results to the online store (push source) for sub-minute freshness.

Run: ``flink run -py flink/jobs/transaction_velocity.py``
"""

from __future__ import annotations


def build_pipeline(env, table_env) -> None:
    """Declare the streaming SQL pipeline.

    Separated from ``main`` so it can be unit-tested with a mini-cluster.
    """
    table_env.execute_sql(
        """
        CREATE TABLE transactions (
            transaction_id STRING,
            user_id        STRING,
            merchant_id    STRING,
            amount         DOUBLE,
            event_ts       TIMESTAMP(3),
            WATERMARK FOR event_ts AS event_ts - INTERVAL '10' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'transactions',
            'properties.bootstrap.servers' = 'kafka:29092',
            'properties.group.id' = 'flink-txn-velocity',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
        """
    )

    table_env.execute_sql(
        """
        CREATE TABLE user_velocity_online (
            user_id           STRING,
            txn_count_5m      BIGINT,
            txn_amount_sum_5m DOUBLE,
            velocity_per_min  DOUBLE,
            window_end        TIMESTAMP(3),
            PRIMARY KEY (user_id) NOT ENFORCED
        ) WITH (
            'connector' = 'redis',
            'host' = 'redis',
            'port' = '6379',
            'key.prefix' = 'transaction_velocity_v1:',
            'ttl' = '600'
        )
        """
    )

    # 5-minute hopping window sliding every minute → near-real-time velocity.
    table_env.execute_sql(
        """
        INSERT INTO user_velocity_online
        SELECT
            user_id,
            COUNT(*)                                         AS txn_count_5m,
            SUM(amount)                                      AS txn_amount_sum_5m,
            COUNT(*) / 5.0                                   AS velocity_per_min,
            HOP_END(event_ts, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE) AS window_end
        FROM transactions
        GROUP BY user_id, HOP(event_ts, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE)
        """
    )


def main() -> None:  # pragma: no cover - requires a Flink cluster
    from pyflink.datastream import StreamExecutionEnvironment
    from pyflink.table import StreamTableEnvironment

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(4)
    env.enable_checkpointing(60_000)  # exactly-once via checkpoints every 60s
    table_env = StreamTableEnvironment.create(env)
    build_pipeline(env, table_env)


if __name__ == "__main__":
    main()
