# SiliconPulse AI — one-command local demo (no Docker, no pip)
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root
Write-Host "Starting SiliconPulse local demo..." -ForegroundColor Cyan
Write-Host "Open http://127.0.0.1:8787 after the server prints Ready."
python scripts/run_local_demo.py @args
