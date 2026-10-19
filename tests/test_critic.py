"""
Unit and Integration Tests for FloodCommand Red-Team Critic
Validates individual enforcement of safety rules R1 through R6 and overall plan certification.
Compatible with both pytest and unittest.
"""

import unittest
from agents.critic import RedTeamCriticAgent


class TestRedTeamCriticRules(unittest.TestCase):
    def setUp(self):
        self.config = {
            "safety_margin_minutes": 30,
            "hospital_village_id": "V09",
        }
        self.critic = RedTeamCriticAgent(config=self.config)

        # Standard baseline mock entities
        self.mock_villages = [
            {"village_id": "V01", "name": "Elderglen", "population": 120, "vulnerable_count": 35, "hours_to_flood": 3.0, "has_hospital": False},
            {"village_id": "V09", "name": "Solis Haven Town", "population": 380, "vulnerable_count": 110, "hours_to_flood": 4.0, "has_hospital": True},
        ]
        self.mock_shelters = [
            {"shelter_id": "S1", "name": "North Hill Fort", "capacity": 500, "current_load": 100, "has_medical": True},
            {"shelter_id": "S3", "name": "East Plateau Academy", "capacity": 200, "current_load": 150, "has_medical": False},
        ]
        self.mock_resources = [
            {"resource_id": "BUS-01", "type": "bus", "capacity": 50, "available": True},
            {"resource_id": "BOAT-01", "type": "boat", "capacity": 40, "available": True},
            {"resource_id": "TEAM-01", "type": "rescue_team", "capacity": 30, "available": True},
        ]
        self.mock_impact = {
            "cut_off_villages": ["V10"],
            "accessible_villages": ["V01", "V09"],
        }

    def test_r1_shelter_capacity_exceeded(self):
        """R1: Test that overflowing a shelter's capacity is caught."""
        # S3 has capacity 200 and current_load 150 (only 50 seats left).
        # We assign V01 (population 120) to S3 -> 150 + 120 = 270 > 200.
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 0,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "shelter_id": "S3",
                "shelter_has_medical": False,
                "eta_minutes": 20.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 380,
                "vulnerable_count": 0,
                "resource_id": "BOAT-01",
                "resource_type": "boat",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R1", rule_ids)
        self.assertEqual(result["verdict"], "NEEDS_REWORK")

    def test_r2_travel_time_exceeds_flood_deadline(self):
        """R2: Test that a vehicle arriving too close to or after flood crest is rejected."""
        # V01 floods in 1.0 hour (60 minutes).
        # ETA is 40 mins + safety margin 30 mins = 70 mins > 60 mins -> R2 violation!
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 35,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 40.0,
                "hours_to_flood": 1.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 380,
                "vulnerable_count": 110,
                "resource_id": "BOAT-01",
                "resource_type": "boat",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R2", rule_ids)

    def test_r3_resource_double_booked_overlapping_time(self):
        """R3: Test that scheduling the same resource concurrently across two villages is caught."""
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 0,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "time_window": {"start_min": 10, "end_min": 60},
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 380,
                "vulnerable_count": 0,
                "resource_id": "BUS-01",  # Same resource!
                "resource_type": "bus",
                "time_window": {"start_min": 30, "end_min": 90},  # Overlaps 30-60!
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R3", rule_ids)

    def test_r4_cut_off_village_given_bus(self):
        """R4: Test that assigning a road bus to an isolated cut-off village is rejected."""
        mock_villages = self.mock_villages + [
            {"village_id": "V10", "name": "Fernbank", "population": 160, "vulnerable_count": 35, "hours_to_flood": 3.0, "has_hospital": False}
        ]
        assignments = [
            {
                "village_id": "V10",  # In cut_off_villages!
                "village_name": "Fernbank",
                "population": 160,
                "vulnerable_count": 35,
                "resource_id": "BUS-01",
                "resource_type": "bus",  # Invalid transport for cut off!
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 25.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 380,
                "vulnerable_count": 0,
                "resource_id": "BOAT-01",
                "resource_type": "boat",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R4", rule_ids)

    def test_r5_vulnerable_population_to_non_medical_shelter(self):
        """R5: Test that sending vulnerable populations to shelters without medical teams is flagged."""
        # V01 has vulnerable_count 35. Destination is S3 which has has_medical=False.
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 35,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "shelter_id": "S3",
                "shelter_has_medical": False,  # Missing medical support!
                "eta_minutes": 20.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 380,
                "vulnerable_count": 0,
                "resource_id": "BOAT-01",
                "resource_type": "boat",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R5", rule_ids)

    def test_r6_hospital_village_left_uncovered(self):
        """R6: Test that omitting the designated hospital village triggers an R6 critical violation."""
        # Plan only assigns V01; V09 (hospital) is completely omitted!
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 35,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            }
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        rule_ids = [v["rule_id"] for v in result["violations"]]
        self.assertIn("R6", rule_ids)

    def test_fully_compliant_plan_approved(self):
        """Test that a plan respecting all R1-R6 rules passes with APPROVED verdict."""
        assignments = [
            {
                "village_id": "V01",
                "village_name": "Elderglen",
                "population": 120,
                "vulnerable_count": 35,
                "resource_id": "BUS-01",
                "resource_type": "bus",
                "time_window": {"start_min": 0, "end_min": 45},
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 3.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
            {
                "village_id": "V09",
                "village_name": "Solis Haven Town",
                "population": 250,
                "vulnerable_count": 50,
                "resource_id": "BOAT-01",
                "resource_type": "boat",
                "time_window": {"start_min": 0, "end_min": 50},
                "shelter_id": "S1",
                "shelter_has_medical": True,
                "eta_minutes": 20.0,
                "hours_to_flood": 4.0,
                "safety_margin_min": 30,
                "status": "ASSIGNED",
            },
        ]

        result = self.critic.audit({
            "assignments": assignments,
            "shelters": self.mock_shelters,
            "villages": self.mock_villages,
            "resources": self.mock_resources,
            "impact_data": self.mock_impact,
        })

        self.assertEqual(result["verdict"], "APPROVED")
        self.assertEqual(len(result["violations"]), 0)


if __name__ == "__main__":
    unittest.main()
