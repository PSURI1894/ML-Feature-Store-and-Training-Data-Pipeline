# On-Demand Features

Some features can only be computed at request time because they depend on the **current** request
(e.g. the amount of the transaction being scored) combined with stored aggregates.

## Define

Two ways, sharing the same pure logic:

- **Feast** `@on_demand_feature_view` in `feature_repo/on_demand/` (used in training joins).
- **Platform** `@on_demand(...)` decorator in `feature_platform/ondemand/executor.py` (used in the
  low-latency serving path, independent of Feast).

## Serve

`services/ondemand_api` exposes `POST /compute`:

```bash
curl -s localhost:8080/compute -H 'content-type: application/json' \
  -d '{"feature":"amount_to_avg_ratio","context":{"amount":250.0,"txn_amount_avg_30d":50.0}}'
# {"feature":"amount_to_avg_ratio","values":{"amount_to_avg_ratio":5.0},"compute_ms":0.1}
```

Co-locate this service with model servers so added latency is negligible. The gRPC serving layer can
call the executor in-process to avoid a network hop entirely.
