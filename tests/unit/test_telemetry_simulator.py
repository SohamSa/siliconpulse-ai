"""Unit tests for the telemetry simulator (no Redpanda required)."""

from __future__ import annotations

import pytest

from shared_models.enums import FailureScenario
from telemetry_generator.config import SimulatorSettings
from telemetry_generator.engine import SimulationEngine
from telemetry_generator.publisher import InMemoryPublisher


@pytest.fixture
def engine() -> SimulationEngine:
    settings = SimulatorSettings(
        device_count=50,
        rack_count=5,
        seed=42,
        emit_interval_ms=200,
        publish_enabled=False,
        redpanda_brokers="localhost:19092",
    )
    return SimulationEngine(settings, InMemoryPublisher())


@pytest.mark.unit
def test_fleet_has_at_least_50_devices(engine: SimulationEngine) -> None:
    assert len(engine.devices) == 50
    assert engine.settings.rack_count == 5
    assert "GPU-042" in engine.states


@pytest.mark.unit
def test_deterministic_seed_produces_stable_first_tick() -> None:
    def once() -> float:
        settings = SimulatorSettings(
            device_count=10,
            rack_count=2,
            seed=7,
            publish_enabled=False,
        )
        eng = SimulationEngine(settings, InMemoryPublisher())
        eng.tick_once()
        return eng.states["GPU-001"].temperature_c

    assert once() == pytest.approx(once(), rel=0, abs=1e-9)


@pytest.mark.unit
def test_valid_telemetry_ranges_and_schema(engine: SimulationEngine) -> None:
    pub = engine.publisher
    assert isinstance(pub, InMemoryPublisher)
    engine.tick_once()
    assert len(pub.messages) == 50
    topic, envelope, key = pub.messages[0]
    assert topic == "telemetry.raw"
    assert key is not None
    assert envelope.event_type == "telemetry.raw"
    assert envelope.source_service == "telemetry-generator"
    payload = envelope.payload
    assert 0 <= payload["utilization_pct"] <= 100
    assert payload["temperature_c"] > 0
    assert payload["power_watts"] > 0
    assert payload["fan_speed_rpm"] >= 0
    assert payload["schema_version"] == "1.0.0"


@pytest.mark.unit
def test_cooling_degradation_raises_temperature_before_critical(engine: SimulationEngine) -> None:
    baseline = engine.states["GPU-042"].temperature_c
    engine.inject(FailureScenario.COOLING_DEGRADATION, device_id="GPU-042", severity=0.8)
    for _ in range(40):
        engine.tick_once()
    degraded = engine.states["GPU-042"].temperature_c
    assert degraded > baseline + 2.0
    # Early stage should still be below a typical critical static threshold
    assert degraded < 95.0
    assert engine.states["GPU-042"].cooling_efficiency < 0.95


@pytest.mark.unit
def test_sensor_drift_separates_true_and_reported(engine: SimulationEngine) -> None:
    engine.inject(FailureScenario.SENSOR_DRIFT, device_id="GPU-010", severity=1.0)
    for _ in range(20):
        engine.tick_once()
    snap = engine.snapshot_device("GPU-010")
    assert snap["reported"]["temperature_c"] > snap["true"]["temperature_c"] + 2.0


@pytest.mark.unit
def test_recovery_improves_cooling_efficiency(engine: SimulationEngine) -> None:
    engine.inject(FailureScenario.COOLING_DEGRADATION, device_id="GPU-042", severity=1.0)
    for _ in range(30):
        engine.tick_once()
    bad = engine.states["GPU-042"].cooling_efficiency
    engine.apply_recovery("GPU-042", severity=1.0)
    for _ in range(20):
        engine.tick_once()
    recovered = engine.states["GPU-042"].cooling_efficiency
    assert recovered > bad


@pytest.mark.unit
def test_reset_fleet_clears_scenarios(engine: SimulationEngine) -> None:
    engine.inject(FailureScenario.FAN_FAILURE, device_id="GPU-003", severity=0.7)
    engine.reset_fleet()
    assert engine.active_scenarios() == []
    assert engine.states["GPU-003"].fan_efficiency == 1.0


@pytest.mark.unit
def test_correlations_power_and_temperature(engine: SimulationEngine) -> None:
    """Higher utilization should generally increase power."""
    state = engine.states["GPU-001"]
    state.utilization_pct = 20.0
    for _ in range(5):
        engine.tick_once()
    low_power = state.power_watts
    state.utilization_pct = 95.0
    for _ in range(5):
        engine.tick_once()
    high_power = state.power_watts
    assert high_power > low_power
