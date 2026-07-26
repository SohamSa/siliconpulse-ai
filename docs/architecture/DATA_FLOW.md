# SiliconPulse AI — Data Flow

## Principles

1. Telemetry is **event-driven** through Redpanda.
2. PostgreSQL is the **durable source of truth**.
3. Valkey is **ephemeral**: latest state, dedupe, locks, SSE fanout.
4. MinIO stores **large artifacts**: Parquet, models, reports.
5. Intelligence consumes validated telemetry / derived features — not raw unvalidated streams for decisions.
6. Generative AI explains **structured evidence**; it does not invent measurements.

## End-to-end telemetry path

```mermaid
flowchart LR
  SIM[Telemetry Generator] -->|telemetry.raw| RP[(Redpanda)]
  RP --> VAL[Validation Consumer]
  VAL -->|telemetry.validated| RP
  VAL -->|telemetry.invalid| RP
  RP --> STOR[Storage Consumer]
  STOR --> PG[(PostgreSQL)]
  STOR --> VK[(Valkey latest state)]
  STOR --> ARCH[Archival Job]
  ARCH --> MINIO[(MinIO Parquet)]
  PG --> API[FastAPI]
  VK --> API
  API -->|SSE / REST| WEB[Next.js UI]
```

### Non-negotiable rule

The simulator **must not** write live telemetry directly to PostgreSQL. Path is always:

`simulator → telemetry.raw → validation → telemetry.validated → storage → Postgres/Valkey`.

## Redpanda topics (v1)

| Topic | Producers | Consumers |
| --- | --- | --- |
| `telemetry.raw` | telemetry-generator | validation |
| `telemetry.validated` | validation | storage, alert, twin, prediction |
| `telemetry.invalid` | validation | monitoring / quarantine |
| `healthcare.telemetry` | healthcare simulator path | healthcare validation/storage |
| `device.events` | API / device registry | cache invalidation, audit |
| `alerts.generated` / `alerts.updated` | alert-service | incident grouping, API/SSE, agents |
| `predictions.generated` | prediction-service | API, agents, lifecycle |
| `digital-twin.updated` | digital-twin-service | API, alerts, agents |
| `incidents.created` / `incidents.updated` | incident module | API/SSE, agents, reporting |
| `maintenance.recommended` / `maintenance.approved` | maintenance / approvals | agents, API |
| `agent.events` / `agent.actions` / `agent.failures` | agent-service | audit, API/SSE, commander |
| `reports.generated` | reporting-service | API, MinIO link |

### Event envelope (all topics)

Every event includes:

- `event_id`, `event_type`, `schema_version`
- `created_at`, `correlation_id`, optional `causation_id`
- `source_service`, `payload`

Shared models live in `packages/shared-events`.

## Intelligence data flow

```mermaid
flowchart TB
  V[telemetry.validated] --> FE[Feature Engineering]
  FE --> AD[Anomaly Detection]
  FE --> FC[Failure Classification]
  FE --> RUL[RUL / Survival]
  FE --> TW[Digital Twin]
  AD --> AL[Alert Rules + Dedupe]
  TW --> AL
  FC --> AL
  AL --> IG[Incident Grouping]
  IG --> RCA[Root-Cause Evidence Engine]
  AD --> RCA
  TW --> RCA
  FC --> RCA
  RCA --> AG[Agents]
  FC --> AG
  RUL --> AG
  AG -->|approval required| HUM[Human Approver]
  HUM -->|approved action| SIM[Simulator intervention]
  AG --> REP[Reporting]
  RCA --> COP[Copilot retrieval]
  AG --> COP
  COP --> OLL[Ollama]
```

### Structured intelligence stack

| Layer | Responsibility | Must not |
| --- | --- | --- |
| Predictive models | Produce scores, classes, attributions | Claim real-world validation |
| Root-cause engine | Combine evidence, rank hypotheses | Use hidden scenario labels |
| Generative AI | Explain retrieved evidence | Invent telemetry or execute actions |
| Agents | Coordinate tools and workflows | Bypass approval or tool allowlists |

## Primary demo sequence (cooling degradation)

```mermaid
sequenceDiagram
  participant Op as Operator UI
  participant API as API
  participant Sim as Simulator
  participant RP as Redpanda
  participant Intel as Intelligence
  participant Ag as Agents

  Op->>API: Inject cooling degradation GPU-042
  API->>Sim: Scenario inject
  loop Telemetry
    Sim->>RP: telemetry.raw
    RP->>Intel: validated path
    Intel->>API: twin deviation / anomaly / prediction
    API-->>Op: SSE updates
  end
  Intel->>RP: alerts.generated / incidents.created
  Op->>API: Launch root-cause agent
  API->>Ag: Root-Cause Investigation
  Ag->>API: Ranked hypotheses + evidence
  Op->>API: Launch predictive maintenance agent
  Ag->>API: Approval request
  Op->>API: Approve simulated action
  API->>Sim: Apply intervention
  Note over Sim,Op: Temperature stabilizes
  Ag->>API: Report generated (MinIO + Postgres)
```

## Cache and consistency

| Data | System of record | Cache |
| --- | --- | --- |
| Historical telemetry | PostgreSQL (+ Parquet archive) | Short query caches optional |
| Latest device state | PostgreSQL `device_latest_state` | Valkey hot cache |
| Active alerts | PostgreSQL | Valkey + dedupe keys |
| Agent locks / workflow | PostgreSQL durable state | Valkey short locks |
| Models / reports | MinIO + metadata in Postgres | — |

## Healthcare path

Healthcare telemetry uses `healthcare.telemetry` (and domain tables/UI) with the same validation → storage pattern, plus mandatory safety disclaimers on every read/generated surface. Physiological signals are **simulated** and never used to infer medical conditions.
