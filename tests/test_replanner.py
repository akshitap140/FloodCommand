"""
Unit and Integration Tests for FloodCommand ReplannerAgent
Validates single and compound (multi-incident) disruption re-planning.
"""

import json
import unittest
import pandas as pd
from data.generate_data import get_data_dir, generate_all_data
from agents.orchestrator import FloodCommandOrchestrator
from agents.replanner import ReplannerAgent


class TestReplannerAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_dir = get_data_dir()
        generate_all_data(data_dir)
        cls.villages = pd.read_csv(data_dir / "villages.csv").to_dict("records")
        cls.shelters = pd.read_csv(data_dir / "shelters.csv").to_dict("records")
        cls.resources = pd.read_csv(data_dir / "resources.csv").to_dict("records")
        cls.roads = pd.read_csv(data_dir / "roads.csv").to_dict("records")
        with open(data_dir / "config.json", encoding="utf-8") as f:
            cls.config = json.load(f)

        orch = FloodCommandOrchestrator(config=cls.config)
        workflow_res = orch.run_workflow(cls.villages, cls.shelters, cls.resources, cls.roads)
        cls.base_plan = workflow_res["final_plan"]
        cls.replanner = ReplannerAgent(config=cls.config)

    def test_single_disruptions(self):
        for event in ["bridge_washout", "flood_accelerated", "vehicle_breakdown", "shelter_full"]:
            res = self.replanner.handle_disruption(
                event, self.base_plan, self.villages, self.shelters, self.resources, self.roads
            )
            self.assertEqual(res["status"], "ok")
            self.assertGreater(len(res["diff"]), 0)
            self.assertEqual(res["event_type"], event)

    def test_multi_disruptions_bridge_and_shelter(self):
        combo = ["bridge_washout", "shelter_full"]
        res = self.replanner.handle_disruption(
            combo, self.base_plan, self.villages, self.shelters, self.resources, self.roads
        )
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["critic_verdict"], "APPROVED")
        self.assertEqual(res["event_type"], "bridge_washout + shelter_full")
        self.assertIn("COMPOUND CRISIS", res["event_description"])
        self.assertIn("V02", res["affected_village_ids"])
        self.assertGreaterEqual(len(res["diff"]), 6)

    def test_multi_disruptions_bridge_breakdown_shelter(self):
        combo = ["bridge_washout", "vehicle_breakdown", "shelter_full"]
        res = self.replanner.handle_disruption(
            combo, self.base_plan, self.villages, self.shelters, self.resources, self.roads
        )
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["critic_verdict"], "APPROVED")
        self.assertEqual(res["event_type"], "bridge_washout + vehicle_breakdown + shelter_full")
        self.assertIn("V02", res["affected_village_ids"])
        self.assertIn("V04", res["affected_village_ids"])
        self.assertEqual(len(res["critic_violations"]), 0)

    def test_empty_disruptions(self):
        res = self.replanner.handle_disruption(
            [], self.base_plan, self.villages, self.shelters, self.resources, self.roads
        )
        self.assertEqual(res["status"], "ok")
        self.assertEqual(len(res["diff"]), 0)
        self.assertEqual(res["critic_verdict"], "APPROVED")


if __name__ == "__main__":
    unittest.main()
