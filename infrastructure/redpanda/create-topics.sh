#!/usr/bin/env bash
# Create SiliconPulse Redpanda topics (idempotent).
set -euo pipefail

BROKERS="${REDPANDA_BROKERS:-redpanda:9092}"
PARTITIONS="${TOPIC_PARTITIONS:-3}"
REPLICAS="${TOPIC_REPLICAS:-1}"

echo "==> Waiting for Redpanda at ${BROKERS}"
for i in $(seq 1 60); do
  if rpk cluster info --brokers "${BROKERS}" >/dev/null 2>&1; then
    echo "Redpanda is reachable"
    break
  fi
  if [ "${i}" -eq 60 ]; then
    echo "ERROR: Redpanda not reachable after timeout" >&2
    exit 1
  fi
  sleep 2
done

topics=(
  telemetry.raw
  telemetry.validated
  telemetry.invalid
  device.events
  alerts.generated
  alerts.updated
  predictions.generated
  digital-twin.updated
  incidents.created
  incidents.updated
  maintenance.recommended
  maintenance.approved
  agent.events
  agent.actions
  agent.failures
  reports.generated
  healthcare.telemetry
)

echo "==> Ensuring ${#topics[@]} topics exist"
for topic in "${topics[@]}"; do
  if rpk topic describe "${topic}" --brokers "${BROKERS}" >/dev/null 2>&1; then
    echo "  exists: ${topic}"
  else
    rpk topic create "${topic}" \
      --brokers "${BROKERS}" \
      --partitions "${PARTITIONS}" \
      --replicas "${REPLICAS}"
    echo "  created: ${topic}"
  fi
done

echo "==> Topic list"
rpk topic list --brokers "${BROKERS}"
echo "==> Redpanda topic init complete"
