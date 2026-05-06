"""Kafka source configuration for streaming feature jobs.

Event-time semantics with a bounded-out-of-orderness watermark: late events
within the bound still update the correct window; later ones are dropped (and
counted) rather than corrupting closed windows.
"""

from __future__ import annotations

from dataclasses import dataclass

from feature_platform.common.config import get_settings


@dataclass(frozen=True, slots=True)
class KafkaSourceConfig:
    topic: str
    group_id: str
    bootstrap_servers: str
    starting_offset: str = "latest"          # latest | earliest
    watermark_delay_seconds: int = 10        # bounded out-of-orderness
    timestamp_field: str = "event_ts"

    @classmethod
    def for_topic(cls, topic: str, group_id: str) -> KafkaSourceConfig:
        return cls(
            topic=topic,
            group_id=group_id,
            bootstrap_servers=get_settings().kafka_bootstrap_servers,
        )

    def to_flink_properties(self) -> dict[str, str]:
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": self.group_id,
            "auto.offset.reset": self.starting_offset,
            "isolation.level": "read_committed",
        }
