"""Simulation engine: steps fleet physics and publishes telemetry.raw events."""

from __future__ import annotations

import logging
import random
import threading
import time
from datetime import UTC, datetime
from typing import Any

from shared_events.envelope import EventEnvelope
from shared_events.topics import TELEMETRY_RAW
from shared_models.enums import FailureScenario
from shared_models.telemetry import TelemetryEvent
from shared_utils.ids import new_id
from telemetry_generator.config import SimulatorSettings
from telemetry_generator.fleet import build_fleet, devices_in_rack
from telemetry_generator.physics import TrueDeviceState, step_device, to_reported_metrics
from telemetry_generator.publisher import TelemetryPublisher
from telemetry_generator.scenarios import (
    SCENARIO_DESCRIPTIONS,
    ActiveScenario,
    new_scenario,
)

logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self, settings: SimulatorSettings, publisher: TelemetryPublisher) -> None:
        self.settings = settings
        self.publisher = publisher
        self.rng = random.Random(settings.seed)
        self.devices, self.states = build_fleet(
            settings.device_count,
            settings.rack_count,
            seed=settings.seed,
            ambient_c=settings.ambient_temperature_c,
        )
        self._device_index = {d.device_id: d for d in self.devices}
        self._scenarios: dict[str, ActiveScenario] = {}
        self._device_scenario: dict[str, str] = {}
        self._lock = threading.RLock()
        self._running = False
        self._paused = False
        self._thread: threading.Thread | None = None
        self.events_generated = 0

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._paused = False
            self._thread = threading.Thread(target=self._loop, name="sim-loop", daemon=True)
            self._thread.start()
            logger.info(
                "Simulator started: devices=%s racks=%s seed=%s",
                self.settings.device_count,
                self.settings.rack_count,
                self.settings.seed,
            )

    def stop(self) -> None:
        with self._lock:
            self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self.publisher.close()

    def pause(self) -> None:
        with self._lock:
            self._paused = True

    def resume(self) -> None:
        with self._lock:
            self._paused = False

    def list_scenarios(self) -> list[dict[str, str]]:
        return [
            {"name": s.value, "description": SCENARIO_DESCRIPTIONS[s]}
            for s in FailureScenario
        ]

    def active_scenarios(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self._scenario_view(s) for s in self._scenarios.values() if not s.stopped]

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        with self._lock:
            s = self._scenarios.get(scenario_id)
            return self._scenario_view(s) if s else None

    def inject(
        self,
        scenario: FailureScenario,
        *,
        device_id: str | None = None,
        rack_id: str | None = None,
        severity: float = 0.5,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            if scenario == FailureScenario.RACK_COOLING_FAILURE:
                if not rack_id:
                    if device_id and device_id in self._device_index:
                        rack_id = self._device_index[device_id].rack_id
                    else:
                        raise ValueError("rack_id required for rack_cooling_failure")
                targets = devices_in_rack(self.devices, rack_id)
            else:
                target = device_id or self.settings.default_device_id
                if target not in self.states:
                    raise ValueError(f"Unknown device_id: {target}")
                targets = [target]
                rack_id = self._device_index[target].rack_id

            active = new_scenario(
                scenario,
                targets,
                severity=severity,
                rack_id=rack_id,
                metadata=metadata,
            )
            self._scenarios[active.scenario_id] = active
            for did in targets:
                self._device_scenario[did] = active.scenario_id
            logger.info(
                "Injected scenario %s id=%s devices=%s severity=%.2f",
                scenario.value,
                active.scenario_id,
                targets,
                severity,
            )
            return self._scenario_view(active)

    def stop_scenario(self, scenario_id: str) -> dict[str, Any]:
        with self._lock:
            s = self._scenarios.get(scenario_id)
            if not s:
                raise ValueError(f"Unknown scenario_id: {scenario_id}")
            s.stopped = True
            for did in s.device_ids:
                if self._device_scenario.get(did) == scenario_id:
                    self._device_scenario.pop(did, None)
            return self._scenario_view(s)

    def increase_severity(self, scenario_id: str, delta: float = 0.1) -> dict[str, Any]:
        with self._lock:
            s = self._get_active(scenario_id)
            s.severity = min(1.0, s.severity + delta)
            return self._scenario_view(s)

    def decrease_severity(self, scenario_id: str, delta: float = 0.1) -> dict[str, Any]:
        with self._lock:
            s = self._get_active(scenario_id)
            s.severity = max(0.0, s.severity - delta)
            return self._scenario_view(s)

    def reset_device(self, device_id: str) -> None:
        with self._lock:
            if device_id not in self.states:
                raise ValueError(f"Unknown device_id: {device_id}")
            sid = self._device_scenario.pop(device_id, None)
            if sid and sid in self._scenarios:
                sc = self._scenarios[sid]
                sc.device_ids = [d for d in sc.device_ids if d != device_id]
                if not sc.device_ids:
                    sc.stopped = True
            self._reset_state(self.states[device_id])

    def reset_fleet(self) -> None:
        with self._lock:
            self._scenarios.clear()
            self._device_scenario.clear()
            for state in self.states.values():
                self._reset_state(state)
            logger.info("Fleet reset to healthy baseline")

    def apply_recovery(self, device_id: str, severity: float = 0.8) -> dict[str, Any]:
        """Simulated approved intervention: inject recovery scenario."""
        return self.inject(
            FailureScenario.RECOVERY,
            device_id=device_id,
            severity=severity,
            metadata={"reason": "approved_intervention"},
        )

    def snapshot_device(self, device_id: str) -> dict[str, Any]:
        with self._lock:
            state = self.states.get(device_id)
            if not state:
                raise ValueError(f"Unknown device_id: {device_id}")
            reported = to_reported_metrics(state)
            return {
                "device_id": device_id,
                "true": {
                    "temperature_c": state.temperature_c,
                    "power_watts": state.power_watts,
                    "cooling_efficiency": state.cooling_efficiency,
                    "fan_efficiency": state.fan_efficiency,
                },
                "reported": reported,
                "active_scenario_id": self._device_scenario.get(device_id),
            }

    def tick_once(self) -> int:
        """Advance one emission cycle (useful for tests)."""
        return self._emit_cycle()

    def _loop(self) -> None:
        interval = max(self.settings.emit_interval_ms / 1000.0, 0.05)
        while self._running:
            started = time.perf_counter()
            if not self._paused:
                try:
                    self._emit_cycle()
                except Exception:
                    logger.exception("Simulation cycle failed")
            elapsed = time.perf_counter() - started
            # Speed multiplier shortens sleep (faster sim)
            sleep_for = max(interval / self.settings.speed_multiplier - elapsed, 0.0)
            time.sleep(sleep_for)

    def _emit_cycle(self) -> int:
        with self._lock:
            dt = (self.settings.emit_interval_ms / 1000.0) * self.settings.speed_multiplier
            count = 0
            now = datetime.now(UTC)
            for device_id, state in self.states.items():
                active = None
                sid = self._device_scenario.get(device_id)
                if sid:
                    active = self._scenarios.get(sid)
                    if active and not active.stopped:
                        active.bump_progress(dt, self.settings.speed_multiplier)
                    else:
                        active = None
                step_device(
                    state,
                    dt_seconds=dt,
                    ambient_c=self.settings.ambient_temperature_c,
                    rng=self.rng,
                    active=active,
                )
                event = self._build_event(device_id, state, now, active)
                envelope = EventEnvelope(
                    event_type="telemetry.raw",
                    source_service=self.settings.source_service,
                    correlation_id=event.event_id,
                    payload=event.model_dump(mode="json"),
                )
                self.publisher.publish(TELEMETRY_RAW, envelope, key=device_id)
                count += 1
            self.events_generated += count
            return count

    def _build_event(
        self,
        device_id: str,
        state: TrueDeviceState,
        now: datetime,
        active: ActiveScenario | None,
    ) -> TelemetryEvent:
        reported = to_reported_metrics(state)
        # Operational telemetry must NOT expose hidden scenario labels as root-cause evidence.
        # simulation_scenario is stored for demo/evaluation tooling only and must be stripped
        # before RCA in later phases.
        return TelemetryEvent(
            event_id=new_id(),
            device_id=device_id,
            timestamp=now,
            schema_version="1.0.0",
            sequence_number=int(reported["sequence_number"]),
            temperature_c=float(reported["temperature_c"]),
            ambient_temperature_c=float(reported["ambient_temperature_c"]),
            power_watts=float(reported["power_watts"]),
            voltage=float(reported["voltage"]),
            utilization_pct=float(reported["utilization_pct"]),
            memory_utilization_pct=float(reported["memory_utilization_pct"]),
            clock_speed_mhz=float(reported["clock_speed_mhz"]),
            fan_speed_rpm=float(reported["fan_speed_rpm"]),
            ecc_correctable_errors=int(reported["ecc_correctable_errors"]),
            ecc_uncorrectable_errors=int(reported["ecc_uncorrectable_errors"]),
            network_latency_ms=float(reported["network_latency_ms"]),
            throughput=float(reported["throughput"]),
            workload_type=state.workload_type,
            firmware_version=str(reported["firmware_version"]),
            sensor_quality=float(reported["sensor_quality"]),
            source=self.settings.source_service,
            simulation_scenario=active.scenario.value if active and not active.stopped else None,
            labels={
                "rack_id": state.rack_id,
                "model_name": state.model_name,
            },
            # Do not publish true internal state — keep it engine-local for evaluation APIs.
            metadata={},
        )

    def _reset_state(self, state: TrueDeviceState) -> None:
        state.cooling_efficiency = 1.0
        state.fan_efficiency = 1.0
        state.temp_sensor_bias_c = 0.0
        state.power_sensor_bias_w = 0.0
        state.sensor_quality = 1.0
        state.ecc_correctable_errors = 0
        state.ecc_uncorrectable_errors = 0
        state.network_latency_ms = 1.2
        state.temperature_c = self.settings.ambient_temperature_c + 32.0
        state.labels.pop("last_reset", None)

    def _get_active(self, scenario_id: str) -> ActiveScenario:
        s = self._scenarios.get(scenario_id)
        if not s or s.stopped:
            raise ValueError(f"Unknown or stopped scenario_id: {scenario_id}")
        return s

    @staticmethod
    def _scenario_view(s: ActiveScenario) -> dict[str, Any]:
        return {
            "scenario_id": s.scenario_id,
            "scenario": s.scenario.value,
            "device_ids": list(s.device_ids),
            "rack_id": s.rack_id,
            "severity": s.severity,
            "progress": s.progress,
            "stopped": s.stopped,
            "started_at": s.started_at.isoformat(),
            "metadata": dict(s.metadata),
        }

    def fleet_summary(self) -> dict[str, Any]:
        with self._lock:
            temps = [st.temperature_c for st in self.states.values()]
            return {
                "device_count": len(self.devices),
                "rack_count": self.settings.rack_count,
                "seed": self.settings.seed,
                "paused": self._paused,
                "running": self._running,
                "events_generated": self.events_generated,
                "active_scenarios": len([s for s in self._scenarios.values() if not s.stopped]),
                "avg_temperature_c": sum(temps) / len(temps) if temps else 0.0,
                "devices": [d.device_id for d in self.devices],
            }
