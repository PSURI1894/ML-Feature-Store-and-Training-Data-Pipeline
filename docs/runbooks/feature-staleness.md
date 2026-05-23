# Runbook: Feature Staleness

**Alert:** `FeatureStale` — `feature_freshness_seconds > SLA` for a view.

## Impact

Models reading this view online are scoring on stale data → degraded predictions, possible
training-serving skew.

## Triage

1. Identify the view from the alert label.
2. Check the batch/materialization DAGs in Airflow:
   - `batch_features` succeeded for the latest logical date?
   - `materialization` ran after it?
3. Check the offline store freshness: `OfflineStore.latest_event_ts(view)`.
4. Check the source contract — did an upstream table stop landing?

## Mitigation

- If materialization failed: re-run the `materialization` DAG for the window.
- If batch compute failed: re-run `batch_features`; if data is missing upstream, page the producing
  team referenced by the view's `source_contract`.
- If a hot view: pre-warm online (`online/prewarm.py`) while the pipeline catches up.

## Prevention

- Tie materialization cadence to the view's SLA.
- Alert on producer-side contract SLAs, not just our freshness.
