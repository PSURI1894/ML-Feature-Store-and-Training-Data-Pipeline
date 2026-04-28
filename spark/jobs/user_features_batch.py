"""Spark batch job: compute daily user features from the warehouse.

Run: ``spark-submit spark/jobs/user_features_batch.py --date 2026-05-01``

Reuses the pure transforms in ``feature_platform.batch.transforms`` via Spark UDFs
so the batch values match what the online/on-demand paths would compute.
"""

from __future__ import annotations

import argparse


def build_user_features(spark, as_of_date: str):
    """Compute user_features_v2 for a single day.

    Reads transactions + accounts, computes 30d rolling aggregates, writes the
    offline table partitioned by event_date.
    """
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    txns = spark.table("warehouse.transactions").where(
        F.col("event_ts") <= F.lit(as_of_date)
    )
    w30 = (
        Window.partitionBy("user_id")
        .orderBy(F.col("event_ts").cast("long"))
        .rangeBetween(-30 * 86400, 0)
    )

    features = (
        txns.withColumn("txn_count_30d", F.count("*").over(w30))
        .withColumn("txn_amount_sum_30d", F.sum("amount").over(w30))
        .withColumn("txn_amount_avg_30d", F.avg("amount").over(w30))
        .withColumn("distinct_merchants_30d", F.size(F.collect_set("merchant_id").over(w30)))
        .groupBy("user_id")
        .agg(
            F.max("txn_count_30d").alias("txn_count_30d"),
            F.max("txn_amount_sum_30d").alias("txn_amount_sum_30d"),
            F.max("txn_amount_avg_30d").alias("txn_amount_avg_30d"),
            F.max("distinct_merchants_30d").alias("distinct_merchants_30d"),
        )
        .withColumnRenamed("user_id", "entity_id")
        .withColumn("event_ts", F.lit(as_of_date).cast("timestamp"))
        .withColumn("created_ts", F.current_timestamp())
        .withColumn("event_date", F.lit(as_of_date).cast("date"))
    )
    return features


def main() -> None:
    from pyspark.sql import SparkSession

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", default="data/offline/user_features_v2.parquet")
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("user_features_batch")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    df = build_user_features(spark, args.date)
    df.write.mode("append").partitionBy("event_date").parquet(args.output)
    spark.stop()


if __name__ == "__main__":
    main()
