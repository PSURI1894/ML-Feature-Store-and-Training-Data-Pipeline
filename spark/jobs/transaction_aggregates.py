"""Spark batch job: user x merchant interaction aggregates (composite key).

Demonstrates writing a composite-key offline table; the entity_id is the
``user_id|merchant_id`` pair produced to match the online key schema.
"""

from __future__ import annotations

import argparse


def build_user_merchant_features(spark, as_of_date: str):
    from pyspark.sql import functions as F

    txns = spark.table("warehouse.transactions").where(F.col("event_ts") <= F.lit(as_of_date))
    return (
        txns.groupBy("user_id", "merchant_id")
        .agg(
            F.count("*").alias("pair_txn_count_90d"),
            F.sum("amount").alias("pair_amount_sum_90d"),
            F.last("amount").alias("pair_last_amount"),
        )
        .withColumn("pair_is_first_txn", (F.col("pair_txn_count_90d") == 1).cast("int"))
        .withColumn("entity_id", F.concat_ws("|", F.col("user_id"), F.col("merchant_id")))
        .withColumn("event_ts", F.lit(as_of_date).cast("timestamp"))
        .withColumn("created_ts", F.current_timestamp())
        .withColumn("event_date", F.lit(as_of_date).cast("date"))
        .drop("user_id", "merchant_id")
    )


def main() -> None:
    from pyspark.sql import SparkSession

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", default="data/offline/user_merchant_features_v1.parquet")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("user_merchant_aggregates").getOrCreate()
    build_user_merchant_features(spark, args.date).write.mode("append").partitionBy(
        "event_date"
    ).parquet(args.output)
    spark.stop()


if __name__ == "__main__":
    main()
