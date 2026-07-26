"""Simulator configuration."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SimulatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    device_count: int = Field(default=50, alias="SIM_DEVICE_COUNT", ge=1)
    rack_count: int = Field(default=5, alias="SIM_RACK_COUNT", ge=1)
    emit_interval_ms: int = Field(default=1000, alias="SIM_EMIT_INTERVAL_MS", ge=50)
    seed: int = Field(default=42, alias="SIM_SEED")
    speed_multiplier: float = Field(default=1.0, alias="SIM_SPEED_MULTIPLIER", gt=0)
    default_device_id: str = Field(default="GPU-042", alias="SIM_DEFAULT_DEVICE_ID")

    redpanda_brokers: str = Field(default="localhost:19092", alias="REDPANDA_BROKERS")
    telemetry_topic: str = Field(default="telemetry.raw")
    publish_enabled: bool = Field(default=True, alias="SIM_PUBLISH_ENABLED")

    control_host: str = Field(default="0.0.0.0", alias="SIM_CONTROL_HOST")
    control_port: int = Field(default=8100, alias="SIM_CONTROL_PORT")

    ambient_temperature_c: float = Field(default=22.0, alias="SIM_AMBIENT_C")
    source_service: str = "telemetry-generator"
