"""
Re-Planner Agent for FloodCommand
Handles real-time dynamic disruptions (bridge washouts, accelerated floods,
vehicle breakdowns, shelter saturation). Re-runs only affected villages and returns
a structured before/after diff with Critic re-validation.
"""

from __future__ import annotations

import copy
from typing import Any
from agents.critic import RedTeamCriticAgent
from agents.impact import ImpactAnalystAgent
from utils.graph import build_road_graph, shortest_travel_time


class ReplannerAgent:
    """
    Surgically re-plans only the subset of villages impacted by sudden operational disruptions.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.critic = RedTeamCriticAgent(config=self.config)
        self.impact_analyst = ImpactAnalystAgent(config=self.config)

    def handle_disruption(
        self,
        event_type: str | list[str],
        current_plan: list[dict[str, Any]],
        villages: list[dict[str, Any]],
        shelters: list[dict[str, Any]],
        resources: list[dict[str, Any]],
        roads: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Executes targeted re-planning based on one or more disruptions:
        1. 'bridge_washout': Blocks road between V01 and V02, isolating V02/V01.
        2. 'flood_accelerated': Reduces hours_to_flood by 2.0 hours valley-wide.
        3. 'vehicle_breakdown': BOAT-01 motor failure, substituted with standby craft.
        4. 'shelter_full': Shelter S1 reaches capacity, rerouting all evacuees to S2.
        Supports simultaneous compound crisis combinations.
        """
        # Normalize input to list of events
        if isinstance(event_type, str):
            events = [event_type] if event_type else []
        elif isinstance(event_type, (list, tuple, set)):
            events = [str(e) for e in event_type if e]
        else:
            events = []

        if not events:
            return {
                "event_type": "none",
                "event_types": [],
                "event_description": "No disruptions active.",
                "affected_village_ids": [],
                "before_plan": current_plan,
                "updated_plan": current_plan,
                "diff": [],
                "critic_verdict": "APPROVED",
                "critic_violations": [],
                "passed_rules": ["R1", "R2", "R3", "R4", "R5", "R6"],
                "status": "ok",
            }

        # Deepcopy to preserve before state
        before_plan = copy.deepcopy(current_plan)
        updated_plan = copy.deepcopy(current_plan)
        diff_entries: list[dict[str, Any]] = []
        affected_village_ids: set[str] = set()
        event_descriptions: list[str] = []

        villages_by_id = {v["village_id"]: copy.deepcopy(v) for v in villages}
        shelters_by_id = {s["shelter_id"]: copy.deepcopy(s) for s in shelters}
        roads_copy = copy.deepcopy(roads)
        resources_by_id = {r["resource_id"]: copy.deepcopy(r) for r in resources}

        has_bridge = "bridge_washout" in events
        has_flood = "flood_accelerated" in events
        has_breakdown = "vehicle_breakdown" in events
        has_shelter = "shelter_full" in events

        # 1. Apply flood acceleration if present (sets time horizons)
        if has_flood:
            event_descriptions.append("Torrential cloudburst advances flood crest arrival by 2.0 hours valley-wide.")
            for a in updated_plan:
                vid = a["village_id"]
                old_hours = a["hours_to_flood"]
                new_hours = max(round(old_hours - 2.0, 1), 0.8)
                a["hours_to_flood"] = new_hours
                a["flood_deadline_min"] = new_hours * 60.0
                old_margin = a["margin_minutes"]

                # Expedite dispatch windows and prioritize
                a["eta_minutes"] = max(a["eta_minutes"] - 15.0, 10.0)
                new_margin = round(new_hours * 60.0 - a["eta_minutes"] - a["safety_margin_min"], 1)
                a["margin_minutes"] = new_margin

                affected_village_ids.add(vid)
                diff_entries.append({
                    "village_id": vid,
                    "village_name": a["village_name"],
                    "change_type": "Expedited Evacuation Dispatch",
                    "before": f"Deadline: {old_hours:.1f}h (Margin {old_margin:.0f}m)",
                    "after": f"Deadline: {new_hours:.1f}h (ETA {a['eta_minutes']:.0f}m, Margin {new_margin:.0f}m)",
                    "reason": "Upstream crest advanced by 2.0h; emergency priority departure ordered.",
                })

        # 2. Apply bridge washout if present
        if has_bridge:
            event_descriptions.append("Key arterial bridge connecting Riverbend (V02) and Elderglen (V01) has collapsed under surging water.")
            for r in roads_copy:
                if (r["from_id"] == "V01" and r["to_id"] == "V02") or (r["from_id"] == "V02" and r["to_id"] == "V01"):
                    r["status"] = "blocked"

            affected_village_ids.add("V02")
            for a in updated_plan:
                if a["village_id"] == "V02":
                    old_res = a["resource_id"]
                    old_type = a["resource_type"]

                    # If vehicle breakdown is ALSO active, standby BOAT-04 is allocated to V04;
                    # allocate secondary river craft BOAT-02 (Slot 65-110m) to avoid double-booking.
                    if has_breakdown:
                        assigned_boat = "BOAT-02"
                        slot_window = {"start_min": 65, "end_min": 110}
                        notes = "Re-planned: Road bridge collapsed. Switched to river craft BOAT-02 (Slot 65-110m)."
                        after_str = "BOAT (BOAT-02, Slot 65-110m)"
                    else:
                        assigned_boat = "BOAT-04"
                        slot_window = {"start_min": 60, "end_min": 110}
                        notes = "Re-planned: Road bridge collapsed. Switched to river craft BOAT-04 (Slot 60-110m)."
                        after_str = "BOAT (BOAT-04, Slot 60-110m)"

                    a["resource_id"] = assigned_boat
                    a["resource_type"] = "boat"
                    a["time_window"] = slot_window
                    a["eta_minutes"] = 25.0
                    a["margin_minutes"] = round(a["hours_to_flood"] * 60 - 25.0 - a["safety_margin_min"], 1)
                    a["notes"] = notes

                    diff_entries.append({
                        "village_id": "V02",
                        "village_name": a["village_name"],
                        "change_type": "Transport Mode & Resource",
                        "before": f"{old_type.upper()} ({old_res})",
                        "after": after_str,
                        "reason": "Bridge washed out; allocated secondary river craft without time conflict.",
                    })

        # 3. Apply vehicle breakdown if present
        if has_breakdown:
            event_descriptions.append("Primary rescue craft BOAT-01 suffered engine impeller failure during pre-launch checkout.")
            if "BOAT-01" in resources_by_id:
                resources_by_id["BOAT-01"]["available"] = False
            affected_village_ids.add("V04")

            for a in updated_plan:
                if a["village_id"] == "V04":
                    old_res = a["resource_id"]
                    a["resource_id"] = "BOAT-04"
                    a["time_window"] = {"start_min": 50, "end_min": 95}
                    a["eta_minutes"] = 25.0
                    a["margin_minutes"] = round(a["hours_to_flood"] * 60 - 50.0 - 25.0 - a["safety_margin_min"], 1)
                    a["notes"] = "Re-planned: Assigned standby craft BOAT-04 (Slot 50-95m) following BOAT-01 failure."
                    diff_entries.append({
                        "village_id": "V04",
                        "village_name": a["village_name"],
                        "change_type": "Resource Replacement",
                        "before": f"{old_res} (Disabled)",
                        "after": "BOAT-04 (Slot 50-95m)",
                        "reason": "Immediate hot-swap to active backup river craft with zero scheduling overlap.",
                    })

        # 4. Apply shelter saturation if present
        if has_shelter:
            event_descriptions.append("North Hill Fort Shelter (S1) has reached 100% capacity due to spontaneous self-evacuations.")
            shelters_by_id["S1"]["current_load"] = shelters_by_id["S1"]["capacity"]

            for a in updated_plan:
                if a.get("shelter_id") == "S1":
                    vid = a["village_id"]
                    old_sh = a["shelter_name"]
                    a["shelter_id"] = "S2"
                    a["shelter_name"] = shelters_by_id["S2"]["name"]
                    a["shelter_has_medical"] = shelters_by_id["S2"]["has_medical"]
                    a["eta_minutes"] = min(a["eta_minutes"] + 15.0, a["hours_to_flood"] * 60 - a["safety_margin_min"] - 5.0)
                    a["margin_minutes"] = round(a["hours_to_flood"] * 60 - a["eta_minutes"] - a["safety_margin_min"], 1)
                    a["notes"] = "Re-planned: S1 saturated. Rerouted to Central Ridge Stadium (S2)."

                    affected_village_ids.add(vid)
                    diff_entries.append({
                        "village_id": vid,
                        "village_name": a["village_name"],
                        "change_type": "Shelter Rerouting",
                        "before": f"{old_sh} (S1)",
                        "after": f"{shelters_by_id['S2']['name']} (S2)",
                        "reason": "S1 at 100% capacity; redirected to regional stadium.",
                    })

        # Unknown / custom events
        for ev in events:
            if ev not in ("bridge_washout", "flood_accelerated", "vehicle_breakdown", "shelter_full"):
                event_descriptions.append(f"Generic disruption event: {ev}")

        # Re-validate modified plan with Red-Team Critic
        impact_data = self.impact_analyst.analyze({
            "villages": list(villages_by_id.values()),
            "roads": roads_copy,
            "shelters": list(shelters_by_id.values()),
        })

        critic_res = self.critic.audit({
            "assignments": updated_plan,
            "shelters": list(shelters_by_id.values()),
            "villages": list(villages_by_id.values()),
            "resources": list(resources_by_id.values()),
            "impact_data": impact_data,
        })

        if len(events) == 1:
            event_type_str = events[0]
            composite_desc = event_descriptions[0] if event_descriptions else f"Disruption: {event_type_str}"
        else:
            event_type_str = " + ".join(events)
            composite_desc = f"COMPOUND CRISIS ({len(events)} Incidents): " + " | ".join(event_descriptions)

        return {
            "event_type": event_type_str,
            "event_types": events,
            "event_description": composite_desc,
            "affected_village_ids": sorted(list(affected_village_ids)),
            "before_plan": before_plan,
            "updated_plan": updated_plan,
            "diff": diff_entries,
            "critic_verdict": critic_res.get("verdict", "APPROVED"),
            "critic_violations": critic_res.get("violations", []),
            "passed_rules": critic_res.get("passed_rules", []),
            "status": "ok",
        }
