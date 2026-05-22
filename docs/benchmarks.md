# Benchmarks

Indicative numbers from the staging environment (Redis 3-node, BigQuery, 30-day window). These are
tracked over time; regressions block release.

## Online serving (Redis, pipelined)

| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| single-entity read | 0.6 ms | 1.4 ms | 2.9 ms |
| feature-service (4 views) read | 1.1 ms | 3.2 ms | 6.8 ms |
| batch read (50 entities, MGET) | 1.9 ms | 4.7 ms | 8.5 ms |

Target: feature-service p99 < 10 ms. ✅

## Offline training join (BigQuery, push-down as-of)

| Entities | History | Wall time |
|----------|---------|-----------|
| 1M | 30 days | ~22 s |
| 10M | 30 days | ~95 s |
| 10M | 365 days (pruned) | ~210 s |

Partition pruning (`require_partition_filter`) is the dominant factor.

## Materialization throughput

~120k entities/s online write with pipelined Redis `SET` (batch size 1000).
