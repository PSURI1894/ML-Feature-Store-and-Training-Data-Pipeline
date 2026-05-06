# Streaming Feature Pipeline

Flink computes time-windowed features from Kafka and **dual-writes**: online immediately (freshness)
and snapshotted to the offline store periodically (training consistency).

## Job

`flink/jobs/transaction_velocity.py` — per-user 5-minute hopping-window velocity, sliding every
minute, with event-time + a 10s bounded-out-of-orderness watermark and 60s checkpoints
(exactly-once).

## Engine-agnostic logic

Windowing primitives live in `feature_platform/streaming/windowing.py` (pure Python) so they are
unit-testable and reusable by the near-real-time Spark Structured Streaming tier.

## Consistency

- `online_sink.OnlineFeatureSink` writes online with a short TTL.
- `offline_snapshot.OfflineSnapshotter` periodically appends current values to the offline store so
  a point-in-time join can recover streaming features for training.
- A daily reconciliation job (`monitoring/skew.py`) compares samples from both stores.

## Tiering

Streaming is the **real-time** tier ($$$). Default new features to **batch**; upgrading to streaming
requires justification (`docs/data-contracts.md`).
