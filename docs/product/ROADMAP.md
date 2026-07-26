# SiliconPulse AI — Implementation Roadmap

Phased delivery. Each phase ends with runnable, tested functionality. Do not skip Redpanda, human approval, or honest limitation docs.

## Phase 0 — Discovery and planning ✅ (this milestone)

- Inspect repository; define architecture and milestones
- Product / architecture / AI / agent design docs
- Acceptance criteria and implementation checklist

## Phase 1 — Repository and tooling ✅ (this milestone)

- Repository structure, `.gitignore`, `.env.example`
- `uv` Python workspace and Next.js app skeleton config
- Makefile placeholders, lint/test skeletons
- README and documentation skeleton

## Phase 2 — Infrastructure ✅

- Docker Compose: PostgreSQL, Redpanda, Redpanda Console, Valkey, MinIO, Prometheus, Grafana
- Health checks, init scripts (topics, buckets, DB extensions)
- Windows helpers: `scripts/setup/Infra-Up.ps1` / `Infra-Down.ps1`
- NGINX reverse proxy deferred until apps exist (Phase 5–6)

**Exit:** `docker compose up` healthy for all infra services.

## Phase 3 — Telemetry simulator

- Configurable fleet (≥50 GPUs), racks, seeds, scenarios
- True vs reported sensor state; cooling and other failure modes
- **Primary runnable path:** `apps/local_platform` (no Docker)
- Optional Compose/Redpanda publisher for later full-stack work

**Exit (local):** Guided demo injects cooling degradation and drives intelligence.

## Phase 4 — Streaming and storage

- Validation consumer → `telemetry.validated` / `telemetry.invalid`
- Storage consumer → PostgreSQL + Valkey latest state
- Archival job → Parquet in MinIO

**Exit:** End-to-end ingest integration test.

## Phase 5 — API

- FastAPI `/api/v1` for fleet, devices, racks, scenarios, health/ready/metrics
- AuthN/Z skeleton (roles)
- OpenAPI, pagination, request IDs

**Exit:** API tests against Compose Postgres/Valkey.

## Phase 6 — Frontend (core)

- Overview, Fleet, Devices, Device Detail, Racks, Scenarios
- Dark operational visual language; SSE for live updates

**Exit:** Operator can inject scenario and see live telemetry.

## Phase 7 — Alerts and incidents

- Rule engine, deduplication, lifecycle
- Incident grouping; UI for alerts/incidents

**Exit:** Cooling scenario creates alert + incident without spam.

## Phase 8 — Anomaly detection

- Feature engineering; Isolation Forest (+ baselines)
- MLflow tracking; UI anomaly signals

**Exit:** Twin/anomaly rises before critical threshold in demo.

## Phase 9 — Failure prediction and lifecycle

- Classifiers, RUL, survival demo, health score
- Lifecycle / maintenance views

**Exit:** Predicted cooling degradation + declining RUL on demo device.

## Phase 10 — Digital twin

- Statistical twins, deviation scoring, versioning, calibration hooks
- Digital Twins UI

**Exit:** Expected vs actual visible; deviation drives early alert path.

## Phase 11 — Root cause

- Weighted evidence engine; peer/firmware/workload comparisons
- Investigation UI; no hidden scenario labels

**Exit:** Demo concludes device-level cooling degradation.

## Phase 12 — Generative AI

- Ollama integration; grounded copilot; guardrails
- Mock fallback for CI

**Exit:** Copilot answers cite evidence; refuses invention.

## Phase 13 — Agents

- Six specialized agents + domain adaptation later
- Tool allowlists, persistence, approval workflow, audit

**Exit:** RCA + maintenance agents with approval → simulated recovery.

## Phase 14 — Healthcare demo

- Second domain telemetry + UI + disclaimers
- Separation of device health vs simulated signals

**Exit:** Healthcare page always shows non-diagnostic warnings.

## Phase 15 — Observability

- Prometheus metrics, Grafana dashboards, OpenTelemetry traces
- Loki/Tempo after core works

**Exit:** Platform / pipeline / agent dashboards load locally.

## Phase 16 — Hardening

- Unit, integration, Playwright E2E, Locust, data-quality tests
- Security baseline, Trivy, Dependabot, CI workflows

**Exit:** CI green locally/GitHub; E2E demo path automated.

## Phase 17 — Packaging

- Demo scripts, docs polish, screenshots, final setup UX
- Optional kind/Helm *after* Compose is solid

**Exit:** Final success criteria in PRD §7 / master prompt §46 met.

---

## Milestones (demo-critical path)

| Milestone | Phases | Demo capability |
| --- | --- | --- |
| M1 Infra + ingest | 2–4 | Telemetry flowing |
| M2 Ops UI | 5–7 | Inject + see alert/incident |
| M3 Intelligence | 8–11 | Anomaly, RUL, twin, RCA |
| M4 Agents + GenAI | 12–13 | Investigation + approval + report |
| M5 Cross-domain + ship | 14–17 | Healthcare + CI + docs |

---

## Explicitly deferred in Phase 0/1

- Advanced ML training pipelines
- Agent orchestration implementation
- Kubernetes / Helm charts beyond empty placeholders
- Loki / Tempo
