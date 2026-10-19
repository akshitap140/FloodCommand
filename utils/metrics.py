"""
Metrics and Evaluation Utilities for FloodCommand
Computes operational performance indicators, coverage ratios,
and safety margins for evacuation plans.
"""

from __future__ import annotations

from typing import Any


def calculate_plan_metrics(
    assignments: list[dict[str, Any]],
    villages: list[dict[str, Any]],
    shelters: list[dict[str, Any]],
    resources: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Computes summary metrics for a set of village evacuation assignments.
    """
    total_villages = len(villages)
    total_population = sum(int(v.get("population", 0)) for v in villages)
    total_vulnerable = sum(int(v.get("vulnerable_count", 0)) for v in villages)

    assigned_villages = {a["village_id"] for a in assignments if a.get("status") != "FAILED"}
    covered_population = sum(int(v.get("population", 0)) for v in villages if v["village_id"] in assigned_villages)
    covered_vulnerable = sum(int(v.get("vulnerable_count", 0)) for v in villages if v["village_id"] in assigned_villages)

    margins = [float(a.get("margin_minutes", 0)) for a in assignments if a.get("margin_minutes") is not None]
    avg_margin = round(sum(margins) / len(margins), 1) if margins else 0.0
    min_margin = min(margins) if margins else 0.0

    # Shelter loads
    shelter_loads: dict[str, dict[str, Any]] = {}
    for s in shelters:
        sid = s["shelter_id"]
        cap = int(s.get("capacity", 0))
        cur = int(s.get("current_load", 0))
        shelter_loads[sid] = {
            "name": s.get("name", sid),
            "capacity": cap,
            "initial_load": cur,
            "allocated": 0,
            "total_projected": cur,
            "occupancy_rate": 0.0,
        }

    for a in assignments:
        sid = a.get("shelter_id")
        if sid in shelter_loads and a.get("status") != "FAILED":
            pop = int(a.get("population", 0))
            shelter_loads[sid]["allocated"] += pop
            shelter_loads[sid]["total_projected"] += pop

    for sid, data in shelter_loads.items():
        if data["capacity"] > 0:
            data["occupancy_rate"] = round((data["total_projected"] / data["capacity"]) * 100, 1)

    # Resource utilization
    assigned_resources = {a.get("resource_id") for a in assignments if a.get("resource_id")}
    total_available_resources = sum(1 for r in resources if bool(r.get("available", True)))
    utilization_rate = round((len(assigned_resources) / max(total_available_resources, 1)) * 100, 1)

    return {
        "total_villages": total_villages,
        "assigned_villages_count": len(assigned_villages),
        "total_population": total_population,
        "covered_population": covered_population,
        "population_coverage_pct": round((covered_population / max(total_population, 1)) * 100, 1),
        "total_vulnerable": total_vulnerable,
        "covered_vulnerable": covered_vulnerable,
        "vulnerable_coverage_pct": round((covered_vulnerable / max(total_vulnerable, 1)) * 100, 1),
        "average_margin_minutes": avg_margin,
        "minimum_margin_minutes": min_margin,
        "shelter_loads": shelter_loads,
        "resource_utilization_pct": utilization_rate,
        "assigned_resources_count": len(assigned_resources),
    }
