# SiliconPulse AI — Implementation Checklist

Track delivery against the master product specification. Update status as phases complete.

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[-]` deferred

---

## Phase 0 — Discovery and planning

- [x] Inspect repository (empty)
- [x] Implementation plan / roadmap
- [x] Product requirements document
- [x] Business problems document
- [x] User personas document
- [x] System context document
- [x] Data flow document
- [x] AI strategy document
- [x] Agent design document
- [x] Identify risks and assumptions (see Phase 0 summary in README / this file §Risks)

## Phase 1 — Repository and tooling

- [x] Repository directory structure
- [x] `.gitignore`
- [x] `.env.example`
- [x] Root `README.md`
- [x] `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`
- [x] Python `uv` workspace (`pyproject.toml` + package members)
- [x] Frontend dependency config (`apps/web/package.json`, TypeScript strict)
- [x] Makefile with placeholder targets
- [x] PowerShell setup helper scaffold
- [x] Implementation checklist
- [x] Minimal unit test scaffolds (Python + Vitest)
- [ ] CI workflows (GitHub Actions) — Phase 16 primary; skeleton optional later
- [ ] `docker-compose.yml` — **Phase 2**

## Phase 2 — Infrastructure

- [x] PostgreSQL + init
- [x] Redpanda + Console + topics
- [x] Valkey
- [x] MinIO + buckets
- [x] Prometheus + Grafana
- [x] Health checks defined (+ runtime verification when Docker available)
- [x] `docker-compose.dev.yml` overlays
- [x] Docs: LOCAL_SETUP, DEPLOYMENT, TROUBLESHOOTING updates

## Phase 3 — Telemetry simulator

- [x] Configurable fleet (≥50 GPUs), racks, seeds — **local demo + telemetry-generator package**
- [x] True vs reported state
- [x] Failure scenarios (14+)
- [x] Local in-process bus (Compose/Redpanda path optional later)
- [x] Scenario inject / stop / reset APIs (`apps/local_platform`)
- [ ] Unit tests (ranges, correlations, determinism) — pending when PyPI available

## Phase 4 — Streaming and storage

- [ ] Validation consumer
- [ ] Storage consumer (Postgres + Valkey)
- [ ] Archival to Parquet / MinIO
- [ ] Integration tests
- [ ] Prometheus metrics for pipeline

## Phase 5 — API

- [ ] `/health`, `/ready`, `/metrics`
- [ ] Fleet / devices / racks / scenarios endpoints
- [ ] AuthN/Z roles
- [ ] OpenAPI, pagination, request IDs
- [ ] Alembic migrations + seed

## Phase 6 — Frontend (core)

- [ ] Dark operational shell + navigation
- [ ] Overview, Fleet, Devices, Device Detail, Racks, Scenarios
- [ ] SSE live updates
- [ ] Loading / empty / error states

## Phase 7 — Alerts and incidents

- [ ] Rule engine + dedupe + lifecycle
- [ ] Incident grouping
- [ ] Alerts / Incidents UI

## Phase 8 — Anomaly detection

- [ ] Feature engineering
- [ ] Isolation Forest (+ baselines)
- [ ] MLflow tracking
- [ ] UI anomaly signals

## Phase 9 — Failure prediction and lifecycle

- [ ] Classifiers, RUL, survival demo
- [ ] Health score + lifecycle states
- [ ] Lifecycle / maintenance UI

## Phase 10 — Digital twin

- [ ] Statistical twins + deviation scoring
- [ ] Versioning / calibration hooks
- [ ] Digital Twins UI

## Phase 11 — Root cause

- [ ] Weighted evidence engine
- [ ] Peer / firmware / workload comparisons
- [ ] Investigation UI
- [ ] No hidden scenario labels in RCA

## Phase 12 — Generative AI

- [ ] Ollama client + model fallback
- [ ] Grounded copilot pipeline
- [ ] Guardrails + mock for CI

## Phase 13 — Agents

- [ ] Specialized agents + tools + persistence
- [ ] Approval workflow UI/API
- [ ] Audit / events
- [ ] Demo path: RCA → maintenance → approve → recover → report

## Phase 14 — Healthcare demo

- [ ] Healthcare devices + scenarios
- [ ] Disclaimers on all surfaces
- [ ] Device health vs signal separation

## Phase 15 — Observability

- [ ] Full Prometheus metric set
- [ ] Grafana dashboards (7)
- [ ] OpenTelemetry traces
- [ ] Loki / Tempo after core

## Phase 16 — Hardening

- [ ] Unit / integration / Playwright / Locust / data-quality tests
- [ ] Trivy + Dependabot
- [ ] GitHub Actions CI
- [ ] Security review of auth, agents, uploads

## Phase 17 — Packaging

- [ ] Demo automation scripts
- [ ] Docs complete per §36
- [ ] Screenshots
- [ ] Final success criteria walkthrough

---

## Primary demo path checklist

- [ ] Start ≥50 GPU fleet healthy
- [ ] Inject cooling degradation on GPU-042
- [ ] Twin deviation before critical threshold
- [ ] Anomaly + prediction + RUL drop
- [ ] Alert + incident
- [ ] Root-cause agent → device-level cooling
- [ ] Maintenance agent → approval → simulated action
- [ ] Stabilization + resolve + report + timeline

---

## Risks and open issues (Phase 0/1)

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Windows + Make / Docker Desktop variability | Setup friction | Provide PowerShell scripts; document Docker Desktop requirement |
| Host Python 3.14 vs package support | `uv sync` / wheel failures | Pin `requires-python = ">=3.12,<3.14"`; use `.python-version` 3.12 |
| Package registry / network hangs | Cannot install deps in session | Retry `make setup`; CI will validate when network allows |
| Ollama optional on host | Copilot flaky in demos | Mock fallback; env-configurable model |
| Scope breadth (17 phases) | Incomplete product if rushed | Strict phase exits; demo-critical path first |
| `uv` workspace member count | Sync complexity | Keep early members small; add services as packages when implemented |
| Synthetic-data overclaim | Trust risk | Mandatory disclaimers in README and model cards |

---

## Assumptions

1. Docker Desktop (or compatible Compose engine) will be available for Phase 2+.
2. Python 3.12+ and Node 20+ are available for local non-container development.
3. Workspace root is this repository (folder name may include spaces on Windows).
4. Intelligence workers may initially co-locate with the API or ingestion process until extraction is justified.
5. Healthcare and GPU domains share packages but separate topics/tables/UI routes.
