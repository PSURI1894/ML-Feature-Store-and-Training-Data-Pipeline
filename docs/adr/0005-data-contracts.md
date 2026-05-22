# ADR 0005: Data contracts between producers and feature views

- Status: Accepted
- Date: 2026-05-10

## Context

Feature definitions drifted from producing teams' schemas; silent column renames broke features.

## Decision

Producing teams declare a **versioned data contract** (e.g. `warehouse.users.v3`). Feature views
reference contract-versioned columns via the `source_contract` tag. CI fails a feature view whose
contract reference is missing or points at a retired contract version.

## Consequences

- A producer rename is a contract version bump, surfaced to feature owners — not a silent break.
- The catalog UI shows each view's source contract for impact analysis.
- See `docs/data-contracts.md` for the contract schema and lifecycle.
