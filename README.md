# SiliconPulse AI

SiliconPulse AI is an end-to-end hardware intelligence prototype that turns chip and accelerator data into decisions people can understand, review, and act on.

I built the project to answer a practical question:

> If a chip or GPU begins behaving differently, can we detect it early, understand what may be causing it, estimate the operational risk, and recommend a safe next step?

The project follows that question from the first telemetry event to the final incident report. It includes a simulated GPU fleet, statistical operational twins, trained and deterministic AI models, lifecycle risk, wafer yield intelligence, evidence-based root cause analysis, human approval, and a working browser experience.

## Try the live project

### [Open the SiliconPulse AI live dashboard](https://sohamsa.github.io/siliconpulse-ai/)

The dashboard runs entirely in the browser.

| | |
| --- | --- |
| Installation | None |
| Terminal | Not required |
| Docker | Not required for the live demo |
| Fleet | 50 simulated GPUs |
| Main scenario | Cooling degradation on GPU-042 |
| Recommended starting point | Click **Run guided demo** |

The guided story is:

GPU-042 begins losing cooling efficiency. SiliconPulse compares the device with its expected behavior and its rack peers. It detects the change, creates an incident, ranks possible causes, proposes a maintenance response, waits for human approval, simulates recovery, and produces an evidence-linked report.

The Semiconductor AI Laboratory on the same page adds three more demonstrations:

1. Survival analysis and remaining useful life
2. Wafer defect and yield triage
3. An evidence-grounded engineering copilot

## The business problem

Modern chips, accelerators, manufacturing tools, and data center systems generate large amounts of data. Having the data does not automatically tell a business what deserves attention.

An operator or business leader still needs clear answers:

- Which device, wafer, lot, or process needs attention first?
- Is the behavior truly unusual for this specific device and workload?
- Could the issue become expensive if nothing is done?
- What evidence supports the suspected cause?
- What evidence contradicts it?
- What information is still missing?
- What action is safe to take now?
- Did the action actually improve the situation?

Slow answers can lead to downtime, wasted engineering time, unnecessary maintenance, lost yield, missed failures, customer impact, and higher operating cost. SiliconPulse is my attempt to connect those questions into one usable decision flow.

## My vision for the project

My goal was not to build another dashboard that only displays charts. I wanted to build the path around the dashboard as well.

The broader vision is a hardware intelligence layer that can learn from data across the silicon lifecycle. That may include design information, in-chip monitors, manufacturing and test history, deployed-device telemetry, maintenance records, firmware, workload, and environmental context.

The system should help people detect risk earlier, investigate faster, make better decisions, and learn from the outcome. AI can do much of the analysis and coordination, but engineers and operators should remain responsible for high-impact decisions.

This prototype is a small, honest version of that vision. It uses synthetic data, but the decision pattern is designed to be replaced with real semiconductor, manufacturing, test, and fleet data.

## What I built from scratch to end

I approached SiliconPulse as a complete product rather than an isolated machine learning experiment.

### 1. Defined the user decisions

I started with the decisions an operator, reliability engineer, product engineer, or business owner would need to make. That shaped the data, models, interface, alerts, agents, and reports.

### 2. Created a working hardware environment

I built a deterministic simulator for 50 GPUs across five racks. It produces connected signals such as temperature, power, utilization, fan speed, voltage, errors, throughput, latency, workload, firmware, age, and sensor quality.

The simulator can inject cooling degradation, fan failure, memory degradation, rack cooling failure, sensor drift, and recovery. Hidden scenario labels are kept away from the investigation logic so the system cannot simply read the answer.

### 3. Built device-specific operational twins

A fixed temperature threshold treats every device the same. Real behavior depends on workload, power, rack conditions, device history, and its own healthy baseline.

SiliconPulse estimates the temperature expected for each device and compares it with the observed value. This creates a contextual deviation signal that can rise before a late static threshold is crossed.

This is a statistical operational twin. It is not a transistor-level physics model.

### 4. Added anomaly and failure intelligence

The intelligence layer combines twin deviation, temperature behavior, fan efficiency, peer comparison, ECC errors, and sensor quality. It estimates health, anomaly level, likely failure category, and operational risk.

A reproducible cooling classifier is trained on one group of synthetic devices and evaluated on unseen synthetic seeds. Deterministic scoring remains in places where a production model would require real labeled data.

### 5. Added lifecycle survival and RUL analysis

I built a discrete-time survival model using right-censored device histories. Instead of returning one overly certain failure date, it estimates hazard over a sequence of intervals and builds a survival curve.

The evaluation keeps training and test devices separate. It records dynamic concordance, interval Brier score, and calibration bins. This makes the limitations visible and creates a clearer path toward product-specific reliability modeling.

Business value:

- Prioritize inspections and maintenance
- Compare risk across a fleet
- Reduce emergency response
- Plan capacity and replacement more intelligently
- Measure whether an early warning provides useful lead time

### 6. Added wafer defect and yield intelligence

I created a synthetic wafer-map module that detects spatial signatures such as edge rings, center clusters, and scratch-like linear patterns. It calculates yield impact, ranks the likely pattern, and recommends what evidence should be collected next.

The module does not claim that an image alone proves the physical cause. In a real fab, the result would need to be connected with wafer and lot genealogy, tool and chamber history, process recipes, metrology, inspection, and electrical test.

Business value:

- Find unusual wafer patterns faster
- Focus engineering attention on the most important yield excursions
- Shorten the path from defect discovery to process investigation
- Preserve learning across wafers, lots, tools, and fabs
- Reduce scrap and improve yield when validated on real data

### 7. Built evidence-based root cause analysis

The root cause workflow treats diagnosis as a competition between hypotheses. It shows supporting evidence, contradicting evidence, missing evidence, peer behavior, and confidence.

For example, abnormal behavior on GPU-042 with healthy rack peers supports a device-local cooling issue and weakens a rack-wide explanation. A physical inspection is still required before the suspected cause becomes a confirmed cause.

### 8. Built a governed engineering copilot

The engineering copilot is designed as a controlled investigation workflow, not an unrestricted chatbot.

It can:

- Retrieve approved device, twin, peer, incident, and monitor evidence
- Preserve source references and evidence IDs
- Rank possible causes
- Show what supports and contradicts each cause
- Identify missing information
- Recommend the next test or action
- Request approval for maintenance or workload changes
- Record the human decision in an audit trail

Free-text AI output is not accepted as sensor evidence. A language model may explain grounded results, but it does not get permission to invent measurements or independently perform high-impact actions.

Business value:

- Give engineers a faster starting point for investigation
- Reduce time spent collecting information from separate systems
- Make AI recommendations easier to review and challenge
- Capture investigation knowledge instead of losing it in isolated conversations
- Keep people accountable for important operational decisions

### 9. Connected detection to action

Alerts are grouped into incidents so related signals become one operational story. A maintenance agent can propose workload redistribution and cooling-path inspection, but the action remains pending until a person approves or rejects it.

After approval, the simulator applies a recovery scenario. SiliconPulse watches the device, updates the evidence, and records the result.

### 10. Created the product experience and documentation

I connected the simulator, models, operational twin, incidents, root cause workflow, approvals, recovery, and reports into a live browser product. I also added model cards, test evidence, architecture documents, product requirements, limitations, and a reproducible local version.

That final connection matters to me. A model becomes useful when someone can understand its output, use it in a decision, and evaluate what happened next.

## How the AI creates business value

| AI capability | Decision it supports | Potential business value |
| --- | --- | --- |
| Device-specific operational twin | Is this behavior abnormal for this device? | Earlier detection with better context |
| Cooling anomaly classifier | Does this pattern resemble degradation? | Faster and more consistent screening |
| Survival and RUL analysis | Which asset should be inspected or replaced first? | Better maintenance and capacity planning |
| Wafer spatial intelligence | Which wafer pattern deserves investigation? | Faster yield learning and less wasted analysis |
| Evidence-ranked RCA | Which cause best fits the available facts? | Shorter investigation time and fewer unsupported conclusions |
| Engineering copilot | What evidence and next step should the engineer review? | Faster access to knowledge with clear governance |
| Human approval workflow | Should the recommended action be executed? | Safer automation and clearer accountability |
| Outcome report | Did the action work, and what should be learned? | Repeatable improvement and institutional memory |

The largest value would come from closing the loop. Real design, manufacturing, test, and field data could help improve future designs, test strategies, maintenance decisions, and operational policies.

## Who could use a system like this

### Semiconductor and hardware companies

They can use silicon and test data to improve reliability, debug, characterization, yield learning, product quality, and in-field performance.

### AI infrastructure and data center operators

They can prioritize unhealthy accelerators, reduce unplanned downtime, protect workloads, and make maintenance decisions with better evidence.

### Manufacturing and process teams

They can connect defect patterns with process history, identify excursions, improve yield, and preserve knowledge from previous investigations.

### Business and operations leaders

They can see which risks matter, what action is being proposed, why it is being proposed, and whether the intervention produced a measurable improvement.

## End-to-end decision flow

```text
Hardware and process signals
        ↓
Data quality and device context
        ↓
Operational twin and anomaly detection
        ↓
Failure risk, survival, and yield intelligence
        ↓
Alerts and incident grouping
        ↓
Evidence-ranked root cause investigation
        ↓
Engineering copilot recommendation
        ↓
Human approval
        ↓
Simulated recovery and monitoring
        ↓
Evidence-linked incident report
```

## Current AI evidence

### Cooling classifier

The committed cooling classifier uses logistic regression trained with gradient descent.

- Training seeds: 10 to 29
- Test seeds: 101 to 110
- Held-out test rows: 1,800
- Precision: 1.000
- Recall: 0.966
- F1: 0.983
- False-positive rate: 0.000

These clean numbers reflect one shared synthetic simulator family. They validate the pipeline and code path only. They do not represent real GPU fleet performance.

### Survival model

The survival benchmark uses unseen synthetic devices and right-censored histories.

- Model: weighted logistic discrete-time survival
- Dynamic concordance: 0.5924
- Interval Brier score: 0.0432
- Calibration bins: included in the committed artifact

The benchmark shows how lifecycle risk can be evaluated. Simulator intervals are not calibrated hours, and the model has not been validated on production silicon.

### Wafer spatial baseline

- Test wafers: 320 generated maps
- Synthetic pattern accuracy: 94.69%
- Patterns: normal, edge ring, center cluster, and scratch-like linear signature

The generator and classifier share the same pattern definitions, so this result does not demonstrate performance on real inspection data.

## Honest project boundaries

- All telemetry, wafer maps, failures, and recovery actions are synthetic.
- The operational twin is statistical, not a transistor-level or multiphysics twin.
- Only the cooling classifier and survival benchmark are trained demonstrations.
- Other risk and RCA components include deterministic logic where real labels are unavailable.
- The wafer module is an interpretable spatial baseline, not a production vision model.
- The RUL intervals are not validated wall-clock predictions.
- The engineering copilot uses structured retrieval and simulated tools.
- Human approval is required for high-impact actions.
- The healthcare example is a non-diagnostic device-monitoring simulation.
- Nothing in this repository is validated for production semiconductor, medical, or safety-critical use.

These boundaries are part of the project, not fine print added afterward. A trustworthy AI product should make it easy to see what has been demonstrated and what still needs real-world proof.

## Reproduce the model evidence

```bash
python ml/train_demo_models.py
python ml/train_survival_model.py
python ml/wafer_yield_intelligence.py
```

Run the complete test suite:

```bash
PYTHONPATH=packages/shared-models/src:packages/shared-events/src:packages/shared-utils/src:services/telemetry-generator/src:apps/local_platform python -m pytest
```

Current result: 19 tests passed.

## Run the optional local platform

The public browser demo is the easiest way to use the project. A local Python version is also included.

```powershell
python scripts/run_local_demo.py
```

Then open `http://127.0.0.1:8787`.

The larger Docker, Postgres, Redpanda, Prometheus, Grafana, and service scaffolding represents a possible production direction. It is not required for the executive demo.

## Project map

| Path | What it contains |
| --- | --- |
| `live/` | Public GitHub Pages product experience |
| `apps/local_platform/` | Local simulator, intelligence, agents, and engineering copilot |
| `ml/train_demo_models.py` | Cooling classifier training and evaluation |
| `ml/train_survival_model.py` | Survival and lifecycle risk benchmark |
| `ml/wafer_yield_intelligence.py` | Wafer pattern and yield triage baseline |
| `ml/artifacts/` | Committed model and evaluation evidence |
| `services/telemetry-generator/` | Fleet and failure-scenario generator |
| `docs/product/` | Business problems, requirements, personas, and roadmap |
| `docs/architecture/` | System context, data flow, containers, and deployment |
| `docs/ai/` | AI strategy and model documentation |
| `docs/agents/` | Agent and copilot design |
| `tests/` | Reproducibility and decision-path tests |

## Key documents

- [Executive value](docs/product/EXECUTIVE_VALUE.md)
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)
- [Business problems](docs/product/BUSINESS_PROBLEMS.md)
- [AI strategy](docs/ai/AI_STRATEGY.md)
- [Cooling model card](docs/ai/MODEL_CARD_COOLING_V1.md)
- [Survival and RUL model card](docs/ai/SURVIVAL_RUL_MODEL_CARD.md)
- [Wafer yield intelligence](docs/ai/WAFER_YIELD_INTELLIGENCE.md)
- [Agent design](docs/agents/AGENT_DESIGN.md)
- [Engineering copilot](docs/agents/ENGINEERING_COPILOT.md)
- [Architecture](ARCHITECTURE.md)
- [Presentation readiness](docs/product/PRESENTATION_READINESS.md)

## Why I built SiliconPulse AI

I wanted to demonstrate how I work when the real product and role are still unclear.

I begin with the business problem and the decision a user needs to make. Then I work through the data, system design, AI, evaluation, controls, interface, and story until the idea becomes something people can question and use.

SiliconPulse does not prove that I have solved semiconductor reliability or manufacturing. It shows that I can take a complex problem, structure it honestly, build the complete path, test the evidence, explain the value, and identify what would be needed next with real customers and real data.

## License

Apache License 2.0. See [LICENSE](LICENSE).
