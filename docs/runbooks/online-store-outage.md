# Runbook: Online Store Outage

**Alert:** `OnlineReadLatencyHigh` (p99 > 10 ms) or read errors spiking.

## Impact

Inference latency rises or feature reads fail. Models may fall back to defaults → quality drop.

## Triage

1. Check Redis cluster health (CPU, memory, evictions, replica lag).
2. Check `online_read_errors_total` by reason (timeout vs. connection vs. NOAUTH).
3. Confirm whether it's one shard (hot key / skew) or cluster-wide.

## Mitigation

- **Hot shard:** check for a hot entity; the composite key escaping fix prevents key collisions, but
  a genuinely hot entity may need request-side caching.
- **Memory pressure / evictions:** `maxmemory-policy allkeys-lru` is set; scale the cluster or shed
  cold views to DynamoDB.
- **Cluster down:** serving fails closed for models that require fresh features; for tolerant models,
  the resolver returns `MISSING` and the model uses its default path.

## Recovery

- After Redis recovers, run `materialization` to repopulate, then pre-warm hot views.
