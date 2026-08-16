# SiliconPulse AI Data Field Catalog

This document explains the meaningful data fields used across SiliconPulse AI in simple language. It answers four questions for every field:

1. What does the field mean?
2. Why does the project need it?
3. What question does it answer?
4. What becomes impossible, unsafe, or misleading if it is removed?

## How to read the catalog

- **Dashboard** means the field is displayed directly or used to create something displayed on the public dashboard.
- **AI input** means a model or intelligent rule uses the field as evidence.
- **AI output** means the field is produced by a model, twin, scoring method, or evidence-ranking process.
- **Control** means the field governs a scenario, action, permission, or workflow.
- **Lineage** means the field helps trace where data came from and when it was produced.
- Aliases show different code names for the same real-world concept.

## 1. Device identity and business context

| Canonical field | Aliases | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- | --- |
| `device_id` | none | Dashboard, AI input | Unique name of a GPU or device | Which exact asset are we discussing? | Data from different devices can mix, so alerts, maintenance, and reports may target the wrong asset. |
| `device_type` | none | Context | Kind of hardware, such as GPU | What type of asset is this? | Rules and models may be applied to the wrong hardware category. |
| `model_name` | model | Dashboard, AI context | Hardware model, such as SP-H100-80G | Which product design and operating limits apply? | Normal power, clock, temperature, and throughput expectations become unreliable. |
| `manufacturer` | none | Context | Company that made the device | Who produced this hardware? | Supplier comparison and responsibility analysis disappear. |
| `manufacturing_batch` | `batch` | AI context | Production batch or cohort | Do failures cluster in one manufacturing batch? | A systemic batch problem can look like unrelated device failures. |
| `serial_number` | none | Identity | Manufacturer serial number | Can this physical unit be traced outside the platform? | Field service and external warranty records cannot be connected safely. |
| `rack_id` | none | Dashboard, AI input | Rack containing the device | Is the issue local to one device or shared across a rack? | Peer comparison and rack cooling diagnosis become impossible. |
| `server_id` | none | Context | Server containing the device | Are several GPUs in the same server affected? | Server-level power, airflow, or firmware patterns are hidden. |
| `firmware_version` | FW | Dashboard, AI input | Software version running on the device | Did behavior change after a firmware version changed? | Firmware regressions cannot be separated from physical failures. |
| `installation_date` | none | Context | Date the device entered service | How long has it been operating in this environment? | Service-life and warranty context become weaker. |
| `manufactured_at` | none | Context | Date the device was produced | Is risk related to production time or process generation? | Manufacturing-era trends cannot be studied. |
| `age_hours` | none | AI input | Total operating age | Is an older device more likely to degrade? | Survival, lifecycle, and maintenance timing lose a core exposure measure. |
| `lifecycle_status` | `lifecycle`, dashboard `status` | Dashboard, AI output | Human-friendly state such as healthy or degraded | What stage of health is the device in now? | Users must interpret many raw scores themselves and may miss priority changes. |
| `operational_status` | none | Context | Online, offline, or unavailable state | Is the device currently able to serve work? | A powered-off device may be mistaken for a healthy low-utilization device. |
| `created_at` | none | Lineage | When the device record was created | When did tracking begin? | Record history and auditability weaken. |
| `updated_at` | none | Lineage | When the device record last changed | Is this device information current? | Stale configuration may be treated as current truth. |
| `labels` | none | Context | Flexible tags such as server or reset markers | What extra grouping or state should travel with the record? | Useful cohort and incident context is lost. |
| `metadata` | none | Context | Additional structured information | What extra source-specific information is available? | New context requires schema changes or is discarded. |

## 2. Event identity, time, and lineage

| Canonical field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `event_id` | Lineage | Unique identifier for one telemetry or workflow event | Which exact event produced this result? | Duplicate detection and event-level audit become unreliable. |
| `event_type` | Lineage | Kind of event, such as telemetry.raw | What happened in this message? | Consumers may interpret one message using the wrong schema or logic. |
| `timestamp` | AI input, Lineage | When the sensor reading occurred | When did the physical behavior happen? | Rates, sequences, lead time, and incident timelines cannot be trusted. |
| `ingestion_timestamp` | Lineage | When the platform received the reading | Was the data delayed? | Late data can be mistaken for current behavior. |
| `created_at` | Lineage | When an event envelope was created | When did the platform publish this event? | Transport delay and audit timing become harder to reconstruct. |
| `schema_version` | Lineage | Version of the record format | Which definition should be used to read this event? | Older and newer records can be combined incorrectly. |
| `sequence_number` | `seq` | AI input, Lineage | Order of readings from one device | Are readings missing or out of order? | Temperature rate and event order can be wrong. |
| `correlation_id` | Lineage | Identifier connecting related events | Which events belong to the same request or incident path? | End-to-end tracing across services becomes difficult. |
| `causation_id` | Lineage | Identifier of the event that caused this event | What triggered this result? | The platform cannot reconstruct cause-and-effect between workflow events. |
| `source` | `source_service` | Lineage | System that produced the data | Can this source be trusted and debugged? | Conflicting sources cannot be separated. |
| `payload` | Transport | Business content carried by an event | What data belongs to this event? | The event envelope contains no useful measurement or action. |

## 3. Reported hardware telemetry

| Canonical field | Aliases | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- | --- |
| `temperature_c` | `temp_c`, dashboard Temp | Dashboard, AI input | Reported device temperature | Is the device becoming too hot? | Thermal degradation, twin deviation, throttling risk, and high-temperature alerts weaken or disappear. |
| `ambient_temperature_c` | `ambient_c` | AI input | Temperature around the device | Is the device hot because the room or rack is hot? | Device-local and environmental cooling problems become easy to confuse. |
| `power_watts` | `power_w`, dashboard Power | Dashboard, AI input | Electrical power being consumed | Is heat expected because the device is drawing more power? | The twin may call normal workload heat abnormal, or miss inefficient power behavior. |
| `voltage` | none | AI input | Electrical voltage level | Is power behavior unstable? | Voltage instability cannot be detected or ruled out. |
| `utilization_pct` | `utilization`, dashboard Util | Dashboard, AI input | Percentage of compute capacity in use | Is temperature or power reasonable for the workload? | A busy healthy GPU may look unhealthy, and idle inefficiency may be missed. |
| `memory_utilization_pct` | `memory_util` | AI input | Percentage of memory capacity in use | Is memory pressure contributing to behavior? | Workload context and memory-related diagnosis become less accurate. |
| `clock_speed_mhz` | `clock_mhz` | AI input | Current operating clock speed | Is the device slowing down because of heat or a firmware issue? | Thermal throttling and clock regressions cannot be measured. |
| `base_clock_mhz` | profile `base_clock` | AI context | Normal reference clock for the model | How far has the current clock fallen from normal? | A clock value has no model-specific baseline. |
| `fan_speed_rpm` | `fan_rpm`, dashboard Fan | Dashboard, AI input | Fan rotation speed | Is the fan responding to rising temperature? | Fan failure and cooling-path hypotheses cannot be compared properly. |
| `fan_efficiency` | `fan_eff` | AI input, Eval | Hidden or derived effectiveness of the fan | Is poor cooling caused by the fan itself? | The simulator cannot create or evaluate a distinct fan-failure story. |
| `cooling_efficiency` | `cooling_eff`, dashboard True cooling efficiency | Dashboard eval, AI input | Effectiveness of the overall cooling path | Is cooling performance degrading even while the fan still spins? | The demonstration loses its ground-truth evaluation signal and cannot simulate gradual cooling degradation. |
| `ecc_correctable_errors` | `ecc_c` | AI input | Memory errors corrected by hardware | Is memory health slowly worsening? | Early memory degradation may be missed. |
| `ecc_uncorrectable_errors` | `ecc_u` | AI input | Memory errors hardware could not correct | Is there an immediate serious memory risk? | Critical memory alerts and replacement decisions may not happen. |
| `network_latency_ms` | `latency_ms` | AI input | Network delay affecting the device | Is lower throughput caused by the network rather than the chip? | Network bottlenecks may be misdiagnosed as device failures. |
| `throughput` | dashboard internal Throughput | AI input | Useful work completed by the device | Is performance actually being lost? | Technical abnormalities cannot be connected to business capacity impact. |
| `workload_type` | `workload` | AI input | Work being performed, such as inference or training | Is behavior normal for this kind of workload? | Different workload profiles are compared as if they were identical. |
| `sensor_quality` | none | AI input | Trust score for the sensor reading | Should the system trust the measurement? | Sensor drift may be mistaken for a real physical failure. |
| `temp_sensor_bias_c` | `temp_bias` | Eval | Difference added to reported temperature during drift | Is the temperature sensor lying relative to simulated truth? | Sensor-drift scenarios cannot be generated or tested. |
| `power_sensor_bias_w` | `power_bias` | Eval | Difference added to reported power during drift | Is the power sensor reporting a biased value? | Power-sensor drift cannot be generated or tested. |

## 4. Scenario and simulator control fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `scenario_id` | Control, Lineage | Unique identifier for an injected scenario | Which simulated event is affecting this device? | Scenarios cannot be stopped, traced, or separated. |
| `scenario` | `simulation_scenario` | Control, Eval | Type of simulated condition | Which known condition is being generated for testing? | Training labels and controlled demonstrations disappear. This field must still be hidden from RCA. |
| `device_ids` | Control | Devices affected by a scenario | Which assets should change? | A scenario may affect the wrong device or no device. |
| `rack_id` | Control | Rack affected by a shared scenario | Which peer group should receive a rack-wide condition? | Rack failure simulation cannot be scoped correctly. |
| `severity` | Control | Strength of the simulated problem | How intense should the condition become? | Tests cannot compare mild and serious cases. |
| `progress` | Control | How far the scenario has developed | Is the issue early, developing, or fully active? | Gradual degradation becomes an unrealistic instant switch. |
| `stopped` | Control | Whether the scenario is inactive | Is this scenario still affecting the device? | Old scenarios may continue changing data after they should end. |
| `started_at` | Control, Lineage | Time the scenario began | How long has the condition been active? | Detection lead time and scenario history cannot be measured. |
| `seed` | Reproducibility | Random seed used by the simulator | Can the same experiment be reproduced? | Model results and tests may change between runs. |
| `device_count` | Control, Dashboard | Number of simulated devices | How large is the fleet? | Fleet totals and test scope become unclear. |
| `rack_count` | Control | Number of racks | How are devices divided into peer groups? | Peer topology cannot be reproduced. |
| `events_generated` | Dashboard, Lineage | Total readings produced | Is the live simulator actively generating data? | Users cannot tell whether the dashboard is alive or frozen. |

## 5. Operational twin and AI-derived device fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `twin_expected_temp` | Dashboard, AI output | Temperature expected for this device and context | What temperature should this device have right now? | Observed temperature loses its contextual comparison. |
| `twin_deviation` | Dashboard, AI output, AI input | Size of the gap between observed and expected behavior | How far from normal is this device? | Early contextual detection, alerting, RCA, and health scoring lose a central signal. |
| `twin_confidence` | Dashboard, AI output | Trust in the learned baseline | Has the twin seen enough healthy history to be relied on? | A new or poorly learned baseline may look as trustworthy as a mature one. |
| `baseline.residual` | AI input | Device-specific healthy adjustment | What is normal for this individual unit? | All devices are forced into one generic baseline. |
| `baseline.n` | AI input | Number of observations used to mature the baseline | Is there enough history to alert safely? | Alerts may fire before the baseline is ready. |
| `anomaly_score` | Dashboard, AI output | Combined measure of unusual behavior | Which devices look most unusual? | Live ranking, incident creation, health, survival view, and copilot evidence lose a primary signal. |
| `failure_type` | `predicted_failure_type` | Dashboard, AI output | Most likely failure category | What kind of issue should be investigated first? | Users see risk without knowing what response is relevant. |
| `failure_probability` | `failure_prob`, Top risk score | Dashboard, AI output | Relative operational risk score | Which device carries the greatest current risk? | Fleet prioritization and maintenance urgency become unclear. |
| `rul_hours` | Demo RUL | Dashboard, AI output | Demonstration estimate of remaining useful life | How soon might attention be needed? | Maintenance planning loses a time-oriented signal. |
| `health_score` | Dashboard, AI output | Overall health from 0 to 100 | How healthy is the device in one understandable number? | Business users must interpret many technical fields separately. |
| `lifecycle` | dashboard `status` | Dashboard, AI output | Healthy, stressed, degraded, maintenance recommended, or critical | What operational state should the user act on? | Severity communication becomes slower and inconsistent. |
| `peer_temperature_delta` | cooling feature | AI input | Device temperature minus peer temperature | Is the problem local to one device? | Device cooling and rack cooling become harder to separate. |
| `temperature_rate` | cooling feature | AI input | Speed of temperature change | Is the device heating unusually fast? | Early acceleration may be missed before the absolute value becomes high. |
| `fan_efficiency_proxy` | cooling feature | AI input | Estimated cooling response from RPM and temperature | Is fan response weaker than expected? | The cooling classifier loses a direct degradation clue. |
| `current_stress_index` | Browser survival output | Dashboard, AI output | Combined twin, anomaly, and risk stress | How stressed is GPU-042 before calculating survival? | The browser survival explanation has no starting risk summary. |
| `hazard` | Dashboard lab, AI output | Chance of failure during one interval among surviving devices | How does near-term risk change over time? | A survival curve cannot be calculated. |
| `survival` | Dashboard lab, AI output | Chance of remaining event-free through an interval | How likely is the asset to remain operating over time? | Lifecycle risk cannot be communicated as a curve. |
| `median_remaining_intervals` | Dashboard lab, AI output | First interval where survival falls to 50 percent | When does the model reach its midpoint estimate? | Users lose a simple time-oriented summary of the survival curve. |
| `interpretation` | Dashboard lab | Plain-language explanation of the survival output | How should a non-specialist read this result? | A technically correct output becomes easier to misunderstand. |
| `boundary` | Dashboard lab, Governance | Explicit limitation attached to an AI result | What must this result not be treated as? | Synthetic output can be mistaken for validated production evidence. |

## 6. Fleet summary fields shown on the dashboard

| Dashboard field | Built from | Question answered | Why it is shown | Worst case if removed |
| --- | --- | --- | --- | --- |
| `device_count` | Fleet inventory | How many devices are being monitored? | Establishes scope | A viewer cannot judge whether totals describe 5 devices or 50. |
| `healthy` | Lifecycle status counts | How many devices need no attention? | Shows normal fleet capacity | The dashboard becomes biased toward problems and hides available healthy capacity. |
| `warning` | Stressed, degraded, and maintenance states | How many devices may need review soon? | Shows developing risk | Early issues disappear until they become critical. |
| `critical` | Critical lifecycle count | How many devices need immediate attention? | Supports urgent triage | A severe fleet condition can be missed. |
| `avg_temperature_c` | Mean reported temperature | Is the fleet generally heating up? | Adds fleet-level thermal context | A shared environmental change may be missed while individual values appear acceptable. |
| `avg_utilization_pct` | Mean utilization | Is fleet heat explained by workload demand? | Separates demand from inefficiency | Average temperature can be interpreted without workload context. |
| `events_generated` | Event counter | Is data still flowing? | Demonstrates live operation | Frozen data can be mistaken for stable equipment. |
| `highest_risk_device` | Maximum failure probability | Which device should be opened first? | Directs attention | Users must scan every row and may choose the wrong asset. |
| `highest_risk_prob` | Maximum failure probability | How strong is the top risk signal? | Adds magnitude to the priority | A named top device may appear urgent even when risk is low. |
| `top_anomalies` | Sorted anomaly and risk scores | Which devices deserve comparison? | Limits the table to the most relevant assets | Important outliers become buried in a full fleet list. |
| `open_alerts` | Alert status | What active signals have fired? | Shows detection output | Users cannot see why an incident exists. |
| `open_incidents` | Incident status | What active operational stories need action? | Groups related alerts | Users must manage isolated alerts and can miss a shared cause. |
| `pending_approvals` | Approval status | Which recommendations are waiting for a person? | Prevents silent automation | Actions may remain blocked without anyone noticing. |
| `agent_runs` | Agent execution records | What did the AI workflow do recently? | Makes automation visible | AI behavior becomes a black box. |

## 7. Alert fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `alert_id` | Lineage | Unique alert identifier | Which exact alert is referenced? | Alerts cannot be linked reliably to incidents or reports. |
| `incident_id` | Lineage | Incident containing the alert | Which larger problem does this signal belong to? | Related alerts remain isolated. |
| `alert_type` | Dashboard | Type of condition detected | What rule or intelligence signal fired? | The user sees severity without knowing the problem. |
| `severity` | Dashboard | Warning or critical level | How urgently should this be reviewed? | All alerts appear equally important. |
| `status` | Dashboard, Workflow | Open, acknowledged, or closed | Is the alert still active? | Old alerts can be mistaken for current problems. |
| `detected_at` | Lineage | Time the alert was created | When did the platform notice the issue? | Detection delay and event order cannot be measured. |
| `current_value` | Evidence | Observed value that triggered attention | What did the system actually see? | The alert becomes an unsupported statement. |
| `expected_value` | Evidence | Baseline or threshold used for comparison | What should the value have been? | Users cannot judge the size of the deviation. |
| `evidence` | AI output | Human-readable facts supporting the alert | Why did the platform raise this alert? | The alert becomes difficult to trust or challenge. |
| `recommendation` | AI output | Suggested next step | What should the operator consider doing? | Detection does not lead to a useful response. |
| `confidence` | AI output | Strength of the alert evidence | How certain is the platform? | Weak and strong alerts look identical. |
| `dedupe_key` | Workflow | Key used to suppress repeated copies | Is this the same continuing problem? | One problem can flood the system with duplicate alerts. |

## 8. Incident and root cause fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `incident_id` | Dashboard, Lineage | Unique operational problem | Which investigation and action history belong together? | Alerts, agents, approvals, and reports cannot share one case. |
| `title` | Dashboard | Short incident name | What happened? | The case is difficult to scan. |
| `description` | Context | Longer explanation of the incident | Why was this incident created? | Users lack initial context. |
| `status` | Dashboard, Workflow | Open, investigating, remediating, or resolved | Where is the incident in its lifecycle? | Work can be duplicated or abandoned. |
| `severity` | Dashboard | Business urgency of the incident | How quickly should people respond? | Critical incidents may not receive priority. |
| `started_at` | Lineage | Time the incident began | How long has the problem been open? | Response-time measurement disappears. |
| `acknowledged_at` | Lineage | Time someone accepted responsibility | When did a person begin handling it? | Operational accountability weakens. |
| `resolved_at` | Lineage | Time the incident ended | How long did resolution take? | Mean time to resolution cannot be calculated. |
| `affected_devices` | Dashboard | Devices involved in the incident | What assets are at risk? | Impact scope becomes unknown. |
| `affected_racks` | Context | Racks involved | Is this a shared infrastructure problem? | Rack-wide failures may look device-local. |
| `primary_alert_id` | Lineage | Alert that started the incident | What evidence opened this case? | Incident origin cannot be traced. |
| `likely_root_cause` | Dashboard, AI output | Highest-ranked explanation | What cause best fits current evidence? | Investigation produces facts without a usable conclusion. |
| `confidence` | Dashboard, AI output | Strength of the leading RCA result | How much should the leading cause be trusted? | A tentative hypothesis may be treated as confirmed. |
| `timeline` | Dashboard, Lineage | Ordered history of the case | What happened from detection to resolution? | Audit, learning, and handoff become difficult. |
| `approved_actions` | Workflow | Human-approved responses | What action was authorized? | The report cannot distinguish proposed work from approved work. |
| `outcome` | AI feedback | Result after the action | Did the intervention stabilize the system? | The platform cannot learn whether recommendations worked. |
| `cause` | AI output | One candidate RCA hypothesis | What possible explanation is being considered? | Alternative explanations cannot be compared. |
| `score` | AI output | Relative strength of a hypothesis | Which cause ranks above another? | RCA becomes an unordered list. |
| `supporting_evidence` | AI output | Facts that strengthen a hypothesis | Why might this cause be correct? | The conclusion becomes ungrounded. |
| `contradicting_evidence` | AI output | Facts that weaken a hypothesis | What argues against this cause? | Confirmation bias increases and weak diagnoses look certain. |
| `most_likely_cause` | AI output | Top result after ranking | Which cause should be investigated first? | The user has no prioritized next step. |
| `missing_evidence` | AI output | Information still needed | What should be collected before confirmation? | The system may stop investigating too early. |

## 9. Approval, action, and agent fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `approval_id` | Dashboard, Lineage | Unique approval request | Which decision is being approved? | A human response may be applied to the wrong action. |
| `action` | Dashboard, Control | Proposed operation | What exactly will happen? | A person cannot give informed approval. |
| `reason` | Dashboard, AI output | Why the action was proposed | Why should this action be considered? | Approval becomes a blind yes or no. |
| `expected_impact` | Dashboard, AI output | Result the action should produce | What change should be monitored after approval? | Success cannot be evaluated. |
| `risk` | Dashboard, Governance | Possible downside of the action | What could go wrong if approved? | The reviewer cannot balance benefit and harm. |
| `requested_by` | Lineage | Agent or person requesting approval | Who proposed this action? | Accountability disappears. |
| `requested_at` | Lineage | Time approval was requested | How long has the request been waiting? | Approval delay cannot be managed. |
| `decided_at` | Lineage | Time a decision was made | When was the action authorized or rejected? | Audit timing is incomplete. |
| `decided_by` | Governance | Person who made the decision | Who accepted responsibility? | Human-in-the-loop becomes unprovable. |
| `comments` | Governance | Reviewer explanation | Why was the decision made? | Important human context is lost. |
| `approval_status` | Dashboard, Governance | Pending, approved, or rejected | May the action proceed? | The system may execute without permission or remain blocked forever. |
| `agent_run_id` | Lineage | Unique AI workflow execution | Which agent run produced this output? | Agent behavior cannot be audited. |
| `agent_type` | Dashboard | Root cause, maintenance, or reporting agent | What job was the agent performing? | Outputs from different workflows can be confused. |
| `started_at` | Lineage | Agent start time | When did automation begin? | Duration and ordering disappear. |
| `completed_at` | Lineage | Agent finish time | Did the run complete, and how long did it take? | Stalled automation cannot be identified. |
| `current_step` | Dashboard | Current workflow stage | What is the agent doing now? | A running agent looks frozen or opaque. |
| `tool_calls` | Dashboard, Governance | Approved tools used by the agent | What data or action did the agent access? | The agent becomes a black box. |
| `evidence` | Dashboard, AI output | Facts gathered by the agent | What grounded its decision? | Decisions cannot be verified. |
| `decisions` | Dashboard, AI output | Conclusions reached during the run | What did the agent decide? | Activity is visible but meaning is not. |
| `confidence` | Dashboard, AI output | Strength of the agent conclusion | How tentative is the result? | Weak output may be treated as strong. |
| `approval_required` | Governance | Whether a human decision is mandatory | Can the agent act automatically? | High-impact actions may bypass review. |
| `output` | Workflow | Structured result of the agent | What usable plan or report did the run produce? | Downstream steps receive no result. |

## 10. Incident report fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `report_id` | Lineage | Unique report identifier | Which final report is being referenced? | Reports cannot be tracked or compared. |
| `generated_at` | Lineage | Time the report was produced | How current is this report? | A stale report may be treated as current. |
| `executive_summary` | Dashboard | Plain-language incident outcome | What should a leader know quickly? | Business users must read raw technical evidence. |
| `technical_summary` | Dashboard | Key device and AI measurements | What technical facts support the report? | The report becomes a narrative without measurements. |
| `timeline` | Dashboard, Lineage | Complete event history | What happened and in what order? | Post-incident review becomes unreliable. |
| `approvals` | Dashboard, Governance | Human decisions included in the report | Which actions were authorized? | Human control cannot be demonstrated. |
| `limitations` | Dashboard, Governance | Boundaries of the result | What must the reader not assume? | Synthetic claims may be overstated. |
| `evidence_refs` | AI governance | IDs of evidence supporting the report | Can the report be traced back to source facts? | The report becomes hard to audit. |

## 11. Cooling classifier fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `temperature_c` | AI input | Current thermal level | Is the device hot? | The classifier loses the main physical symptom. |
| `power_watts` | AI input | Power causing heat | Is temperature expected for current power? | Normal workload heat may look abnormal. |
| `utilization_pct` | AI input | Compute demand | Is heat expected for current work? | Workload context disappears. |
| `fan_efficiency_proxy` | AI input | Estimated cooling response | Is cooling response weakening? | Cooling degradation becomes harder to distinguish from heavy work. |
| `peer_temperature_delta` | AI input | Difference from rack peers | Is the issue device-local? | Rack and device causes become confused. |
| `temperature_rate` | AI input | Thermal acceleration | Is temperature rising unusually fast? | Earlier deterioration is missed. |
| `y` | AI training target | Whether synthetic degradation is active | What should the model learn to predict? | Supervised training and evaluation are impossible. |
| `seed` | AI evaluation | Simulator group used for a row | Are train and test rows generated independently? | Leakage between training and test becomes harder to prevent. |
| `step` | AI evaluation | Position in the scenario timeline | When did detection occur? | Lead time cannot be measured. |
| `scenario` | AI evaluation | Normal or cooling-degradation label | Which generated population produced the row? | Class-level evaluation cannot be explained. |
| `normalization.mean` | AI model | Training average for each feature | How are new inputs centered consistently? | Inference no longer matches training. |
| `normalization.scale` | AI model | Training spread for each feature | How are differently sized features made comparable? | Large-unit fields can dominate the model. |
| `intercept` | AI model | Baseline model tendency | What risk exists before feature effects? | The trained logistic equation is incomplete. |
| `coefficients` | AI model | Learned effect of each feature | How does each input change the prediction? | The model cannot calculate a prediction. |
| `decision_threshold` | AI model | Probability cutoff for a positive result | When should the model call degradation? | Predictions cannot become an operational class. |
| `precision` | AI evaluation, Dashboard static | Share of positive predictions that were correct | How many cooling alerts were false alarms? | False-alarm burden is hidden. |
| `recall` | AI evaluation, Dashboard static | Share of degradation cases detected | How many true problems were found? | Missed failures are hidden. |
| `f1` | AI evaluation, Dashboard static | Balance of precision and recall | Is detection balanced overall? | Model comparison loses a useful combined measure. |
| `false_positive_rate` | AI evaluation, Dashboard static | Share of normal rows incorrectly flagged | How often are healthy devices disturbed? | Operational cost of false alerts is unknown. |
| `tp`, `fp`, `tn`, `fn` | AI evaluation | Confusion-matrix counts | What exact outcomes produced the metrics? | Summary metrics cannot be independently checked. |
| `detection_lead_steps.mean` | AI evaluation, Dashboard static | Average early-warning advantage over 85°C | How much earlier does the model react? | Business value of early detection is not quantified. |
| `detection_lead_steps.minimum` | AI evaluation | Worst observed lead | Does the model ever provide little warning? | Weak cases are hidden by the average. |
| `detection_lead_steps.maximum` | AI evaluation | Best observed lead | What is the largest synthetic early-warning gain? | Range of performance is incomplete. |
| `train_rows`, `test_rows` | AI evaluation | Number of records used | How much synthetic evidence supports the metrics? | Scale of the evaluation is unclear. |
| `training_seeds`, `test_seeds` | AI evaluation | Separated simulator groups | Was evaluation performed on unseen synthetic seeds? | Leakage controls are not visible. |

## 12. Survival and RUL model fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `age_fraction` | AI input | Relative point in simulated life | How far through its observation life is the device? | Hazard lacks time exposure. |
| `thermal_stress` | AI input | Accumulated heat-related burden | Is heat increasing lifecycle risk? | Thermal aging is ignored. |
| `twin_deviation` | AI input | Contextual abnormality | Does abnormal behavior raise lifecycle risk? | The survival model loses personalized condition evidence. |
| `ecc_rate` | AI input | Growth rate of memory errors | Is memory degradation contributing to risk? | Memory-related lifecycle risk is hidden. |
| `fan_loss` | AI input | Loss of cooling effectiveness | Is cooling degradation shortening expected life? | A central degradation mechanism disappears. |
| `failed` | AI target | Whether failure occurred in the interval | Did the event happen now? | Hazard training is impossible. |
| `interval` | AI input, Dashboard lab | Time bucket being evaluated | When is risk being estimated? | Hazard and survival cannot be ordered over time. |
| `event_interval` | AI target | Interval where failure occurred | When did the device fail? | Event timing and censoring logic break. |
| `device_id` | AI evaluation | Device owning the history | Are train and test split by physical device? | The same device may leak into both sets. |
| `hazard` | AI output | Conditional event risk in one interval | What is the near-term risk among surviving devices? | Survival cannot be updated. |
| `survival_curve` | AI output, Dashboard lab | Survival probability across intervals | How does risk accumulate over time? | RUL becomes one unexplained number. |
| `interval_brier_score` | AI evaluation | Error of predicted interval risk | Are the probabilities close to actual outcomes? | Probability quality is unknown. |
| `concordance_index` | AI evaluation | Ability to rank higher-risk devices above controls | Does the model prioritize risk correctly? | Ranking usefulness cannot be evaluated. |
| `comparable_device_pairs` | AI evaluation | Number of event-control comparisons | How much evidence supports concordance? | Metric stability is unclear. |
| `calibration_bins.range` | AI evaluation | Probability band | At what predicted risk level are we checking calibration? | Calibration results lack context. |
| `calibration_bins.n` | AI evaluation | Records in a probability band | Is a calibration estimate based on enough examples? | Small unstable groups look trustworthy. |
| `calibration_bins.mean_predicted` | AI evaluation | Average predicted risk in the band | What did the model predict? | Prediction and outcome cannot be compared. |
| `calibration_bins.observed` | AI evaluation | Actual event rate in the band | What really happened? | Calibration cannot be measured. |
| `positive_weight` | AI training | Extra training weight for rare events | How is event imbalance handled? | Rare failures may be ignored or risk may be overstated without documentation. |
| `training_split`, `test_split` | AI evaluation | Definitions of model-development populations | Was evaluation separated properly? | Results can be overstated through leakage. |
| `train_intervals`, `test_intervals` | AI evaluation | Number of interval rows | How much evidence was used? | Evaluation scale disappears. |
| `rul_output` | AI metadata | Definition of the lifecycle output | What does the model mean by RUL? | Users may interpret simulator intervals as real hours. |

## 13. Wafer defect and yield fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `wafer_id` | Dashboard lab, Lineage | Unique wafer name | Which wafer is being analyzed? | Results cannot be linked to genealogy or disposition. |
| `pattern` | AI target | Generated defect family | What synthetic class should be recovered? | Evaluation cannot compare predicted and known patterns. |
| `dies` | AI input | Die coordinates and pass/fail values | Where are defects located on the wafer? | Spatial analysis is impossible. |
| `x`, `y` | AI input | Normalized die position | Is a defect near the edge, center, or a line? | Spatial signatures disappear. |
| `row`, `col` | Dashboard lab | Grid position used to draw a die | Where should the die appear on the map? | The wafer visualization cannot be rendered. |
| `bad` | Dashboard lab, AI input | Whether a die failed | Which dies are defects? | Yield and spatial features cannot be calculated. |
| `defect_rate` | AI input | Failed dies divided by tested dies | How severe is the wafer problem overall? | Yield impact and normal-pattern scoring weaken. |
| `edge_concentration` | AI input | Share of defects near the edge | Does the map resemble an edge ring? | Edge-related signatures are missed. |
| `center_concentration` | AI input | Share of defects near the center | Does the map resemble a center cluster? | Center-zone signatures are missed. |
| `linear_concentration` | AI input | Share of defects following a line | Does the map resemble a scratch? | Handling-related linear signatures are missed. |
| `scores.normal` | AI output | Strength of the normal hypothesis | Does the wafer lack a dominant abnormal pattern? | Normal wafers may be forced into a defect class. |
| `scores.edge_ring` | AI output | Strength of the edge-ring hypothesis | How well does edge concentration fit? | Edge-ring ranking cannot be explained. |
| `scores.center_cluster` | AI output | Strength of the center-cluster hypothesis | How well does center concentration fit? | Center-cluster ranking cannot be explained. |
| `scores.scratch` | AI output | Strength of the linear hypothesis | How well does a scratch-like line fit? | Scratch ranking cannot be explained. |
| `predicted_pattern` | Dashboard lab, AI output | Highest-ranked spatial signature | Which pattern should an engineer inspect first? | The analysis produces features without a conclusion. |
| `confidence` | AI output | Relative strength of the top pattern | How decisive is the pattern ranking? | Weak and strong classifications look the same. |
| `yield_pct` | Dashboard lab, AI output | Percentage of passing dies | What is the business impact on usable output? | Pattern analysis is disconnected from production value. |
| `ranked_patterns` | Dashboard lab, AI output | Ordered alternatives and scores | What other patterns could explain the wafer? | The top result looks certain and alternatives disappear. |
| `recommended_next_step` | AI output | Suggested engineering follow-up | What evidence should be checked next? | Classification does not lead to investigation. |
| `next_step` | Browser alias | Plain-language follow-up | What should the viewer do with the map result? | The live demonstration stops at a label. |
| `accuracy` | AI evaluation | Share of generated wafers classified correctly | Does the baseline recover its synthetic patterns? | There is no summary of test performance. |
| `test_wafers` | AI evaluation | Number of evaluated maps | How much synthetic evidence supports accuracy? | Evaluation scale is hidden. |
| `confusion_matrix` | AI evaluation | Actual versus predicted pattern counts | Which pattern types are confused? | Overall accuracy can hide class-specific failure. |
| `data_boundary` | AI governance | Statement describing synthetic evaluation | What does the accuracy prove and not prove? | Synthetic accuracy can be mistaken for fab performance. |

## 14. Engineering copilot and evidence fields

| Field | Role | Simple meaning | Question answered | If removed |
| --- | --- | --- | --- | --- |
| `evidence_id` | Dashboard lab, AI governance | Unique identifier for one fact | Which exact fact supports the answer? | Citations and auditability disappear. |
| `source_type` | AI governance | Approved category of evidence source | Is this evidence allowed into the investigation? | Free text or unsafe sources can be treated as sensor truth. |
| `source_ref` | AI governance | Pointer to the original source | Where can an engineer verify this fact? | Evidence becomes difficult to check. |
| `statement` | Dashboard lab | Human-readable fact | What does the evidence say? | IDs exist without understandable meaning. |
| `tags` | AI input | Search and reasoning labels | Which evidence relates to thermal, cooling, peers, or maintenance? | Retrieval and rule-based grouping become slow or inaccurate. |
| `quality` | AI input | Trust score for evidence | Should one source rank above another? | Weak and strong evidence are treated equally. |
| `case_id` | Lineage | Unique copilot investigation | Which question, evidence, and action belong together? | Cases cannot be audited or resumed. |
| `question` | Dashboard lab, AI input | Engineering problem being investigated | What is the copilot trying to answer? | Retrieval and conclusions have no defined purpose. |
| `retrieved` | AI output | Evidence selected for the case | What facts did the copilot actually use? | The answer cannot be reproduced. |
| `hypotheses` | AI output | Ranked possible causes | What explanations are being compared? | The copilot becomes a one-answer chatbot. |
| `rank` | AI output | Order of a hypothesis | Which cause should be investigated first? | Alternatives are not prioritized. |
| `cause` | AI output | Name of a hypothesis | What possible explanation is this row about? | Scores and evidence have no meaning. |
| `supporting_evidence_ids` | Dashboard lab, AI output | Facts strengthening a hypothesis | Why might this cause be right? | Grounding cannot be checked. |
| `contradicting_evidence_ids` | Dashboard lab, AI output | Facts weakening a hypothesis | Why might this cause be wrong? | Confirmation bias increases. |
| `reasoning` | AI output | Explanation connecting evidence to the hypothesis | How did the facts lead to this ranking? | The result becomes hard to understand. |
| `leading_hypothesis` | Dashboard lab, AI output | Top cause in the browser demonstration | What should be investigated first? | The live case lacks a conclusion. |
| `contradicting_alternative` | Dashboard lab, AI output | Alternative weakened by evidence | What important explanation was considered and challenged? | The demonstration hides counterevidence. |
| `missing_evidence` | Dashboard lab, AI output | Facts still required | What must be collected before confirmation? | The copilot may sound more certain than the evidence allows. |
| `proposed_actions` | AI output | Bounded next steps | What should be done next? | Investigation does not turn into a workflow. |
| `approval_required` | AI governance | Whether an action needs a person | Can this action proceed automatically? | Human control can be bypassed. |
| `grounding_boundary` | Dashboard lab, AI governance | Statement limiting what the answer claims | Is this evidence or confirmed physical truth? | A ranked hypothesis may be mistaken for proof. |
| `audit_note` | AI governance | Record of what was or was not executed | Did approval cause an external action? | The action history becomes ambiguous. |

## 15. Static healthcare demonstration fields

These fields appear only as illustrative device-monitoring content on the dashboard.

| Field | Simple meaning | Why included | If removed |
| --- | --- | --- | --- |
| `sensor_id` | Example device such as HS-001 | Shows that the architecture can identify another sensor category | Cross-domain identity is not demonstrated. |
| `device_health` | Healthy or degraded device condition | Separates device health from clinical interpretation | The safety point about monitoring hardware rather than diagnosing people is weaker. |
| `signal_quality` | Trust in the sensor signal | Shows that data quality matters in every sensing domain | Bad measurements may appear trustworthy. |
| `battery_voltage` | Device battery level | Demonstrates operational device telemetry | The example has less concrete hardware context. |
| `packet_loss` | Missing communication packets | Demonstrates communication degradation | Network quality cannot be separated from the measured signal. |
| `drift` | Sensor measurement drift | Demonstrates measurement reliability risk | Sensor problems may be confused with real-world change. |

## 16. Question-to-field map

Important questions are rarely answered by one field. The project combines fields so that context, evidence, and uncertainty stay visible.

| Business or engineering question | Fields used together | Why the combination matters |
| --- | --- | --- |
| Which device needs attention first? | `device_id` + `anomaly_score` + `failure_probability` + `health_score` + `lifecycle` | Identity tells us where to act, while several scores prevent one signal from controlling the decision alone. |
| Is GPU-042 hotter than it should be? | `temperature_c` + `utilization_pct` + `power_watts` + `ambient_temperature_c` + `twin_expected_temp` | Temperature only becomes meaningful after workload, power, environment, and expected behavior are considered. |
| Is the issue local to the device or shared by the rack? | `device_id` + `rack_id` + `temperature_c` + `twin_deviation` + `peer_temperature_delta` | Peer grouping separates device-local cooling from rack cooling. |
| Is the fan failing or is the wider cooling path degrading? | `fan_speed_rpm` + `fan_efficiency_proxy` + `cooling_efficiency` + `temperature_rate` + `twin_deviation` | A spinning fan does not prove that heat is being removed effectively. |
| Is performance being affected? | `throughput` + `utilization_pct` + `clock_speed_mhz` + `base_clock_mhz` + `network_latency_ms` + `temperature_c` | The combination separates thermal throttling, low demand, and network bottlenecks. |
| Is memory degrading? | `ecc_correctable_errors` + `ecc_uncorrectable_errors` + `memory_utilization_pct` + `age_hours` | Correctable errors show a trend; uncorrectable errors show critical impact; utilization and age add context. |
| Can we trust the measurement? | `sensor_quality` + `timestamp` + `ingestion_timestamp` + `sequence_number` + drift evidence | Quality, freshness, order, and drift determine whether a value is usable. |
| Did firmware contribute to the problem? | `firmware_version` + `timestamp` + error, clock, and incident trends | A version only becomes useful when aligned with behavior before and after deployment. |
| How urgent is the incident? | `severity` + `failure_probability` + `rul_hours` + `affected_devices` + `status` | Risk, time, scope, and workflow state together define urgency. |
| What cause best fits the evidence? | `cause` + `score` + `supporting_evidence` + `contradicting_evidence` + `missing_evidence` | Ranking without counterevidence or missing facts creates false certainty. |
| What should the engineer do next? | `likely_root_cause` + `recommendation` + `expected_impact` + `risk` + `missing_evidence` | The action must connect diagnosis, expected benefit, downside, and remaining uncertainty. |
| May the action proceed? | `approval_required` + `approval_status` + `decided_by` + `decided_at` + `comments` | These fields prove that a responsible person reviewed the action. |
| Did the action work? | Before-and-after `temperature_c`, `twin_deviation`, `anomaly_score`, `failure_probability`, `health_score`, plus `outcome` | Outcome requires comparison, not merely a record that an action occurred. |
| How much earlier did AI detect degradation? | `model_detection_step` + static threshold step + `detection_lead_steps` | The comparison translates a model prediction into operational lead time. |
| Which device is likely to fail earlier? | Survival features + `hazard` + `survival_curve` + `concordance_index` | Inputs create risk, the curve shows time, and concordance checks ranking quality. |
| Are lifecycle probabilities believable? | `mean_predicted` + `observed` + `n` within each calibration range | Calibration compares what the model said with what happened. |
| Which wafer pattern deserves investigation? | Die `x`, `y`, `bad` + spatial concentrations + ranked pattern scores | A label is only understandable when tied to the spatial evidence that produced it. |
| What is the wafer business impact? | `yield_pct` + `defect_rate` + `predicted_pattern` + wafer and lot identity | Yield quantifies impact while the pattern and genealogy guide investigation. |
| Can the copilot answer safely? | `question` + approved `source_type` + `source_ref` + `quality` + evidence IDs + `grounding_boundary` | Safe answers require a defined question, allowed sources, traceability, and explicit limits. |
| Can the entire incident be audited? | Event IDs + correlation and causation IDs + incident ID + agent run ID + approval ID + report ID + timestamps | Linked identifiers reconstruct the full path from signal to decision. |

## 17. What happens if one dashboard field disappears?

Dashboard fields are not equally prominent, but every displayed field protects against a specific misunderstanding.

- Removing an identity field creates action risk because a correct insight may be applied to the wrong asset.
- Removing a raw measurement hides the physical evidence behind the result.
- Removing context such as workload, power, rack, or firmware increases false conclusions.
- Removing a twin or AI score eliminates prioritization and early detection.
- Removing confidence, counterevidence, or limitations creates false certainty.
- Removing time or status makes old information look current.
- Removing approval fields weakens safety and accountability.
- Removing outcome fields breaks the feedback loop, so the system cannot learn whether an intervention helped.

The worst overall case is not simply a blank card. It is a dashboard that still looks complete while silently losing the context needed to make a safe decision.

## 18. AI field dependency summary

### Cooling detection

Inputs: temperature, power, utilization, fan proxy, peer delta, and temperature rate.

Output: cooling-degradation probability and class.

Without any one input, the model loses a different piece of physical context. Without the output, the project can still show telemetry, but it cannot demonstrate trained early-warning intelligence.

### Operational twin and anomaly

Inputs: device identity, rack peers, utilization, power, temperature, baseline residual, baseline maturity, fan behavior, ECC errors, and sensor quality.

Outputs: expected temperature, deviation, twin confidence, and anomaly score.

Without these outputs, the dashboard becomes primarily threshold monitoring. It loses personalization, early contextual detection, and risk ranking.

### Failure risk and health

Inputs: twin deviation, anomaly, cooling and fan behavior, errors, temperature, RUL, and sensor quality.

Outputs: failure type, failure probability, health score, and lifecycle state.

Without them, a business user must interpret raw engineering signals and cannot quickly prioritize the fleet.

### Survival and RUL

Inputs: age fraction, thermal stress, twin deviation, ECC rate, fan loss, failure indicator, interval, and censoring information.

Outputs: hazard, survival curve, and remaining-life summaries.

Without these fields, the project can say that a device looks abnormal but cannot organize risk over time or support maintenance planning.

### Wafer intelligence

Inputs: wafer identity, die position, die result, and spatial concentrations.

Outputs: yield, predicted pattern, confidence, ranked alternatives, and next step.

Without these fields, the project loses its manufacturing intelligence story and cannot connect AI to yield learning.

### Root cause and engineering copilot

Inputs: evidence IDs, source references, evidence quality, tags, device and peer facts, incident history, and the engineering question.

Outputs: ranked hypotheses, supporting evidence, contradicting evidence, missing evidence, proposed actions, and grounding boundary.

Without these fields, the copilot becomes an ungrounded chatbot. It may sound helpful, but engineers cannot verify its answer or understand what is still unknown.

### Evaluation and governance

Inputs and outputs: train/test split fields, seeds, confusion counts, precision, recall, F1, false-positive rate, Brier score, concordance, calibration, limitations, approvals, and audit identifiers.

Without these fields, the project may still run, but there is no honest evidence that the AI works, no visible boundary around synthetic results, and no proof that people remain in control.

## 19. Final principle

Every field should earn its place by supporting one of five needs:

1. Identify the asset or case
2. Describe what physically happened
3. Add the context needed to interpret it
4. Produce or evaluate an AI-assisted decision
5. Preserve safety, lineage, and accountability

If a field does none of these, it probably does not belong. If it does one of them, removing it should be treated as a product decision rather than a cosmetic dashboard change.
