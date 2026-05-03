# Point-in-Time Correctness

The single most important guarantee in this platform: **training data must contain only
information that was available at prediction time.**

## The invariant

For each request row `(entity, event_ts)` and a feature view with rows `(entity, feature_ts, value)`:

```
value*(entity, event_ts) =
    value at  argmax{ feature_ts : feature_ts <= event_ts  AND  event_ts - feature_ts <= TTL }
```

Two constraints:

1. `feature_ts <= event_ts` — **no future leakage**.
2. `event_ts - feature_ts <= TTL` — **freshness**, so offline matches what online would have served.

## Why "nearest" is wrong

A tempting but incorrect implementation uses `merge_asof(direction="nearest")`, which can attach a
feature value observed *after* the event — leaking the future and inflating offline metrics. The
correct direction is `backward`, combined with a TTL filter. See
`fix/pit-join-future-leakage` for the bug and the regression test that locks it down.

## Testing it

`tests/pit_correctness/` injects adversarial future-dated feature rows and asserts they never appear
in the output, across single and composite keys, ties on `feature_ts`, and TTL boundaries.

```bash
make test-pit
```

## Reproducibility

Pinning a training run to `feature_view_versions` (and, on Iceberg, a table snapshot id) lets us
rebuild the exact dataset months later for audit or debugging.
