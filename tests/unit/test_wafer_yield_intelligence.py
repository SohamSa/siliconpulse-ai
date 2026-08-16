from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "ml" / "wafer_yield_intelligence.py"
SPEC = importlib.util.spec_from_file_location("wafer_yield_intelligence", PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class WaferYieldTests(unittest.TestCase):
    def test_pattern_baseline_is_reproducible_and_accurate(self) -> None:
        result = module.evaluate()
        self.assertGreaterEqual(result["accuracy"], 0.85)
        wafer = module.generate_wafer(404, "edge_ring")
        self.assertEqual(wafer, module.generate_wafer(404, "edge_ring"))
        self.assertEqual(module.classify(wafer)["predicted_pattern"], "edge_ring")


if __name__ == "__main__":
    unittest.main()
