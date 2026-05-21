# ADR 0001: Adopt Feast as the feature platform

- Status: Accepted
- Date: 2026-04-16

## Context

We need a feature store that serves the same feature definitions to offline training and online
inference, with a Git-native registry. Options considered: build in-house, Tecton (managed), Feast
(open-source).

## Decision

Adopt **Feast 0.39+**. It gives us a registry, offline/online store abstractions, materialization,
on-demand feature views, and composite entities out of the box, while remaining open-source and
embeddable in our own library layer.

## Consequences

- We wrap Feast in `feature_platform/*` so our internal contracts don't break on SDK changes.
- The registry (`feature_repo/`) is the single source of truth; `feast apply` syncs to Postgres.
- We accept Feast's entity-key serialization v3 for composite keys.
- Tecton remains a fallback if managed operations become preferable at larger scale.
