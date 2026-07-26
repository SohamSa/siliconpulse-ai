"""SiliconPulse shared domain models."""

from shared_models.device import Device
from shared_models.enums import (
    DeviceType,
    FailureScenario,
    LifecycleStatus,
    OperationalStatus,
    WorkloadType,
)
from shared_models.telemetry import TelemetryEvent

__version__ = "0.1.0"

__all__ = [
    "Device",
    "DeviceType",
    "FailureScenario",
    "LifecycleStatus",
    "OperationalStatus",
    "TelemetryEvent",
    "WorkloadType",
    "__version__",
]
