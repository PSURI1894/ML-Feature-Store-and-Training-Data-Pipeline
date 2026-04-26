# Online Store

Serves features for inference with **p99 < 10 ms**.

## Key / value

```
key   = "{feature_view}:{entity_id}"
entity_id (composite) = "{k1}|{k2}"   # join-key values, sorted by key name
value = version_byte || msgpack({feature: value, ...})   with TTL
```

## Adapters

| Adapter | Path | Tier | TTL |
|---------|------|------|-----|
| Redis | `online/redis_store.py` | hot | 24h (pipelined `MGET`) |
| DynamoDB | `online/dynamodb_store.py` | cold | 7d (server-side TTL) |

## Latency

- Multi-entity reads are pipelined (`MGET`) so a feature service is one round trip.
- `ONLINE_READ_LATENCY` histogram buckets target the 0.5–10 ms range.

## TTL & pre-warming

TTL expiry just before a traffic peak caused cold reads. The fix (see
`fix/online-ttl-expiry-peak`) ties materialization to traffic patterns and pre-warms critical
feature views before known peaks via `online/prewarm.py`.

## Composite keys

Composite entity keys are concatenated with `|`. The initial implementation didn't escape the
separator, allowing collisions (`a|b` + `c` vs `a` + `b|c`); fixed in
`fix/redis-composite-key-separator` by escaping.

## Right-to-be-forgotten

`OnlineStore.delete()` removes a single entity's keys; `governance/rtbf.py` orchestrates deletes
across online + offline + materialized backups.
