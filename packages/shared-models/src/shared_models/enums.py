"""Shared enumerations for SiliconPulse domain models."""

from __future__ import annotations

from enum import StrEnum


class DeviceType(StrEnum):
    GPU = "gpu"
    ACCELERATOR = "accelerator"
    SERVER = "server"
    HEALTHCARE_SENSOR = "healthcare_sensor"


class LifecycleStatus(StrEnum):
    HEALTHY = "healthy"
    STRESSED = "stressed"
    DEGRADED = "degraded"
    MAINTENANCE_RECOMMENDED = "maintenance_recommended"
    CRITICAL = "critical"
    RETIRED = "retired"


class OperationalStatus(StrEnum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    REBOOTING = "rebooting"


class WorkloadType(StrEnum):
    IDLE = "idle"
    INFERENCE = "inference"
    TRAINING = "training"
    MIXED = "mixed"
    BATCH = "batch"


class FailureScenario(StrEnum):
    NORMAL = "normal"
    HEAVY_WORKLOAD = "heavy_workload"
    IDLE = "idle"
    COOLING_DEGRADATION = "cooling_degradation"
    FAN_FAILURE = "fan_failure"
    MEMORY_DEGRADATION = "memory_degradation"
    VOLTAGE_INSTABILITY = "voltage_instability"
    FIRMWARE_REGRESSION = "firmware_regression"
    RACK_COOLING_FAILURE = "rack_cooling_failure"
    SENSOR_DRIFT = "sensor_drift"
    NETWORK_BOTTLENECK = "network_bottleneck"
    CASCADING_WORKLOAD_OVERLOAD = "cascading_workload_overload"
    INTERMITTENT_DEVICE_RESET = "intermittent_device_reset"
    RECOVERY = "recovery"
