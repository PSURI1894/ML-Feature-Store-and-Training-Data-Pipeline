# Feature Authoring Guide

This guide walks a feature engineer from idea to a serving, monitored feature.

## 1. Define the feature view

Add a module under `feature_repo/feature_views/`. A view must declare its entity, source,
schema, TTL, and **standard tags** (owner, team, sensitivity, tier, sla_freshness):

```python
from feature_repo.tags import standard_tags

user_features_v2 = FeatureView(
    name="user_features_v2",         # <snake_case>_v<int>
    entities=[user],
    ttl=timedelta(days=90),
    schema=[Field(name="txn_count_30d", dtype=Int64)],
    source=user_features_source,
    tags=standard_tags(
        owner="you@example.com", team="growth",
        sensitivity="financial", tier="batch", sla_freshness="24h",
        source_contract="warehouse.users.v3",
    ),
)
```

Register it in `feature_repo/feature_views/__init__.py::ALL_FEATURE_VIEWS`.

## 2. Write the transformation once

Put the transform in `feature_platform/batch/transforms.py` (batch) or
`feature_platform/streaming/windowing.py` (streaming). The **same** function must be reachable
offline and online — do not re-implement it in a notebook.

## 3. Test the transform

Add unit tests in `tests/unit/`. The feature-validation CI job runs
`pytest -k "transform or feature_view"`.

## 4. Open a PR into `develop`

CI runs `feature-validation.yml`:
- validates naming / tags / SLA-vs-TTL,
- runs your transform tests,
- checks backward compatibility (removing a column requires a new `_vN`),
- posts a plan table to the PR summary.

## 5. Backfill & materialize

After merge, request a backfill (`docs/runbooks/backfill.md`) and let the daily materialization
populate the online store.

## Versioning & deprecation

- Backward-incompatible change → new version (`user_features_v3`).
- Deprecate the old view with a `sunset_date`; notify consumers; remove after the date.
- Models pin a **feature service**, which pins feature-view versions.
