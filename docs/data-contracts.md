# Data Contracts

A data contract is a versioned promise from a producing team about a source table's schema and
semantics. Feature views depend on contracts, not on raw columns.

## Why

Silent upstream renames used to break feature views with no warning. Contracts make a rename an
explicit, versioned, reviewable event.

## Shape

```yaml
contract: warehouse.users
version: 3
owner: data-platform@example.com
columns:
  - { name: user_id, type: string, nullable: false, pii: true }
  - { name: account_created_at, type: timestamp, nullable: false }
  - { name: home_country, type: string, nullable: true }
slo:
  freshness: 6h
  availability: 99.9
```

## Lifecycle

1. Producer publishes/updates a contract (version bump on breaking change).
2. Feature views reference it via the `source_contract` tag (e.g. `warehouse.users.v3`).
3. CI fails a view that references a missing or retired contract version.
4. A breaking producer change requires a new contract version; consumers migrate before sunset.

## Tiering & cost

Defaulting a feature to a cheaper compute tier is encouraged. Upgrading to **real-time** (Flink)
requires a written justification recorded here, because streaming cost often exceeds value for
low-traffic models.
