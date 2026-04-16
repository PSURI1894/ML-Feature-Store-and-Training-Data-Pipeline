# Contributing

Thanks for contributing to the Feature Platform. This repo follows a trunk-based-ish flow with a
`develop` integration branch and short-lived `feat/*` and `fix/*` branches.

## Branching & commits

- Branch off `develop`: `feat/<scope>` or `fix/<scope>`.
- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat(streaming): add tumbling window aggregator`.
- Open a PR into `develop`. Releases flow `develop → main` and are tagged `vMAJOR.MINOR.PATCH`.

## Definition of Done for a feature view

A new or changed feature view is **not mergeable** until it has:

1. An **owner** (`owner=` on the `FeatureView`) and a team tag.
2. A declared **freshness / TTL** and an **SLA**.
3. A **sensitivity** tag (`public` | `financial` | `pii`).
4. **Unit tests** for the transformation logic.
5. A passing `feature-definition-lint` pre-commit hook.
6. Documentation of the source **data contract** it depends on.

CI enforces 1–5 automatically (`.github/workflows/feature-validation.yml`).

## Local checks

```bash
make fmt      # auto-format
make lint     # ruff + black
make type     # mypy
make test     # unit tests
make test-pit # point-in-time invariants
```

## Code style

- Python 3.10+, fully type-hinted (`mypy` strict-ish).
- Pure transformation functions where possible — easy to unit test and reuse offline+online.
- No feature logic in notebooks that isn't mirrored in a registered feature view.
