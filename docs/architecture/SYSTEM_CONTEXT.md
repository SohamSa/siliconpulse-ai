# SiliconPulse AI — System Context

## Purpose

Describe who uses SiliconPulse AI, what external systems it depends on (all local/self-hosted), and the major containers that make up the system.

## System context (C4 Level 1)

```mermaid
C4Context
title SiliconPulse AI — System Context

Person(operator, "Infrastructure Operator", "Monitors fleet health and alerts")
Person(sre, "Reliability Engineer", "Investigates anomalies and root causes")
Person(mgr, "Operations Manager", "Prioritizes maintenance and reviews reports")
Person(admin, "Administrator", "Manages users, simulation, and config")

System(sp, "SiliconPulse AI", "Local-first hardware intelligence platform")

System_Ext(ollama, "Ollama", "Local instruction LLM for grounded explanations")
System_Ext(browser, "Web Browser", "Operator workstation UI")

Rel(operator, sp, "Uses UI / API")
Rel(sre, sp, "Uses UI / API")
Rel(mgr, sp, "Uses UI / reports")
Rel(admin, sp, "Configures and administers")
Rel(sp, ollama, "Grounded prompts / completions")
Rel(browser, sp, "HTTPS via NGINX")
```

### External dependencies (local only)

| System | Role | Notes |
| --- | --- | --- |
| Ollama | Generative explanations | Optional at runtime; mock fallback in tests |
| Operator browser | UI | Next.js served behind NGINX |

No AWS, Azure, GCP, paid OpenAI, or paid observability SaaS.

## Container overview (C4 Level 2)

```mermaid
C4Container
title SiliconPulse AI — Containers

Person(user, "Platform User")

System_Boundary(sp, "SiliconPulse AI") {
  Container(web, "Web UI", "Next.js / React", "Operational dashboards and workflows")
  Container(api, "API", "FastAPI", "Versioned REST + SSE + auth")
  Container(sim, "Telemetry Generator", "Python", "Simulated GPU / healthcare fleet")
  Container(ingest, "Ingestion Pipeline", "Python consumers", "Validate, store, archive")
  Container(intel, "Intelligence Modules", "Python", "Alerts, twins, predictions, RCA, agents, reports")
  ContainerDb(pg, "PostgreSQL", "RDBMS", "Source of truth")
  ContainerDb(valkey, "Valkey", "Cache / pub-sub", "Latest state, dedupe, locks, SSE fanout")
  ContainerDb(minio, "MinIO", "Object store", "Parquet, models, reports")
  ContainerQueue(rp, "Redpanda", "Kafka-compatible", "Event streaming")
  Container(obs, "Observability", "Prometheus / Grafana / OTel", "Metrics and traces")
}

System_Ext(ollama, "Ollama")

Rel(user, web, "Uses")
Rel(web, api, "REST / SSE")
Rel(sim, rp, "Publishes telemetry.raw")
Rel(ingest, rp, "Consumes / publishes topics")
Rel(ingest, pg, "Writes telemetry / state")
Rel(ingest, valkey, "Latest state cache")
Rel(ingest, minio, "Archives Parquet")
Rel(api, pg, "Reads / writes domain entities")
Rel(api, valkey, "Cache / SSE")
Rel(api, intel, "Invokes modules / services")
Rel(intel, rp, "Agent and domain events")
Rel(intel, ollama, "Grounded generation")
Rel(api, obs, "Exports metrics / traces")
```

## Modular monolith principle

v1 favors **clear Python modules** with shared packages (`shared-models`, `shared-events`, `shared-db`, …) and a small set of runnable processes:

| Process | Responsibility |
| --- | --- |
| `apps/api` | HTTP API, auth, SSE, orchestration entrypoints |
| `telemetry-generator` | Simulation + scenario control |
| `ingestion-service` | Validate + store + archive consumers |
| Intelligence workers (may co-locate initially) | Alerts, predictions, twins, RCA, agents, reporting |

Separate Deployable folders under `services/` exist for future extraction. Co-location in fewer containers is preferred until scaling or ownership requires splits. **Document any co-location in `ARCHITECTURE.md`.**

## Trust boundaries

1. **Simulator → Redpanda only** for telemetry (never direct Postgres writes for live telemetry).
2. **LLM** receives grounded context only; cannot mutate state or invent telemetry as fact.
3. **Agents** call allowlisted tools; high-impact actions require human approval records.
4. **Healthcare domain** is isolated in API/UI with mandatory disclaimers.

## Deployment context (v1)

```text
Developer machine
  └── Docker Compose
        ├── infra (Postgres, Redpanda, Valkey, MinIO, Prometheus, Grafana, NGINX)
        ├── apps (api, web)
        ├── services (simulator, ingestion, intelligence workers)
        └── optional Ollama (host or container)
```

Kubernetes (kind + Helm) is a **later** demonstration only after Compose works end-to-end.
