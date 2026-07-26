# SiliconPulse AI

Local-first **hardware intelligence** platform that turns GPU / accelerator telemetry into fleet observability, digital-twin deviation, anomaly + failure risk + RUL, evidence-ranked root cause, human-supervised agent actions, and incident reports.

Built to demonstrate product and systems thinking to hardware / semiconductor leaders — not to showcase Docker.

---

## Working execution link (live demo)

### [https://sohamsa.github.io/siliconpulse-ai/](https://sohamsa.github.io/siliconpulse-ai/)

| | |
| --- | --- |
| **Status** | Live on GitHub Pages — always on |
| **Needs terminal?** | No |
| **Needs Docker / install?** | No |
| **Updates** | Real-time while the browser tab is open |
| **What to click** | **Run guided demo** |

Share that URL with anyone. They open it in a browser and the full cooling-degradation story runs end to end:

Reset → Inject GPU-042 cooling degradation → twin / anomaly / prediction → incident → RCA → maintenance approval → recovery → report.

Demo source: [`live/`](live/)

Repo: [github.com/SohamSa/siliconpulse-ai](https://github.com/SohamSa/siliconpulse-ai)

---

## Optional: local Python demo

Only if you want to run on your machine (terminal must stay open):

```powershell
python scripts/run_local_demo.py
```

Then open http://127.0.0.1:8787

---

## Why this is valuable

For an audience with Intel / NVIDIA / Synopsys depth, the product question is:

> Can you turn messy hardware signals into earlier, explainable, approvable decisions?

SiliconPulse answers with a working path:

1. Statistical digital twin catches drift before naive critical thresholds  
2. Structured RCA compares device vs rack peers (no LLM inventing sensors)  
3. Agents propose remediation; humans approve high-impact actions  
4. Full timeline + evidence-linked report  

Pitch notes: [docs/product/EXECUTIVE_VALUE.md](docs/product/EXECUTIVE_VALUE.md)

## Business problems covered

1. AI hardware observability  
2. Predictive maintenance / lifecycle  
3. Root-cause investigation  
4. Device-specific digital twins  
5. Cross-domain sensor intelligence (healthcare **simulation** with hard disclaimers)

## Architecture (browser live demo)

```text
In-browser simulator (50 GPUs)
   → twin / anomaly / prediction / health
   → alerts + incident grouping
   → RCA agent + maintenance agent + approvals
   → report
   → live UI (GitHub Pages)
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
| `live/` | Always-on public demo (GitHub Pages) |
| `apps/local_platform/` | Optional local Python demo |
| `docs/product/` | PRD, personas, executive value |
| `docs/architecture/` | System context / data flow |
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
