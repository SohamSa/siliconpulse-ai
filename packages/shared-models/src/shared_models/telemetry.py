"""Telemetry event domain model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from shared_models.enums import WorkloadType


class TelemetryEvent(BaseModel):
    """Reported telemetry published to telemetry.raw."""

    event_id: str
    device_id: str
    timestamp: datetime
    ingestion_timestamp: datetime | None = None
    schema_version: str = "1.0.0"
    sequence_number: int = Field(ge=0)

    temperature_c: float
    ambient_temperature_c: float
    power_watts: float
    voltage: float
    utilization_pct: float = Field(ge=0, le=100)
    memory_utilization_pct: float = Field(ge=0, le=100)
    clock_speed_mhz: float
    fan_speed_rpm: float
    ecc_correctable_errors: int = Field(ge=0)
    ecc_uncorrectable_errors: int = Field(ge=0)
    network_latency_ms: float = Field(ge=0)
    throughput: float = Field(ge=0)
    workload_type: WorkloadType
    firmware_version: str
    sensor_quality: float = Field(ge=0, le=1)
    source: str = "telemetry-generator"
    simulation_scenario: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
