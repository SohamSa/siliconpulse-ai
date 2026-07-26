"""Publish telemetry envelopes to Redpanda (or an in-memory sink for tests)."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from shared_events.envelope import EventEnvelope

logger = logging.getLogger(__name__)


class TelemetryPublisher(ABC):
    @abstractmethod
    def publish(self, topic: str, envelope: EventEnvelope, *, key: str | None = None) -> None:
        raise NotImplementedError

    def close(self) -> None:
        return None


class InMemoryPublisher(TelemetryPublisher):
    """Test/dev publisher that stores messages in memory."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, EventEnvelope, str | None]] = []

    def publish(self, topic: str, envelope: EventEnvelope, *, key: str | None = None) -> None:
        self.messages.append((topic, envelope, key))


class KafkaTelemetryPublisher(TelemetryPublisher):
    """Kafka-compatible publisher for Redpanda."""

    def __init__(self, brokers: str) -> None:
        from kafka import KafkaProducer  # type: ignore[import-untyped]

        self._producer = KafkaProducer(
            bootstrap_servers=[b.strip() for b in brokers.split(",") if b.strip()],
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            linger_ms=20,
        )

    def publish(self, topic: str, envelope: EventEnvelope, *, key: str | None = None) -> None:
        payload: dict[str, Any] = envelope.model_dump(mode="json")
        future = self._producer.send(topic, value=payload, key=key)
        future.get(timeout=10)

    def close(self) -> None:
        self._producer.flush(timeout=10)
        self._producer.close()


def create_publisher(*, brokers: str, enabled: bool) -> TelemetryPublisher:
    if not enabled:
        logger.warning("Publish disabled — using in-memory publisher")
        return InMemoryPublisher()
    try:
        return KafkaTelemetryPublisher(brokers)
    except Exception:
        logger.exception("Failed to create Kafka publisher for %s; falling back to in-memory", brokers)
        return InMemoryPublisher()
