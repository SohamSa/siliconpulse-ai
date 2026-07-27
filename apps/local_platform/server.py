"""Stdlib HTTP API + static UI for the SiliconPulse local demo.

No Docker. No pip. Run: python apps/local_platform/server.py
"""

from __future__ import annotations

import json
import mimetypes
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from agents import AgentOrchestrator
from intelligence import IntelligenceEngine
from simulator import SCENARIOS, Simulator

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

SIM = Simulator(device_count=50, rack_count=5, seed=42, interval_s=1.0)
INTEL = IntelligenceEngine(SIM)
AGENTS = AgentOrchestrator(SIM, INTEL)
SIM.on_telemetry = INTEL.on_telemetry


def _json(handler: BaseHTTPRequestHandler, code: int, payload: Any) -> None:
    body = json.dumps(payload, default=str).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _serve_static(handler: BaseHTTPRequestHandler, rel: str) -> None:
    if rel in {"", "/"}:
        rel = "/index.html"
    path = (STATIC / rel.lstrip("/")).resolve()
    if not str(path).startswith(str(STATIC.resolve())) or not path.is_file():
        _json(handler, 404, {"error": "not found"})
        return
    data = path.read_bytes()
    ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    handler.send_response(200)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


RouteHandler = Callable[[BaseHTTPRequestHandler, dict[str, str], dict[str, Any]], None]


def route_get_overview(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    summary = SIM.fleet_summary()
    devices = INTEL.list_devices()
    open_alerts = [a.__dict__ for a in INTEL.alerts.values() if a.status == "open"]
    open_incidents = [
        {
            "incident_id": i.incident_id,
            "title": i.title,
            "status": i.status,
            "severity": i.severity,
            "affected_devices": i.affected_devices,
            "likely_root_cause": i.likely_root_cause,
            "confidence": i.confidence,
        }
        for i in INTEL.incidents.values()
        if i.status != "resolved"
    ]
    pending = [AGENTS._approval_view(a) for a in AGENTS.approvals.values() if a.status == "pending"]
    _json(
        h,
        200,
        {
            "summary": summary,
            "top_anomalies": devices[:8],
            "open_alerts": open_alerts[-10:],
            "open_incidents": open_incidents,
            "pending_approvals": pending,
            "value_proposition": {
                "headline": "Turn raw accelerator telemetry into trusted operational decisions",
                "for": "Infrastructure operators, reliability engineers, and hardware platform leaders",
                "differentiation": [
                    "Statistical digital twins catch drift before static thresholds",
                    "Structured root-cause evidence — not LLM guesswork",
                    "Human-supervised agents for high-impact actions",
                    "Same architecture transferable beyond one device category",
                ],
            },
        },
    )


def route_get_devices(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    _json(h, 200, {"devices": INTEL.list_devices()})


def route_get_device(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    try:
        _json(h, 200, INTEL.device_view(p["device_id"]))
    except ValueError as exc:
        _json(h, 404, {"error": str(exc)})


def route_get_alerts(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    alerts = sorted(INTEL.alerts.values(), key=lambda a: a.detected_at, reverse=True)
    _json(h, 200, {"alerts": [a.__dict__ for a in alerts[:100]]})


def route_get_incidents(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    items = []
    for i in INTEL.incidents.values():
        items.append(
            {
                "incident_id": i.incident_id,
                "title": i.title,
                "description": i.description,
                "status": i.status,
                "severity": i.severity,
                "started_at": i.started_at,
                "resolved_at": i.resolved_at,
                "affected_devices": i.affected_devices,
                "affected_racks": i.affected_racks,
                "likely_root_cause": i.likely_root_cause,
                "confidence": i.confidence,
                "timeline": i.timeline,
                "approved_actions": i.approved_actions,
                "outcome": i.outcome,
            }
        )
    items.sort(key=lambda x: x["started_at"], reverse=True)
    _json(h, 200, {"incidents": items})


def route_get_incident(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    i = INTEL.incidents.get(p["incident_id"])
    if not i:
        _json(h, 404, {"error": "incident not found"})
        return
    _json(
        h,
        200,
        {
            "incident_id": i.incident_id,
            "title": i.title,
            "description": i.description,
            "status": i.status,
            "severity": i.severity,
            "started_at": i.started_at,
            "resolved_at": i.resolved_at,
            "affected_devices": i.affected_devices,
            "affected_racks": i.affected_racks,
            "likely_root_cause": i.likely_root_cause,
            "confidence": i.confidence,
            "timeline": i.timeline,
            "approved_actions": i.approved_actions,
            "outcome": i.outcome,
        },
    )


def route_post_investigate(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    try:
        _json(h, 200, AGENTS.run_root_cause(p["incident_id"]))
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_post_maintenance(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    try:
        _json(h, 200, AGENTS.run_predictive_maintenance(p["incident_id"]))
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_post_report(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    try:
        _json(h, 200, AGENTS.generate_report(p["incident_id"]))
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_get_approvals(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    _json(h, 200, {"approvals": [AGENTS._approval_view(a) for a in AGENTS.approvals.values()]})


def route_post_approve(h: BaseHTTPRequestHandler, p: dict[str, str], body: dict[str, Any]) -> None:
    try:
        _json(
            h,
            200,
            AGENTS.decide_approval(p["approval_id"], True, comments=body.get("comments", ""), user=body.get("user", "operator")),
        )
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_post_reject(h: BaseHTTPRequestHandler, p: dict[str, str], body: dict[str, Any]) -> None:
    try:
        _json(
            h,
            200,
            AGENTS.decide_approval(p["approval_id"], False, comments=body.get("comments", ""), user=body.get("user", "operator")),
        )
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_get_scenarios(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    active = [SIM._scenario_view(s) for s in SIM.scenarios.values() if not s.stopped]
    _json(
        h,
        200,
        {
            "catalog": [{"name": k, "description": v} for k, v in SCENARIOS.items()],
            "active": active,
        },
    )


def route_post_inject(h: BaseHTTPRequestHandler, _p: dict[str, str], body: dict[str, Any]) -> None:
    try:
        result = SIM.inject(
            scenario=body.get("scenario", "cooling_degradation"),
            device_id=body.get("device_id", "GPU-042"),
            rack_id=body.get("rack_id"),
            severity=float(body.get("severity", 0.75)),
        )
        _json(h, 200, result)
    except Exception as exc:
        _json(h, 400, {"error": str(exc)})


def route_post_reset(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    SIM.reset_fleet()
    INTEL.history.clear()
    INTEL.peer_temp.clear()
    INTEL.baselines.clear()
    INTEL._dedupe_until.clear()
    INTEL.alerts.clear()
    INTEL.incidents.clear()
    INTEL.reports.clear()
    AGENTS.runs.clear()
    AGENTS.approvals.clear()
    _json(h, 200, {"status": "reset"})


def route_get_agents(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    runs = [AGENTS._run_view(r) for r in AGENTS.runs.values()]
    runs.sort(key=lambda r: r["started_at"], reverse=True)
    _json(h, 200, {"runs": runs})


def route_get_healthcare(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    _json(
        h,
        200,
        {
            "disclaimer": (
                "This module is a simulated device-monitoring demonstration. "
                "It is not a medical diagnostic system and must not be used for patient-care decisions."
            ),
            "devices": [
                {
                    "device_id": "HS-001",
                    "device_health": "healthy",
                    "signal_quality": 0.97,
                    "battery_voltage": 3.9,
                    "packet_loss": 0.01,
                    "calibration_drift": 0.02,
                    "device_temperature_c": 34.2,
                    "note": "Simulated physiological channels intentionally separated from device health.",
                },
                {
                    "device_id": "HS-002",
                    "device_health": "degraded",
                    "signal_quality": 0.71,
                    "battery_voltage": 3.4,
                    "packet_loss": 0.08,
                    "calibration_drift": 0.18,
                    "device_temperature_c": 39.1,
                    "note": "Battery + drift scenario — still not a clinical signal.",
                },
            ],
        },
    )


def route_get_report(h: BaseHTTPRequestHandler, p: dict[str, str], _b: dict[str, Any]) -> None:
    report = INTEL.reports.get(p["report_id"])
    if not report:
        _json(h, 404, {"error": "report not found"})
        return
    _json(h, 200, report)


def route_health(h: BaseHTTPRequestHandler, _p: dict[str, str], _b: dict[str, Any]) -> None:
    _json(h, 200, {"status": "ok", "mode": "local-no-docker", "events": SIM.events_generated})


ROUTES: list[tuple[str, str, RouteHandler]] = [
    ("GET", "/health", route_health),
    ("GET", "/api/v1/overview", route_get_overview),
    ("GET", "/api/v1/devices", route_get_devices),
    ("GET", "/api/v1/devices/{device_id}", route_get_device),
    ("GET", "/api/v1/alerts", route_get_alerts),
    ("GET", "/api/v1/incidents", route_get_incidents),
    ("GET", "/api/v1/incidents/{incident_id}", route_get_incident),
    ("POST", "/api/v1/incidents/{incident_id}/investigate", route_post_investigate),
    ("POST", "/api/v1/incidents/{incident_id}/maintenance", route_post_maintenance),
    ("POST", "/api/v1/incidents/{incident_id}/report", route_post_report),
    ("GET", "/api/v1/approvals", route_get_approvals),
    ("POST", "/api/v1/approvals/{approval_id}/approve", route_post_approve),
    ("POST", "/api/v1/approvals/{approval_id}/reject", route_post_reject),
    ("GET", "/api/v1/scenarios", route_get_scenarios),
    ("POST", "/api/v1/scenarios/inject", route_post_inject),
    ("POST", "/api/v1/scenarios/reset", route_post_reset),
    ("GET", "/api/v1/agents/runs", route_get_agents),
    ("GET", "/api/v1/healthcare/devices", route_get_healthcare),
    ("GET", "/api/v1/reports/{report_id}", route_get_report),
]


def match_route(method: str, path: str) -> tuple[RouteHandler, dict[str, str]] | None:
    for m, pattern, handler in ROUTES:
        if m != method:
            continue
        pp = pattern.strip("/").split("/")
        ap = path.strip("/").split("/")
        if len(pp) != len(ap):
            continue
        params: dict[str, str] = {}
        ok = True
        for a, b in zip(pp, ap):
            if a.startswith("{") and a.endswith("}"):
                params[a[1:-1]] = urllib.parse.unquote(b)
            elif a != b:
                ok = False
                break
        if ok:
            return handler, params
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def _dispatch(self, method: str) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            matched = match_route(method, path)
            if matched:
                handler, params = matched
                body = _read_json(self) if method == "POST" else {}
                handler(self, params, body)
                return
            if method == "GET":
                _serve_static(self, path)
                return
            _json(self, 404, {"error": "not found", "path": path})
        except Exception as exc:
            _json(self, 500, {"error": str(exc), "trace": traceback.format_exc()})


def main(host: str = "127.0.0.1", port: int = 8787) -> None:
    # Warm baseline before starting the background emitter (avoids lock contention at boot)
    for _ in range(8):
        SIM.tick()
    SIM.start()
    httpd = ThreadingHTTPServer((host, port), Handler)
    print("", flush=True)
    print("  SiliconPulse AI - Local Demo (no Docker)", flush=True)
    print(f"  Open:  http://{host}:{port}", flush=True)
    print("  Demo:  Overview > Inject cooling on GPU-042 > Investigate > Approve > Report", flush=True)
    print("  Stop:  Ctrl+C", flush=True)
    print("", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
    finally:
        SIM.stop()
        httpd.server_close()


if __name__ == "__main__":
    main()
