# SiliconPulse AI — AI Strategy

## Guiding principle

**Structured intelligence first, language last.**

1. Predictive models produce **evidence** (scores, classes, attributions).
2. Root-cause logic **combines evidence** into ranked hypotheses.
3. Generative AI **explains evidence** with citations.
4. Agents **coordinate workflows** with tool allowlists and human approval.

The LLM must not invent telemetry or independently diagnose raw signals without structured support.

## Local / open-source constraint

| Capability | Technology | Notes |
| --- | --- | --- |
| Classical ML | scikit-learn, NumPy, Pandas | Isolation Forest primary anomaly model initially |
| Explainability | SHAP (where compatible) | Stored with model version |
| Experiment tracking | MLflow | Local tracking server or file store in Compose |
| Generative AI | Ollama + configurable instruction model | Fallback model names via env; mock in CI |
| Retrieval | Postgres + runbooks + incident features | No paid vector DB required for v1 |

## Model portfolio (v1)

### Anomaly detection

- Baselines: z-score, rolling percentile
- Models: Isolation Forest (primary), LOF / One-Class SVM where practical
- Outputs: anomaly score, status, top abnormal features, model version, timestamp

### Failure classification

- Candidates: Logistic Regression, Random Forest, Gradient Boosting
- Classes: cooling degradation, fan failure, memory degradation, voltage instability, firmware regression, rack cooling failure, sensor drift, network bottleneck, workload overload, normal
- Metrics: precision, recall, F1, confusion matrix, calibration
- Caveat: synthetic data only — not production-validated

### Remaining useful life

- Baselines: linear regression
- Candidates: RF / GBR regressors
- Output: RUL hours (+ CI where practical)

### Survival analysis (demonstration)

- Kaplan-Meier by cohort; Cox PH and/or random survival forest if justified
- Outputs: 24h / 7d survival probability, hazard score

### Digital twin (statistical)

- Peer-group baseline + regressors (linear / RF / GBR) per metric
- Outputs: expected metrics, deviation score, confidence, twin version
- Not a transistor-level physics twin

### Health score (0–100)

- Configurable, documented, testable formula from thermal stress, anomaly frequency, failure probability, RUL, errors, voltage, throughput, age, maintenance, twin deviation, sensor confidence
- Lifecycle states: `healthy`, `stressed`, `degraded`, `maintenance_recommended`, `critical`, `retired`
- Labeled as **platform-derived operational score**

## Feature engineering (initial set)

Rolling temperature mean/std, temperature ROC, power mean/variance, voltage variance, utilization-adjusted temperature/power, fan efficiency, throughput change, error rate/acceleration, clock throttling ratio, peer/rack temperature difference, twin deviation, missingness, sensor confidence, device age, firmware/workload encodings.

## Training and reproducibility

- Deterministic simulation seeds for datasets
- Versioned datasets in MinIO (`training-datasets`)
- MLflow: params, metrics, artifacts, selected production version
- Model cards under `ml/model-cards/` and `docs/ai/MODEL_CARDS.md`
- Training via `make train-models` / `scripts/training/` (implemented in later phases)

## Generative AI (Copilot)

### Pipeline

1. Receive question → classify intent → extract entities  
2. Retrieve trusted structured data, runbooks, related incidents  
3. Construct grounded prompt → call Ollama → validate output  
4. Return answer with evidence references  

### Guardrails

- No invented telemetry or fabricated incidents
- Distinguish fact vs hypothesis; surface uncertainty and missing data
- Cite evidence IDs or timestamps
- Do not execute actions; do not provide medical diagnoses
- Preserve simulation and healthcare disclaimers
- Prompt-injection boundaries: tool outputs treated as untrusted text for instructions

### Supported answer styles

Technical explanation, operator summary, executive summary, maintenance recommendation draft, incident report draft, root-cause narrative, daily fleet briefing — all grounded.

## Evaluation honesty

Document in every model card and README:

- Synthetic training data
- Demonstration-grade predictions
- Simplified semiconductor behavior
- Human review required for operational decisions
- Real deployment would require domain data and validation

## Phase boundary

The repository now includes dependency-free trained demonstrations for cooling classification and discrete-time survival, an interpretable wafer-pattern baseline, and a structured engineering-copilot reference. Full inference services, SHAP storage, production retrieval, and configurable LLM integration remain later-phase work.

## Implemented semiconductor-AI extensions

SiliconPulse uses different model families for different engineering decisions. “AI” is not a single undifferentiated component.

| Decision | Current evidence | Production direction |
| --- | --- | --- |
| Detect cooling degradation | Trained logistic classifier on held-out synthetic seeds | Calibrated multivariate time-series models on device/time-aware splits |
| Estimate lifecycle risk | Discrete-time survival benchmark with censoring and calibration bins | Product-specific survival, uncertainty, competing risks, and shadow-mode validation |
| Triage wafer signatures | Interpretable spatial-feature baseline on generated maps | Vision + genealogy + process analytics with lot/time-aware validation |
| Rank root cause | Deterministic device/peer evidence competition | Causal and graph evidence over monitor, test, maintenance, firmware, and workload history |
| Explain and act | Structured copilot case with evidence IDs and approval gates | Governed retrieval, expert evaluation, least-privilege tools, and immutable audit |

### Updated governing principles

1. Evidence first; language last.
2. Split by physical entity and forward time to prevent leakage.
3. Calibrate risk before attaching operational meaning.
4. Show contradicting and missing evidence, not only a leading hypothesis.
5. Require human approval for high-impact actions.
6. Label synthetic evidence and transfer boundaries prominently.
