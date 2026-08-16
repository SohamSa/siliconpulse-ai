"""Failure scenario definitions and active scenario state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from shared_models.enums import FailureScenario


@dataclass
class ActiveScenario:
    scenario_id: str
    scenario: FailureScenario
    device_ids: list[str]
    rack_id: str | None
    severity: float  # 0.0 – 1.0
    started_at: datetime
    progress: float = 0.0
    stopped: bool = False
    metadata: dict[str, str] = field(default_factory=dict)

    def bump_progress(self, dt_seconds: float, speed: float) -> None:
        if self.stopped or self.scenario in {FailureScenario.NORMAL, FailureScenario.IDLE}:
            return
        # Interactive scenarios reach full progression in roughly 11 simulated
        # seconds at severity 1.0. The prior minute-scale rate made the public
        # demo and deterministic scenario tests appear almost unchanged.
        rate = 0.09 * max(self.severity, 0.05) * speed
        self.progress = min(1.0, self.progress + rate * dt_seconds)


def new_scenario(
    scenario: FailureScenario,
    device_ids: list[str],
    *,
    severity: float = 0.5,
    rack_id: str | None = None,
    metadata: dict[str, str] | None = None,
) -> ActiveScenario:
    return ActiveScenario(
        scenario_id=str(uuid4()),
        scenario=scenario,
        device_ids=list(device_ids),
        rack_id=rack_id,
        severity=max(0.0, min(1.0, severity)),
        started_at=datetime.now(UTC),
        metadata=metadata or {},
    )


SCENARIO_DESCRIPTIONS: dict[FailureScenario, str] = {
    FailureScenario.NORMAL: "Nominal fleet operation",
    FailureScenario.HEAVY_WORKLOAD: "Sustained high utilization and power",
    FailureScenario.IDLE: "Low utilization idle state",
    FailureScenario.COOLING_DEGRADATION: "Gradual loss of cooling effectiveness",
    FailureScenario.FAN_FAILURE: "Fan speed collapse and thermal rise",
    FailureScenario.MEMORY_DEGRADATION: "Rising ECC correctable/uncorrectable errors",
    FailureScenario.VOLTAGE_INSTABILITY: "Voltage variance and power instability",
    FailureScenario.FIRMWARE_REGRESSION: "Firmware-induced error and clock issues",
    FailureScenario.RACK_COOLING_FAILURE: "Shared rack ambient / cooling impact",
    FailureScenario.SENSOR_DRIFT: "Reported sensors diverge from true state",
    FailureScenario.NETWORK_BOTTLENECK: "Latency spike reducing effective throughput",
    FailureScenario.CASCADING_WORKLOAD_OVERLOAD: "Neighbor overload spillover",
    FailureScenario.INTERMITTENT_DEVICE_RESET: "Brief offline/reboot events",
    FailureScenario.RECOVERY: "Post-intervention stabilization",
}
