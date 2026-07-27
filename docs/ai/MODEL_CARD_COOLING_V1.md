# Model Card — Synthetic Cooling Detector v1

## Intended use

`synthetic-cooling-logistic-v1` demonstrates a reproducible model lifecycle for detecting
simulated device-local cooling degradation. It is an executive-prototype model, not a
production GPU reliability model.

## Model

- Logistic regression trained with batch gradient descent
- Six observable features: temperature, power, utilization, fan-efficiency proxy,
  device-to-peer temperature delta, and temperature rate of change
- Decision threshold: 0.5
- Dependency-free training implementation: `ml/train_demo_models.py`
- Serialized artifact: `ml/artifacts/cooling_anomaly_model.json`

## Data boundary

- Training seeds: 10–29
- Test seeds: 101–110
- Training and test seeds do not overlap
- 3,600 training rows and 1,800 held-out test rows
- Both normal and cooling-degradation trajectories are represented
- Hidden labels are used only as supervised targets and evaluation truth
- Inference receives observable features only

## Held-out synthetic results

| Metric | Result |
| --- | ---: |
| Precision | 1.000 |
| Recall | 0.966 |
| F1 | 0.983 |
| False-positive rate | 0.000 |
| True positives | 589 |
| False positives | 0 |
| True negatives | 1,190 |
| False negatives | 21 |

Across ten held-out cooling trajectories, the detector fired an average of 59.8 simulation
steps before an 85°C static threshold. When the static threshold did not fire during the
90-step observation window, the end of that window was used for a conservative finite
comparison.

## Interpretation

These results establish that:

1. The repository contains a real train/evaluate/serialize/infer path.
2. The model generalizes across unseen random seeds within the same simulator family.
3. Coupled features can detect the simulated degradation before a late temperature threshold.

These results do **not** establish:

- Performance on NVIDIA, AMD, Intel, or customer telemetry
- Calibrated probability of physical GPU failure
- Generalization across hardware generations, workloads, firmware, facilities, or sensor stacks
- A validated remaining-useful-life estimate

## Known risks

- Synthetic train and test data share the same generating assumptions.
- The simulator may make the classification boundary unrealistically clean.
- The reported probability is class probability under this synthetic model, not physical
  failure probability.
- Production validation requires real incident labels, device-aware/time-aware splits,
  calibration, drift tests, and cost-sensitive thresholds.

## Reproduction

```bash
python ml/train_demo_models.py
python -m unittest tests.unit.test_demo_model -v
```

The training script deterministically regenerates both committed JSON artifacts.
