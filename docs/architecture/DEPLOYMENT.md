# Deployment

## v1 target — Docker Compose (Phase 2)

Local developer workstation via Docker Compose.

```bash
cp .env.example .env
docker compose up -d
# Windows:
# ./scripts/setup/Infra-Up.ps1
```

### Services

| Service | Container | Host ports | Purpose |
| --- | --- | --- | --- |
| PostgreSQL 16 | `sp-postgres` | `5432` | Durable source of truth |
| Valkey 8 | `sp-valkey` | `6379` | Cache, dedupe, locks, SSE fanout |
| Redpanda | `sp-redpanda` | `19092` (Kafka), `18081` (schema), `9644` (admin) | Event streaming |
| Redpanda Console | `sp-redpanda-console` | `8080` | Topic / consumer UI |
| MinIO | `sp-minio` | `9000` (API), `9001` (console) | Object storage |
| Prometheus | `sp-prometheus` | `9090` | Metrics |
| Grafana OSS | `sp-grafana` | `3001` | Dashboards |

One-shot init jobs:

- `redpanda-init` — creates required topics
- `minio-init` — creates required buckets

### Network

All services join Compose network `siliconpulse-net`.

Internal Kafka broker address for other containers: `redpanda:9092`  
Host producers (later): `localhost:19092`

### Volumes

Named volumes retain data across restarts: `postgres_data`, `valkey_data`, `redpanda_data`, `minio_data`, `prometheus_data`, `grafana_data`.

To wipe local state:

```bash
docker compose down -v
```

### Health checks

Every long-running service defines a Docker healthcheck. Init containers exit `0` after successful setup.

### Dev overlay

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Not in Phase 2

- API / web / simulator containers (Phases 3–6)
- NGINX reverse proxy (when apps exist)
- Ollama (Phase 12; typically host-side)
- Kubernetes / Helm (after Compose demo works)

## Later demonstration

kind + Kubernetes + Helm — only after the Compose-based product demo works end-to-end.
