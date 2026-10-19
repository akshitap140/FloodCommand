"""
Red-Team Critic Agent for FloodCommand
Actively performs adversarial audits of proposed evacuation schedules against 6 strict safety rules:
R1: Shelter load never exceeds capacity
R2: Vehicle arrival time + safety margin < hours_to_flood
R3: No resource is assigned to two villages with overlapping time
R4: Every cut-off village has boat or rescue team access, not a bus
R5: Every village with vulnerable people goes to a shelter with medical support
R6: The hospital village is covered
"""

from __future__ import annotations

from typing import Any


class RedTeamCriticAgent:
    """
    Adversarial validation agent that inspects evacuation plans and emits granular violation logs.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.safety_margin = float(self.config.get("safety_margin_minutes", 30))
        self.hospital_village_id = str(self.config.get("hospital_village_id", "V09"))

    def audit(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Takes: {
            "assignments": list[dict],
            "shelters": list[dict],
            "villages": list[dict],
            "resources": list[dict],
            "impact_data": dict,
            "config": dict (optional)
        }
        Returns: {
            "verdict": "APPROVED" | "APPROVED_WITH_CONDITIONS" | "NEEDS_REWORK",
            "violations": list[dict],
            "passed_rules": list[str],
            "violation_count_by_rule": dict[str, int],
            "audit_summary": str,
            "status": "ok"
        }
        """
        assignments = input_data.get("assignments", [])
        shelters = input_data.get("shelters", [])
        villages = input_data.get("villages", [])
        resources = input_data.get("resources", [])
        impact_data = input_data.get("impact_data", {})

        shelters_by_id = {str(s["shelter_id"]): s for s in shelters}
        villages_by_id = {str(v["village_id"]): v for v in villages}
        cut_off_ids = set(impact_data.get("cut_off_villages", []))

        violations: list[dict[str, Any]] = []
        passed_rules: set[str] = {"R1", "R2", "R3", "R4", "R5", "R6"}

        # -------------------------------------------------------------
        # Rule R1: Shelter load never exceeds capacity
        # -------------------------------------------------------------
        shelter_projected_load: dict[str, int] = {
            sid: int(s.get("current_load", 0)) for sid, s in shelters_by_id.items()
        }

        for a in assignments:
            sid = str(a.get("shelter_id", ""))
            pop = int(a.get("population", 0))
            if sid in shelter_projected_load:
                shelter_projected_load[sid] += pop

        for sid, proj_load in shelter_projected_load.items():
            sh = shelters_by_id.get(sid)
            if sh:
                cap = int(sh.get("capacity", 0))
                if proj_load > cap:
                    passed_rules.discard("R1")
                    overflow = proj_load - cap
                    sh_name = sh.get("name", sid)
                    violations.append({
                        "rule_id": "R1",
                        "rule_name": "Shelter Capacity Limit Exceeded",
                        "severity": "CRITICAL",
                        "village_id": "MULTIPLE",
                        "shelter_id": sid,
                        "reason": (
                            f"{sh_name} ({sid}) has capacity {cap} and existing load {sh.get('current_load', 0)}. "
                            f"Projected load is {proj_load} ({overflow} people over capacity)."
                        ),
                        "suggested_fix": (
                            f"Reroute one or more villages assigned to {sid} to Central Ridge Stadium (S2) "
                            f"or North Hill Fort (S1)."
                        ),
                    })

        # -------------------------------------------------------------
        # Rule R2: Vehicle arrival time + safety margin < hours_to_flood
        # -------------------------------------------------------------
        for a in assignments:
            vid = str(a.get("village_id", ""))
            eta = float(a.get("eta_minutes", 0.0))
            margin_min = float(a.get("safety_margin_min", self.safety_margin))
            hours_flood = float(a.get("hours_to_flood", 0.0))
            deadline_min = hours_flood * 60.0

            if eta + margin_min >= deadline_min:
                passed_rules.discard("R2")
                deficit = (eta + margin_min) - deadline_min
                vname = a.get("village_name", vid)
                violations.append({
                    "rule_id": "R2",
                    "rule_name": "Insufficient Flood Evacuation Time Window",
                    "severity": "CRITICAL",
                    "village_id": vid,
                    "reason": (
                        f"{vname} ({vid}) will flood in {hours_flood:.1f} hrs ({deadline_min:.0f} mins). "
                        f"Assigned vehicle arrival time ({eta:.1f}m) + required safety margin ({margin_min:.0f}m) "
                        f"equals {eta + margin_min:.1f} mins ({deficit:.1f} mins past safe cutoff)."
                    ),
                    "suggested_fix": (
                        f"Replace long bus route with high-speed river craft or dispatch from closer staging point."
                    ),
                })

        # -------------------------------------------------------------
        # Rule R3: No resource is assigned to two villages with overlapping time
        # -------------------------------------------------------------
        # Collect schedules for each resource (both primary resource_id and co_assigned_team)
        resource_intervals: dict[str, list[dict[str, Any]]] = {}

        for a in assignments:
            rid = a.get("resource_id")
            window = a.get("time_window")
            vid = a.get("village_id")
            if rid and window:
                resource_intervals.setdefault(str(rid), []).append({
                    "village_id": vid,
                    "start": float(window.get("start_min", 0)),
                    "end": float(window.get("end_min", 0)),
                })

            co_team = a.get("co_assigned_team")
            if co_team and window:
                resource_intervals.setdefault(str(co_team), []).append({
                    "village_id": vid,
                    "start": float(window.get("start_min", 0)),
                    "end": float(window.get("end_min", 0)),
                })

        for rid, intervals in resource_intervals.items():
            if len(intervals) > 1:
                # Check all pairs
                for i in range(len(intervals)):
                    for j in range(i + 1, len(intervals)):
                        int_a = intervals[i]
                        int_b = intervals[j]
                        # Overlap if max(start) < min(end)
                        if max(int_a["start"], int_b["start"]) < min(int_a["end"], int_b["end"]):
                            passed_rules.discard("R3")
                            violations.append({
                                "rule_id": "R3",
                                "rule_name": "Resource Double-Booking Conflict",
                                "severity": "CRITICAL",
                                "village_id": f"{int_a['village_id']}, {int_b['village_id']}",
                                "resource_id": rid,
                                "reason": (
                                    f"Resource {rid} is scheduled simultaneously for {int_a['village_id']} "
                                    f"[{int_a['start']:.0f}-{int_a['end']:.0f}m] and {int_b['village_id']} "
                                    f"[{int_b['start']:.0f}-{int_b['end']:.0f}m]."
                                ),
                                "suggested_fix": (
                                    f"Assign separate vehicle/team to one village or stagger departure windows."
                                ),
                            })

        # -------------------------------------------------------------
        # Rule R4: Every cut-off village has boat or rescue team access, not a bus
        # -------------------------------------------------------------
        for a in assignments:
            vid = str(a.get("village_id", ""))
            rtype = str(a.get("resource_type", "")).lower()
            if vid in cut_off_ids:
                if rtype == "bus":
                    passed_rules.discard("R4")
                    vname = a.get("village_name", vid)
                    violations.append({
                        "rule_id": "R4",
                        "rule_name": "Invalid Vehicle Type for Cut-Off Village",
                        "severity": "CRITICAL",
                        "village_id": vid,
                        "reason": (
                            f"{vname} ({vid}) is cut off by floodwaters and blocked bridges. "
                            f"Assigned transport is a road bus ({a.get('resource_id')}), which cannot traverse flooded water barriers."
                        ),
                        "suggested_fix": (
                            f"Reallocate an amphibious rescue team or watercraft (e.g. BOAT-05) to {vname}."
                        ),
                    })

        # -------------------------------------------------------------
        # Rule R5: Every village with vulnerable people goes to a shelter with medical support
        # -------------------------------------------------------------
        for a in assignments:
            vid = str(a.get("village_id", ""))
            vuln = int(a.get("vulnerable_count", 0))
            sid = str(a.get("shelter_id", ""))
            has_med = bool(a.get("shelter_has_medical", False))

            if vuln > 0 and not has_med:
                passed_rules.discard("R5")
                vname = a.get("village_name", vid)
                sh_name = a.get("shelter_name", sid)
                violations.append({
                    "rule_id": "R5",
                    "rule_name": "Vulnerable Population Sent to Non-Medical Shelter",
                    "severity": "CRITICAL",
                    "village_id": vid,
                    "reason": (
                        f"{vname} ({vid}) has {vuln} vulnerable residents (elderly/patients/children) "
                        f"but is assigned to {sh_name} ({sid}), which lacks medical staff and emergency triage."
                    ),
                    "suggested_fix": (
                        f"Re-assign {vname} to North Hill Fort Shelter (S1) or Central Ridge Stadium (S2), "
                        f"both of which have on-site emergency medical facilities."
                    ),
                })

        # -------------------------------------------------------------
        # Rule R6: The hospital village is covered
        # -------------------------------------------------------------
        # Find hospital village in villages data
        hospital_vids = {str(v["village_id"]) for v in villages if bool(v.get("has_hospital", False))}
        if not hospital_vids and self.hospital_village_id:
            hospital_vids = {self.hospital_village_id}

        assigned_vids = {str(a.get("village_id")) for a in assignments if a.get("status") == "ASSIGNED"}

        for hvid in hospital_vids:
            if hvid not in assigned_vids:
                passed_rules.discard("R6")
                h_name = villages_by_id.get(hvid, {}).get("name", hvid)
                violations.append({
                    "rule_id": "R6",
                    "rule_name": "Hospital Village Left Uncovered",
                    "severity": "CRITICAL",
                    "village_id": hvid,
                    "reason": (
                        f"Hospital village {h_name} ({hvid}) contains critical patients and medical staff "
                        f"but has NO evacuation resources or transport assigned in the plan."
                    ),
                    "suggested_fix": (
                        f"Ensure priority allocation of dedicated transport (e.g. BUS-03 with medical support) to {h_name}."
                    ),
                })

        # Determine overall verdict
        if not violations:
            verdict = "APPROVED"
            audit_summary = "All 6 Red-Team Critic safety rules passed successfully. Plan is verified for deployment."
        elif any(v["severity"] == "CRITICAL" for v in violations):
            verdict = "NEEDS_REWORK"
            audit_summary = f"Detected {len(violations)} safety violations across rules {[v['rule_id'] for v in violations]}. Mandatory rework triggered."
        else:
            verdict = "APPROVED_WITH_CONDITIONS"
            audit_summary = f"Plan approved with {len(violations)} non-critical advisory conditions."

        violation_counts = {
            "R1": sum(1 for v in violations if v["rule_id"] == "R1"),
            "R2": sum(1 for v in violations if v["rule_id"] == "R2"),
            "R3": sum(1 for v in violations if v["rule_id"] == "R3"),
            "R4": sum(1 for v in violations if v["rule_id"] == "R4"),
            "R5": sum(1 for v in violations if v["rule_id"] == "R5"),
            "R6": sum(1 for v in violations if v["rule_id"] == "R6"),
        }

        return {
            "verdict": verdict,
            "violations": violations,
            "passed_rules": sorted(list(passed_rules)),
            "violation_count_by_rule": violation_counts,
            "audit_summary": audit_summary,
            "status": "ok",
        }
