"""Reproducible discrete-time survival benchmark for synthetic silicon telemetry.

The model estimates interval failure hazard and derives a survival curve and
remaining-useful-life quantiles. It is intentionally dependency-free and is a
method demonstration, not a production reliability claim.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
FEATURES = ["age_fraction", "thermal_stress", "twin_deviation", "ecc_rate", "fan_loss"]


@dataclass
class Interval:
    device_id: str
    x: list[float]
    failed: int
    interval: int
    event_interval: int | None


def sigmoid(value: float) -> float:
    value = max(-35.0, min(35.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def generate_fleet(seed: int, devices: int = 240, intervals: int = 24) -> list[Interval]:
    """Generate right-censored interval records from a coupled degradation process."""
    rng = random.Random(seed)
    rows: list[Interval] = []
    for index in range(devices):
        device_id = f"SIM-{seed}-{index:04d}"
        vulnerability = rng.uniform(-0.7, 0.8)
        fan_loss = max(0.0, rng.gauss(0.12 + 0.12 * max(vulnerability, 0), 0.08))
        event_interval: int | None = None
        pending: list[tuple[list[float], int]] = []
        for interval in range(intervals):
            age_fraction = interval / (intervals - 1)
            thermal = max(0.0, 0.18 + 0.58 * age_fraction + 0.24 * fan_loss + rng.gauss(0, 0.05))
            twin = max(0.0, thermal - 0.35 + rng.gauss(0, 0.04))
            ecc = max(0.0, age_fraction * max(vulnerability, 0) * 0.65 + rng.gauss(0, 0.025))
            x = [age_fraction, thermal, twin, ecc, fan_loss]
            logit = -6.2 + 1.1 * age_fraction + 2.4 * thermal + 2.0 * twin + 1.5 * ecc + 1.8 * fan_loss
            failed = int(rng.random() < sigmoid(logit))
            pending.append((x, failed))
            if failed:
                event_interval = interval
                break
        for interval, (x, failed) in enumerate(pending):
            rows.append(Interval(device_id, x, failed, interval, event_interval))
    return rows


def standardize(train: list[Interval], test: list[Interval]) -> tuple[list[float], list[float]]:
    means = [sum(row.x[i] for row in train) / len(train) for i in range(len(FEATURES))]
    scales = []
    for i, mean in enumerate(means):
        variance = sum((row.x[i] - mean) ** 2 for row in train) / len(train)
        scales.append(max(variance**0.5, 1e-6))
    for row in train + test:
        row.x = [(value - means[i]) / scales[i] for i, value in enumerate(row.x)]
    return means, scales


def train_hazard(rows: list[Interval], epochs: int = 600, rate: float = 0.045) -> tuple[float, list[float]]:
    bias = 0.0
    weights = [0.0] * len(FEATURES)
    positives = sum(row.failed for row in rows)
    # Temper imbalance rather than fully reweighting it; full balancing badly
    # overstates absolute hazard and damages calibration.
    positive_weight = min(4.0, math.sqrt((len(rows) - positives) / max(positives, 1)))
    for _ in range(epochs):
        grad_b = 0.0
        grad_w = [0.0] * len(weights)
        for row in rows:
            pred = sigmoid(bias + sum(w * x for w, x in zip(weights, row.x, strict=True)))
            sample_weight = positive_weight if row.failed else 1.0
            error = (pred - row.failed) * sample_weight
            grad_b += error
            for i, value in enumerate(row.x):
                grad_w[i] += error * value
        bias -= rate * grad_b / len(rows)
        for i in range(len(weights)):
            weights[i] -= rate * (grad_w[i] / len(rows) + 0.002 * weights[i])
    return bias, weights


def hazard(row: Interval, bias: float, weights: list[float]) -> float:
    return sigmoid(bias + sum(w * x for w, x in zip(weights, row.x, strict=True)))


def evaluate(rows: list[Interval], bias: float, weights: list[float]) -> dict[str, object]:
    predictions = [(hazard(row, bias, weights), row.failed) for row in rows]
    brier = sum((pred - actual) ** 2 for pred, actual in predictions) / len(predictions)
    # Dynamic concordance: at each interval compare an event with devices still
    # at risk at that same interval. This avoids rewarding age alone.
    pairs = 0
    concordant = 0.0
    by_interval: dict[int, list[tuple[float, int]]] = {}
    for row in rows:
        by_interval.setdefault(row.interval, []).append((hazard(row, bias, weights), row.failed))
    for group in by_interval.values():
        events = [risk for risk, failed in group if failed]
        controls = [risk for risk, failed in group if not failed]
        for event_risk in events:
            for control_risk in controls:
                pairs += 1
                if event_risk > control_risk:
                    concordant += 1
                elif event_risk == control_risk:
                    concordant += 0.5
    bins = []
    for low in (0.0, 0.05, 0.10, 0.20, 0.40):
        high = {0.0: 0.05, 0.05: 0.10, 0.10: 0.20, 0.20: 0.40, 0.40: 1.01}[low]
        group = [(p, y) for p, y in predictions if low <= p < high]
        if group:
            bins.append({"range": f"{low:.2f}-{min(high, 1):.2f}", "n": len(group),
                         "mean_predicted": round(sum(p for p, _ in group) / len(group), 4),
                         "observed": round(sum(y for _, y in group) / len(group), 4)})
    return {"interval_brier_score": round(brier, 4), "concordance_index": round(concordant / max(pairs, 1), 4),
            "comparable_device_pairs": pairs, "calibration_bins": bins}


def survival_curve(features_by_interval: list[list[float]], bias: float, weights: list[float]) -> list[float]:
    survival = 1.0
    curve = []
    for index, features in enumerate(features_by_interval):
        survival *= 1.0 - hazard(Interval("inference", features, 0, index, None), bias, weights)
        curve.append(survival)
    return curve


def main() -> None:
    train = generate_fleet(17)
    test = generate_fleet(91, devices=160)
    means, scales = standardize(train, test)
    bias, weights = train_hazard(train)
    evaluation = evaluate(test, bias, weights)
    artifact = {
        "model_name": "synthetic-silicon-discrete-hazard-v1",
        "model_type": "weighted_logistic_discrete_time_survival",
        "features": FEATURES,
        "training_split": "device-separated synthetic fleet seed 17",
        "test_split": "unseen devices synthetic fleet seed 91",
        "train_intervals": len(train), "test_intervals": len(test),
        "normalization": {"mean": means, "scale": scales},
        "intercept": bias, "coefficients": weights, "evaluation": evaluation,
        "rul_output": "survival curve plus median/10th/90th percentile interval when identifiable",
        "limitations": [
            "Synthetic right-censored telemetry only; no production silicon validation.",
            "Intervals are simulator units, not calibrated wall-clock hours.",
            "Calibration must be repeated by product, environment, workload, and monitor revision.",
        ],
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "silicon_survival_model.json").write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
