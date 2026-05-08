"""Alert routing for monitoring results.

Severity tiers map to channels: SLA/leakage breaches page on-call; drift watches
go to the owning team's Slack. Routing is data-driven so adding a channel doesn't
touch detection logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from feature_platform.common.logging import get_logger

log = get_logger(__name__)


class Severity(str, Enum):
    PAGE = "page"        # wake someone up
    TICKET = "ticket"    # create an issue
    SLACK = "slack"      # notify channel


@dataclass(frozen=True, slots=True)
class Alert:
    feature_view: str
    title: str
    severity: Severity
    detail: str


ROUTING = {
    Severity.PAGE: "pagerduty:ml-platform-oncall",
    Severity.TICKET: "jira:MLP",
    Severity.SLACK: "slack:#feature-platform-alerts",
}


def dispatch(alert: Alert) -> str:
    """Route an alert to its channel. Returns the channel id (no-op transport here)."""
    channel = ROUTING[alert.severity]
    log.warning(
        "alert.dispatch",
        feature_view=alert.feature_view,
        severity=alert.severity.value,
        channel=channel,
        title=alert.title,
    )
    return channel
