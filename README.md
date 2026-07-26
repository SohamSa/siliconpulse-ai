# SiliconPulse AI

Local-first **hardware intelligence** platform that turns GPU / accelerator telemetry into:

- fleet observability  
- digital-twin deviation  
- anomaly + failure risk + RUL  
- evidence-ranked root cause  
- human-supervised agent actions  
- incident reports  

Built to demonstrate product and systems thinking to hardware / semiconductor leaders — not to showcase Docker.

## Live public demo (share this with the owner)

Always-on link (no terminal on anyone’s machine):

**https://sohamsa.github.io/siliconpulse-ai/**

The simulation runs in the browser with real-time updates while the tab is open. Click **Run guided demo**.

Source for that site: [`live/`](live/) (deployed via GitHub Pages).

### Optional: local Python demo

```powershell
python scripts/run_local_demo.py
```

Open http://127.0.0.1:8787 — requires that terminal process to stay running.

## Why this is valuable

For an audience with Intel / NVIDIA / Synopsys depth, the product question is:

> Can you turn messy hardware signals into earlier, explainable, approvable decisions?

SiliconPulse answers with a working path:

1. Statistical digital twin catches drift before naive critical thresholds  
2. Structured RCA compares device vs rack peers (no LLM inventing sensors)  
3. Agents propose remediation; humans approve high-impact actions  
4. Full timeline + evidence-linked report  

Read the pitch notes: [docs/product/EXECUTIVE_VALUE.md](docs/product/EXECUTIVE_VALUE.md)

## Business problems covered

1. AI hardware observability  
2. Predictive maintenance / lifecycle  
3. Root-cause investigation  
4. Device-specific digital twins  
5. Cross-domain sensor intelligence (healthcare **simulation** with hard disclaimers)

## Architecture (local demo mode)

```text
Simulator (50 GPUs)
   → in-process telemetry events
   → twin / anomaly / prediction / health
   → alerts + incident grouping
   → RCA agent + maintenance agent + approvals
   → report
   → browser UI on :8787
```

Optional fuller stack (Postgres, Redpanda, Compose) exists under `docker-compose.yml` for later — **not required** for the executive demo.

## Honest limitations

- Telemetry is **synthetic**  
- Models are **demonstration-grade**  
- Twin is **statistical**, not transistor-level  
- Healthcare module is **not medical / not diagnostic**  
- Agent actions are **simulated** and **human-supervised**  
- Not validated on real semiconductor production fleets  

## Project layout (high signal)

| Path | Purpose |
| --- | --- |
| `apps/local_platform/` | Runnable no-Docker demo (start here) |
| `docs/product/` | PRD, personas, executive value |
| `docs/architecture/` | System context / data flow |
| `services/telemetry-generator/` | Earlier Compose-oriented simulator package |
| `docker-compose.yml` | Optional infra (network-dependent) |

## Docs

- [Executive value](docs/product/EXECUTIVE_VALUE.md)  
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)  
- [Business problems](docs/product/BUSINESS_PROBLEMS.md)  
- [AI strategy](docs/ai/AI_STRATEGY.md)  
- [Agent design](docs/agents/AGENT_DESIGN.md)  
- [Local setup](docs/operations/LOCAL_SETUP.md)  

## License

Apache License 2.0 — see [LICENSE](LICENSE).
