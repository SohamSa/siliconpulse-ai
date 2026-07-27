"""Fast end-to-end test for the dependency-free local decision path."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


LOCAL = Path(__file__).resolve().parents[2] / "apps" / "local_platform"
sys.path.insert(0, str(LOCAL))

from agents import AgentOrchestrator  # noqa: E402
from intelligence import IntelligenceEngine  # noqa: E402
from simulator import Simulator  # noqa: E402


class LocalDecisionPathTests(unittest.TestCase):
    def test_gpu_042_device_cooling_story(self) -> None:
        simulator = Simulator(device_count=50, rack_count=5, seed=42)
        intelligence = IntelligenceEngine(simulator)
        simulator.on_telemetry = intelligence.on_telemetry
        agents = AgentOrchestrator(simulator, intelligence)

        for _ in range(35):
            simulator.tick()
        self.assertEqual(intelligence.incidents, {})

        simulator.inject("cooling_degradation", device_id="GPU-042", severity=0.9)
        incident = None
        detection_temperature = None
        for _ in range(80):
            simulator.tick()
            hits = [
                item
                for item in intelligence.incidents.values()
                if "GPU-042" in item.affected_devices
            ]
            if hits:
                incident = hits[0]
                detection_temperature = simulator.devices["GPU-042"].temp_c
                break

        self.assertIsNotNone(incident)
        self.assertLess(detection_temperature, 85.0)
        assert incident is not None
        rca = agents.run_root_cause(incident.incident_id)
        self.assertEqual(rca["result"]["most_likely_cause"], "device_cooling_degradation")

        maintenance = agents.run_predictive_maintenance(incident.incident_id)
        approval_id = maintenance["approval"]["approval_id"]
        agents.decide_approval(approval_id, True, "test")
        for _ in range(25):
            simulator.tick()
        report = agents.generate_report(incident.incident_id)
        self.assertEqual(
            report["technical_summary"]["likely_root_cause"],
            "device_cooling_degradation",
        )
        self.assertTrue(report["approvals"])


if __name__ == "__main__":
    unittest.main()
