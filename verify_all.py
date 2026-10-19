"""
End-to-end verification script for FloodCommand multi-agent system.
"""

import json
import pandas as pd
from data.generate_data import get_data_dir, generate_all_data
from agents.orchestrator import FloodCommandOrchestrator
from agents.replanner import ReplannerAgent

def run_tests():
    data_dir = get_data_dir()
    generate_all_data(data_dir)

    villages = pd.read_csv(data_dir / "villages.csv").to_dict("records")
    shelters = pd.read_csv(data_dir / "shelters.csv").to_dict("records")
    resources = pd.read_csv(data_dir / "resources.csv").to_dict("records")
    roads = pd.read_csv(data_dir / "roads.csv").to_dict("records")

    with open(data_dir / "config.json", encoding="utf-8") as f:
        config = json.load(f)

    # 1. Orchestrator workflow
    orch = FloodCommandOrchestrator(config=config)
    res = orch.run_workflow(villages, shelters, resources, roads)

    print(f"Workflow verdict: {res['verdict']}")
    print(f"Initial violations: {len(res['initial_audit']['violations'])}")
    print(f"Final violations: {len(res['final_audit']['violations'])}")
    print(f"Rework iterations: {res['rework_iterations']}")
    print(f"Trace steps: {len(res['trace'])}")
    print(f"Population coverage: {res['metrics']['population_coverage_pct']}% ({res['metrics']['covered_population']} people)")

    assert res["verdict"] == "APPROVED", f"Expected APPROVED, got {res['verdict']}"
    assert len(res["final_audit"]["violations"]) == 0, "Expected 0 final violations"
    assert len(res["alerts"]) == 12, "Expected 12 alerts"
    assert res["metrics"]["population_coverage_pct"] == 100.0, "Expected 100% population coverage"

    # 2. Re-planner disruptions
    replanner = ReplannerAgent(config=config)
    for event in ["bridge_washout", "flood_accelerated", "vehicle_breakdown", "shelter_full"]:
        dis_res = replanner.handle_disruption(event, res["final_plan"], villages, shelters, resources, roads)
        assert dis_res["status"] == "ok", f"Disruption {event} failed"
        print(f"Disruption [{event}]: {len(dis_res['diff'])} changes, verdict={dis_res['critic_verdict']}")

    print("\nSUCCESS: All agents, adversarial audits, rework loops, and disruption handlers passed 100%!")

if __name__ == "__main__":
    run_tests()
