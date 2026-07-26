# Local Setup

## Recommended: no-Docker demo

```powershell
cd "SiliconPulse AI"
python scripts/run_local_demo.py
```

Open http://127.0.0.1:8787

Requirements:

- Python 3.10+ (stdlib only — no `pip install` needed)

### Demo buttons

| Control | What it does |
| --- | --- |
| Reset fleet | Healthy baseline; clears incidents/approvals |
| Inject cooling degradation | Starts GPU-042 thermal drift scenario |
| Run guided demo | Full path: inject → wait → RCA → maintenance → approve → report |

## Optional: Docker Compose infrastructure

Only if registries are reachable on your machine:

```powershell
Copy-Item .env.example .env
docker compose up -d
```

This is **not** required for the executive demo path.

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Port 8787 in use | `python scripts/run_local_demo.py --port 8790` |
| Page loads but KPIs empty | Check terminal for Python errors; open `/health` |
| Guided demo finds no incident | Wait longer, or inject again with severity 0.9 |
