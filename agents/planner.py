"""
Planner Agent for FloodCommand
Calculates urgency scores per village based on time to flood, vulnerable population,
and total population. Determines execution workflow and task sequencing.
"""

from __future__ import annotations

from typing import Any


class PlannerAgent:
    """
    Computes village urgency indices and generates execution sequence for downstream agents.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def plan(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Takes: {"villages": list[dict], "config": dict}
        Returns: {
            "village_priority_order": list[str],
            "urgency_scores": dict[str, float],
            "tasks": list[str],
            "rationale": str,
            "status": "ok"
        }
        """
        villages = input_data.get("villages", [])
        urgency_scores: dict[str, float] = {}

        for v in villages:
            vid = str(v["village_id"])
            pop = float(v.get("population", 0))
            vuln = float(v.get("vulnerable_count", 0))
            hours = max(float(v.get("hours_to_flood", 1.0)), 0.5)

            # Hospital village priority weight
            hospital_boost = 1.3 if bool(v.get("has_hospital", False)) else 1.0

            # Urgency formula: (vulnerable * 2.5 + population * 0.75) / hours_to_flood
            score = round(((vuln * 2.5 + pop * 0.75) / hours) * hospital_boost, 2)
            urgency_scores[vid] = score

        # Sort villages by descending urgency score
        sorted_villages = sorted(
            villages,
            key=lambda item: urgency_scores.get(str(item["village_id"]), 0.0),
            reverse=True,
        )
        priority_order = [str(v["village_id"]) for v in sorted_villages]

        top_village = sorted_villages[0] if sorted_villages else None
        rationale = (
            f"Prioritized {top_village['name']} ({top_village['village_id']}) with urgency index "
            f"{urgency_scores.get(str(top_village['village_id']), 0):.1f} due to {top_village.get('vulnerable_count', 0)} "
            f"vulnerable residents and flood arrival in {top_village.get('hours_to_flood', 0)} hours."
            if top_village
            else "No villages provided."
        )

        tasks = [
            "calculate_village_urgency_matrix",
            "audit_road_network_and_cut_off_risks",
            "allocate_transport_fleet_and_shelters",
            "execute_red_team_adversarial_validation",
            "trigger_rework_loop_if_violations_detected",
            "generate_ground_truth_sms_alerts",
        ]

        return {
            "village_priority_order": priority_order,
            "urgency_scores": urgency_scores,
            "tasks": tasks,
            "rationale": rationale,
            "status": "ok",
        }
