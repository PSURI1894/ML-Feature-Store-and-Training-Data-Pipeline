# MLflow Integration

The model registry and the feature registry are linked: a model records the **exact features** it
was trained on.

## What we log

On every training run:

- `fv.<feature_view>` params → the pinned version of each view.
- `feature_view_versions` tag → e.g. `user_features:v2,merchant_features:v1`.
- `feature_service` tag → the bundle the model consumes at serving time.
- `offline_snapshot_id` tag (Iceberg) → exact table snapshot for reproducibility.

## Promotion gate

`assert_feature_provenance(run_id)` blocks promoting a model to Production unless it recorded its
feature provenance. No provenance → not promotable.

## Why

- **Audit:** answer "which features (and versions) does this production model use?" instantly.
- **Reproducibility:** rebuild the exact training set later from pinned versions + snapshot id.
- **Skew triage:** when a model degrades, compare serving feature versions to the trained-on
  versions in one place.
