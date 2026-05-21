# ADR 0004: Online store tiering (Redis hot / DynamoDB cold)

- Status: Accepted
- Date: 2026-05-02

## Context

Keeping every feature in Redis was expensive; many views are low-traffic.

## Decision

Two-tier online storage:

- **Redis** (hot) — 24h TTL, p99 < 10 ms, pipelined `MGET`. For high-traffic / latency-critical views.
- **DynamoDB** (cold) — longer TTL, server-side expiry. For low-traffic views.

Pre-warm critical Redis views before known traffic peaks (`online/prewarm.py`) to avoid TTL-expiry
stampedes.

## Consequences

- Redis memory is reserved for features that need it.
- A new `extend_ttl` op enables pre-warming without rewriting values
  (see `fix/online-ttl-expiry-peak`).
