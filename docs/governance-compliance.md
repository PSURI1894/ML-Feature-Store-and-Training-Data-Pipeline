# Governance & Compliance

Every feature view is tagged `public` | `financial` | `pii`. That tag drives access control and
audit automatically.

## RBAC

`governance/rbac.py` enforces least-privilege reads:

| Sensitivity | Roles allowed | Audited |
|-------------|---------------|---------|
| public | viewer, analyst, ml-engineer, admin | no |
| financial | analyst, ml-engineer, admin | yes |
| pii | ml-engineer, admin | yes |

`enforce_read(role, sensitivity, …)` raises `AccessDeniedError` when not permitted and emits an
audit event on every sensitive read.

## Right-to-be-forgotten

`governance/rtbf.py` erases an entity across **online + offline + materialized backups**,
idempotently, and writes a compliance audit record. Triggered by a deletion request keyed on
entity id.

## Audit

`governance/audit.py` emits structured, append-only events (`audit.access`, `audit.erasure`) shipped
to an immutable store. This is how we answer "who read which PII feature, when?" and prove erasure.

## Compliance questions we can answer

- Which features touch PII? → registry `sensitivity` tag (catalog UI).
- Who accessed them? → audit log.
- Was a user's data erased everywhere? → erasure audit record + idempotent re-run.
