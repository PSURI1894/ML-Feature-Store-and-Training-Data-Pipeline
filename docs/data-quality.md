# Feature Data Quality

Two layers, sharing intent:

1. **Inline checks** (`feature_platform/dq/`) — dependency-free expectations that run *inside* batch
   and streaming jobs. A batch that fails a hard expectation is **not** materialized to the online
   store, so a bad batch can't corrupt serving.
2. **Great Expectations** (`great_expectations/`) — the full suite used in CI and scheduled
   validation, with data docs.

## Example

```python
from feature_platform.dq import validate_dataframe
from feature_platform.dq.expectations import USER_FEATURES_EXPECTATIONS

result = validate_dataframe(batch_df, USER_FEATURES_EXPECTATIONS, fail_fraction=0.001)
if not result.passed:
    raise RuntimeError(result.failures)   # block materialization
```

## What we assert

- Keys (`entity_id`, `event_ts`) are non-null.
- Numeric features fall in sane ranges (e.g. `chargeback_rate_90d` in [0, 1]).
- Types are stable (catches upstream contract drift early).

`mostly` / `fail_fraction` tolerate a tiny, expected fraction of anomalies without flapping.
