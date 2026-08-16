# Synthetic Silicon Survival Model Card

## Intended decision

Estimate interval failure hazard and a survival curve so an engineer can prioritize inspection or maintenance. The output is a risk estimate, not a guaranteed failure time.

## Model

- Weighted logistic discrete-time survival model
- Right-censored synthetic device histories
- Features: age fraction, thermal stress, twin deviation, ECC rate, and fan-loss proxy
- Device-separated training and test fleets
- Outputs: per-interval hazard, survival curve, and RUL quantiles when the curve crosses the relevant probability

## Evaluation

Run `python ml/train_survival_model.py`. The committed artifact records dynamic concordance, interval Brier score, and calibration bins on unseen synthetic devices.

Dynamic concordance compares an event with devices still at risk during the same interval. This prevents device age alone from receiving artificial credit.

## Required production validation

1. Define failure and censoring with reliability engineers.
2. Split by physical device and forward time; also hold out product, lot, workload, and environment where appropriate.
3. Calibrate hazard for each deployment population.
4. Report uncertainty, false-alarm burden, lead time, and decision utility.
5. Validate monitor drift and missingness.
6. Operate in shadow mode before maintenance decisions.

## Limitations

- Synthetic telemetry only.
- Simulator intervals are not wall-clock hours.
- No production silicon failure labels.
- No claim of transfer across products, process nodes, packaging, firmware, or environments.
