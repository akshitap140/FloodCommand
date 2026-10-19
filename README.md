# 🌊 FloodCommand: Multi-Agent Evacuation and Relief Planner

> **DISCLAIMER:** Educational prototype on synthetic data. Not an operational tool.
> All geography, villages, river contours, and disaster timelines represent a fictional scenario (Aethel Valley Basin) developed strictly for multi-agent systems research and evaluation.

---

## 📌 Executive Overview

During sudden-onset natural emergencies like river valley floods, emergency coordinators face severe cognitive load. Traditional manual dispatch often suffers from fatal oversights:
- Assigning buses to villages whose access bridges are already underwater.
- Overloading emergency shelters beyond sanitation and physical capacity.
- Routing vehicles along slow corridors that flood before the vehicle reaches the victims.
- Double-booking specialized swiftwater rescue teams across simultaneous incidents.
- Overlooking vulnerable hospital hubs during high-tempo evacuation planning.

**FloodCommand** is an adversarial multi-agent system built on pure Python heuristic and graph intelligence (no paid APIs, zero LLM hallucination). It demonstrates automated task planning, topological graph reachability, greedy fleet allocation, **adversarial Red-Team criticism with an automated rework loop**, and real-time surgical re-planning under dynamic field disruptions.

---

## 🏛️ System Architecture

```text
                               ┌────────────────────────────────┐
                               │     1. PLANNER AGENT           │
                               │  - Urgency Index Scoring       │
                               │  - Priority Task Graph         │
                               └───────────────┬────────────────┘
                                               │
                                               ▼
                               ┌────────────────────────────────┐
                               │   2. IMPACT ANALYST AGENT      │
                               │  - BFS Road Network Traversal  │
                               │  - Cut-Off Village Detection   │
                               └───────────────┬────────────────┘
                                               │
                                               ▼
                               ┌────────────────────────────────┐
                               │   3. RESOURCE AGENT (EXECUTOR) │
                               │  - Pass 1: Naive Greedy Plan   │
                               │  - Pass 2+: Structural Repair  │
                               └───────────────┬────────────────┘
                                               │
                                               ▼
           ┌───────────────────► 4. RED-TEAM CRITIC AGENT       │
           │                   │  - Audits Rules R1 through R6  │
           │                   └───────────────┬────────────────┘
           │                                   │
      REWORK LOOP                              │
(Max 3 iterations)                     Violations Detected?
           │                                   │
           │                                   ├──► [YES] ──► Passes Violation Context to Resource Agent
           │                                   │
           │                                   └──► [NO: APPROVED]
           │                                           │
           │                                           ▼
           │                           ┌────────────────────────────────┐
           │                           │     5. ALERT AGENT             │
           │                           │  - Ground-Truth SMS Broadcast  │
           │                           │  - Zero Hallucination Policy   │
           │                           └────────────────────────────────┘
           │
           │ (On Dynamic Incident)
 ┌─────────┴───────────────┐
 │ 6. RE-PLANNER AGENT     │
 │ - Surgical Diff Engine  │
 │ - Minimizes Re-routes   │
 └─────────────────────────┘
```

---

## 🤖 Agent Roles & Responsibilities

| Agent | Responsibility | Core Mechanism |
| :--- | :--- | :--- |
| **Planner Agent** | Calculates urgency matrices combining demographic vulnerability and flood arrival speed. | Weighted urgency index: `(vuln * 2.5 + pop * 0.75) / hours_to_flood` |
| **Impact Analyst Agent** | Identifies topological isolation caused by submerged bridges. | Breadth-First Search (BFS) over open edge graph |
| **Resource Agent** | Schedules 5 boats, 4 buses, and 4 rescue teams to shelters. | Greedy initial pass, followed by feedback-guided multi-constraint optimization |
| **Red-Team Critic Agent** | Adversarial safety validator enforcing 6 non-negotiable life-safety invariants. | Deterministic invariant checking (R1 to R6) |
| **Re-Planner Agent** | Surgically handles unexpected field events (bridge washouts, accelerated floods, breakdowns). | Differential impact subgraph isolation |
| **Alert Agent** | Composes unambiguous, deterministic emergency SMS alerts for civilian broadcast. | Template engine driven 100% by ground-truth manifest data |

---

## 🛡️ The 6 Red-Team Safety Invariants

1. **R1 (Shelter Capacity):** `current_load + sum(assigned_evacuees) <= shelter_capacity`
2. **R2 (Flood Deadline Margin):** `vehicle_eta_minutes + safety_margin_minutes < hours_to_flood * 60`
3. **R3 (No Resource Conflicts):** No vehicle or rescue team may be scheduled in overlapping operational windows.
4. **R4 (Amphibious Integrity):** Cut-off villages without open road access must strictly receive boats or amphibious rescue teams (no buses).
5. **R5 (Medical Triage Coverage):** Any community with vulnerable residents (`vulnerable_count > 0`) must be assigned to a shelter with on-site medical staffing (`has_medical = True`).
6. **R6 (Hospital Protection):** Designated hospital centers (`has_hospital = True`) must never be left uncovered.

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
*(Alternatively, run `streamlit run floodcommand/app.py` from within the project directory)*

### 4. Run the Automated Test Suite
```bash
python -m unittest floodcommand/tests/test_critic.py
```
*(Or run `pytest` if pytest is installed)*

---

## 🖥️ User Interface Overview

The interface features an ultra-modern dark theme (`#07121F` deep navy, `#22D3EE` cyan, and `#8B5CF6` violet):

1. **🗺️ Situation Map:** Visualizes the Aethel Valley schematic 0-100 grid, curved river basin, open road links, blocked bridges, safe shelters, and villages colored by hazard status.
2. **⚡ Run Agents & Live Trace:** Executes the full multi-agent pipeline with real-time timeline cards showing Planner, Impact Analyst, Resource Agent, Critic rejections, Rework corrections, and final Approval.
3. **📋 Final Plan & SMS:** Displays the full evacuation assignment matrix, time margins, CSV export, and realistic mobile SMS dispatch cards.
4. **🚨 Real-Time Disruption:** Interactive scenario injection (*Bridge Washed Out*, *Flood 2h Early*, *Boat Breakdown*, *Shelter Full*) with before/after maps and surgical diffs.
5. **📊 Validation & Benchmark:** Quantitative metrics demonstrating 100% detection of planted failure modes and comparisons against manual operational dispatch.

---

## 🔬 Assumptions & Limitations

- **Synthetic Scenario:** All geography, river contours, road networks, and population statistics are entirely synthetic.
- **Kinematic Travel Times:** Travel times are modeled via graph-based Dijkstra algorithms and straight-line river velocities rather than live GPS traffic feeds.
- **Hydrological Discretization:** The simulation operates on hourly flood arrival horizons rather than 2D hydrodynamic finite-volume Navier-Stokes models.
- **Operational Scope:** Designed as an educational proof-of-concept for multi-agent reasoning, adversarial validation, and self-healing systems.
