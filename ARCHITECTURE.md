# SiliconPulse AI — Architecture

## Summary

SiliconPulse AI is a **local-first, event-driven, modular monolith** that transforms simulated hardware telemetry into observability, predictive maintenance, digital twins, structured root-cause analysis, grounded generative explanations, and human-supervised agents.

Detailed diagrams:

- [System context](docs/architecture/SYSTEM_CONTEXT.md)
- [Data flow](docs/architecture/DATA_FLOW.md)
- Deployment notes will expand in `docs/architecture/DEPLOYMENT.md` (Phase 2+)

## Architectural decisions (Phase 0/1)

| Decision | Choice | Rationale |
| --- | --- | --- |
| AD-001 Deployment | Docker Compose first | Local reproducibility; K8s only after demo works |
| AD-002 Telemetry path | Redpanda mandatory | Decouple simulator from storage; enable multiple consumers |
| AD-003 Service granularity | Modular monolith + extractable `services/` | Avoid premature microservice sprawl |
| AD-004 Source of truth | PostgreSQL | Relational domain entities with indexes |
| AD-005 Cache | Valkey | Hot state, dedupe, locks, SSE — not durable SoT |
| AD-006 Object store | MinIO | Parquet, models, reports |
| AD-007 Intelligence layering | Models → RCA → LLM → Agents | Prevent LLM inventing diagnoses |
| AD-008 Human control | Approval records for high-impact actions | Safety and auditability |
| AD-009 Python tooling | `uv` workspace | Fast, reproducible Python deps |
| AD-010 Frontend | Next.js + TypeScript strict + Tailwind | Operational UI with typed clients |
| AD-011 GenAI | Ollama local | No paid LLM APIs |
| AD-012 Cross-domain | Shared core + healthcare module | Prove architecture transfer with safety boundaries |

## Repository layout

Matches the product specification under `apps/`, `services/`, `packages/`, `ml/`, `infrastructure/`, `docs/`, `tests/`, `scripts/`.

### Documented deviations

| Deviation | Reason |
| --- | --- |
| Workspace folder may be `SiliconPulse AI` (with space) on disk | Existing download path; package name remains `siliconpulse-ai` |
| Not all `services/*` are uv workspace members yet | Only scaffolding packages that need early shared deps; others join when implemented |
| `docker-compose.yml` absent until Phase 2 | Explicit phase boundary from master prompt |
| Intelligence services may co-locate in fewer containers initially | Modular monolith principle; folders preserved for extraction |

## Runtime processes (target)

1. **telemetry-generator** — publishes `telemetry.raw`
2. **ingestion-service** — validate + store + archive
3. **api** — REST / SSE / auth / orchestration entrypoints
4. **web** — Next.js UI
5. **intelligence workers** — alerts, predictions, twins, RCA, agents, reporting (packaging TBD per phase)
6. **infra** — Postgres, Redpanda, Valkey, MinIO, Prometheus, Grafana, NGINX
7. **ollama** — host or optional container

## Security & trust

See [SECURITY.md](SECURITY.md). Key boundaries: no simulator→Postgres shortcut; no unrestricted agents; no medical claims; no secrets in git.

## Evolution

After the primary cooling-degradation demo works end-to-end, consider:

- Splitting hot consumers for scale
- Loki / Tempo
- kind + Helm demonstration
- Stronger retrieval (still local/open-source) if runbook volume grows
