# Cost Optimization

The economics of an ML feature platform are storage + compute + serving memory. We track
`$/feature_view/month` and review quarterly.

## Levers

| Lever | Mechanism |
|-------|-----------|
| Offline storage | Partition expiration (3y) + lifecycle to cold storage |
| Offline compute | Partition pruning + cluster keys; DuckDB sampling before full BQ joins |
| Online memory | Redis (hot, 24h TTL) vs. DynamoDB (cold, longer TTL) tiering |
| Streaming | Tier features: real-time (Flink) / near-real-time (Spark 5-min) / batch — default batch |
| Materialization | Cadence tied to SLA + traffic; pre-warm only critical views before peaks |

## Tiering policy

New features default to the **batch** tier. Promotion to a hotter tier requires justification (see
`docs/data-contracts.md`) because:

- Real-time (Flink) state + compute is the most expensive.
- Many low-traffic models gain nothing from sub-minute freshness.

## Quarterly review

- Deprecate low-usage features (no consumer in 90 days) with a sunset date.
- Flag high-cost views for optimization (re-tier, reduce TTL, or merge).
- Usage is derived from feature-service membership + serving request samples.
