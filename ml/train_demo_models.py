"""Reproducible, dependency-free benchmark for the SiliconPulse executive demo.

This is intentionally small enough to audit.  It trains a logistic-regression
anomaly classifier with gradient descent on synthetic devices and evaluates it
on unseen random seeds.  Hidden scenario labels are used only as training /
evaluation targets; they are never exposed to inference or RCA.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
FEATURES = [
    "temperature_c",
    "power_watts",
    "utilization_pct",
    "fan_efficiency_proxy",
    "peer_temperature_delta",
    "temperature_rate",
]


@dataclass
class Row:
    x: list[float]
    y: int
    seed: int
    step: int
    scenario: str


def sigmoid(value: float) -> float:
    value = max(-35.0, min(35.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def generate(seed: int, scenario: str, steps: int = 90) -> list[Row]:
    """Generate coupled thermal telemetry, not independent random columns."""
    rng = random.Random(seed)
    temp = 54.0 + rng.uniform(-2.0, 2.0)
    previous = temp
    rows: list[Row] = []
    for step in range(steps):
        utilization = max(15.0, min(98.0, 58.0 + rng.gauss(0, 8)))
        power = 90.0 + utilization * 4.2 + rng.gauss(0, 7)
        progress = max(0.0, (step - 22) / 55.0)
        degraded = scenario == "cooling_degradation" and step >= 22
        cooling = 1.0 - (0.52 * min(progress, 1.0) if degraded else 0.0)
        peer_temp = 53.0 + utilization * 0.08 + rng.gauss(0, 0.7)
        expected = 31.0 + utilization * 0.18 + power * 0.022
        thermal_target = expected + ((1.0 - cooling) * 30.0)
        temp += (thermal_target - temp) * 0.14 + rng.gauss(0, 0.12)
        fan_rpm = max(500.0, (1850.0 + (temp - 40.0) * 52.0) * cooling)
        fan_proxy = fan_rpm / max(1850.0 + (temp - 40.0) * 52.0, 1.0)
        rate = temp - previous
        previous = temp
        rows.append(
            Row(
                x=[temp, power, utilization, fan_proxy, temp - peer_temp, rate],
                y=int(degraded and progress >= 0.12),
                seed=seed,
                step=step,
                scenario=scenario,
            )
        )
    return rows


def standardize(train: list[Row], test: list[Row]) -> tuple[list[float], list[float]]:
    means = [sum(row.x[i] for row in train) / len(train) for i in range(len(FEATURES))]
    scales = []
    for i, mean in enumerate(means):
        variance = sum((row.x[i] - mean) ** 2 for row in train) / len(train)
        scales.append(max(variance**0.5, 1e-6))
    for row in train + test:
        row.x = [(value - means[i]) / scales[i] for i, value in enumerate(row.x)]
    return means, scales


def train_logistic(rows: list[Row], epochs: int = 900, learning_rate: float = 0.08) -> tuple[float, list[float]]:
    bias = 0.0
    weights = [0.0] * len(FEATURES)
    positive = sum(row.y for row in rows)
    positive_weight = (len(rows) - positive) / max(positive, 1)
    for _ in range(epochs):
        grad_b = 0.0
        grad_w = [0.0] * len(weights)
        for row in rows:
            prediction = sigmoid(bias + sum(w * x for w, x in zip(weights, row.x, strict=True)))
            weight = positive_weight if row.y else 1.0
            error = (prediction - row.y) * weight
            grad_b += error
            for i, value in enumerate(row.x):
                grad_w[i] += error * value
        n = len(rows)
        bias -= learning_rate * grad_b / n
        for i in range(len(weights)):
            weights[i] -= learning_rate * (grad_w[i] / n + 0.001 * weights[i])
    return bias, weights


def probability(row: Row, bias: float, weights: list[float]) -> float:
    return sigmoid(bias + sum(w * x for w, x in zip(weights, row.x, strict=True)))


def metrics(rows: list[Row], bias: float, weights: list[float], threshold: float = 0.5) -> dict[str, float | int]:
    tp = fp = tn = fn = 0
    for row in rows:
        predicted = int(probability(row, bias, weights) >= threshold)
        if predicted and row.y:
            tp += 1
        elif predicted:
            fp += 1
        elif row.y:
            fn += 1
        else:
            tn += 1
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(2 * precision * recall / max(precision + recall, 1e-12), 4),
        "false_positive_rate": round(fp / max(fp + tn, 1), 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def lead_time(rows: list[Row], bias: float, weights: list[float]) -> dict[str, float | int | None]:
    degraded = [row for row in rows if row.scenario == "cooling_degradation"]
    model_step = next((row.step for row in degraded if probability(row, bias, weights) >= 0.5), None)
    threshold_step = next((row.step for row in degraded if row.x[0] >= 85.0), None)
    # row.x is standardized here, so reconstruct threshold timing separately in main.
    return {"model_detection_step": model_step, "static_threshold_step": threshold_step}


def main() -> None:
    train_rows = [
        row
        for seed in range(10, 30)
        for scenario in ("normal", "cooling_degradation")
        for row in generate(seed, scenario)
    ]
    raw_test = [
        row
        for seed in range(101, 111)
        for scenario in ("normal", "cooling_degradation")
        for row in generate(seed, scenario)
    ]
    test_rows = [Row(list(row.x), row.y, row.seed, row.step, row.scenario) for row in raw_test]
    means, scales = standardize(train_rows, test_rows)
    bias, weights = train_logistic(train_rows)
    result = metrics(test_rows, bias, weights)

    detection_leads = []
    for seed in range(101, 111):
        standardized = [row for row in test_rows if row.seed == seed and row.scenario == "cooling_degradation"]
        raw = [row for row in raw_test if row.seed == seed and row.scenario == "cooling_degradation"]
        model_step = next((row.step for row in standardized if probability(row, bias, weights) >= 0.5), None)
        threshold_step = next((row.step for row in raw if row.x[0] >= 85.0), None)
        if model_step is not None:
            comparison_step = threshold_step if threshold_step is not None else 90
            detection_leads.append(comparison_step - model_step)

    artifact = {
        "model_name": "synthetic-cooling-logistic-v1",
        "model_type": "logistic_regression_gradient_descent",
        "features": FEATURES,
        "training_seeds": "10-29",
        "test_seeds": "101-110",
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "normalization": {"mean": means, "scale": scales},
        "intercept": bias,
        "coefficients": weights,
        "decision_threshold": 0.5,
        "test_metrics": result,
        "detection_lead_steps": {
            "mean": round(sum(detection_leads) / len(detection_leads), 2),
            "minimum": min(detection_leads),
            "maximum": max(detection_leads),
            "note": "Compared with an 85C static threshold; 90 means threshold did not fire in the window.",
        },
        "limitations": [
            "Trained and tested only on synthetic telemetry.",
            "Metrics demonstrate pipeline correctness, not production GPU reliability.",
            "One simulation step represents one demo sampling interval, not a validated wall-clock duration.",
        ],
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "cooling_anomaly_model.json").write_text(json.dumps(artifact, indent=2) + "\n")
    (ARTIFACT_DIR / "evaluation_summary.json").write_text(
        json.dumps(
            {
                "model": artifact["model_name"],
                "test_metrics": result,
                "detection_lead_steps": artifact["detection_lead_steps"],
                "data_boundary": "unseen random seeds; synthetic telemetry only",
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
