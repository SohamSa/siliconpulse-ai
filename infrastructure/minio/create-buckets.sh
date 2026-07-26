#!/bin/sh
# Create SiliconPulse MinIO buckets (idempotent).
set -eu

ENDPOINT="${MINIO_ENDPOINT:-http://minio:9000}"
ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin_dev_password}"

echo "==> Waiting for MinIO at ${ENDPOINT}"
i=1
while [ "${i}" -le 60 ]; do
  if mc alias set local "${ENDPOINT}" "${ACCESS_KEY}" "${SECRET_KEY}" >/dev/null 2>&1 \
    && mc ready local >/dev/null 2>&1; then
    echo "MinIO is ready"
    break
  fi
  if [ "${i}" -eq 60 ]; then
    echo "ERROR: MinIO not ready after timeout" >&2
    exit 1
  fi
  i=$((i + 1))
  sleep 2
done

buckets="
${MINIO_BUCKET_RAW_TELEMETRY:-raw-telemetry}
${MINIO_BUCKET_PROCESSED_TELEMETRY:-processed-telemetry}
${MINIO_BUCKET_TRAINING:-training-datasets}
${MINIO_BUCKET_MODELS:-ml-models}
${MINIO_BUCKET_EVAL:-evaluation-reports}
${MINIO_BUCKET_REPORTS:-incident-reports}
${MINIO_BUCKET_FIRMWARE:-firmware-artifacts}
${MINIO_BUCKET_EXPORTS:-exports}
"

echo "==> Ensuring buckets exist"
for bucket in ${buckets}; do
  if mc ls "local/${bucket}" >/dev/null 2>&1; then
    echo "  exists: ${bucket}"
  else
    mc mb "local/${bucket}"
    echo "  created: ${bucket}"
  fi
done

echo "==> Bucket list"
mc ls local
echo "==> MinIO bucket init complete"
