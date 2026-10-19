"""
Impact Analyst Agent for FloodCommand
Performs network reachability analysis using BFS over the road network
to detect cut-off villages, washed-out bridges, and isolated populations.
"""

from __future__ import annotations

from typing import Any
from utils.graph import build_road_graph, is_village_cut_off, shortest_travel_time


class ImpactAnalystAgent:
    """
    Evaluates topological connectivity of each village to designated emergency shelters and hospitals.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def analyze(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Takes: {
            "villages": list[dict],
            "roads": list[dict],
            "shelters": list[dict],
            "hospital_village_id": str (optional),
            "config": dict (optional)
        }
        Returns: {
            "cut_off_villages": list[str],
            "accessible_villages": list[str],
            "connectivity_details": dict[str, dict],
            "status": "ok"
        }
        """
        villages = input_data.get("villages", [])
        roads = input_data.get("roads", [])
        shelters = input_data.get("shelters", [])
        hospital_id = input_data.get("hospital_village_id", "V09")

        # Destination hubs are all shelters plus the hospital town
        destination_hubs = [str(s["shelter_id"]) for s in shelters]
        if hospital_id and hospital_id not in destination_hubs:
            destination_hubs.append(hospital_id)

        # Build road graph considering only open roads
        road_graph = build_road_graph(roads, only_open=True)

        cut_off_villages: list[str] = []
        accessible_villages: list[str] = []
        connectivity_details: dict[str, dict[str, Any]] = {}

        for v in villages:
            vid = str(v["village_id"])
            vname = v.get("name", vid)

            is_isolated = is_village_cut_off(road_graph, vid, destination_hubs)

            if is_isolated:
                cut_off_villages.append(vid)
                connectivity_details[vid] = {
                    "village_id": vid,
                    "village_name": vname,
                    "status": "CUT_OFF",
                    "accessible_by_road": False,
                    "required_transport": "boat_or_rescue_team",
                    "nearest_shelter_id": None,
                    "shortest_road_time": None,
                    "reason": "All connecting arterial roads and bridges are submerged or blocked.",
                }
            else:
                accessible_villages.append(vid)
                # Find nearest shelter by road
                best_shelter = None
                min_time = float("inf")
                for s in shelters:
                    sid = str(s["shelter_id"])
                    time_cost = shortest_travel_time(road_graph, vid, sid)
                    if time_cost is not None and time_cost < min_time:
                        min_time = time_cost
                        best_shelter = sid

                connectivity_details[vid] = {
                    "village_id": vid,
                    "village_name": vname,
                    "status": "ACCESSIBLE",
                    "accessible_by_road": True,
                    "required_transport": "bus_or_any",
                    "nearest_shelter_id": best_shelter,
                    "shortest_road_time": min_time if min_time != float("inf") else 30.0,
                    "reason": f"Open road corridor available to {best_shelter} ({min_time:.1f} mins).",
                }

        return {
            "cut_off_villages": cut_off_villages,
            "accessible_villages": accessible_villages,
            "connectivity_details": connectivity_details,
            "status": "ok",
        }
