"""Human-supervised specialized agents (stdlib)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from intelligence import IntelligenceEngine
from simulator import Simulator


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Approval:
    approval_id: str
    action: str
    reason: str
    expected_impact: str
    risk: str
    requested_by: str
    device_id: str
    incident_id: str | None
    status: str = "pending"
    requested_at: str = field(default_factory=utcnow)
    decided_at: str | None = None
    decided_by: str | None = None
    comments: str = ""


@dataclass
class AgentRun:
    agent_run_id: str
    agent_type: str
    incident_id: str | None
    device_id: str | None
    status: str
    started_at: str
    completed_at: str | None = None
    current_step: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    approval_required: bool = False
    approval_status: str | None = None
    output: dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    def __init__(self, sim: Simulator, intel: IntelligenceEngine) -> None:
        self.sim = sim
        self.intel = intel
        self.runs: dict[str, AgentRun] = {}
        self.approvals: dict[str, Approval] = {}

    def _tool(self, run: AgentRun, name: str, detail: str) -> None:
        run.tool_calls.append({"tool": name, "detail": detail, "at": utcnow()})

    def run_root_cause(self, incident_id: str) -> dict[str, Any]:
        run = AgentRun(
            agent_run_id=str(uuid.uuid4()),
            agent_type="root_cause_investigation",
            incident_id=incident_id,
            device_id=None,
            status="running",
            started_at=utcnow(),
            current_step="gather_evidence",
        )
        self.runs[run.agent_run_id] = run
        inc = self.intel.incidents[incident_id]
        device_id = inc.affected_devices[0]
        run.device_id = device_id
        self._tool(run, "get_device_state", device_id)
        self._tool(run, "get_digital_twin", device_id)
        self._tool(run, "get_peer_devices", self.sim.devices[device_id].rack_id)
        self._tool(run, "get_firmware_history", "demo-static")
        self._tool(run, "get_workload_history", "demo-static")
        result = self.intel.investigate(incident_id)
        run.evidence = result["hypotheses"][0]["supporting_evidence"]
        run.decisions = [f"Ranked cause: {result['most_likely_cause']}"]
        run.confidence = result["confidence"]
        run.output = result
        run.current_step = "complete"
        run.status = "completed"
        run.completed_at = utcnow()
        inc.timeline.append({"at": utcnow(), "type": "agent", "message": "Root-Cause Investigation Agent completed"})
        return {"agent_run": self._run_view(run), "result": result}

    def run_predictive_maintenance(self, incident_id: str) -> dict[str, Any]:
        run = AgentRun(
            agent_run_id=str(uuid.uuid4()),
            agent_type="predictive_maintenance",
            incident_id=incident_id,
            device_id=None,
            status="running",
            started_at=utcnow(),
            current_step="assess_risk",
            approval_required=True,
            approval_status="pending",
        )
        self.runs[run.agent_run_id] = run
        inc = self.intel.incidents[incident_id]
        device_id = inc.affected_devices[0]
        run.device_id = device_id
        st = self.sim.devices[device_id]
        self._tool(run, "get_prediction", f"{st.failure_type} p={st.failure_prob:.2f}")
        self._tool(run, "get_remaining_useful_life", f"{st.rul_hours:.1f}h")
        self._tool(run, "get_workload_criticality", "demo-high")
        plan = {
            "device_id": device_id,
            "actions": [
                {
                    "action": "simulate_workload_redistribution",
                    "description": "Shift non-critical training jobs off this GPU for 30 minutes",
                    "risk": "medium",
                },
                {
                    "action": "simulate_fan_inspection",
                    "description": "Queue simulated fan / cooling-path inspection",
                    "risk": "low",
                },
            ],
            "rationale": [
                f"Predicted failure type: {st.failure_type}",
                f"Failure probability: {st.failure_prob:.0%}",
                f"RUL estimate: {st.rul_hours:.0f} hours",
                f"Twin deviation: {st.twin_deviation:.2f}",
            ],
            "requires_human_approval": True,
        }
        approval = Approval(
            approval_id=str(uuid.uuid4()),
            action="simulate_workload_redistribution+fan_inspection",
            reason="Reduce thermal stress while validating cooling degradation hypothesis",
            expected_impact="Temperature should stabilize; anomaly and twin deviation should fall",
            risk="medium — simulated only; no physical change",
            requested_by="predictive_maintenance_agent",
            device_id=device_id,
            incident_id=incident_id,
        )
        self.approvals[approval.approval_id] = approval
        run.output = {"plan": plan, "approval_id": approval.approval_id}
        run.decisions = ["Proposed simulated remediation; waiting for human approval"]
        run.confidence = min(0.9, 0.5 + st.failure_prob * 0.4)
        run.current_step = "awaiting_approval"
        run.status = "awaiting_approval"
        inc.timeline.append(
            {
                "at": utcnow(),
                "type": "approval_requested",
                "message": f"Maintenance plan awaiting approval ({approval.approval_id[:8]})",
            }
        )
        return {"agent_run": self._run_view(run), "plan": plan, "approval": self._approval_view(approval)}

    def decide_approval(self, approval_id: str, approve: bool, comments: str = "", user: str = "operator") -> dict[str, Any]:
        ap = self.approvals.get(approval_id)
        if not ap:
            raise ValueError("approval not found")
        if ap.status != "pending":
            raise ValueError("approval already decided")
        ap.status = "approved" if approve else "rejected"
        ap.decided_at = utcnow()
        ap.decided_by = user
        ap.comments = comments
        inc = self.intel.incidents.get(ap.incident_id) if ap.incident_id else None
        if approve:
            # Apply simulated recovery
            self.sim.apply_recovery(ap.device_id)
            if inc:
                inc.approved_actions.append(self._approval_view(ap))
                inc.timeline.append({"at": utcnow(), "type": "action_applied", "message": "Approved simulated remediation applied"})
                inc.status = "remediating"
            for run in self.runs.values():
                if run.output.get("approval_id") == approval_id:
                    run.approval_status = "approved"
                    run.status = "completed"
                    run.completed_at = utcnow()
                    run.current_step = "monitor_post_action"
                    run.decisions.append("Human approved; recovery scenario injected")
        else:
            if inc:
                inc.timeline.append({"at": utcnow(), "type": "approval_rejected", "message": comments or "Rejected by operator"})
            for run in self.runs.values():
                if run.output.get("approval_id") == approval_id:
                    run.approval_status = "rejected"
                    run.status = "completed"
                    run.completed_at = utcnow()
        return self._approval_view(ap)

    def generate_report(self, incident_id: str) -> dict[str, Any]:
        inc = self.intel.incidents.get(incident_id)
        if not inc:
            raise ValueError("incident not found")
        device_id = inc.affected_devices[0]
        st = self.sim.devices[device_id]
        run = AgentRun(
            agent_run_id=str(uuid.uuid4()),
            agent_type="reporting",
            incident_id=incident_id,
            device_id=device_id,
            status="running",
            started_at=utcnow(),
            current_step="compile_evidence",
        )
        self.runs[run.agent_run_id] = run
        report = {
            "report_id": str(uuid.uuid4()),
            "incident_id": incident_id,
            "title": inc.title,
            "generated_at": utcnow(),
            "executive_summary": (
                f"{device_id} developed abnormal thermal behavior relative to its statistical digital twin. "
                f"Structured investigation ranked '{inc.likely_root_cause or 'pending'}' "
                f"with confidence {inc.confidence:.0%}. "
                f"{'Remediation was human-approved and applied.' if inc.approved_actions else 'No remediation approved yet.'}"
            ),
            "technical_summary": {
                "device_id": device_id,
                "health_score": st.health_score,
                "anomaly_score": st.anomaly_score,
                "twin_deviation": st.twin_deviation,
                "failure_probability": st.failure_prob,
                "predicted_failure_type": st.failure_type,
                "rul_hours": st.rul_hours,
                "likely_root_cause": inc.likely_root_cause,
                "confidence": inc.confidence,
            },
            "timeline": list(inc.timeline),
            "approvals": list(inc.approved_actions),
            "limitations": [
                "Telemetry and models are synthetic / demonstration-grade",
                "Digital twin is statistical, not transistor-level",
                "Not validated on real semiconductor production fleets",
            ],
            "evidence_refs": [a.alert_id for a in self.intel.alerts.values() if a.incident_id == incident_id][:10],
        }
        self.intel.reports[report["report_id"]] = report
        if inc.status in {"remediating", "investigating", "acknowledged", "open"} and st.twin_deviation < 0.35 and st.anomaly_score < 0.35:
            inc.status = "resolved"
            inc.resolved_at = utcnow()
            inc.outcome = "stabilized_after_approved_action"
            inc.timeline.append({"at": utcnow(), "type": "resolved", "message": "Incident resolved after observed stabilization"})
        run.output = report
        run.status = "completed"
        run.completed_at = utcnow()
        run.current_step = "complete"
        return report

    def _run_view(self, run: AgentRun) -> dict[str, Any]:
        return {
            "agent_run_id": run.agent_run_id,
            "agent_type": run.agent_type,
            "incident_id": run.incident_id,
            "device_id": run.device_id,
            "status": run.status,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "current_step": run.current_step,
            "tool_calls": run.tool_calls,
            "evidence": run.evidence,
            "decisions": run.decisions,
            "confidence": run.confidence,
            "approval_required": run.approval_required,
            "approval_status": run.approval_status,
            "output": run.output,
        }

    def _approval_view(self, ap: Approval) -> dict[str, Any]:
        return {
            "approval_id": ap.approval_id,
            "action": ap.action,
            "reason": ap.reason,
            "expected_impact": ap.expected_impact,
            "risk": ap.risk,
            "requested_by": ap.requested_by,
            "device_id": ap.device_id,
            "incident_id": ap.incident_id,
            "status": ap.status,
            "requested_at": ap.requested_at,
            "decided_at": ap.decided_at,
            "decided_by": ap.decided_by,
            "comments": ap.comments,
        }
