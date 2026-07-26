# SiliconPulse AI — Product Requirements

## 1. Product summary

**SiliconPulse AI** is a local-first hardware intelligence platform that converts real-time telemetry from GPUs, AI accelerators, semiconductor devices, servers, racks, and simulated healthcare sensors into operational intelligence:

- real-time hardware observability
- anomaly detection
- failure prediction
- remaining useful life (RUL) estimation
- device health scoring
- lifecycle intelligence
- statistical digital twins
- root-cause analysis
- generative AI explanations
- predictive maintenance recommendations
- human-supervised AI-agent workflows
- incident coordination
- operational reports

The platform demonstrates how raw hardware signals become trusted operational decisions. Version 1 runs entirely locally via Docker Compose using free, open-source, community, or self-hosted technologies only.

## 2. Non-goals (v1)

- Cloud dependency (AWS, Azure, GCP)
- Paid OpenAI, Datadog, databases, vector DBs, or streaming SaaS
- Production claims of semiconductor validation
- Medical diagnosis or clinical decision support
- Kubernetes-first deployment (Compose first; kind/Helm later)

## 3. Primary demonstration

The platform must support an end-to-end cooling-degradation demo:

1. Start ≥50 simulated GPUs across several racks in a healthy state.
2. Inject cooling degradation into a selected device (e.g. `GPU-042`).
3. Temperature rises gradually while remaining below critical static thresholds initially.
4. Digital twin detects abnormal deviation; anomaly score increases.
5. Failure category predicted as cooling degradation; RUL decreases.
6. Alert and incident created; Root-Cause Investigation Agent runs.
7. Evidence: peers, workload, firmware, fan efficiency, twin deviation.
8. Conclusion: device-level cooling degradation (not rack-wide).
9. Predictive Maintenance Agent proposes simulated actions (e.g. workload redistribution, fan inspection).
10. Human approval required; action applied; temperature stabilizes.
11. Health updated; incident resolved; report generated; timeline preserved.

## 4. Functional requirements by business problem

### BP1 — AI hardware observability

- Fleet / rack / device health views
- Live telemetry (temp, power, utilization, throughput, memory errors)
- Abnormal-device ranking and grouped incidents
- Real-time UI updates (SSE)

### BP2 — Predictive maintenance and lifecycle

- Anomaly detection, failure-category prediction, failure probability
- RUL, survival probabilities (24h / 7d)
- Health score, lifecycle state, maintenance / replacement recommendations

### BP3 — Root-cause investigation

- Evidence collection, peer/rack/workload/firmware comparison
- Feature attribution (SHAP or equivalent)
- Ranked hypotheses with supporting / contradicting evidence
- Similar-incident retrieval; next diagnostic checks

### BP4 — Device-specific digital twins

Per device: expected vs actual temperature, power, throughput, fan speed, error rate; deviation metrics; confidence; twin version.

### BP5 — Cross-domain (healthcare simulation)

Simulated healthcare sensors with device-health vs signal-quality separation, mandatory disclaimers, human review required.

## 5. Target users

| Persona | Primary needs |
| --- | --- |
| Infrastructure Operator | Live fleet, alerts, rack status, recommendations |
| Reliability Engineer | History, anomalies, twins, RCA evidence, explanations |
| Operations Manager | Priority, downtime risk, lifecycle, reports |
| Administrator | Users, simulation, devices, models, roles |

## 6. Technical constraints

- Event-driven telemetry via Redpanda (simulator must not write Postgres directly)
- Modular monolith first; extract services only with strong justification
- Structured intelligence: models → evidence; RCA → ranked evidence; LLM explains only
- Human-in-the-loop for high-impact actions
- Reproducible seeds, pinned deps, migrations, audit trails

## 7. Success criteria (product)

A new user can clone, compose-up, log in, inject failure, observe anomaly → prediction → twin deviation → alert → incident → investigation → approval → recovery → report, explore healthcare demo and Grafana, run tests, and read honest limitations.

## 8. Limitations (must document)

- Synthetic telemetry and models trained on synthetic data
- Demonstration-grade predictions; simplified semiconductor behavior
- Statistical (not transistor-level) digital twins
- Healthcare module is simulated and non-diagnostic
- Agent actions are simulated and human-supervised
- No claim of production-scale performance
