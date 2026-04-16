# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x     | ✅        |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities. Email the maintainer at
`parthsuri009@gmail.com` with a description, reproduction steps, and impact assessment. You can
expect an acknowledgement within 72 hours.

## Data sensitivity

This platform handles features tagged `pii` and `financial`. When reporting issues that touch
sensitive data, **do not** include real feature values, entity identifiers, or credentials in
your report. Use synthetic examples.

## Hardening checklist

- Online/offline credentials are read from the environment, never committed (`.env` is gitignored).
- `detect-private-key` runs as a pre-commit hook.
- RBAC gates reads of `pii`/`financial` feature views (`feature_platform.governance.rbac`).
- Right-to-be-forgotten deletes propagate across online + offline + materialized backups.
