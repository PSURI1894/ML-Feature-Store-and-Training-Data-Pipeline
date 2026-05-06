# Online Serving Layer

A gRPC service co-located with model servers; **p99 < 10 ms** reads from Redis.

## API

`feature_service.proto` defines `GetOnlineFeatures` — one request resolves an entire feature service
for a batch of entities (single round trip). Each feature is tagged with a status:
`PRESENT` / `MISSING` / `STALE`.

```bash
make proto                      # generate stubs
python -m services.serving_grpc.server
```

## Design

- **Thin handler, fat resolver.** All logic is in `feature_platform/serving/resolver.py`, which is
  unit-testable without gRPC.
- **Batched online reads** via `read_many` (Redis `MGET`).
- **On-demand in-process** — the resolver can run on-demand transforms without a network hop.
- **Hard deadlines** — the client sets a 50 ms timeout; the model degrades gracefully on `MISSING`.

## Latency budget

| Step | Budget |
|------|--------|
| Redis MGET | < 3 ms |
| Deserialize + assemble | < 2 ms |
| On-demand transforms | < 2 ms |
| gRPC overhead | < 3 ms |
| **Total p99** | **< 10 ms** |
