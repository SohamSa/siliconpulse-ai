"""Redpanda topic names."""

from __future__ import annotations

TELEMETRY_RAW = "telemetry.raw"
TELEMETRY_VALIDATED = "telemetry.validated"
TELEMETRY_INVALID = "telemetry.invalid"
DEVICE_EVENTS = "device.events"
ALERTS_GENERATED = "alerts.generated"
ALERTS_UPDATED = "alerts.updated"
PREDICTIONS_GENERATED = "predictions.generated"
DIGITAL_TWIN_UPDATED = "digital-twin.updated"
INCIDENTS_CREATED = "incidents.created"
INCIDENTS_UPDATED = "incidents.updated"
MAINTENANCE_RECOMMENDED = "maintenance.recommended"
MAINTENANCE_APPROVED = "maintenance.approved"
AGENT_EVENTS = "agent.events"
AGENT_ACTIONS = "agent.actions"
AGENT_FAILURES = "agent.failures"
REPORTS_GENERATED = "reports.generated"
HEALTHCARE_TELEMETRY = "healthcare.telemetry"

ALL_TOPICS: tuple[str, ...] = (
    TELEMETRY_RAW,
    TELEMETRY_VALIDATED,
    TELEMETRY_INVALID,
    DEVICE_EVENTS,
    ALERTS_GENERATED,
    ALERTS_UPDATED,
    PREDICTIONS_GENERATED,
    DIGITAL_TWIN_UPDATED,
    INCIDENTS_CREATED,
    INCIDENTS_UPDATED,
    MAINTENANCE_RECOMMENDED,
    MAINTENANCE_APPROVED,
    AGENT_EVENTS,
    AGENT_ACTIONS,
    AGENT_FAILURES,
    REPORTS_GENERATED,
    HEALTHCARE_TELEMETRY,
)
