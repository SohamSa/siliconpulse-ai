"""Stdlib-compatible tests for the reproducible demo model."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "ml" / "train_demo_models.py"
SPEC = importlib.util.spec_from_file_location("train_demo_models", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class DemoModelTests(unittest.TestCase):
    def test_training_generalizes_to_unseen_seeds(self) -> None:
        train = [
            row
            for seed in range(10, 18)
            for scenario in ("normal", "cooling_degradation")
            for row in module.generate(seed, scenario)
        ]
        test = [
            row
            for seed in range(101, 105)
            for scenario in ("normal", "cooling_degradation")
            for row in module.generate(seed, scenario)
        ]
        module.standardize(train, test)
        bias, weights = module.train_logistic(train, epochs=500)
        result = module.metrics(test, bias, weights)
        self.assertGreaterEqual(result["f1"], 0.85)
        self.assertLessEqual(result["false_positive_rate"], 0.08)

    def test_generation_is_deterministic(self) -> None:
        first = module.generate(42, "cooling_degradation")
        second = module.generate(42, "cooling_degradation")
        self.assertEqual([row.x for row in first], [row.x for row in second])
        self.assertEqual([row.y for row in first], [row.y for row in second])


if __name__ == "__main__":
    unittest.main()
