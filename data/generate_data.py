"""
FloodCommand Synthetic Data Generator
Generates reproducible synthetic datasets for a fictional valley:
villages, roads, shelters, resources, and policy configuration.

IMPORTANT: Educational prototype on synthetic data. Not an operational tool.
All place names, villages, and figures are fictional.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path


def get_data_dir() -> Path:
    """Returns the data directory path."""
    return Path(__file__).resolve().parent


def generate_all_data(target_dir: Path | None = None) -> dict[str, Path]:
    """
    Generates all synthetic dataset files in target_dir using a fixed seed for reproducibility.
    Returns mapping of dataset name to file path.
    """
    if target_dir is None:
        target_dir = get_data_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    random.seed(42)
    files_created = {}

    # 1. villages.csv
    # 12 fictional villages along a schematic river
    villages_file = target_dir / "villages.csv"
    villages = [
        {"village_id": "V01", "name": "Elderglen", "x": 15, "y": 78, "population": 120, "vulnerable_count": 35, "hours_to_flood": 2.5, "has_hospital": False},
        {"village_id": "V02", "name": "Riverbend", "x": 25, "y": 68, "population": 240, "vulnerable_count": 60, "hours_to_flood": 3.0, "has_hospital": False},
        {"village_id": "V03", "name": "Highcliff", "x": 12, "y": 52, "population": 90, "vulnerable_count": 15, "hours_to_flood": 6.0, "has_hospital": False},
        {"village_id": "V04", "name": "Millhaven", "x": 34, "y": 62, "population": 310, "vulnerable_count": 85, "hours_to_flood": 2.0, "has_hospital": False},
        {"village_id": "V05", "name": "Oakhaven", "x": 45, "y": 50, "population": 180, "vulnerable_count": 40, "hours_to_flood": 4.5, "has_hospital": False},
        {"village_id": "V06", "name": "Willowdale", "x": 28, "y": 38, "population": 220, "vulnerable_count": 50, "hours_to_flood": 3.5, "has_hospital": False},
        {"village_id": "V07", "name": "Clearwater", "x": 58, "y": 62, "population": 280, "vulnerable_count": 70, "hours_to_flood": 2.2, "has_hospital": False},
        {"village_id": "V08", "name": "Pinecrest", "x": 65, "y": 42, "population": 140, "vulnerable_count": 25, "hours_to_flood": 5.0, "has_hospital": False},
        {"village_id": "V09", "name": "Solis Haven Town", "x": 42, "y": 30, "population": 380, "vulnerable_count": 110, "hours_to_flood": 4.0, "has_hospital": True},
        {"village_id": "V10", "name": "Fernbank", "x": 72, "y": 76, "population": 160, "vulnerable_count": 35, "hours_to_flood": 2.8, "has_hospital": False},
        {"village_id": "V11", "name": "Brookside", "x": 82, "y": 56, "population": 210, "vulnerable_count": 45, "hours_to_flood": 3.2, "has_hospital": False},
        {"village_id": "V12", "name": "Stonemeadow", "x": 86, "y": 32, "population": 175, "vulnerable_count": 40, "hours_to_flood": 5.5, "has_hospital": False},
    ]
    with open(villages_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["village_id", "name", "x", "y", "population", "vulnerable_count", "hours_to_flood", "has_hospital"])
        writer.writeheader()
        writer.writerows(villages)
    files_created["villages"] = villages_file

    # 2. shelters.csv
    # 3 shelters on higher ground
    shelters_file = target_dir / "shelters.csv"
    shelters = [
        {"shelter_id": "S1", "name": "North Hill Fort Shelter", "x": 22, "y": 92, "capacity": 1100, "current_load": 80, "has_medical": True},
        {"shelter_id": "S2", "name": "Central Ridge Stadium", "x": 52, "y": 18, "capacity": 2800, "current_load": 120, "has_medical": True},
        {"shelter_id": "S3", "name": "East Plateau Academy", "x": 88, "y": 88, "capacity": 450, "current_load": 190, "has_medical": False},
    ]
    with open(shelters_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shelter_id", "name", "x", "y", "capacity", "current_load", "has_medical"])
        writer.writeheader()
        writer.writerows(shelters)
    files_created["shelters"] = shelters_file

    # 3. roads.csv
    # Connects villages, shelters, and hospital town.
    # Notice: V10's connecting bridge road to S3/network is marked "blocked" to plant the cut-off condition!
    roads_file = target_dir / "roads.csv"
    roads = [
        # Sector North-West (S1, V01, V02, V03, V04)
        {"from_id": "S1", "to_id": "V01", "travel_minutes": 20, "has_bridge": False, "status": "open"},
        {"from_id": "V01", "to_id": "V02", "travel_minutes": 25, "has_bridge": True, "status": "open"},
        {"from_id": "V01", "to_id": "V03", "travel_minutes": 35, "has_bridge": False, "status": "open"},
        {"from_id": "V02", "to_id": "V04", "travel_minutes": 20, "has_bridge": True, "status": "open"},
        {"from_id": "V03", "to_id": "V06", "travel_minutes": 30, "has_bridge": False, "status": "open"},

        # Central Sector (V04, V05, V06, V07, V09, S2)
        {"from_id": "V04", "to_id": "V05", "travel_minutes": 25, "has_bridge": True, "status": "open"},
        {"from_id": "V05", "to_id": "V06", "travel_minutes": 25, "has_bridge": False, "status": "open"},
        {"from_id": "V06", "to_id": "V09", "travel_minutes": 20, "has_bridge": False, "status": "open"},
        {"from_id": "V09", "to_id": "S2", "travel_minutes": 15, "has_bridge": False, "status": "open"},
        {"from_id": "V05", "to_id": "V07", "travel_minutes": 30, "has_bridge": True, "status": "open"},
        {"from_id": "V05", "to_id": "V08", "travel_minutes": 35, "has_bridge": False, "status": "open"},
        {"from_id": "V08", "to_id": "S2", "travel_minutes": 40, "has_bridge": False, "status": "open"},
        {"from_id": "V08", "to_id": "V12", "travel_minutes": 30, "has_bridge": False, "status": "open"},
        {"from_id": "V12", "to_id": "S2", "travel_minutes": 35, "has_bridge": False, "status": "open"},

        # East Sector (V10, V11, S3)
        # Note: V10 is cut off because its main connection to S3 (Fern Bridge) is BLOCKED!
        {"from_id": "V10", "to_id": "S3", "travel_minutes": 30, "has_bridge": True, "status": "blocked"},
        {"from_id": "V10", "to_id": "V07", "travel_minutes": 45, "has_bridge": True, "status": "blocked"},
        {"from_id": "V07", "to_id": "V11", "travel_minutes": 35, "has_bridge": True, "status": "open"},
        {"from_id": "V11", "to_id": "S3", "travel_minutes": 25, "has_bridge": False, "status": "open"},
        {"from_id": "V11", "to_id": "V12", "travel_minutes": 40, "has_bridge": False, "status": "open"},

        # Long arterial cross-links
        {"from_id": "V02", "to_id": "S1", "travel_minutes": 35, "has_bridge": False, "status": "open"},
        {"from_id": "V04", "to_id": "S2", "travel_minutes": 105, "has_bridge": True, "status": "open"}, # slow cross route
    ]
    with open(roads_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["from_id", "to_id", "travel_minutes", "has_bridge", "status"])
        writer.writeheader()
        writer.writerows(roads)
    files_created["roads"] = roads_file

    # 4. resources.csv (5 boats, 4 buses, 4 rescue teams)
    resources_file = target_dir / "resources.csv"
    resources = [
        {"resource_id": "BOAT-01", "type": "boat", "capacity": 40, "base_location": "S1", "available": True},
        {"resource_id": "BOAT-02", "type": "boat", "capacity": 45, "base_location": "S2", "available": True},
        {"resource_id": "BOAT-03", "type": "boat", "capacity": 35, "base_location": "S1", "available": True},
        {"resource_id": "BOAT-04", "type": "boat", "capacity": 50, "base_location": "S2", "available": True},
        {"resource_id": "BOAT-05", "type": "boat", "capacity": 60, "base_location": "S3", "available": True},
        {"resource_id": "BUS-01", "type": "bus", "capacity": 55, "base_location": "S1", "available": True},
        {"resource_id": "BUS-02", "type": "bus", "capacity": 55, "base_location": "S2", "available": True},
        {"resource_id": "BUS-03", "type": "bus", "capacity": 60, "base_location": "S2", "available": True},
        {"resource_id": "BUS-04", "type": "bus", "capacity": 50, "base_location": "S3", "available": True},
        {"resource_id": "TEAM-01", "type": "rescue_team", "capacity": 30, "base_location": "S1", "available": True},
        {"resource_id": "TEAM-02", "type": "rescue_team", "capacity": 30, "base_location": "S2", "available": True},
        {"resource_id": "TEAM-03", "type": "rescue_team", "capacity": 25, "base_location": "S2", "available": True},
        {"resource_id": "TEAM-04", "type": "rescue_team", "capacity": 25, "base_location": "S3", "available": True},
    ]
    with open(resources_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["resource_id", "type", "capacity", "base_location", "available"])
        writer.writeheader()
        writer.writerows(resources)
    files_created["resources"] = resources_file

    # 5. config.json
    config_file = target_dir / "config.json"
    config = {
        "safety_margin_minutes": 30,
        "boat_speed_factor": 1.2,
        "bus_load_minutes": 20,
        "max_rework_rounds": 3,
        "fictional_disclaimer": "Educational prototype on synthetic data. Not an operational tool.",
        "hospital_village_id": "V09",
        "river_curve": [
            {"x": 10, "y": 85},
            {"x": 20, "y": 72},
            {"x": 32, "y": 64},
            {"x": 48, "y": 55},
            {"x": 62, "y": 60},
            {"x": 75, "y": 70},
            {"x": 88, "y": 60},
            {"x": 95, "y": 45}
        ]
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    files_created["config"] = config_file

    return files_created


if __name__ == "__main__":
    out = generate_all_data()
    print("Synthetic data generated successfully:")
    for k, v in out.items():
        print(f" - {k}: {v}")
