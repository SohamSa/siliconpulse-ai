"""GPU telemetry physics with true internal state vs reported sensors."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from shared_models.enums import FailureScenario, WorkloadType
from telemetry_generator.scenarios import ActiveScenario


@dataclass
class TrueDeviceState:
    """Internal simulated truth — not published directly."""

    device_id: str
    rack_id: str
    model_name: str
    firmware_version: str
    age_hours: float
    utilization_pct: float = 55.0
    memory_utilization_pct: float = 40.0
    power_watts: float = 220.0
    voltage: float = 12.0
    temperature_c: float = 58.0
    ambient_temperature_c: float = 22.0
    fan_speed_rpm: float = 3200.0
    fan_efficiency: float = 1.0
    cooling_efficiency: float = 1.0
    clock_speed_mhz: float = 1410.0
    base_clock_mhz: float = 1410.0
    throughput: float = 180.0
    network_latency_ms: float = 1.2
    ecc_correctable_errors: int = 0
    ecc_uncorrectable_errors: int = 0
    sensor_quality: float = 1.0
    workload_type: WorkloadType = WorkloadType.INFERENCE
    sequence_number: int = 0
    # Sensor bias for drift scenarios (reported = true + bias * scale)
    temp_sensor_bias_c: float = 0.0
    power_sensor_bias_w: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)


MODEL_PROFILES: dict[str, dict[str, float]] = {
    "SP-H100-80G": {"tdp": 700.0, "base_clock": 1410.0, "idle_power": 70.0, "max_throughput": 400.0},
    "SP-A100-40G": {"tdp": 400.0, "base_clock": 1410.0, "idle_power": 50.0, "max_throughput": 250.0},
    "SP-L40S": {"tdp": 350.0, "base_clock": 2520.0, "idle_power": 40.0, "max_throughput": 220.0},
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def apply_workload_target(state: TrueDeviceState, scenario: FailureScenario | None, rng: random.Random) -> None:
    if scenario == FailureScenario.IDLE:
        state.workload_type = WorkloadType.IDLE
        target_util = rng.uniform(3.0, 12.0)
    elif scenario in {
        FailureScenario.HEAVY_WORKLOAD,
        FailureScenario.CASCADING_WORKLOAD_OVERLOAD,
    }:
        state.workload_type = WorkloadType.TRAINING
        target_util = rng.uniform(88.0, 98.0)
    else:
        state.workload_type = WorkloadType.INFERENCE
        target_util = rng.uniform(45.0, 75.0)
    state.utilization_pct += (target_util - state.utilization_pct) * 0.25
    state.utilization_pct = _clamp(state.utilization_pct, 0.0, 100.0)
    state.memory_utilization_pct = _clamp(
        state.utilization_pct * 0.75 + rng.uniform(-5.0, 5.0),
        5.0,
        98.0,
    )


def step_device(
    state: TrueDeviceState,
    *,
    dt_seconds: float,
    ambient_c: float,
    rng: random.Random,
    active: ActiveScenario | None,
) -> None:
    """Advance true internal state by one simulation tick."""
    profile = MODEL_PROFILES.get(state.model_name, MODEL_PROFILES["SP-A100-40G"])
    scenario = active.scenario if active and not active.stopped else FailureScenario.NORMAL
    severity = (active.severity * active.progress) if active and not active.stopped else 0.0

    apply_workload_target(state, scenario if active else None, rng)

    # Scenario modifiers on true physics
    if scenario == FailureScenario.COOLING_DEGRADATION:
        state.cooling_efficiency = _clamp(1.0 - 0.55 * severity, 0.35, 1.0)
    elif scenario == FailureScenario.FAN_FAILURE:
        state.fan_efficiency = _clamp(1.0 - 0.9 * severity, 0.05, 1.0)
    elif scenario == FailureScenario.RACK_COOLING_FAILURE:
        ambient_c = ambient_c + 8.0 * severity
        state.cooling_efficiency = _clamp(1.0 - 0.35 * severity, 0.45, 1.0)
    elif scenario == FailureScenario.RECOVERY:
        state.cooling_efficiency += (1.0 - state.cooling_efficiency) * 0.15
        state.fan_efficiency += (1.0 - state.fan_efficiency) * 0.15
        state.temp_sensor_bias_c *= 0.85
        state.power_sensor_bias_w *= 0.85

    if scenario == FailureScenario.SENSOR_DRIFT:
        state.temp_sensor_bias_c = 6.0 * severity
        state.power_sensor_bias_w = 40.0 * severity
        state.sensor_quality = _clamp(1.0 - 0.5 * severity, 0.3, 1.0)
    else:
        state.sensor_quality = _clamp(state.sensor_quality + 0.02, 0.3, 1.0)

    idle = profile["idle_power"]
    tdp = profile["tdp"]
    util = state.utilization_pct / 100.0
    target_power = idle + (tdp - idle) * (0.85 * util + 0.15 * util**2)
    if scenario == FailureScenario.VOLTAGE_INSTABILITY:
        target_power *= 1.0 + 0.12 * severity * math.sin(state.sequence_number / 3.0)
        state.voltage = 12.0 + rng.uniform(-0.8, 0.8) * severity
    else:
        state.voltage = 12.0 + rng.uniform(-0.05, 0.05)

    state.power_watts += (target_power - state.power_watts) * 0.35
    state.power_watts = _clamp(state.power_watts, idle * 0.8, tdp * 1.05)

    # Thermal model: power heats, cooling + fans remove heat
    state.ambient_temperature_c = ambient_c
    cooling = state.cooling_efficiency * state.fan_efficiency
    heat_in = 0.045 * state.power_watts * dt_seconds
    heat_out = (0.08 + 0.22 * cooling) * max(state.temperature_c - ambient_c, 0.0) * dt_seconds
    state.temperature_c += heat_in - heat_out + rng.uniform(-0.05, 0.05)
    state.temperature_c = _clamp(state.temperature_c, ambient_c + 5.0, 105.0)

    # Fan responds to temperature
    target_fan = 1800.0 + (state.temperature_c - 40.0) * 55.0
    target_fan *= state.fan_efficiency
    if scenario == FailureScenario.FAN_FAILURE:
        target_fan *= max(0.05, 1.0 - 0.95 * severity)
    state.fan_speed_rpm += (target_fan - state.fan_speed_rpm) * 0.4
    state.fan_speed_rpm = _clamp(state.fan_speed_rpm, 0.0, 7500.0)

    # Thermal throttling
    throttle = 0.0
    if state.temperature_c > 85.0:
        throttle = _clamp((state.temperature_c - 85.0) / 15.0, 0.0, 0.55)
    state.clock_speed_mhz = profile["base_clock"] * (1.0 - throttle)
    state.base_clock_mhz = profile["base_clock"]

    # Throughput from util, clock, and network
    if scenario == FailureScenario.NETWORK_BOTTLENECK:
        state.network_latency_ms = 1.2 + 40.0 * severity + rng.uniform(0, 5)
    else:
        state.network_latency_ms = _clamp(1.0 + rng.uniform(0, 0.8), 0.4, 80.0)

    net_penalty = 1.0 / (1.0 + max(state.network_latency_ms - 2.0, 0.0) / 20.0)
    state.throughput = (
        profile["max_throughput"]
        * util
        * (state.clock_speed_mhz / profile["base_clock"])
        * net_penalty
        * rng.uniform(0.97, 1.03)
    )

    # Memory errors
    if scenario == FailureScenario.MEMORY_DEGRADATION:
        if rng.random() < 0.35 * severity:
            state.ecc_correctable_errors += rng.randint(1, max(1, int(5 * severity)))
        if severity > 0.7 and rng.random() < 0.05 * severity:
            state.ecc_uncorrectable_errors += 1
    elif scenario == FailureScenario.FIRMWARE_REGRESSION:
        if rng.random() < 0.2 * severity:
            state.ecc_correctable_errors += 1
        state.clock_speed_mhz *= 1.0 - 0.1 * severity

    if scenario == FailureScenario.INTERMITTENT_DEVICE_RESET and severity > 0.3:
        if rng.random() < 0.03 * severity:
            state.labels["last_reset"] = "true"
            state.utilization_pct = 0.0
            state.throughput = 0.0
        else:
            state.labels.pop("last_reset", None)

    state.age_hours += dt_seconds / 3600.0
    state.sequence_number += 1


def to_reported_metrics(state: TrueDeviceState) -> dict[str, float | int | str]:
    """Map true state to reported sensor readings."""
    return {
        "temperature_c": state.temperature_c + state.temp_sensor_bias_c,
        "ambient_temperature_c": state.ambient_temperature_c,
        "power_watts": state.power_watts + state.power_sensor_bias_w,
        "voltage": state.voltage,
        "utilization_pct": state.utilization_pct,
        "memory_utilization_pct": state.memory_utilization_pct,
        "clock_speed_mhz": state.clock_speed_mhz,
        "fan_speed_rpm": state.fan_speed_rpm,
        "ecc_correctable_errors": state.ecc_correctable_errors,
        "ecc_uncorrectable_errors": state.ecc_uncorrectable_errors,
        "network_latency_ms": state.network_latency_ms,
        "throughput": state.throughput,
        "sensor_quality": state.sensor_quality,
        "firmware_version": state.firmware_version,
        "workload_type": state.workload_type.value,
        "sequence_number": state.sequence_number,
    }
