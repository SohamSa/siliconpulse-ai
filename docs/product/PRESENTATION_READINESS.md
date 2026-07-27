# Presentation Readiness — Honest Technical Positioning

## What is implemented

- Browser-only 50-GPU executive demo
- Standard-library local Python demo and API
- Coupled synthetic telemetry with true versus reported state
- Statistical operational temperature twin
- Trained cooling-anomaly logistic regression with held-out synthetic evaluation
- Deterministic multi-cause risk scoring and demo RUL
- Alert deduplication and incident grouping
- Evidence-ranked RCA that excludes hidden scenario labels
- Auditable agent workflow prototypes
- Human approval before simulated remediation
- Evidence-linked incident report

## What is not implemented

- Validation on real production hardware telemetry
- Calibrated physical failure probability
- Scientifically validated RUL or survival model
- Transistor-level or physics-simulation twin
- LLM/Ollama copilot
- Autonomous multi-agent reasoning
- Production authentication, authorization, persistence, or fleet-scale SLOs
- Connected end-to-end Redpanda/Postgres/MinIO deployment
- Medical or diagnostic capability

## Preferred vocabulary

| Avoid | Use |
| --- | --- |
| Production failure probability | Synthetic-model probability or deterministic risk score |
| Accurate RUL | Demo RUL estimate |
| Physics digital twin | Statistical operational twin |
| Autonomous AI agents | Auditable agent workflow prototypes |
| Production platform | Executive prototype and architecture foundation |
| Medical AI | Non-diagnostic sensor simulation |

## Technical questions to expect

1. How are train and test data separated?
2. Why do synthetic held-out metrics look unusually high?
3. How would coefficients and thresholds be recalibrated for a customer?
4. How do you distinguish workload heat from cooling degradation?
5. How do you prevent hidden simulator labels from leaking into RCA?
6. Which values are trained probabilities versus heuristic scores?
7. What happens when firmware, workload, or rack conditions shift?
8. How would the in-process demo evolve into a streaming deployment?
9. What customer data and labels are required for a pilot?
10. Which decisions remain human-gated?

## Recommended answer

The prototype proves an execution pattern: telemetry becomes structured evidence, evidence
becomes a ranked decision, and high-impact action remains human-controlled. It does not prove
production semiconductor reliability. A design-partner pilot would begin with schema mapping,
historical incident reconstruction, device/time-aware validation, calibration, and shadow-mode
operation before any operational recommendation is trusted.
