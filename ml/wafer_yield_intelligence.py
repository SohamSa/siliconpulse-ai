"""Synthetic wafer-map classification and yield-impact demonstration.

The module models the decision path (map -> features -> pattern -> evidence ->
disposition) without shipping proprietary fab data or pretending to identify a
physical process root cause from an image alone.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
PATTERNS = ("normal", "edge_ring", "center_cluster", "scratch")


@dataclass
class Wafer:
    wafer_id: str
    pattern: str
    dies: list[tuple[float, float, int]]


def generate_wafer(seed: int, pattern: str, size: int = 17) -> Wafer:
    if pattern not in PATTERNS:
        raise ValueError(f"unknown pattern: {pattern}")
    rng = random.Random(seed)
    dies = []
    radius = size / 2
    for row in range(size):
        for col in range(size):
            x = col - (size - 1) / 2
            y = row - (size - 1) / 2
            r = math.sqrt(x * x + y * y) / radius
            if r > 1:
                continue
            probability = 0.015
            if pattern == "edge_ring" and r > 0.72:
                probability += 0.58
            elif pattern == "center_cluster" and r < 0.34:
                probability += 0.66
            elif pattern == "scratch" and abs(y - 0.42 * x) < 0.8:
                probability += 0.72
            failed = int(rng.random() < probability)
            dies.append((x / radius, y / radius, failed))
    return Wafer(f"WAFER-{seed:04d}", pattern, dies)


def features(wafer: Wafer) -> dict[str, float]:
    failed = [(x, y) for x, y, bad in wafer.dies if bad]
    count = max(len(failed), 1)
    edge = sum(math.sqrt(x * x + y * y) > 0.72 for x, y in failed) / count
    center = sum(math.sqrt(x * x + y * y) < 0.34 for x, y in failed) / count
    scratch = sum(abs(y - 0.42 * x) < 0.10 for x, y in failed) / count
    defect_rate = len(failed) / len(wafer.dies)
    return {"defect_rate": defect_rate, "edge_concentration": edge,
            "center_concentration": center, "linear_concentration": scratch}


def classify(wafer: Wafer) -> dict[str, object]:
    f = features(wafer)
    scores = {
        "normal": max(0.0, 1.0 - f["defect_rate"] * 7),
        "edge_ring": f["edge_concentration"] * 1.15 + f["defect_rate"],
        "center_cluster": f["center_concentration"] * 1.2 + f["defect_rate"],
        "scratch": f["linear_concentration"] * 1.25 + f["defect_rate"],
    }
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    total = sum(max(score, 0.01) for score in scores.values())
    predicted, top = ranked[0]
    confidence = top / total
    hypotheses = {
        "normal": "No dominant spatial signature; continue routine sampling.",
        "edge_ring": "Edge-concentrated signature; inspect edge process and handling history.",
        "center_cluster": "Center-localized signature; inspect center-zone process conditions.",
        "scratch": "Linear signature; inspect handling, transport, and contact events.",
    }
    return {
        "wafer_id": wafer.wafer_id, "predicted_pattern": predicted,
        "confidence": round(confidence, 4), "yield_pct": round((1 - f["defect_rate"]) * 100, 2),
        "features": {key: round(value, 4) for key, value in f.items()},
        "ranked_patterns": [{"pattern": name, "score": round(score, 4)} for name, score in ranked],
        "recommended_next_step": hypotheses[predicted],
        "boundary": "Spatial signature is evidence for triage, not proof of physical root cause.",
    }


def evaluate() -> dict[str, object]:
    confusion = {actual: {pred: 0 for pred in PATTERNS} for actual in PATTERNS}
    total = correct = 0
    for seed in range(100, 180):
        for pattern in PATTERNS:
            pred = classify(generate_wafer(seed, pattern))["predicted_pattern"]
            confusion[pattern][str(pred)] += 1
            total += 1
            correct += int(pred == pattern)
    return {"accuracy": round(correct / total, 4), "test_wafers": total, "confusion_matrix": confusion,
            "data_boundary": "generated wafer maps; pattern families match the generator"}


def main() -> None:
    examples = [classify(generate_wafer(901 + i, pattern)) for i, pattern in enumerate(PATTERNS)]
    artifact = {"model_name": "synthetic-wafer-spatial-triage-v1", "patterns": PATTERNS,
                "evaluation": evaluate(), "examples": examples,
                "limitations": ["Synthetic wafer maps only.", "Rule-based spatial baseline, not a vision foundation model.",
                                "Process engineers must validate any physical-cause hypothesis."]}
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "wafer_yield_intelligence.json").write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
