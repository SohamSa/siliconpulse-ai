# Troubleshooting

## Infrastructure (Phase 2)

### Compose file fails to validate

```bash
docker compose -f docker-compose.yml config
```

Ensure Docker Desktop is running and Compose v2 is available (`docker compose version`).

### Healthcheck stuck on `starting`

1. `docker compose ps`
2. `docker compose logs <service>`
3. Confirm host resources (RAM/CPU) and that required ports are free

### Redpanda topics missing

```bash
docker compose logs redpanda-init
docker compose run --rm redpanda-init
docker exec sp-redpanda rpk topic list --brokers localhost:9092
```

### MinIO buckets missing

```bash
docker compose logs minio-init
docker compose run --rm minio-init
```

### Grafana cannot reach Prometheus

Inside Compose they use `http://prometheus:9090`. Confirm both containers are on `siliconpulse-net` and Prometheus is healthy.

### Windows path with spaces

This repository may live under a folder with spaces. Prefer PowerShell helpers under `scripts/setup/` and quote paths. Compose bind mounts use relative paths from the project root.
