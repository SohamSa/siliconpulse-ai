# Data Catalog Source Inventory

This inventory records the code and artifacts used to build the SiliconPulse AI data-field catalog.

| Source | Coverage | Confidence |
| --- | --- | --- |
| `packages/shared-models/src/shared_models/telemetry.py` | Published telemetry schema | High |
| `packages/shared-models/src/shared_models/device.py` | Device master data | High |
| `packages/shared-events/src/shared_events/envelope.py` | Event lineage and transport fields | High |
| `services/telemetry-generator/src/telemetry_generator/physics.py` | Internal simulator truth and reported sensor mapping | High |
| `apps/local_platform/simulator.py` | Local fleet, scenario, and intelligence state | High |
| `apps/local_platform/intelligence.py` | Twin, anomaly, risk, alert, incident, and RCA fields | High |
| `apps/local_platform/agents.py` | Agent, approval, action, and report fields | High |
| `apps/local_platform/engineering_copilot.py` | Evidence, case, hypothesis, and governance fields | High |
| `live/engine.js` | Browser data contracts and fleet summary | High |
| `live/app.js` | Fields actually rendered in the public dashboard | High |
| `live/semiconductor_ai.js` | Browser survival, wafer, and copilot outputs | High |
| `ml/train_demo_models.py` | Cooling model features, labels, and evaluation fields | High |
| `ml/train_survival_model.py` | Survival features, censoring, model, and evaluation fields | High |
| `ml/wafer_yield_intelligence.py` | Wafer map, spatial features, classification, and yield fields | High |
| `ml/artifacts/*.json` | Committed model evidence and metrics | High |
| `live/index.html` | Static benchmark values and healthcare demonstration fields | High |

## Scope

The catalog includes domain data, dashboard data, AI inputs and outputs, workflow state, evidence, evaluation metrics, and lineage fields that carry meaning outside a single function.

The catalog does not treat local loop counters, temporary variables, CSS properties, DOM element IDs, function parameters used only for implementation, or infrastructure configuration as business data fields.

When two runtimes use different names for the same concept, the catalog lists one canonical field and records the aliases. For example, `temperature_c`, `temp_c`, and the dashboard label `Temp` are one concept.

## Current boundaries

- All device telemetry and wafer data are synthetic.
- The live browser version and local Python version implement the same decision story, but some internal names differ.
- The browser survival view is explanatory. The Python survival artifact is the reproducible model evidence.
- Static healthcare values are demonstration content, not a clinical schema.
