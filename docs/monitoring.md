# Monitoring & Observability

Nightly, every feature is checked for drift, freshness, and null-rate; serving latency and skew are
tracked continuously.

## Signals

| Signal | Module | Alert when |
|--------|--------|-----------|
| Drift (PSI) | `monitoring/drift.py` | PSI > 0.2 |
| Drift (KS) | `monitoring/drift.py` | KS p-value < 0.05 |
| Freshness | `monitoring/freshness.py` | age > view SLA |
| Null-rate | `monitoring/null_rate.py` | nulls > 5% |
| Online latency | `metrics.ONLINE_READ_LATENCY` | p99 > 10 ms |
| Training-serving skew | `monitoring/skew.py` | skew score > 0.1 |

## Baselines

Baselines refresh monthly (`monitoring/baseline.py`). Comparing today's sample to a fixed monthly
baseline avoids the "slow boiling frog" problem of comparing only to yesterday.

## Dashboards & alerts

- Grafana: `monitoring/grafana/feature_health_dashboard.json`
- Prometheus alert rules: `monitoring/prometheus/alerts.yml`
- Routing by severity: page / ticket / slack (`monitoring/alerts.py`).

## Cost

We also track `$/feature_view/month` (storage + compute). Quarterly review deprecates low-usage,
high-cost views — see `docs/cost-optimization.md`.
