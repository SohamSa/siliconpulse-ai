"""Structured intelligence: twin, anomaly, prediction, health, alerts, incidents, RCA.

No LLM inventing telemetry. Hidden simulator labels are never used as RCA evidence.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from simulator import DeviceState, Simulator


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Alert:
    alert_id: str
    device_id: str
    incident_id: str | None
    alert_type: str
    severity: str
    status: str
    detected_at: str
    current_value: float
    expected_value: float
    evidence: list[str]
    recommendation: str
    confidence: float
    dedupe_key: str


@dataclass
class Incident:
    incident_id: str
    title: str
    description: str
    status: str
    severity: str
    started_at: str
    acknowledged_at: str | None = None
    resolved_at: str | None = None
    affected_devices: list[str] = field(default_factory=list)
    affected_racks: list[str] = field(default_factory=list)
    primary_alert_id: str | None = None
    likely_root_cause: str | None = None
    confidence: float = 0.0
    timeline: list[dict[str, Any]] = field(default_factory=list)
    approved_actions: list[dict[str, Any]] = field(default_factory=list)
    outcome: str | None = None


class IntelligenceEngine:
    def __init__(self, sim: Simulator) -> None:
        self.sim = sim
        self._lock = threading.RLock()
        self.history: dict[str, deque[dict[str, Any]]] = defaultdict(lambda: deque(maxlen=120))
        self.peer_temp: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=30))
        self.alerts: dict[str, Alert] = {}
        self.incidents: dict[str, Incident] = {}
        self._dedupe_until: dict[str, float] = {}
        self.reports: dict[str, dict[str, Any]] = {}
        self.baselines: dict[str, dict[str, float]] = {}

    def on_telemetry(self, event: dict[str, Any]) -> None:
        # Strip hidden scenario before any intelligence use
        clean = {k: v for k, v in event.items() if not k.startswith("_")}
        did = clean["device_id"]
        with self._lock:
            self.history[did].append(clean)
            st = self.sim.devices[did]
            self._update_twin(st, clean)
            self._update_anomaly(st, clean)
            self._update_prediction(st, clean)
            self._update_health(st)
            self._evaluate_alerts(st, clean)

    def _update_twin(self, st: DeviceState, evt: dict[str, Any]) -> None:
        # Peer-group + utilization-adjusted expected temperature
        peers = [d for d in self.sim.devices.values() if d.rack_id == st.rack_id and d.device_id != st.device_id]
        peer_avg = sum(p.temp_c for p in peers) / len(peers) if peers else st.temp_c
        util = evt["utilization_pct"] / 100.0
        expected = 28.0 + 22.0 * util + 0.02 * evt["power_watts"] + (peer_avg - 55.0) * 0.15
        # Warm baseline after a few samples
        key = st.device_id
        if key not in self.baselines:
            self.baselines[key] = {"temp": expected, "n": 1.0}
        baseline = self.baselines[key]
        # Only learn baseline while healthy / low anomaly
        if st.anomaly_score < 0.35 and st.cooling_eff > 0.9:
            baseline["temp"] = 0.95 * baseline["temp"] + 0.05 * expected
            baseline["n"] += 1
        expected = 0.6 * expected + 0.4 * baseline["temp"]

        actual = evt["temperature_c"]
        deviation = abs(actual - expected)
        pct = deviation / max(expected, 1.0)
        st.twin_expected_temp = expected
        st.twin_deviation = min(1.0, deviation / 12.0 + pct * 0.5)
        st.twin_confidence = min(0.95, 0.55 + min(baseline["n"], 40) / 80)

    def _update_anomaly(self, st: DeviceState, evt: dict[str, Any]) -> None:
        hist = list(self.history[st.device_id])
        if len(hist) < 5:
            st.anomaly_score = max(st.anomaly_score, st.twin_deviation * 0.5)
            return
        temps = [h["temperature_c"] for h in hist[-20:]]
        mean = sum(temps) / len(temps)
        var = sum((t - mean) ** 2 for t in temps) / len(temps)
        std = max(var**0.5, 0.5)
        z = abs(evt["temperature_c"] - mean) / std
        fan_eff_proxy = evt["fan_speed_rpm"] / max(1800 + (evt["temperature_c"] - 40) * 55, 1)
        score = 0.0
        score += min(1.0, st.twin_deviation) * 0.45
        score += min(1.0, z / 4.0) * 0.25
        score += max(0.0, 1.0 - fan_eff_proxy) * 0.15
        score += min(1.0, evt["ecc_correctable_errors"] / 10.0) * 0.1
        score += (1.0 - evt["sensor_quality"]) * 0.05
        st.anomaly_score = max(0.0, min(1.0, 0.7 * st.anomaly_score + 0.3 * score))

    def _update_prediction(self, st: DeviceState, evt: dict[str, Any]) -> None:
        # Evidence-weighted failure class probabilities (synthetic demo-grade)
        scores = {
            "normal": 0.4,
            "cooling_degradation": st.twin_deviation * 1.2 + (1.0 - st.cooling_eff) * 0.8,
            "fan_failure": max(0.0, 1.0 - st.fan_eff) * 1.4 + (1.0 if evt["fan_speed_rpm"] < 1500 else 0),
            "memory_degradation": min(1.5, evt["ecc_correctable_errors"] / 8.0 + evt["ecc_uncorrectable_errors"] * 0.8),
            "voltage_instability": abs(evt["voltage"] - 12.0) / 0.8,
            "rack_cooling_failure": 0.0,
            "sensor_drift": (1.0 - evt["sensor_quality"]) * 1.2,
            "network_bottleneck": min(1.2, max(0, evt["network_latency_ms"] - 5) / 20.0),
            "workload_overload": max(0, evt["utilization_pct"] - 90) / 10.0,
            "firmware_regression": 0.15 if evt["ecc_correctable_errors"] > 0 and st.twin_deviation < 0.3 else 0.05,
        }
        # Peer comparison: if peers also deviant → rack cooling more likely
        peers = [d for d in self.sim.devices.values() if d.rack_id == st.rack_id and d.device_id != st.device_id]
        if peers:
            hot_peers = sum(1 for p in peers if p.twin_deviation > 0.4 or p.anomaly_score > 0.45)
            if hot_peers >= max(2, len(peers) // 3):
                scores["rack_cooling_failure"] += 0.9
                scores["cooling_degradation"] *= 0.6
            else:
                scores["cooling_degradation"] += 0.35 * st.twin_deviation
                scores["rack_cooling_failure"] *= 0.3

        best = max(scores.items(), key=lambda kv: kv[1])
        total = sum(max(0.01, v) for v in scores.values())
        st.failure_type = best[0] if best[1] > 0.45 else "normal"
        st.failure_prob = min(0.98, max(0.02, best[1] / (total * 0.35)))
        if st.failure_type == "normal":
            st.failure_prob = min(st.failure_prob, 0.15)
        # RUL shrinks with failure probability and anomaly
        st.rul_hours = max(4.0, 720.0 * (1.0 - 0.85 * st.failure_prob) * (1.0 - 0.5 * st.anomaly_score))

    def _update_health(self, st: DeviceState) -> None:
        thermal = min(1.0, max(0.0, (st.temp_c - 55) / 35.0))
        score = 100.0
        score -= thermal * 25
        score -= st.anomaly_score * 20
        score -= st.failure_prob * 25
        score -= min(1.0, (720 - st.rul_hours) / 720) * 10
        score -= min(1.0, st.ecc_c / 20.0) * 8
        score -= st.twin_deviation * 12
        score -= (1.0 - st.sensor_quality) * 5
        st.health_score = max(0.0, min(100.0, score))
        if st.health_score >= 85:
            st.lifecycle = "healthy"
        elif st.health_score >= 70:
            st.lifecycle = "stressed"
        elif st.health_score >= 55:
            st.lifecycle = "degraded"
        elif st.health_score >= 40:
            st.lifecycle = "maintenance_recommended"
        else:
            st.lifecycle = "critical"

    def _evaluate_alerts(self, st: DeviceState, evt: dict[str, Any]) -> None:
        import time

        now = time.time()
        candidates: list[tuple[str, str, float, float, list[str], str]] = []

        if st.twin_deviation >= 0.35 and evt["temperature_c"] < 95:
            candidates.append(
                (
                    "twin_temperature_deviation",
                    "warning" if st.twin_deviation < 0.7 else "critical",
                    evt["temperature_c"],
                    st.twin_expected_temp,
                    [
                        f"Twin expected {st.twin_expected_temp:.1f}°C, observed {evt['temperature_c']:.1f}°C",
                        f"Twin deviation score {st.twin_deviation:.2f}",
                        f"Anomaly score {st.anomaly_score:.2f}",
                    ],
                    "Inspect cooling path and compare with rack peers before critical threshold breach.",
                )
            )
        if evt["temperature_c"] >= 85:
            candidates.append(
                (
                    "high_temperature",
                    "critical" if evt["temperature_c"] >= 95 else "warning",
                    evt["temperature_c"],
                    80.0,
                    [f"Temperature {evt['temperature_c']:.1f}°C"],
                    "Reduce workload and inspect cooling.",
                )
            )
        if st.fan_eff < 0.5 or evt["fan_speed_rpm"] < 1200:
            candidates.append(
                (
                    "low_fan_efficiency",
                    "warning",
                    evt["fan_speed_rpm"],
                    3000.0,
                    [f"Fan RPM {evt['fan_speed_rpm']:.0f}", f"Fan efficiency {st.fan_eff:.2f}"],
                    "Inspect fan assembly.",
                )
            )
        if evt["ecc_uncorrectable_errors"] > 0:
            candidates.append(
                (
                    "uncorrectable_ecc",
                    "critical",
                    float(evt["ecc_uncorrectable_errors"]),
                    0.0,
                    ["Uncorrectable ECC error detected"],
                    "Schedule memory diagnostics / replacement.",
                )
            )

        for alert_type, severity, cur, exp, evidence, rec in candidates:
            key = f"{st.device_id}:{alert_type}"
            if self._dedupe_until.get(key, 0) > now:
                continue
            self._dedupe_until[key] = now + 45  # cooldown seconds
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                device_id=st.device_id,
                incident_id=None,
                alert_type=alert_type,
                severity=severity,
                status="open",
                detected_at=utcnow(),
                current_value=cur,
                expected_value=exp,
                evidence=evidence,
                recommendation=rec,
                confidence=min(0.95, 0.55 + st.anomaly_score * 0.4),
                dedupe_key=key,
            )
            self.alerts[alert.alert_id] = alert
            incident = self._group_incident(alert, st)
            alert.incident_id = incident.incident_id

    def _group_incident(self, alert: Alert, st: DeviceState) -> Incident:
        # Reuse open incident on same device, or rack-wide if many peers alerting
        for inc in self.incidents.values():
            if inc.status in {"open", "acknowledged", "investigating"} and st.device_id in inc.affected_devices:
                inc.timeline.append({"at": utcnow(), "type": "alert", "alert_id": alert.alert_id, "message": alert.alert_type})
                if alert.severity == "critical":
                    inc.severity = "critical"
                return inc

        rack_open = [
            a
            for a in self.alerts.values()
            if a.status == "open"
            and self.sim.devices[a.device_id].rack_id == st.rack_id
            and a.alert_type in {"twin_temperature_deviation", "high_temperature"}
        ]
        if len(rack_open) >= 4:
            title = f"Rack thermal incident on {st.rack_id}"
            devices = sorted({a.device_id for a in rack_open} | {st.device_id})
            severity = "critical"
        else:
            title = f"Device anomaly on {st.device_id}"
            devices = [st.device_id]
            severity = alert.severity

        inc = Incident(
            incident_id=str(uuid.uuid4()),
            title=title,
            description=f"Auto-grouped from {alert.alert_type}",
            status="open",
            severity=severity,
            started_at=utcnow(),
            affected_devices=devices,
            affected_racks=[st.rack_id],
            primary_alert_id=alert.alert_id,
            timeline=[{"at": utcnow(), "type": "created", "message": title}],
        )
        self.incidents[inc.incident_id] = inc
        return inc

    def investigate(self, incident_id: str) -> dict[str, Any]:
        """Structured RCA — never uses hidden simulator scenario labels."""
        with self._lock:
            inc = self.incidents.get(incident_id)
            if not inc:
                raise ValueError("incident not found")
            device_id = inc.affected_devices[0]
            st = self.sim.devices[device_id]
            peers = [d for d in self.sim.devices.values() if d.rack_id == st.rack_id and d.device_id != device_id]
            peer_avg_temp = sum(p.temp_c for p in peers) / len(peers) if peers else st.temp_c
            peer_hot = sum(1 for p in peers if p.twin_deviation > 0.4)

            hypotheses = []

            def add(name: str, score: float, support: list[str], contradict: list[str]) -> None:
                hypotheses.append(
                    {
                        "cause": name,
                        "score": round(score, 3),
                        "supporting_evidence": support,
                        "contradicting_evidence": contradict,
                    }
                )

            # Device cooling degradation
            support = []
            contradict = []
            if st.twin_deviation > 0.4:
                support.append(f"Twin deviation {st.twin_deviation:.2f} with expected {st.twin_expected_temp:.1f}°C")
            if peer_hot <= 1:
                support.append("Rack peers mostly normal — points to device-local issue")
            else:
                contradict.append(f"{peer_hot} peer devices also abnormal")
            if st.fan_eff > 0.7:
                support.append("Fan still responding — cooling path degradation more likely than total fan failure")
            add("device_cooling_degradation", 0.35 + st.twin_deviation * 0.5 + (0.2 if peer_hot <= 1 else -0.2), support, contradict)

            # Rack cooling
            rs, rc = [], []
            if peer_hot >= max(2, len(peers) // 3):
                rs.append(f"Multiple peers hot in {st.rack_id}")
            else:
                rc.append(f"Peer average temp {peer_avg_temp:.1f}°C near normal")
            add("rack_cooling_failure", 0.15 + (0.5 if peer_hot >= 2 else 0.0), rs, rc)

            # Fan failure
            fs, fc = [], []
            if st.fan_eff < 0.5 or st.fan_rpm < 1500:
                fs.append(f"Fan efficiency {st.fan_eff:.2f}, RPM {st.fan_rpm:.0f}")
            else:
                fc.append(f"Fan RPM {st.fan_rpm:.0f} still tracking temperature")
            add("fan_failure", 0.1 + (0.6 if st.fan_eff < 0.5 else 0.0), fs, fc)

            # Memory / voltage / sensor / workload
            add(
                "memory_degradation",
                0.05 + min(0.7, st.ecc_c / 15.0) + st.ecc_u * 0.4,
                [f"ECC correctable={st.ecc_c}, uncorrectable={st.ecc_u}"] if st.ecc_c or st.ecc_u else [],
                [] if st.ecc_c or st.ecc_u else ["No elevated ECC errors"],
            )
            add(
                "sensor_drift",
                0.05 + (1.0 - st.sensor_quality) * 0.8,
                [f"Sensor quality {st.sensor_quality:.2f}"] if st.sensor_quality < 0.85 else [],
                ["Sensor quality healthy"] if st.sensor_quality >= 0.85 else [],
            )
            add(
                "workload_overload",
                0.05 + max(0, st.utilization - 90) / 20.0,
                [f"Utilization {st.utilization:.0f}%"] if st.utilization > 90 else [],
                ["Utilization not extreme"] if st.utilization <= 90 else [],
            )

            hypotheses.sort(key=lambda h: h["score"], reverse=True)
            top = hypotheses[0]
            conf = min(0.93, 0.45 + top["score"] * 0.4)
            inc.likely_root_cause = top["cause"]
            inc.confidence = conf
            inc.status = "investigating"
            result = {
                "incident_id": incident_id,
                "device_id": device_id,
                "most_likely_cause": top["cause"],
                "confidence": conf,
                "hypotheses": hypotheses[:5],
                "recommended_next_checks": [
                    "Compare device fan curve vs peer devices",
                    "Inspect device-local heatsink / coolant path",
                    "Confirm firmware and workload unchanged",
                    "Verify rack inlet temperature sensors",
                ],
                "missing_evidence": ["Physical inspection not yet performed", "Maintenance history incomplete in demo"],
                "note": "Root cause ranked from observed telemetry/twin/peer evidence only — not from hidden simulation labels.",
            }
            inc.timeline.append({"at": utcnow(), "type": "investigation", "message": f"RCA: {top['cause']} ({conf:.0%})"})
            return result

    def device_view(self, device_id: str) -> dict[str, Any]:
        st = self.sim.devices.get(device_id)
        if not st:
            raise ValueError("device not found")
        hist = list(self.history[device_id])[-40:]
        return {
            "device_id": st.device_id,
            "rack_id": st.rack_id,
            "server_id": st.server_id,
            "model_name": st.model_name,
            "firmware_version": st.firmware_version,
            "batch": st.batch,
            "age_hours": round(st.age_hours, 1),
            "telemetry": {
                "temperature_c": round(st.temp_c + st.temp_bias, 2),
                "power_watts": round(st.power_w + st.power_bias, 1),
                "utilization_pct": round(st.utilization, 1),
                "fan_speed_rpm": round(st.fan_rpm, 0),
                "throughput": round(st.throughput, 1),
                "voltage": round(st.voltage, 3),
                "ecc_correctable_errors": st.ecc_c,
                "network_latency_ms": round(st.latency_ms, 2),
                "sensor_quality": round(st.sensor_quality, 2),
                "workload_type": st.workload,
            },
            "true_internal": {
                "temperature_c": round(st.temp_c, 2),
                "cooling_efficiency": round(st.cooling_eff, 3),
                "fan_efficiency": round(st.fan_eff, 3),
            },
            "intelligence": {
                "anomaly_score": round(st.anomaly_score, 3),
                "failure_probability": round(st.failure_prob, 3),
                "predicted_failure_type": st.failure_type,
                "remaining_useful_life_hours": round(st.rul_hours, 1),
                "health_score": round(st.health_score, 1),
                "lifecycle": st.lifecycle,
                "twin_expected_temperature_c": round(st.twin_expected_temp, 2),
                "twin_deviation_score": round(st.twin_deviation, 3),
                "twin_confidence": round(st.twin_confidence, 3),
                "twin_version": "stat-twin-v0.1",
            },
            "history": hist,
        }

    def list_devices(self) -> list[dict[str, Any]]:
        rows = []
        for st in self.sim.devices.values():
            rows.append(
                {
                    "device_id": st.device_id,
                    "model_name": st.model_name,
                    "rack_id": st.rack_id,
                    "status": st.lifecycle,
                    "temperature_c": round(st.temp_c + st.temp_bias, 1),
                    "utilization_pct": round(st.utilization, 1),
                    "power_watts": round(st.power_w, 0),
                    "throughput": round(st.throughput, 0),
                    "anomaly_score": round(st.anomaly_score, 3),
                    "failure_probability": round(st.failure_prob, 3),
                    "health_score": round(st.health_score, 1),
                    "rul_hours": round(st.rul_hours, 1),
                    "twin_deviation": round(st.twin_deviation, 3),
                }
            )
        rows.sort(key=lambda r: (-r["anomaly_score"], -r["failure_probability"]))
        return rows
