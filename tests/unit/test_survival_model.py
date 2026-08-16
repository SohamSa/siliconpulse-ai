from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "ml" / "train_survival_model.py"
SPEC = importlib.util.spec_from_file_location("train_survival_model", PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class SurvivalModelTests(unittest.TestCase):
    def test_device_separated_survival_evaluation(self) -> None:
        train = module.generate_fleet(7, devices=90)
        test = module.generate_fleet(70, devices=60)
        module.standardize(train, test)
        bias, weights = module.train_hazard(train, epochs=350)
        result = module.evaluate(test, bias, weights)
        self.assertGreater(result["concordance_index"], 0.50)
        self.assertLess(result["interval_brier_score"], 0.20)

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(module.generate_fleet(8, 5), module.generate_fleet(8, 5))


if __name__ == "__main__":
    unittest.main()
