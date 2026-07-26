# SiliconPulse AI — Implementation Plan (Phase 0)

## Repository state at discovery

- Empty workspace (no prior source, no git history)
- Git initialized on `main` during Phase 1
- Working directory may include a space (`SiliconPulse AI`); package name remains `siliconpulse-ai`

## Delivery strategy

1. Ship phases in order with hard exit criteria ([ROADMAP.md](ROADMAP.md)).
2. Prefer modular monolith processes over many microservices.
3. Unblock the primary cooling-degradation demo before optional polish (Loki/Tempo/K8s).
4. Keep shared domain models in `packages/` to avoid duplication.
5. Document every simulated/experimental claim.

## Milestones

| ID | Name | Phases | Outcome |
| --- | --- | --- | --- |
| M0 | Foundation | 0–1 | Docs, structure, tooling |
| M1 | Data plane | 2–4 | Compose + simulator + ingest |
| M2 | Ops surface | 5–7 | API + UI + alerts/incidents |
| M3 | Intelligence | 8–11 | Anomaly, RUL, twin, RCA |
| M4 | Agents + GenAI | 12–13 | Copilot, agents, approvals |
| M5 | Cross-domain + ship | 14–17 | Healthcare, observability, CI, demo |

## Missing dependencies (host)

Observed on the initial engineering workstation:

| Tool | Status | Action |
| --- | --- | --- |
| Python | Present (3.14.x) | Prefer **3.12** via `.python-version` / uv for package compatibility |
| Node / npm | Present (Node 24 / npm 11) | Use for `apps/web` |
| uv | Not on PATH initially | Install from https://github.com/astral-sh/uv |
| Docker Compose | Not verified in Phase 1 | Required for Phase 2 |
| Ollama | Not required until Phase 12 | Optional local LLM |

## Risks

See [IMPLEMENTATION_CHECKLIST.md](../../IMPLEMENTATION_CHECKLIST.md) §Risks.

## Phase 1 acceptance

- [x] Required product/architecture docs written
- [x] Repository structure created
- [x] README, gitignore, env example, Makefile, checklist
- [x] Python and frontend dependency manifests
- [x] Scaffold smoke verification (manual import + file presence)
- [ ] Full `uv sync` / `npm install` / CI green — blocked until package registries are reachable and `uv` is installed

## Next task

**Phase 2 — Infrastructure:** implement `docker-compose.yml` with PostgreSQL, Redpanda (+ Console), Valkey, MinIO, Prometheus, Grafana, health checks, and init scripts for topics and buckets.
