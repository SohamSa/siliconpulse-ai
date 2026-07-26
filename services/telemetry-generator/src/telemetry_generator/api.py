"""HTTP control plane for scenario injection and simulator lifecycle."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shared_models.enums import FailureScenario
from telemetry_generator.engine import SimulationEngine


class InjectRequest(BaseModel):
    scenario: FailureScenario
    device_id: str | None = None
    rack_id: str | None = None
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict[str, str] = Field(default_factory=dict)


class SeverityRequest(BaseModel):
    delta: float = Field(default=0.1, gt=0.0, le=1.0)


def create_app(engine: SimulationEngine) -> FastAPI:
    app = FastAPI(
        title="SiliconPulse Telemetry Generator",
        version="0.1.0",
        description="Control API for the local GPU telemetry simulator. Publishes only to Redpanda.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "telemetry-generator"}

    @app.get("/ready")
    def ready() -> dict[str, Any]:
        summary = engine.fleet_summary()
        return {"ready": summary["running"], **summary}

    @app.get("/api/v1/scenarios")
    def list_scenarios() -> dict[str, Any]:
        return {"scenarios": engine.list_scenarios(), "active": engine.active_scenarios()}

    @app.get("/api/v1/scenarios/{scenario_id}")
    def get_scenario(scenario_id: str) -> dict[str, Any]:
        view = engine.get_scenario(scenario_id)
        if not view:
            raise HTTPException(status_code=404, detail="scenario not found")
        return view

    @app.post("/api/v1/scenarios/inject")
    def inject(body: InjectRequest) -> dict[str, Any]:
        try:
            return engine.inject(
                body.scenario,
                device_id=body.device_id,
                rack_id=body.rack_id,
                severity=body.severity,
                metadata=body.metadata,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/v1/scenarios/{scenario_id}/stop")
    def stop_scenario(scenario_id: str) -> dict[str, Any]:
        try:
            return engine.stop_scenario(scenario_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/v1/scenarios/{scenario_id}/severity/increase")
    def increase_severity(scenario_id: str, body: SeverityRequest | None = None) -> dict[str, Any]:
        delta = body.delta if body else 0.1
        try:
            return engine.increase_severity(scenario_id, delta)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/v1/scenarios/{scenario_id}/severity/decrease")
    def decrease_severity(scenario_id: str, body: SeverityRequest | None = None) -> dict[str, Any]:
        delta = body.delta if body else 0.1
        try:
            return engine.decrease_severity(scenario_id, delta)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/v1/scenarios/reset")
    def reset_fleet() -> dict[str, str]:
        engine.reset_fleet()
        return {"status": "reset"}

    @app.post("/api/v1/devices/{device_id}/reset")
    def reset_device(device_id: str) -> dict[str, str]:
        try:
            engine.reset_device(device_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"status": "reset", "device_id": device_id}

    @app.post("/api/v1/devices/{device_id}/recovery")
    def recovery(device_id: str) -> dict[str, Any]:
        try:
            return engine.apply_recovery(device_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/v1/devices/{device_id}")
    def device_snapshot(device_id: str) -> dict[str, Any]:
        try:
            return engine.snapshot_device(device_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/v1/fleet")
    def fleet() -> dict[str, Any]:
        return engine.fleet_summary()

    @app.post("/api/v1/control/pause")
    def pause() -> dict[str, str]:
        engine.pause()
        return {"status": "paused"}

    @app.post("/api/v1/control/resume")
    def resume() -> dict[str, str]:
        engine.resume()
        return {"status": "resumed"}

    return app
