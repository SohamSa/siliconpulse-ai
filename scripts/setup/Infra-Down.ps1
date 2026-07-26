# Stop SiliconPulse infrastructure (keeps volumes).
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $Root
docker compose -f docker-compose.yml down
Write-Host "Infrastructure stopped (volumes retained)." -ForegroundColor Green
