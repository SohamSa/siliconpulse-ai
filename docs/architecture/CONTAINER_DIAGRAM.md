# Container Diagram

## Phase 2 infrastructure containers

```mermaid
flowchart TB
  subgraph compose ["Docker Compose — siliconpulse-ai"]
    PG[(PostgreSQL)]
    VK[(Valkey)]
    RP[Redpanda]
    RPC[Redpanda Console]
    MN[(MinIO)]
    PROM[Prometheus]
    GRAF[Grafana]
    RPI[redpanda-init]
    MNI[minio-init]
  end

  RPI -->|rpk topic create| RP
  MNI -->|mc mb| MN
  RPC --> RP
  GRAF --> PROM
  PROM -->|scrape admin| RP
```

## System context

See [SYSTEM_CONTEXT.md](SYSTEM_CONTEXT.md) for C4 Level 1/2 diagrams including future API/web/simulator containers.

## Data flow

See [DATA_FLOW.md](DATA_FLOW.md) for telemetry topic paths that will attach in Phases 3–4.
