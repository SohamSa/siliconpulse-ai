"""Entry point for the telemetry generator service."""

from __future__ import annotations

import logging
import signal
import sys

import uvicorn

from telemetry_generator.api import create_app
from telemetry_generator.config import SimulatorSettings
from telemetry_generator.engine import SimulationEngine
from telemetry_generator.publisher import create_publisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("telemetry_generator")


def run() -> None:
    settings = SimulatorSettings()
    # Host producers use localhost:19092; in-compose use redpanda:9092 via env.
    publisher = create_publisher(
        brokers=settings.redpanda_brokers,
        enabled=settings.publish_enabled,
    )
    engine = SimulationEngine(settings, publisher)
    app = create_app(engine)

    def _shutdown(*_args: object) -> None:
        logger.info("Shutting down simulator")
        engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    engine.start()
    uvicorn.run(
        app,
        host=settings.control_host,
        port=settings.control_port,
        log_level="info",
    )


if __name__ == "__main__":
    run()
