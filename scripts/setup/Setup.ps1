# SiliconPulse AI — Windows PowerShell setup helper (Phase 1)
# Usage: ./scripts/setup/Setup.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $Root

Write-Host "==> SiliconPulse AI setup (Phase 1)" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example (development only)." -ForegroundColor Yellow
} else {
  Write-Host ".env already exists — leaving unchanged."
}

function Assert-Command($Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command not found: $Name"
  }
}

Assert-Command "uv"
Assert-Command "npm"

Write-Host "==> uv sync (Python workspace)"
uv sync --all-packages --group dev

Write-Host "==> npm install (apps/web)"
Push-Location "apps/web"
npm install
Pop-Location

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next recommended task: Phase 2 — Docker Compose infrastructure."
Write-Host "Note: make up / docker compose are not available until Phase 2."
