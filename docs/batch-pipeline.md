# Batch Feature Pipeline

Spark jobs compute features from the warehouse on a schedule, write to the offline store
(partitioned by `event_date`), then `materialize` copies recent values to the online store.

## Jobs

| Job | Output view | Cadence |
|-----|-------------|---------|
| `spark/jobs/user_features_batch.py` | `user_features_v2` | daily |
| `spark/jobs/transaction_aggregates.py` | `user_merchant_features_v1` (composite) | daily |

## Offline → online

`feature_platform.batch.runner.materialize_recent` reads the offline window and writes the latest
row per entity to the online store with the view TTL. It is idempotent, so re-runs are safe.

```bash
spark-submit spark/jobs/user_features_batch.py --date 2026-05-01
fp materialize --since 1d
```

## Skew prevention

Batch UDFs call the **same** pure functions in `feature_platform/batch/transforms.py` that the
streaming and on-demand paths use. There is exactly one implementation of each feature's logic.

## Tuning

See `spark/conf/spark-defaults.conf`: adaptive query execution, skew-join handling, zstd Parquet,
dynamic allocation (2–50 executors), and dynamic partition overwrite for idempotent backfills.
