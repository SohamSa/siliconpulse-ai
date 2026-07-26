"""GPU fleet simulator — stdlib only. Publishes into an in-process event bus."""

from __future__ import annotations

import math
import random
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def gpu_id(i: int) -> str:
    return f"GPU-{i:03d}"


def rack_id(i: int) -> str:
    return f"RACK-{i:02d}"


MODELS = {
    "SP-H100-80G": {"tdp": 700.0, "base_clock": 1410.0, "idle": 70.0, "max_tps": 400.0},
    "SP-A100-40G": {"tdp": 400.0, "base_clock": 1410.0, "idle": 50.0, "max_tps": 250.0},
    "SP-L40S": {"tdp": 350.0, "base_clock": 2520.0, "idle": 40.0, "max_tps": 220.0},
}

SCENARIOS = {
    "normal": "Nominal fleet operation",
    "heavy_workload": "Sustained high utilization",
    "idle": "Low utilization idle state",
    "cooling_degradation": "Gradual loss of cooling effectiveness",
    "fan_failure": "Fan collapse and thermal rise",
    "memory_degradation": "Rising ECC errors",
    "voltage_instability": "Voltage / power instability",
    "firmware_regression": "Firmware-induced errors",
    "rack_cooling_failure": "Shared rack cooling impact",
    "sensor_drift": "Reported sensors diverge from truth",
    "network_bottleneck": "Latency spike cutting throughput",
    "cascading_workload_overload": "Neighbor overload spillover",
    "intermittent_device_reset": "Brief reboot events",
    "recovery": "Post-intervention stabilization",
}


@dataclass
class DeviceState:
    device_id: str
    rack_id: str
    server_id: str
    model_name: str
    firmware_version: str
    batch: str
    age_hours: float
    utilization: float = 55.0
    memory_util: float = 40.0
    power_w: float = 220.0
    voltage: float = 12.0
    temp_c: float = 58.0
    ambient_c: float = 22.0
    fan_rpm: float = 3200.0
    fan_eff: float = 1.0
    cooling_eff: float = 1.0
    clock_mhz: float = 1410.0
    throughput: float = 180.0
    latency_ms: float = 1.2
    ecc_c: int = 0
    ecc_u: int = 0
    sensor_quality: float = 1.0
    workload: str = "inference"
    seq: int = 0
    temp_bias: float = 0.0
    power_bias: float = 0.0
    # Intelligence fields (updated by platform)
    anomaly_score: float = 0.0
    failure_prob: float = 0.05
    failure_type: str = "normal"
    rul_hours: float = 720.0
    health_score: float = 92.0
    lifecycle: str = "healthy"
    twin_expected_temp: float = 58.0
    twin_deviation: float = 0.0
    twin_confidence: float = 0.85


@dataclass
class ActiveScenario:
    scenario_id: str
    scenario: str
    device_ids: list[str]
    rack_id: str | None
    severity: float
    progress: float = 0.0
    stopped: bool = False
    started_at: str = field(default_factory=lambda: utcnow().isoformat())


class Simulator:
    def __init__(
        self,
        device_count: int = 50,
        rack_count: int = 5,
        seed: int = 42,
        interval_s: float = 1.0,
        on_telemetry: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.device_count = device_count
        self.rack_count = rack_count
        self.seed = seed
        self.interval_s = interval_s
        self.on_telemetry = on_telemetry
        self.rng = random.Random(seed)
        self.devices: dict[str, DeviceState] = {}
        self.scenarios: dict[str, ActiveScenario] = {}
        self.device_scenario: dict[str, str] = {}
        self._lock = threading.RLock()
        self._running = False
        self._paused = False
        self._thread: threading.Thread | None = None
        self.events_generated = 0
        self._build_fleet()

    def _build_fleet(self) -> None:
        models = list(MODELS)
        firmwares = ["1.8.2", "2.1.0", "2.3.1", "2.4.0"]
        batches = ["BATCH-2023-A", "BATCH-2024-B", "BATCH-2024-C", "BATCH-2025-A"]
        for i in range(1, self.device_count + 1):
            did = gpu_id(i)
            ridx = ((i - 1) % self.rack_count) + 1
            rid = rack_id(ridx)
            slot = ((i - 1) // self.rack_count) + 1
            model = models[(i - 1) % len(models)]
            profile = MODELS[model]
            self.devices[did] = DeviceState(
                device_id=did,
                rack_id=rid,
                server_id=f"{rid}-SRV-{slot:02d}",
                model_name=model,
                firmware_version=firmwares[(i + self.seed) % len(firmwares)],
                batch=batches[(i + self.seed) % len(batches)],
                age_hours=float(self.rng.randint(500, 12000)),
                utilization=self.rng.uniform(40, 70),
                power_w=profile["idle"] + self.rng.uniform(80, 180),
                temp_c=22 + self.rng.uniform(28, 40),
                clock_mhz=profile["base_clock"],
            )

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._paused = False
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def _loop(self) -> None:
        while self._running:
            t0 = time.perf_counter()
            if not self._paused:
                try:
                    self.tick()
                except Exception:
                    pass
            sleep = max(self.interval_s - (time.perf_counter() - t0), 0.05)
            time.sleep(sleep)

    def tick(self) -> int:
        with self._lock:
            n = 0
            for did, st in self.devices.items():
                active = None
                sid = self.device_scenario.get(did)
                if sid:
                    active = self.scenarios.get(sid)
                    if active and not active.stopped:
                        # Progress reaches ~0.6 within ~25 ticks so demos show twin/anomaly quickly
                        active.progress = min(1.0, active.progress + 0.025 * max(active.severity, 0.15))
                    else:
                        active = None
                self._step(st, active)
                evt = self._event(st, active)
                self.events_generated += 1
                n += 1
                if self.on_telemetry:
                    self.on_telemetry(evt)
            return n

    def _step(self, st: DeviceState, active: ActiveScenario | None) -> None:
        profile = MODELS[st.model_name]
        scenario = active.scenario if active and not active.stopped else "normal"
        severity = (active.severity * active.progress) if active and not active.stopped else 0.0
        ambient = 22.0

        if scenario == "idle":
            st.workload = "idle"
            target_util = self.rng.uniform(3, 12)
        elif scenario in {"heavy_workload", "cascading_workload_overload"}:
            st.workload = "training"
            target_util = self.rng.uniform(88, 98)
        else:
            st.workload = "inference"
            target_util = self.rng.uniform(45, 75)
        st.utilization += (target_util - st.utilization) * 0.25
        st.utilization = max(0, min(100, st.utilization))
        st.memory_util = max(5, min(98, st.utilization * 0.75 + self.rng.uniform(-5, 5)))

        if scenario == "cooling_degradation":
            st.cooling_eff = max(0.35, 1.0 - 0.55 * severity)
        elif scenario == "fan_failure":
            st.fan_eff = max(0.05, 1.0 - 0.9 * severity)
        elif scenario == "rack_cooling_failure":
            ambient = 22.0 + 8.0 * severity
            st.cooling_eff = max(0.45, 1.0 - 0.35 * severity)
        elif scenario == "recovery":
            st.cooling_eff += (1.0 - st.cooling_eff) * 0.18
            st.fan_eff += (1.0 - st.fan_eff) * 0.18
            st.temp_bias *= 0.85
            st.power_bias *= 0.85

        if scenario == "sensor_drift":
            st.temp_bias = 6.0 * severity
            st.power_bias = 40.0 * severity
            st.sensor_quality = max(0.3, 1.0 - 0.5 * severity)
        else:
            st.sensor_quality = min(1.0, st.sensor_quality + 0.02)

        util = st.utilization / 100.0
        target_power = profile["idle"] + (profile["tdp"] - profile["idle"]) * (0.85 * util + 0.15 * util * util)
        if scenario == "voltage_instability":
            target_power *= 1.0 + 0.12 * severity * math.sin(st.seq / 3.0)
            st.voltage = 12.0 + self.rng.uniform(-0.8, 0.8) * severity
        else:
            st.voltage = 12.0 + self.rng.uniform(-0.05, 0.05)
        st.power_w += (target_power - st.power_w) * 0.35
        st.power_w = max(profile["idle"] * 0.8, min(profile["tdp"] * 1.05, st.power_w))

        st.ambient_c = ambient
        cooling = st.cooling_eff * st.fan_eff
        dt = self.interval_s
        heat_in = 0.045 * st.power_w * dt
        heat_out = (0.08 + 0.22 * cooling) * max(st.temp_c - ambient, 0) * dt
        st.temp_c += heat_in - heat_out + self.rng.uniform(-0.05, 0.05)
        st.temp_c = max(ambient + 5, min(105, st.temp_c))

        target_fan = (1800 + (st.temp_c - 40) * 55) * st.fan_eff
        if scenario == "fan_failure":
            target_fan *= max(0.05, 1.0 - 0.95 * severity)
        st.fan_rpm += (target_fan - st.fan_rpm) * 0.4
        st.fan_rpm = max(0, min(7500, st.fan_rpm))

        throttle = 0.0
        if st.temp_c > 85:
            throttle = min(0.55, (st.temp_c - 85) / 15)
        st.clock_mhz = profile["base_clock"] * (1.0 - throttle)

        if scenario == "network_bottleneck":
            st.latency_ms = 1.2 + 40 * severity + self.rng.uniform(0, 5)
        else:
            st.latency_ms = max(0.4, 1.0 + self.rng.uniform(0, 0.8))
        net_penalty = 1.0 / (1.0 + max(st.latency_ms - 2.0, 0) / 20.0)
        st.throughput = (
            profile["max_tps"] * util * (st.clock_mhz / profile["base_clock"]) * net_penalty * self.rng.uniform(0.97, 1.03)
        )

        if scenario == "memory_degradation":
            if self.rng.random() < 0.35 * severity:
                st.ecc_c += self.rng.randint(1, max(1, int(5 * severity)))
            if severity > 0.7 and self.rng.random() < 0.05 * severity:
                st.ecc_u += 1
        elif scenario == "firmware_regression":
            if self.rng.random() < 0.2 * severity:
                st.ecc_c += 1
            st.clock_mhz *= 1.0 - 0.1 * severity

        if scenario == "intermittent_device_reset" and severity > 0.3 and self.rng.random() < 0.03 * severity:
            st.utilization = 0
            st.throughput = 0

        st.age_hours += dt / 3600
        st.seq += 1

    def _event(self, st: DeviceState, active: ActiveScenario | None) -> dict[str, Any]:
        return {
            "event_id": str(uuid.uuid4()),
            "event_type": "telemetry.raw",
            "schema_version": "1.0.0",
            "created_at": utcnow().isoformat(),
            "source_service": "telemetry-generator",
            "device_id": st.device_id,
            "timestamp": utcnow().isoformat(),
            "sequence_number": st.seq,
            "temperature_c": st.temp_c + st.temp_bias,
            "ambient_temperature_c": st.ambient_c,
            "power_watts": st.power_w + st.power_bias,
            "voltage": st.voltage,
            "utilization_pct": st.utilization,
            "memory_utilization_pct": st.memory_util,
            "clock_speed_mhz": st.clock_mhz,
            "fan_speed_rpm": st.fan_rpm,
            "ecc_correctable_errors": st.ecc_c,
            "ecc_uncorrectable_errors": st.ecc_u,
            "network_latency_ms": st.latency_ms,
            "throughput": st.throughput,
            "workload_type": st.workload,
            "firmware_version": st.firmware_version,
            "sensor_quality": st.sensor_quality,
            "rack_id": st.rack_id,
            "model_name": st.model_name,
            # Hidden from RCA path — evaluation only
            "_sim_scenario": active.scenario if active and not active.stopped else None,
        }

    def inject(
        self,
        scenario: str,
        device_id: str | None = None,
        rack_id: str | None = None,
        severity: float = 0.7,
    ) -> dict[str, Any]:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")
        with self._lock:
            if scenario == "rack_cooling_failure":
                if not rack_id:
                    if not device_id or device_id not in self.devices:
                        raise ValueError("rack_id or device_id required")
                    rack_id = self.devices[device_id].rack_id
                targets = [d for d, st in self.devices.items() if st.rack_id == rack_id]
            else:
                device_id = device_id or "GPU-042"
                if device_id not in self.devices:
                    raise ValueError(f"Unknown device: {device_id}")
                targets = [device_id]
                rack_id = self.devices[device_id].rack_id
            sc = ActiveScenario(
                scenario_id=str(uuid.uuid4()),
                scenario=scenario,
                device_ids=targets,
                rack_id=rack_id,
                severity=max(0, min(1, severity)),
            )
            self.scenarios[sc.scenario_id] = sc
            for did in targets:
                self.device_scenario[did] = sc.scenario_id
            return self._scenario_view(sc)

    def stop_scenario(self, scenario_id: str) -> dict[str, Any]:
        with self._lock:
            sc = self.scenarios.get(scenario_id)
            if not sc:
                raise ValueError("scenario not found")
            sc.stopped = True
            for did in sc.device_ids:
                if self.device_scenario.get(did) == scenario_id:
                    del self.device_scenario[did]
            return self._scenario_view(sc)

    def reset_fleet(self) -> None:
        with self._lock:
            self.scenarios.clear()
            self.device_scenario.clear()
            for st in self.devices.values():
                st.cooling_eff = 1.0
                st.fan_eff = 1.0
                st.temp_bias = 0.0
                st.power_bias = 0.0
                st.sensor_quality = 1.0
                st.ecc_c = 0
                st.ecc_u = 0
                st.temp_c = 22 + 32
                st.anomaly_score = 0.05
                st.failure_prob = 0.05
                st.failure_type = "normal"
                st.rul_hours = 720
                st.health_score = 92
                st.lifecycle = "healthy"
                st.twin_deviation = 0.0

    def apply_recovery(self, device_id: str) -> dict[str, Any]:
        return self.inject("recovery", device_id=device_id, severity=0.9)

    def _scenario_view(self, sc: ActiveScenario) -> dict[str, Any]:
        return {
            "scenario_id": sc.scenario_id,
            "scenario": sc.scenario,
            "device_ids": list(sc.device_ids),
            "rack_id": sc.rack_id,
            "severity": sc.severity,
            "progress": sc.progress,
            "stopped": sc.stopped,
            "started_at": sc.started_at,
            "description": SCENARIOS.get(sc.scenario, ""),
        }

    def fleet_summary(self) -> dict[str, Any]:
        with self._lock:
            temps = [d.temp_c for d in self.devices.values()]
            utils = [d.utilization for d in self.devices.values()]
            critical = sum(1 for d in self.devices.values() if d.lifecycle == "critical")
            warn = sum(1 for d in self.devices.values() if d.lifecycle in {"stressed", "degraded", "maintenance_recommended"})
            healthy = self.device_count - critical - warn
            riskiest = max(self.devices.values(), key=lambda d: d.failure_prob)
            return {
                "device_count": self.device_count,
                "rack_count": self.rack_count,
                "healthy": healthy,
                "warning": warn,
                "critical": critical,
                "avg_temperature_c": sum(temps) / len(temps),
                "avg_utilization_pct": sum(utils) / len(utils),
                "events_generated": self.events_generated,
                "active_scenarios": len([s for s in self.scenarios.values() if not s.stopped]),
                "highest_risk_device": riskiest.device_id,
                "highest_risk_prob": riskiest.failure_prob,
                "paused": self._paused,
                "running": self._running,
            }
