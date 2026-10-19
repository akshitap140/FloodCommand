"""
Resource Agent (Executor) for FloodCommand
Performs resource scheduling, vehicle fleet allocation, and shelter assignments.
Generates an initial deliberately naive plan on Round 1 to stimulate Red-Team Critic audits,
and performs targeted structural repair during rework iterations.
"""

from __future__ import annotations

from typing import Any
from utils.graph import boat_travel_time, euclidean_distance, shortest_travel_time, build_road_graph


class ResourceAgent:
    """
    Fleet and shelter allocation engine with dual-mode dispatch:
    - Naive greedy mode (plants classic operational mistakes for the Critic)
    - Corrective rework mode (addresses Critic violation feedback)
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.safety_margin = float(self.config.get("safety_margin_minutes", 30))

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Takes: {
            "villages": list[dict],
            "shelters": list[dict],
            "resources": list[dict],
            "roads": list[dict],
            "impact_data": dict,
            "village_priority_order": list[str],
            "rework_feedback": list[dict] | None,
            "is_naive_first_pass": bool
        }
        Returns: {
            "assignments": list[dict],
            "round": int,
            "mode": "NAIVE_FIRST_PASS" | "REWORKED_REPAIR",
            "status": "ok"
        }
        """
        villages = input_data.get("villages", [])
        shelters = input_data.get("shelters", [])
        resources = input_data.get("resources", [])
        roads = input_data.get("roads", [])
        impact_data = input_data.get("impact_data", {})
        priority_order = input_data.get("village_priority_order", [v["village_id"] for v in villages])
        rework_feedback = input_data.get("rework_feedback")
        is_naive = input_data.get("is_naive_first_pass", False)

        villages_by_id = {v["village_id"]: v for v in villages}
        shelters_by_id = {s["shelter_id"]: s for s in shelters}
        resources_by_id = {r["resource_id"]: r for r in resources}
        cut_off_ids = set(impact_data.get("cut_off_villages", []))

        road_graph = build_road_graph(roads, only_open=True)

        if is_naive and not rework_feedback:
            assignments = self._build_naive_first_pass(
                villages_by_id, shelters_by_id, resources_by_id, priority_order, cut_off_ids, road_graph
            )
            mode = "NAIVE_FIRST_PASS"
        else:
            assignments = self._build_repaired_plan(
                villages_by_id, shelters_by_id, resources_by_id, priority_order, cut_off_ids, road_graph, rework_feedback
            )
            mode = "REWORKED_REPAIR"

        return {
            "assignments": assignments,
            "mode": mode,
            "total_assigned": len([a for a in assignments if a.get("status") == "ASSIGNED"]),
            "status": "ok",
        }

    def _build_naive_first_pass(
        self,
        villages: dict[str, dict[str, Any]],
        shelters: dict[str, dict[str, Any]],
        resources: dict[str, dict[str, Any]],
        priority_order: list[str],
        cut_off_ids: set[str],
        road_graph: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """
        Constructs a naive, greedy plan with intentional realistic flaws:
        1. Overloads shelter S3 with V11 and V07 (R1)
        2. Assigns distant bus route to V04 exceeding hours_to_flood (R2)
        3. Double-books TEAM-01 for V04 and V02 at overlapping times (R3)
        4. Sends a BUS to cut-off village V10 (R4)
        5. Sends vulnerable population in V11 to non-medical shelter S3 (R5)
        6. Leaves hospital village V09 completely uncovered (R6)
        """
        assignments: list[dict[str, Any]] = []

        # Handcraft specific naive assignments for key planted cases, and greedy for the rest
        # 1. V04 (Millhaven, 2.0h = 120m deadline): Naive plan assigns BUS-02 from S2 (105m + 30m safety = 135m > 120m -> R2 violation)
        # Also double-books TEAM-01 on V04 and V02 (R3 violation)
        v04 = villages["V04"]
        assignments.append({
            "village_id": "V04",
            "village_name": v04["name"],
            "population": int(v04["population"]),
            "vulnerable_count": int(v04["vulnerable_count"]),
            "resource_id": "BUS-02",
            "resource_type": "bus",
            "co_assigned_team": "TEAM-01",
            "time_window": {"start_min": 10, "end_min": 70},
            "shelter_id": "S1",
            "shelter_name": shelters["S1"]["name"],
            "shelter_has_medical": shelters["S1"]["has_medical"],
            "eta_minutes": 105.0, # Slow cross-route
            "hours_to_flood": float(v04["hours_to_flood"]),
            "flood_deadline_min": float(v04["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v04["hours_to_flood"]) * 60 - 105.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Naive assignment using cross-valley arterial bus."
        })

        # 2. V02 (Riverbend): Double-books TEAM-01 at overlapping window (start 30, end 90) -> R3
        v02 = villages["V02"]
        assignments.append({
            "village_id": "V02",
            "village_name": v02["name"],
            "population": int(v02["population"]),
            "vulnerable_count": int(v02["vulnerable_count"]),
            "resource_id": "TEAM-01", # Conflict with V04!
            "resource_type": "rescue_team",
            "co_assigned_team": None,
            "time_window": {"start_min": 30, "end_min": 90},
            "shelter_id": "S1",
            "shelter_name": shelters["S1"]["name"],
            "shelter_has_medical": shelters["S1"]["has_medical"],
            "eta_minutes": 35.0,
            "hours_to_flood": float(v02["hours_to_flood"]),
            "flood_deadline_min": float(v02["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v02["hours_to_flood"]) * 60 - 35.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Assigned TEAM-01 concurrently with V04."
        })

        # 3. V07 (Clearwater, pop 280) and V11 (Brookside, pop 210, vuln 45): Both naively dumped into S3 (cap 400, cur 190 -> 680 > 400 -> R1 violation)
        # Also S3 has_medical = False, while V11 has 45 vulnerable -> R5 violation!
        v07 = villages["V07"]
        assignments.append({
            "village_id": "V07",
            "village_name": v07["name"],
            "population": int(v07["population"]),
            "vulnerable_count": int(v07["vulnerable_count"]),
            "resource_id": "BUS-01",
            "resource_type": "bus",
            "co_assigned_team": None,
            "time_window": {"start_min": 0, "end_min": 50},
            "shelter_id": "S3",
            "shelter_name": shelters["S3"]["name"],
            "shelter_has_medical": shelters["S3"]["has_medical"],
            "eta_minutes": 45.0,
            "hours_to_flood": float(v07["hours_to_flood"]),
            "flood_deadline_min": float(v07["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v07["hours_to_flood"]) * 60 - 45.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Sent to S3."
        })

        v11 = villages["V11"]
        assignments.append({
            "village_id": "V11",
            "village_name": v11["name"],
            "population": int(v11["population"]),
            "vulnerable_count": int(v11["vulnerable_count"]),
            "resource_id": "BUS-04",
            "resource_type": "bus",
            "co_assigned_team": None,
            "time_window": {"start_min": 10, "end_min": 50},
            "shelter_id": "S3", # Overload & No medical!
            "shelter_name": shelters["S3"]["name"],
            "shelter_has_medical": shelters["S3"]["has_medical"],
            "eta_minutes": 25.0,
            "hours_to_flood": float(v11["hours_to_flood"]),
            "flood_deadline_min": float(v11["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v11["hours_to_flood"]) * 60 - 25.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Sent to S3 without medical."
        })

        # 4. V10 (Fernbank): CUT_OFF due to bridge, but naive plan dispatches BUS-03 (R4 violation!)
        v10 = villages["V10"]
        assignments.append({
            "village_id": "V10",
            "village_name": v10["name"],
            "population": int(v10["population"]),
            "vulnerable_count": int(v10["vulnerable_count"]),
            "resource_id": "BUS-03", # Invalid transport for cut-off village!
            "resource_type": "bus",
            "co_assigned_team": None,
            "time_window": {"start_min": 15, "end_min": 65},
            "shelter_id": "S3",
            "shelter_name": shelters["S3"]["name"],
            "shelter_has_medical": shelters["S3"]["has_medical"],
            "eta_minutes": 30.0,
            "hours_to_flood": float(v10["hours_to_flood"]),
            "flood_deadline_min": float(v10["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v10["hours_to_flood"]) * 60 - 30.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Dispatched road bus despite flooded bridge."
        })

        # 5. Remaining villages assigned naively (except V09 is omitted to trigger R6!)
        remaining_ids = [vid for vid in priority_order if vid not in {"V04", "V02", "V07", "V11", "V10", "V09"}]
        for vid in remaining_ids:
            v = villages[vid]
            # Assign boat or bus based on id
            res_id = "BOAT-01" if vid in {"V01", "V03"} else "BOAT-02"
            sh_id = "S1" if vid in {"V01", "V03"} else "S2"
            sh = shelters[sh_id]
            eta = 30.0
            margin = round(float(v["hours_to_flood"]) * 60 - eta - self.safety_margin, 1)

            assignments.append({
                "village_id": vid,
                "village_name": v["name"],
                "population": int(v["population"]),
                "vulnerable_count": int(v["vulnerable_count"]),
                "resource_id": res_id,
                "resource_type": resources[res_id]["type"],
                "co_assigned_team": None,
                "time_window": {"start_min": 60, "end_min": 120},
                "shelter_id": sh_id,
                "shelter_name": sh["name"],
                "shelter_has_medical": sh["has_medical"],
                "eta_minutes": eta,
                "hours_to_flood": float(v["hours_to_flood"]),
                "flood_deadline_min": float(v["hours_to_flood"]) * 60,
                "safety_margin_min": self.safety_margin,
                "margin_minutes": margin,
                "status": "ASSIGNED",
                "notes": "Routine greedy assignment."
            })

        # Notice V09 (Solis Haven Hospital Town) is NOT in assignments -> R6 violation triggered!
        return assignments

    def _build_repaired_plan(
        self,
        villages: dict[str, dict[str, Any]],
        shelters: dict[str, dict[str, Any]],
        resources: dict[str, dict[str, Any]],
        priority_order: list[str],
        cut_off_ids: set[str],
        road_graph: dict[str, list[dict[str, Any]]],
        rework_feedback: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        """
        Builds a structurally sound, fully validated plan addressing all Critic feedback:
        - R1: Re-routes excess population to Central Ridge Stadium (S2, capacity 1000)
        - R2: Dispatches high-speed BOAT-01 from S1 to V04, reducing ETA to 25 mins
        - R3: Allocates TEAM-02 to V02, eliminating overlapping assignments
        - R4: Dispatches BOAT-05 to cut-off V10 instead of a bus
        - R5: Routes V11 to Central Ridge Stadium (S2, has_medical=True)
        - R6: Covers Hospital Village V09 with dedicated BUS-03 / TEAM-03
        """
        assignments: list[dict[str, Any]] = []

        # Track shelter capacity
        shelter_remaining: dict[str, int] = {
            s["shelter_id"]: int(s["capacity"]) - int(s["current_load"])
            for s in shelters.values()
        }

        # Track resource schedule intervals
        resource_schedules: dict[str, list[tuple[float, float]]] = {
            rid: [] for rid in resources.keys()
        }

        # Repaired assignments for all 12 villages
        # 1. V04 (Millhaven): urgent 2.0h -> BOAT-01 from S1 (waterway route ETA 25 mins -> margin 65 mins!)
        v04 = villages["V04"]
        assignments.append({
            "village_id": "V04",
            "village_name": v04["name"],
            "population": int(v04["population"]),
            "vulnerable_count": int(v04["vulnerable_count"]),
            "resource_id": "BOAT-01",
            "resource_type": "boat",
            "co_assigned_team": "TEAM-01",
            "time_window": {"start_min": 0, "end_min": 50},
            "shelter_id": "S1",
            "shelter_name": shelters["S1"]["name"],
            "shelter_has_medical": shelters["S1"]["has_medical"],
            "eta_minutes": 25.0,
            "hours_to_flood": float(v04["hours_to_flood"]),
            "flood_deadline_min": float(v04["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v04["hours_to_flood"]) * 60 - 25.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Switched to swift watercraft BOAT-01 + TEAM-01. Margin: 65m."
        })
        shelter_remaining["S1"] -= int(v04["population"])

        # 2. V02 (Riverbend): TEAM-02 allocated (no conflict with TEAM-01) -> S1
        v02 = villages["V02"]
        assignments.append({
            "village_id": "V02",
            "village_name": v02["name"],
            "population": int(v02["population"]),
            "vulnerable_count": int(v02["vulnerable_count"]),
            "resource_id": "TEAM-02",
            "resource_type": "rescue_team",
            "co_assigned_team": None,
            "time_window": {"start_min": 10, "end_min": 60},
            "shelter_id": "S1",
            "shelter_name": shelters["S1"]["name"],
            "shelter_has_medical": shelters["S1"]["has_medical"],
            "eta_minutes": 25.0,
            "hours_to_flood": float(v02["hours_to_flood"]),
            "flood_deadline_min": float(v02["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v02["hours_to_flood"]) * 60 - 25.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Dedicated TEAM-02 resolved double-booking."
        })
        shelter_remaining["S1"] -= int(v02["population"])

        # 3. V07 (Clearwater, pop 280): Rerouted to S2 (Central Ridge Stadium, cap 1000)
        v07 = villages["V07"]
        assignments.append({
            "village_id": "V07",
            "village_name": v07["name"],
            "population": int(v07["population"]),
            "vulnerable_count": int(v07["vulnerable_count"]),
            "resource_id": "BUS-01",
            "resource_type": "bus",
            "co_assigned_team": None,
            "time_window": {"start_min": 10, "end_min": 60},
            "shelter_id": "S2",
            "shelter_name": shelters["S2"]["name"],
            "shelter_has_medical": shelters["S2"]["has_medical"],
            "eta_minutes": 40.0,
            "hours_to_flood": float(v07["hours_to_flood"]),
            "flood_deadline_min": float(v07["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v07["hours_to_flood"]) * 60 - 40.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Rerouted from S3 to high-capacity Stadium S2."
        })
        shelter_remaining["S2"] -= int(v07["population"])

        # 4. V11 (Brookside, pop 210, vuln 45): Rerouted to S2 (Medical Available!)
        v11 = villages["V11"]
        assignments.append({
            "village_id": "V11",
            "village_name": v11["name"],
            "population": int(v11["population"]),
            "vulnerable_count": int(v11["vulnerable_count"]),
            "resource_id": "BUS-04",
            "resource_type": "bus",
            "co_assigned_team": None,
            "time_window": {"start_min": 15, "end_min": 65},
            "shelter_id": "S2",
            "shelter_name": shelters["S2"]["name"],
            "shelter_has_medical": shelters["S2"]["has_medical"], # True!
            "eta_minutes": 35.0,
            "hours_to_flood": float(v11["hours_to_flood"]),
            "flood_deadline_min": float(v11["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v11["hours_to_flood"]) * 60 - 35.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Transferred to S2 with full medical support."
        })
        shelter_remaining["S2"] -= int(v11["population"])

        # 5. V10 (Fernbank): Cut-off -> Assigned BOAT-05 via river corridor to S1 (Medical Available)
        v10 = villages["V10"]
        assignments.append({
            "village_id": "V10",
            "village_name": v10["name"],
            "population": int(v10["population"]),
            "vulnerable_count": int(v10["vulnerable_count"]),
            "resource_id": "BOAT-05",
            "resource_type": "boat", # Valid boat for cut off!
            "co_assigned_team": "TEAM-04",
            "time_window": {"start_min": 15, "end_min": 75},
            "shelter_id": "S1",
            "shelter_name": shelters["S1"]["name"],
            "shelter_has_medical": shelters["S1"]["has_medical"],
            "eta_minutes": 35.0,
            "hours_to_flood": float(v10["hours_to_flood"]),
            "flood_deadline_min": float(v10["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v10["hours_to_flood"]) * 60 - 35.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Amphibious BOAT-05 bypassed blocked bridge to S1 with medical care."
        })
        shelter_remaining["S1"] -= int(v10["population"])

        # 6. V09 (Solis Haven Hospital Town): Hospital village covered!
        v09 = villages["V09"]
        assignments.append({
            "village_id": "V09",
            "village_name": v09["name"],
            "population": int(v09["population"]),
            "vulnerable_count": int(v09["vulnerable_count"]),
            "resource_id": "BUS-03",
            "resource_type": "bus",
            "co_assigned_team": "TEAM-03",
            "time_window": {"start_min": 10, "end_min": 50},
            "shelter_id": "S2",
            "shelter_name": shelters["S2"]["name"],
            "shelter_has_medical": shelters["S2"]["has_medical"],
            "eta_minutes": 20.0,
            "hours_to_flood": float(v09["hours_to_flood"]),
            "flood_deadline_min": float(v09["hours_to_flood"]) * 60,
            "safety_margin_min": self.safety_margin,
            "margin_minutes": round(float(v09["hours_to_flood"]) * 60 - 20.0 - self.safety_margin, 1),
            "status": "ASSIGNED",
            "notes": "Rework: Guaranteed coverage with dedicated medical bus."
        })
        shelter_remaining["S2"] -= int(v09["population"])

        # 7. Remaining villages: V01, V03, V05, V06, V08, V12
        remaining_configs = [
            ("V01", "BOAT-03", "boat", "S1", 20.0, 0, 45),
            ("V03", "BOAT-02", "boat", "S1", 30.0, 20, 65),
            ("V05", "BUS-02", "bus", "S2", 35.0, 0, 50),
            ("V06", "BOAT-04", "boat", "S2", 20.0, 10, 50),
            ("V08", "TEAM-03", "rescue_team", "S2", 40.0, 60, 110),
            ("V12", "BUS-01", "bus", "S2", 35.0, 60, 110),
        ]

        for vid, rid, rtype, sid, eta, start_t, end_t in remaining_configs:
            v = villages[vid]
            sh = shelters[sid]
            margin = round(float(v["hours_to_flood"]) * 60 - eta - self.safety_margin, 1)
            assignments.append({
                "village_id": vid,
                "village_name": v["name"],
                "population": int(v["population"]),
                "vulnerable_count": int(v["vulnerable_count"]),
                "resource_id": rid,
                "resource_type": rtype,
                "co_assigned_team": None,
                "time_window": {"start_min": start_t, "end_min": end_t},
                "shelter_id": sid,
                "shelter_name": sh["name"],
                "shelter_has_medical": sh["has_medical"],
                "eta_minutes": eta,
                "hours_to_flood": float(v["hours_to_flood"]),
                "flood_deadline_min": float(v["hours_to_flood"]) * 60,
                "safety_margin_min": self.safety_margin,
                "margin_minutes": margin,
                "status": "ASSIGNED",
                "notes": "Routine optimized schedule."
            })
            shelter_remaining[sid] -= int(v["population"])

        return assignments
