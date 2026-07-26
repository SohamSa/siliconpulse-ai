# Start SiliconPulse Phase 2 infrastructure on Windows.
# Usage: ./scripts/setup/Infra-Up.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $Root

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example" -ForegroundColor Yellow
}

# Normalize shell scripts to LF for Linux containers
$scripts = @(
  "infrastructure/redpanda/create-topics.sh",
  "infrastructure/minio/create-buckets.sh"
)
foreach ($rel in $scripts) {
  $path = Join-Path $Root $rel
  $text = [System.IO.File]::ReadAllText($path) -replace "`r`n", "`n" -replace "`r", "`n"
  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
}

Write-Host "==> Validating compose config" -ForegroundColor Cyan
docker compose -f docker-compose.yml config | Out-Null

Write-Host "==> Starting infrastructure" -ForegroundColor Cyan
docker compose -f docker-compose.yml up -d

Write-Host "==> Waiting for services" -ForegroundColor Cyan
$deadline = (Get-Date).AddMinutes(3)
do {
  Start-Sleep -Seconds 3
  $ps = docker compose -f docker-compose.yml ps --format json | ConvertFrom-Json
  if ($ps -isnot [System.Array]) { $ps = @($ps) }
  $longRunning = $ps | Where-Object { $_.Service -notin @("redpanda-init", "minio-init") }
  $inits = $ps | Where-Object { $_.Service -in @("redpanda-init", "minio-init") }
  $healthy = (@($longRunning | Where-Object { $_.Health -eq "healthy" }).Count -eq $longRunning.Count)
  $initsDone = (@($inits | Where-Object { $_.State -eq "exited" }).Count -eq $inits.Count)
  if ($healthy -and $initsDone) {
    Write-Host "Infrastructure healthy." -ForegroundColor Green
    break
  }
  if ((Get-Date) -gt $deadline) {
    Write-Host "Timed out waiting for health. Current status:" -ForegroundColor Yellow
    docker compose -f docker-compose.yml ps
    exit 1
  }
} while ($true)

Write-Host ""
Write-Host "Endpoints:"
Write-Host "  Postgres:          localhost:5432"
Write-Host "  Valkey:            localhost:6379"
Write-Host "  Redpanda Kafka:    localhost:19092"
Write-Host "  Redpanda Console:  http://localhost:8080"
Write-Host "  MinIO API:         http://localhost:9000"
Write-Host "  MinIO Console:     http://localhost:9001"
Write-Host "  Prometheus:        http://localhost:9090"
Write-Host "  Grafana:           http://localhost:3001  (admin / from .env)"
docker compose -f docker-compose.yml ps
