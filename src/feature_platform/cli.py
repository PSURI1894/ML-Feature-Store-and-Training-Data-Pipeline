"""Unified command-line entrypoint: ``fp <command>``.

Thin orchestration only — every command delegates to a library function so the
same behaviour is reachable from Airflow operators and tests.
"""

from __future__ import annotations

import argparse
import sys

from feature_platform.common.logging import get_logger
from feature_platform.common.time_utils import parse_duration, utcnow

log = get_logger(__name__)


def _cmd_materialize(args: argparse.Namespace) -> int:
    from feature_platform.batch.runner import materialize_recent

    window = parse_duration(args.since)
    end = utcnow()
    start = end - window
    log.info("materialize.start", since=args.since, start=str(start), end=str(end))
    rows = materialize_recent(start=start, end=end, feature_views=args.feature_views)
    log.info("materialize.done", rows=rows)
    return 0


def _cmd_monitor(args: argparse.Namespace) -> int:
    from feature_platform.monitoring.drift import run_drift_scan

    report = run_drift_scan(all_views=args.all, feature_views=args.feature_views)
    log.info("monitor.done", alerted=report.alerted, checked=report.checked)
    return 1 if report.alerted else 0


def _cmd_validate(_: argparse.Namespace) -> int:
    from feature_platform.registry.validation import validate_repo

    errors = validate_repo()
    for err in errors:
        log.error("validation.error", rule=err.rule, message=str(err))
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fp", description="Feature Platform CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("materialize", help="Materialize offline -> online")
    p_mat.add_argument("--since", default="1d", help="e.g. 1d, 6h")
    p_mat.add_argument("--feature-views", nargs="*", dest="feature_views")
    p_mat.set_defaults(func=_cmd_materialize)

    p_mon = sub.add_parser("monitor", help="Run drift / freshness monitor")
    p_mon.add_argument("--all", action="store_true")
    p_mon.add_argument("--feature-views", nargs="*", dest="feature_views")
    p_mon.set_defaults(func=_cmd_monitor)

    p_val = sub.add_parser("validate", help="Validate feature definitions")
    p_val.set_defaults(func=_cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
