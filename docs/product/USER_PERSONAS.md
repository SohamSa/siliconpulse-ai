# SiliconPulse AI — User Personas

## 1. Infrastructure Operator

### Goals

Keep the GPU / accelerator fleet stable and respond quickly to emerging issues.

### Needs

- Live fleet health and active alerts
- Rack status and incident priority
- Telemetry visibility (temperature, power, utilization, throughput)
- Clear operational recommendations

### Primary surfaces

- Overview, Fleet, Alerts, Incidents, Scenarios (when authorized)
- Device detail for triage
- Approvals for low-risk simulated actions (Operator role)

### Success moments

- Sees abnormal device before critical threshold breach
- Acknowledges alert, opens incident, understands recommended next step

---

## 2. Reliability Engineer

### Goals

Understand *why* devices degrade and validate model / twin behavior.

### Needs

- Device history and anomaly features
- Failure predictions and RUL
- Twin expected-vs-actual comparisons
- Root-cause evidence and similar incidents
- Model explanations (feature attribution)

### Primary surfaces

- Devices / Device Detail, Digital Twins, Lifecycle, Investigations
- Agents (root-cause runs), AI Copilot (grounded Q&A)
- Model metadata / system health for pipeline health

### Success moments

- Confirms device-level cooling degradation vs rack-wide failure using peer evidence
- Traces prediction to features and twin deviation without trusting the LLM alone

---

## 3. Operations Manager

### Goals

Prioritize maintenance spend and communicate risk to stakeholders.

### Needs

- Maintenance priority and downtime risk
- Replacement candidates and fleet lifecycle health
- Incident summaries and business-facing reports

### Primary surfaces

- Overview, Lifecycle, Maintenance, Reports, Incidents
- Executive summaries from Reporting Agent / Copilot

### Success moments

- Sees ranked replacement / PM candidates with RUL and health score
- Downloads or views an evidence-linked incident report after recovery

---

## 4. Administrator

### Goals

Operate the local platform safely: users, simulation, configuration, models.

### Needs

- User and role management
- Simulation controls and device registration
- Model configuration and system settings
- Permission enforcement

### Primary surfaces

- Settings, Scenarios, System Health, Devices (registration)
- User management APIs / UI

### Success moments

- Seeds demo users, resets fleet, configures Ollama model fallback
- Ensures high-impact actions require approval

---

## Role × permission summary (v1)

| Capability | Viewer | Engineer | Operator | Administrator |
| --- | --- | --- | --- | --- |
| View dashboards / devices / alerts / incidents / reports | ✓ | ✓ | ✓ | ✓ |
| Launch investigation / use copilot / acknowledge alerts | | ✓ | ✓ | ✓ |
| Inject simulations / resolve alerts / approve low-risk actions | | | ✓ | ✓ |
| Manage users / devices / models / system settings | | | | ✓ |

Authorization is enforced in the API, not only in the UI.

---

## Healthcare demo note

All personas interacting with the healthcare module must see:

> This module is a simulated device-monitoring demonstration. It is not a medical diagnostic system and must not be used for patient-care decisions.
