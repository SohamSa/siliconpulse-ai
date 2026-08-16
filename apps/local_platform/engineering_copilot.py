"""Evidence-grounded engineering copilot with explicit permission boundaries."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_type: str
    source_ref: str
    statement: str
    tags: tuple[str, ...]
    quality: float


@dataclass
class CopilotCase:
    case_id: str
    question: str
    created_at: str
    retrieved: list[Evidence] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    proposed_actions: list[dict[str, Any]] = field(default_factory=list)
    status: str = "draft"


class EngineeringCopilot:
    """Small auditable retrieval/ranking engine; no model is allowed to invent telemetry."""

    ALLOWED_READ_TOOLS = {"device_state", "twin", "peer_group", "incident_history", "monitor_history"}
    GATED_ACTIONS = {"redistribute_workload", "change_power_limit", "schedule_maintenance", "quarantine_wafer_lot"}

    def __init__(self, evidence: list[Evidence] | None = None) -> None:
        self.evidence = evidence or []
        self.cases: dict[str, CopilotCase] = {}
        self.approvals: dict[str, dict[str, Any]] = {}

    def add_evidence(self, item: Evidence) -> None:
        self.evidence.append(item)

    def retrieve(self, question: str, limit: int = 8) -> list[Evidence]:
        tokens = set(re.findall(r"[a-z0-9_]+", question.lower()))
        scored = []
        for item in self.evidence:
            haystack = set(re.findall(r"[a-z0-9_]+", (item.statement + " " + " ".join(item.tags)).lower()))
            overlap = len(tokens & haystack)
            if overlap:
                scored.append((overlap * item.quality, item))
        return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]]

    def investigate(self, question: str, live_facts: list[Evidence]) -> CopilotCase:
        for fact in live_facts:
            if fact.source_type not in self.ALLOWED_READ_TOOLS:
                raise ValueError(f"unapproved evidence source: {fact.source_type}")
        retrieved = live_facts + self.retrieve(question)
        support_cooling = [e for e in retrieved if set(e.tags) & {"thermal", "cooling", "fan", "peer_delta"}]
        contradict_rack = [e for e in retrieved if "healthy_peers" in e.tags]
        hypotheses = [
            {
                "rank": 1, "cause": "device_local_cooling_degradation",
                "supporting_evidence_ids": [e.evidence_id for e in support_cooling],
                "contradicting_evidence_ids": [],
                "reasoning": "Device-local thermal and cooling evidence is present.",
            },
            {
                "rank": 2, "cause": "rack_cooling_failure",
                "supporting_evidence_ids": [],
                "contradicting_evidence_ids": [e.evidence_id for e in contradict_rack],
                "reasoning": "Healthy rack peers weaken a shared rack explanation.",
            },
        ]
        missing = []
        tags = {tag for item in retrieved for tag in item.tags}
        if "inspection" not in tags:
            missing.append("Physical cooling-path inspection result")
        if "maintenance_history" not in tags:
            missing.append("Device maintenance and replacement history")
        case = CopilotCase(str(uuid.uuid4()), question, utcnow(), retrieved, hypotheses, missing)
        case.proposed_actions = [
            {"action": "schedule_maintenance", "reason": "Validate the leading cooling hypothesis", "approval_required": True},
            {"action": "redistribute_workload", "reason": "Reduce stress during investigation", "approval_required": True},
        ]
        case.status = "awaiting_human_review"
        self.cases[case.case_id] = case
        return case

    def request_action(self, case_id: str, action: str) -> dict[str, Any]:
        case = self.cases[case_id]
        if action not in self.GATED_ACTIONS:
            raise ValueError("action is not in the governed tool registry")
        if not any(item["action"] == action for item in case.proposed_actions):
            raise ValueError("action was not proposed by this investigation")
        approval = {"approval_id": str(uuid.uuid4()), "case_id": case_id, "action": action,
                    "status": "pending", "requested_at": utcnow(), "decided_at": None,
                    "decided_by": None, "audit_note": "No external action executed."}
        self.approvals[approval["approval_id"]] = approval
        return approval

    def decide(self, approval_id: str, approved: bool, reviewer: str) -> dict[str, Any]:
        approval = self.approvals[approval_id]
        if approval["status"] != "pending":
            raise ValueError("approval already decided")
        approval["status"] = "approved" if approved else "rejected"
        approval["decided_at"] = utcnow()
        approval["decided_by"] = reviewer
        approval["audit_note"] = "Approved for simulated execution only." if approved else "No action executed."
        return approval

    @staticmethod
    def case_view(case: CopilotCase) -> dict[str, Any]:
        return {"case_id": case.case_id, "question": case.question, "created_at": case.created_at,
                "evidence": [{"id": e.evidence_id, "source": e.source_ref, "statement": e.statement,
                              "quality": e.quality} for e in case.retrieved],
                "hypotheses": case.hypotheses, "missing_evidence": case.missing_evidence,
                "proposed_actions": case.proposed_actions, "status": case.status,
                "grounding_boundary": "Answer contains only retrieved evidence IDs and explicitly labeled inference."}
