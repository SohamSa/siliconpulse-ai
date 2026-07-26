FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/packages/shared-models/src:/app/packages/shared-events/src:/app/packages/shared-utils/src:/app/packages/shared-observability/src:/app/services/telemetry-generator/src

RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY packages/shared-models /app/packages/shared-models
COPY packages/shared-events /app/packages/shared-events
COPY packages/shared-utils /app/packages/shared-utils
COPY packages/shared-observability /app/packages/shared-observability
COPY services/telemetry-generator /app/services/telemetry-generator

RUN pip install --no-cache-dir \
    "pydantic>=2.10,<3" \
    "pydantic-settings>=2.7,<3" \
    "fastapi>=0.115,<1" \
    "uvicorn[standard]>=0.34,<1" \
    "kafka-python>=2.0.2,<3" \
    "prometheus-client>=0.21,<1" \
    "structlog>=24.4,<26"

EXPOSE 8100

HEALTHCHECK --interval=10s --timeout=5s --retries=10 --start-period=20s \
  CMD curl -f http://localhost:8100/health || exit 1

CMD ["python", "-m", "telemetry_generator"]
