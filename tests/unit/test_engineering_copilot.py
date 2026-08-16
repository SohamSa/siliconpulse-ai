from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "local_platform"))
from engineering_copilot import EngineeringCopilot, Evidence


class EngineeringCopilotTests(unittest.TestCase):
    def test_evidence_ids_and_human_gate_are_preserved(self) -> None:
        copilot = EngineeringCopilot()
        facts = [
            Evidence("E-1", "twin", "GPU-042/twin", "Thermal deviation increased", ("thermal", "peer_delta"), 0.95),
            Evidence("E-2", "peer_group", "RACK-02/peers", "Rack peers remain healthy", ("healthy_peers",), 0.92),
        ]
        case = copilot.investigate("Why is GPU-042 heating?", facts)
        view = copilot.case_view(case)
        self.assertIn("E-1", view["hypotheses"][0]["supporting_evidence_ids"])
        approval = copilot.request_action(case.case_id, "schedule_maintenance")
        self.assertEqual(approval["status"], "pending")
        self.assertEqual(copilot.decide(approval["approval_id"], True, "operator")["status"], "approved")

    def test_unapproved_sources_are_rejected(self) -> None:
        copilot = EngineeringCopilot()
        with self.assertRaises(ValueError):
            copilot.investigate("question", [Evidence("X", "free_text_llm", "none", "guess", (), 0.1)])


if __name__ == "__main__":
    unittest.main()
