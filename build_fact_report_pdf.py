"""
Script to generate the comprehensive, professional PDF:
'Architectural and Operational Fact Report.pdf'
Uses ReportLab to produce a publication-grade technical report for presentations,
architecture diagrams, and viva defense.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count and professional running headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(
                45,
                letter[1] - 32,
                "FloodCommand — Architectural & Operational Fact Report",
            )
            self.drawRightString(
                letter[0] - 45,
                letter[1] - 32,
                "System Architecture & Viva Defense Reference",
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, letter[1] - 36, letter[0] - 45, letter[1] - 36)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 40, letter[0] - 45, 40)

        self.drawString(
            45,
            28,
            "Educational prototype on synthetic data. Not an operational tool.",
        )
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 45, 28, page_str)
        self.restoreState()


def create_fact_report_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F2236"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F2236"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5,
    )

    body_bold = ParagraphStyle(
        "DocBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    mono_style = ParagraphStyle(
        "MonoStyle",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#0F172A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#FFFFFF"),
        alignment=0,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    story = []

    # Title block
    story.append(Paragraph("FloodCommand: Architectural & Operational Fact Report", title_style))
    story.append(Paragraph("Multi-Agent Evacuation & Relief Operations Center — Aethel Valley Basin", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F2236"), spaceAfter=8))

    # Grounding Box
    grounding_text = (
        "<b>REPORT GROUNDING & AUDIT MANDATE:</b><br/>"
        "• All data, code symbols, formulas, and operational figures are drawn strictly from runtime execution of the codebase.<br/>"
        "• The initial schedule is a <b>baseline with known flaws, built specifically to test the Critic</b> (not an unguided heuristic).<br/>"
        "• The repair step is acknowledged upfront as <b>rule-templated</b> for this scenario; a general solver like Google OR-Tools could replace it. The <b>Critic is genuinely general</b> and audits any plan.<br/>"
        "• Alerts are <b>template-generated directly from plan data</b>, so there is no model to invent numbers."
    )
    grounding_table = Table([[Paragraph(grounding_text, callout_style)]], colWidths=[522])
    grounding_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("LINELEFT", (0, 0), (0, -1), 3.5, colors.HexColor("#2563EB")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(grounding_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 1: PROJECT BASICS
    # =========================================================================
    story.append(Paragraph("1. PROJECT BASICS", h1_style))
    story.append(Paragraph("• <b>Exact Project Title:</b> <code>FloodCommand: Multi-Agent Evacuation and Relief Planner</code> (UI Header: <code>FloodCommand - Operations Center</code>, browser title: <code>FloodCommand</code>).", bullet_style))
    story.append(Paragraph("• <b>One-Line Description:</b> <code>Multi-Agent Evacuation and Relief Planner for Aethel Valley Basin</code> (Disclaimer: <i>'Educational prototype on synthetic data. Not an operational tool.'</i>).", bullet_style))
    story.append(Paragraph("• <b>Fictional Valley Name:</b> <code>Aethel Valley</code> (or <code>Aethel Valley Basin</code>).", bullet_style))
    story.append(Paragraph("• <b>Python Runtime:</b> <code>Python 3.13.0</code> | <b>Exact Launch Command:</b> <code>streamlit run app.py</code>", bullet_style))
    story.append(Paragraph("• <b>Dependencies (requirements.txt vs installed):</b> <code>streamlit>=1.35.0</code> (1.54.0), <code>pandas>=2.0.0</code> (2.2.3), <code>plotly>=5.18.0</code> (6.5.2), <code>pytest>=7.4.0</code> (9.1.1).", bullet_style))
    story.append(Spacer(1, 4))

    # File Tree Table
    tree_data = [
        [Paragraph("File / Directory", table_header_style), Paragraph("One-Line Purpose & Functional Role", table_header_style)],
        [Paragraph("<code>app.py</code>", table_cell_bold), Paragraph("Streamlit dashboard UI: views, tabs, scenario presets, Plotly maps, state machine.", table_cell_style)],
        [Paragraph("<code>floodcommand.py</code>", table_cell_bold), Paragraph("Module compatibility shim exposing agents, data, and utils packages.", table_cell_style)],
        [Paragraph("<code>requirements.txt</code>", table_cell_bold), Paragraph("Official Python library dependency specifications.", table_cell_style)],
        [Paragraph("<code>verify_all.py</code>", table_cell_bold), Paragraph("Automated integration script validating baseline and 4 field disruptions.", table_cell_style)],
        [Paragraph("<code>agents/planner.py</code>", table_cell_bold), Paragraph("PlannerAgent: calculates demographic urgency scores and prioritization order.", table_cell_style)],
        [Paragraph("<code>agents/impact.py</code>", table_cell_bold), Paragraph("ImpactAnalystAgent: evaluates road graph BFS connectivity and cut-off nodes.", table_cell_style)],
        [Paragraph("<code>agents/resource.py</code>", table_cell_bold), Paragraph("ResourceAgent: dual-mode dispatch (flawed baseline pass vs template repair).", table_cell_style)],
        [Paragraph("<code>agents/critic.py</code>", table_cell_bold), Paragraph("RedTeamCriticAgent: adversarial auditor enforcing safety rules R1 to R6.", table_cell_style)],
        [Paragraph("<code>agents/replanner.py</code>", table_cell_bold), Paragraph("ReplannerAgent: surgical before/after diff engine for sudden disruptions.", table_cell_style)],
        [Paragraph("<code>agents/alerts.py</code>", table_cell_bold), Paragraph("AlertAgent: template-generated civilian emergency SMS bulletins from plan data.", table_cell_style)],
        [Paragraph("<code>agents/orchestrator.py</code>", table_cell_bold), Paragraph("FloodCommandOrchestrator: manages agent pipeline, trace log, and rework loop.", table_cell_style)],
        [Paragraph("<code>data/generate_data.py</code>", table_cell_bold), Paragraph("Synthetic data generator producing reproducible CSVs with fixed random seed 42.", table_cell_style)],
        [Paragraph("<code>data/*.csv, config.json</code>", table_cell_bold), Paragraph("Synthetic datasets: 12 villages, 21 roads, 13 resources, 3 shelters, config parameters.", table_cell_style)],
        [Paragraph("<code>tests/test_critic.py</code>", table_cell_bold), Paragraph("Automated pytest test suite verifying Critic audit rules R1 through R6.", table_cell_style)],
        [Paragraph("<code>utils/graph.py, metrics.py</code>", table_cell_bold), Paragraph("Graph tools (BFS, Dijkstra) and summary metrics calculation utilities.", table_cell_style)],
    ]
    t_tree = Table(tree_data, colWidths=[140, 382])
    t_tree.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tree)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: AGENTS
    # =========================================================================
    story.append(Paragraph("2. AGENTS", h1_style))
    story.append(Paragraph("All 7 agents in FloodCommand are strictly <b>rule-based</b> (zero LLM / zero ML).", body_style))

    agent_data = [
        [Paragraph("Agent Name", table_header_style), Paragraph("Class & File", table_header_style), Paragraph("Inputs & Outputs", table_header_style), Paragraph("Core Logic & Formulas", table_header_style)],
        [
            Paragraph("<b>Planner</b>", table_cell_bold),
            Paragraph("<code>PlannerAgent</code><br/><code>agents/planner.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>villages</code>, <code>config</code><br/><b>Out:</b> <code>priority_order</code>, <code>urgency_scores</code>, <code>tasks</code>", table_cell_style),
            Paragraph("Urgency Score = round(((vuln * 2.5 + pop * 0.75) / max(hours, 0.5)) * hospital_boost, 2), where hospital_boost = 1.3 if has_hospital else 1.0. Sorts descending to establish execution queue.", table_cell_style),
        ],
        [
            Paragraph("<b>Impact Analyst</b>", table_cell_bold),
            Paragraph("<code>ImpactAnalystAgent</code><br/><code>agents/impact.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>villages</code>, <code>roads</code>, <code>shelters</code>, <code>hosp_id</code><br/><b>Out:</b> <code>cut_off_villages</code>, <code>accessible</code>, <code>details</code>", table_cell_style),
            Paragraph("Builds road graph (ignoring blocked roads). Executes Breadth-First Search (BFS) from each village to relief hubs. Nodes with 0 paths are tagged CUT_OFF; others use Dijkstra for shortest road travel time.", table_cell_style),
        ],
        [
            Paragraph("<b>Resource Agent</b>", table_cell_bold),
            Paragraph("<code>ResourceAgent</code><br/><code>agents/resource.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>villages</code>, <code>shelters</code>, <code>fleet</code>, <code>roads</code>, <code>feedback</code><br/><b>Out:</b> <code>assignments</code>, <code>mode</code>, <code>total_assigned</code>", table_cell_style),
            Paragraph("Dual-mode dispatch. Pass 1 creates a baseline with known flaws built specifically to test the Critic. Pass 2 executes rule-templated repairs addressing Critic feedback (rerouting S3 to S2, boat to V04, team to V02).", table_cell_style),
        ],
        [
            Paragraph("<b>Red-Team Critic</b>", table_cell_bold),
            Paragraph("<code>RedTeamCriticAgent</code><br/><code>agents/critic.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>assignments</code>, <code>shelters</code>, <code>villages</code>, <code>fleet</code><br/><b>Out:</b> <code>verdict</code>, <code>violations</code>, <code>passed_rules</code>", table_cell_style),
            Paragraph("Genuinely general auditor. Evaluates proposed plans against 6 domain safety invariants (R1-R6). Emits granular violation records with root cause descriptions and recommended actions.", table_cell_style),
        ],
        [
            Paragraph("<b>Re-planner</b>", table_cell_bold),
            Paragraph("<code>ReplannerAgent</code><br/><code>agents/replanner.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>event_type</code>, <code>current_plan</code>, <code>env_data</code><br/><b>Out:</b> <code>affected_vids</code>, <code>updated_plan</code>, <code>diff</code>, <code>verdict</code>", table_cell_style),
            Paragraph("Handles 4 operational disruptions (bridge_washout, flood_accelerated, vehicle_breakdown, shelter_full). Surgically modifies only affected villages; re-audits via Critic returning a before/after diff.", table_cell_style),
        ],
        [
            Paragraph("<b>Alert Agent</b>", table_cell_bold),
            Paragraph("<code>AlertAgent</code><br/><code>agents/alerts.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>assignments</code>, <code>villages</code>, <code>shelters</code><br/><b>Out:</b> <code>alerts</code>, <code>total_alerts</code>, <code>status</code>", table_cell_style),
            Paragraph("Alerts are template-generated from verified plan data, so there is no model to invent numbers. Emits deterministic SMS text with vehicle ID, ETA, shelter, medical status, and safe margin.", table_cell_style),
        ],
        [
            Paragraph("<b>Orchestrator</b>", table_cell_bold),
            Paragraph("<code>FloodCommandOrchestrator</code><br/><code>agents/orchestrator.py</code>", table_cell_style),
            Paragraph("<b>In:</b> <code>villages</code>, <code>shelters</code>, <code>fleet</code>, <code>roads</code>, <code>max_rounds</code><br/><b>Out:</b> <code>initial_plan</code>, <code>final_plan</code>, <code>trace</code>, <code>metrics</code>", table_cell_style),
            Paragraph("Coordinates multi-agent lifecycle: Planner -> Impact -> Resource (baseline) -> Critic -> Rework Loop (up to 3 rounds) -> Alert Agent. Compiles an audit-grade execution trace and summary KPIs.", table_cell_style),
        ],
    ]
    t_agent = Table(agent_data, colWidths=[80, 100, 122, 220])
    t_agent.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_agent)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: WORKFLOW AND DECISIONS
    # =========================================================================
    story.append(Paragraph("3. WORKFLOW AND DECISIONS", h1_style))
    story.append(Paragraph("• <b>Execution Order:</b> 1. PlannerAgent.plan() ➔ 2. ImpactAnalystAgent.analyze() ➔ 3. ResourceAgent.execute(baseline) ➔ 4. RedTeamCriticAgent.audit(baseline) ➔ 5. Rework Loop (ResourceAgent template repair ➔ Critic re-audit) ➔ 6. AlertAgent.generate_alerts() ➔ 7. calculate_plan_metrics().", bullet_style))
    story.append(Paragraph("• <b>Baseline with Known Flaws (Why it breaks rules):</b> The first pass intentionally plants 6 operational flaws: overloads shelter S3 with V07 & V11 (R1); dispatches slow bus to V04 arriving past 2h flood deadline (R2); schedules TEAM-01 simultaneously on V04 & V02 with 8 pairwise overlaps (R3); sends wheeled bus BUS-03 to cut-off V10 (R4); routes three vulnerable communities—<b>Clearwater (V07)</b>, <b>Brookside (V11)</b>, and <b>Fernbank (V10)</b>—to non-medical S3 (R5); and omits hospital village V09 entirely (R6).", bullet_style))
    story.append(Paragraph("• <b>Rework Loop Mechanics:</b> The Critic is genuinely general and audits any plan against safety invariants. The repair logic is rule-templated for the demonstration (a solver like Google OR-Tools could replace it). Max rework rounds = 3. If violations remain after 3 rounds, the orchestrator triggers an escalation protocol, sets trace status to 'warning', and flags the plan for human commander override.", bullet_style))
    story.append(Paragraph("• <b>Decision Points:</b> (1) Cut-off vs Accessible: BFS reachable nodes determine if road is open; if isolated, transport must be boat or rescue team. (2) Vehicle Choice: If cut-off ➔ amphibious boat; if acute deadline (≤2h) ➔ fast boat; else open roads ➔ mass-transit buses. (3) Shelter Choice: If vulnerable evacuees exist ➔ shelter must have medical facilities (S1/S2); if S3 reaches capacity ➔ divert to regional Central Stadium S2 (capacity 2,800).", bullet_style))
    story.append(Spacer(1, 4))

    flowchart_text = """+-----------------------------------------------------------------------------------------+
|                                    DATA STORES                                          |
|  [villages.csv]     [roads.csv]     [shelters.csv]     [resources.csv]   [config.json]  |
+--------+-----------------+----------------+-------------------+-----------------+-------+
         |                 |                |                   |                 |
         v                 v                v                   v                 v
+-----------------------------------------------------------------------------------------+
|                         FloodCommandOrchestrator Pipeline                               |
|                                                                                         |
| 1. PlannerAgent ----------------------------------------------------------------------+ |
|    Input: villages.csv | Output: Priority queue by Urgency Index                      | |
|                                                                                       | |
| 2. ImpactAnalystAgent --------------------------------------------------------------+ | |
|    Input: roads.csv, villages.csv | Output: cut_off_villages list (V10 isolated)    | | |
|                                                                                       | |
| 3. ResourceAgent (Pass 1: Baseline with Known Flaws) -------------------------------+ | |
|    Output: Baseline schedule (Contains 15 deliberate R1-R6 errors)                  | | |
|                                                                                       | |
| 4. RedTeamCriticAgent (Audit Round 1) <---------------------------------------------+ | |
|    Output: Verdict = NEEDS_REWORK (15 violations caught across R1-R6)                 | |
|                                                                                       | |
|    +---> REWORK LOOP (Max 3 rounds) <--------------------------------------------+    | |
|    |     5a. ResourceAgent (Rule-Templated Repair)                               |    | |
|    |         Action: Reroute S3 to S2, Boat to V04, Decouple Teams, Add V09      |    | |
|    |     5b. RedTeamCriticAgent (Re-Audit)                                       |    | |
|    |         If Approved (0 violations) ------------------------> BREAK LOOP     |    | |
|    +---------Else if rounds < 3 --------------------------------> REPEAT LOOP   |    | |
|              Else ----------------------------------------------> ESCALATE HUMAN |    | |
|                                                                                  |    | |
| 6. AlertAgent <------------------------------------------------------------------+    | |
|    Output: Template-generated civilian emergency SMS bulletins (Zero hallucination)   | |
|                                                                                         | |
| 7. calculate_plan_metrics ------------------------------------------------------------+ |
|    Output: Coverage % (2,505/2,505), shelter loads, average safety margins              |
+--------------------------------------------+--------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                          STREAMLIT PRESENTATION DASHBOARD                               |
|  [Tab 1: Situation]   [Tab 2: Agent Run]   [Tab 3: Final Plan]   [Tab 4: Disruption]    |
|  [Tab 5: What-If Fleet Sensitivity]        [Tab 6: Validation & Benchmark]              |
+-----------------------------------------------------------------------------------------+"""
    story.append(Preformatted(flowchart_text, mono_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 4: THE RULES
    # =========================================================================
    story.append(Paragraph("4. THE RULES (INVARIANTS AS IMPLEMENTED)", h1_style))
    rules_data = [
        [Paragraph("Rule", table_header_style), Paragraph("Invariant Title", table_header_style), Paragraph("Mathematical Implementation", table_header_style), Paragraph("Thresholds & Units", table_header_style), Paragraph("Safety Margin Usage", table_header_style)],
        [
            Paragraph("<b>R1</b>", table_cell_bold), Paragraph("Shelter Capacity", table_cell_style),
            Paragraph("sum(assigned_pop) + current_load &le; capacity", table_cell_style),
            Paragraph("Integer head count (people)", table_cell_style), Paragraph("Not used", table_cell_style)
        ],
        [
            Paragraph("<b>R2</b>", table_cell_bold), Paragraph("Evacuation Window", table_cell_style),
            Paragraph("eta_minutes + safety_margin &lt; hours_to_flood * 60", table_cell_style),
            Paragraph("Time in minutes (&lt; deadline)", table_cell_style), Paragraph("Mandatory buffer added to ETA", table_cell_style)
        ],
        [
            Paragraph("<b>R3</b>", table_cell_bold), Paragraph("Zero Double-Booking", table_cell_style),
            Paragraph("max(start_a, start_b) &ge; min(end_a, end_b)", table_cell_style),
            Paragraph("Time intervals in minutes", table_cell_style), Paragraph("Evaluates scheduled intervals", table_cell_style)
        ],
        [
            Paragraph("<b>R4</b>", table_cell_bold), Paragraph("Cut-Off Viability", table_cell_style),
            Paragraph("if village in cut_off_ids &rArr; type != 'bus'", table_cell_style),
            Paragraph("Categorical: 'boat' or 'rescue_team'", table_cell_style), Paragraph("Not used", table_cell_style)
        ],
        [
            Paragraph("<b>R5</b>", table_cell_bold), Paragraph("Medical Triage", table_cell_style),
            Paragraph("if vulnerable_count &gt; 0 &rArr; shelter_has_medical == True", table_cell_style),
            Paragraph("Count: vuln &gt; 0; Boolean: has_medical", table_cell_style), Paragraph("Not used", table_cell_style)
        ],
        [
            Paragraph("<b>R6</b>", table_cell_bold), Paragraph("Hospital Protection", table_cell_style),
            Paragraph("&forall; v where has_hospital &rArr; v.id in assigned_ids", table_cell_style),
            Paragraph("Set membership of hospital IDs", table_cell_style), Paragraph("Not used", table_cell_style)
        ],
    ]
    t_rules = Table(rules_data, colWidths=[30, 110, 180, 102, 100])
    t_rules.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_rules)
    story.append(Paragraph("<i>Rule Discrepancies Check: Exactly rules R1 to R6 are implemented. No extra rules exist, and no requested rules are missing.</i>", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 5: DATA
    # =========================================================================
    story.append(Paragraph("5. DATASETS", h1_style))
    data_summary = [
        [Paragraph("Dataset", table_header_style), Paragraph("Rows / Cols", table_header_style), Paragraph("Columns List", table_header_style), Paragraph("3 Sample Records", table_header_style)],
        [
            Paragraph("<code>villages.csv</code>", table_cell_bold), Paragraph("12 rows<br/>8 cols", table_cell_style),
            Paragraph("village_id, name, x, y, population, vulnerable_count, hours_to_flood, has_hospital", table_cell_style),
            Paragraph("V01: Elderglen (pop 120, vuln 35, 2.5h)<br/>V02: Riverbend (pop 240, vuln 60, 3.0h)<br/>V03: Highcliff (pop 90, vuln 15, 6.0h)", table_cell_style)
        ],
        [
            Paragraph("<code>roads.csv</code>", table_cell_bold), Paragraph("21 rows<br/>5 cols", table_cell_style),
            Paragraph("from_id, to_id, travel_minutes, has_bridge, status", table_cell_style),
            Paragraph("S1->V01 (20m, bridge False, open)<br/>V01->V02 (25m, bridge True, open)<br/>V10->S3 (30m, bridge True, <b>blocked</b>)", table_cell_style)
        ],
        [
            Paragraph("<code>resources.csv</code>", table_cell_bold), Paragraph("13 rows<br/>5 cols", table_cell_style),
            Paragraph("resource_id, type, capacity, base_location, available", table_cell_style),
            Paragraph("5 boats (BOAT-01 to 05, cap 35-60)<br/>4 buses (BUS-01 to 04, cap 50-60)<br/>4 teams (TEAM-01 to 04, cap 25-30)", table_cell_style)
        ],
        [
            Paragraph("<code>shelters.csv</code>", table_cell_bold), Paragraph("3 rows<br/>7 cols", table_cell_style),
            Paragraph("shelter_id, name, x, y, capacity, current_load, has_medical", table_cell_style),
            Paragraph("S1: North Hill Fort (cap 1100, load 80, Med: True)<br/>S2: Central Ridge Stadium (cap 2800, load 120, Med: True)<br/>S3: East Plateau Academy (cap 450, load 190, Med: False)", table_cell_style)
        ],
        [
            Paragraph("<code>config.json</code>", table_cell_bold), Paragraph("7 keys", table_cell_style),
            Paragraph("safety_margin_minutes (30), boat_speed_factor (1.2), bus_load_minutes (20), max_rework_rounds (3), hospital_village_id (V09), river_curve (8 coords)", table_cell_style),
            Paragraph("Defines valley simulation parameters, disclaimer text, river spline coordinates, and safety constraints.", table_cell_style)
        ],
    ]
    t_data = Table(data_summary, colWidths=[80, 55, 175, 212])
    t_data.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_data)
    story.append(Paragraph("• <b>Planted Data Problems:</b> (1) In <code>roads.csv</code>, roads V10->S3 and V10->V07 are both set to <code>status='blocked'</code>, completely isolating Fernbank (V10) from the road network. (2) In <code>agents/resource.py</code>, baseline assignments plant 15 invariant violations across R1-R6.<br/>• <b>Data Generation:</b> <code>data/generate_data.py</code> sets <code>random.seed(42)</code> and uses deterministic dictionaries for reproducible benchmarking.", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 6: UI: WHAT ACTUALLY EXISTS
    # =========================================================================
    story.append(Paragraph("6. UI: WHAT ACTUALLY EXISTS", h1_style))
    story.append(Paragraph("• <b>Sidebar Controls (Order):</b> 1. Brand Header & Disclaimer ➔ 2. Selectbox: <code>Select Scenario Preset</code> ('Normal monsoon', 'Dam release', 'Cloudburst') ➔ 3. Slider: <code>Safety Margin Buffer</code> (15 to 60m, step 5) ➔ 4. Primary Button: <code>Generate Response Plan</code> ➔ 5. Secondary Button: <code>Run Full Demo Workflow</code> ➔ 6. Utility Button: <code>Reset Scenario Data</code> ➔ 7. Expander: <code>Active Agent Roster</code> ➔ 8. Expander: <code>How It Works</code> ➔ 9. Download Button: <code>Download PDF Report</code>.", bullet_style))
    story.append(Paragraph("• <b>Main Tabs (Order):</b> [Tab 1: Situation] ➔ [Tab 2: Agent Run] ➔ [Tab 3: Final Plan] ➔ [Tab 4: Disruption] ➔ [Tab 5: What-If] ➔ [Tab 6: Validation].", bullet_style))

    ui_data = [
        [Paragraph("Requested Feature", table_header_style), Paragraph("Status", table_header_style), Paragraph("Exact UI Location in Dashboard", table_header_style)],
        [Paragraph("Why-this explanations", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 3 (Final Plan): Collapsible expanders under each village assignment.", table_cell_style)],
        [Paragraph("Critic on/off comparison", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 3 (Final Plan): Toggle 'Show plan without Critic' (side-by-side view).", table_cell_style)],
        [Paragraph("Trace download (JSON)", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 2 (Agent Run) & Tab 3 (Final Plan): 'Download Agent Trace (JSON)' buttons.", table_cell_style)],
        [Paragraph("Situation report (.txt & card)", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 1 (Situation): 'Generate situation report' button + download button.", table_cell_style)],
        [Paragraph("Scenario presets", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Sidebar dropdown: 'Normal monsoon', 'Dam release', 'Cloudburst'.", table_cell_style)],
        [Paragraph("What-if sliders", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 5 (What-If): Sliders for boats (1-5), buses (1-4), and rescue teams (1-4).", table_cell_style)],
        [Paragraph("Assignment arrows on map", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 1 (Situation): Toggle 'Show evacuation assignments on map'.", table_cell_style)],
        [Paragraph("Empty states", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tabs 2, 3, 4, 5: Friendly st.info('No plan yet...') prior to execution.", table_cell_style)],
        [Paragraph("Guided progress steps", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Under header: 4-step progress bar (Review, Generate, Review Alerts, Disruption).", table_cell_style)],
        [Paragraph("CSV download", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 3 (Final Plan): 'Download Final Plan (CSV)' button.", table_cell_style)],
        [Paragraph("JSON trace download", table_cell_bold), Paragraph("IMPLEMENTED", table_cell_bold), Paragraph("Tab 2 (Agent Run) & Tab 3 (Final Plan): 'Download Agent Trace (JSON)'.", table_cell_style)],
    ]
    t_ui = Table(ui_data, colWidths=[140, 95, 287])
    t_ui.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_ui)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 7: RESULTS
    # =========================================================================
    story.append(Paragraph("7. RESULTS (RUN WITH DEFAULT SETTINGS)", h1_style))
    story.append(Paragraph("• <b>Violations Found in Flawed Baseline:</b> <b>15 violations total</b> (R1: 1, R2: 1, R3: 8, R4: 1, R5: 3 on <b>V07, V11, and V10</b>, R6: 1).<br/>• <b>Violations Fixed:</b> 15 fixed (0 remaining). | <b>Rounds Needed:</b> 1 rework iteration. | <b>Human Escalations:</b> 0.<br/>• <b>People Covered:</b> 2,505 out of 2,505 (100% across all 12 communities).<br/>• <b>Runtime:</b> <b>1.24 s</b> displayed on dashboard KPI card (pure Python orchestration executes in ~1.3 ms; Streamlit UI rendering takes about a second).", bullet_style))
    story.append(Spacer(1, 4))

    disrupt_data = [
        [Paragraph("Disruption Event", table_header_style), Paragraph("Affected Villages", table_header_style), Paragraph("Critic Verdict", table_header_style), Paragraph("Violations", table_header_style), Paragraph("Operational Actions & Re-Planning", table_header_style)],
        [
            Paragraph("<b>Bridge Washout</b>", table_cell_bold), Paragraph("V02 (Riverbend)", table_cell_style),
            Paragraph("APPROVED", table_cell_bold), Paragraph("0", table_cell_style),
            Paragraph("Arterial bridge V01-V02 blocked. Replaced overland TEAM-02 with river craft BOAT-04 (Slot 60-110m, ETA 25m, margin 65m).", table_cell_style)
        ],
        [
            Paragraph("<b>Accelerated Flood</b>", table_cell_bold), Paragraph("All 12 villages", table_cell_style),
            Paragraph("NEEDS_REWORK", table_cell_bold), Paragraph("2 (R2)", table_cell_style),
            Paragraph("Flood crest advanced 2h valley-wide. Triggers 2 R2 violations: V07 Clearwater (-7m margin) and V10 Fernbank (-2m margin). <i>(Honest limitation case, skip in live demo)</i>.", table_cell_style)
        ],
        [
            Paragraph("<b>Vehicle Breakdown</b>", table_cell_bold), Paragraph("V04 (Millhaven)", table_cell_style),
            Paragraph("APPROVED", table_cell_bold), Paragraph("0", table_cell_style),
            Paragraph("Primary craft BOAT-01 motor failed. Hot-swapped to standby river craft BOAT-04 (Slot 50-95m, ETA 25m, margin 65m).", table_cell_style)
        ],
        [
            Paragraph("<b>Shelter Full</b>", table_cell_bold), Paragraph("5 villages (V04, V02, V10, V01, V03)", table_cell_style),
            Paragraph("APPROVED", table_cell_bold), Paragraph("0", table_cell_style),
            Paragraph("S1 reached capacity from walk-ins. All 5 assigned villages safely rerouted to Central Ridge Stadium S2 (capacity 2,800).", table_cell_style)
        ],
    ]
    t_disrupt = Table(disrupt_data, colWidths=[90, 85, 75, 45, 227])
    t_disrupt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_disrupt)
    story.append(Spacer(1, 4))
    story.append(Paragraph("• <b>What-If Result (2 Boats, 2 Buses):</b> Critic verdict = <code>NEEDS_REWORK</code> with <b>9 R3 double-booking violations</b>. 12/12 villages covered (0 stranded) because the algorithm forced missions onto busy vehicles, demonstrating the Critic's sensitivity.<br/>• <b>Safety Margins (15, 30, 60m):</b> All three produce identical violation counts (15 initial, 0 final) because baseline V04 bus ETA (105m) violates 120m deadline at all margins &ge; 15m, while repaired boat ETA (25m) satisfies margins &le; 60m. <i>Presenter Note: Do not demo this slider live as it causes no visible visual change.</i><br/>• <b>Pytest Test Suite:</b> 7 tests collected, <b>7 passed in 0.05s</b>. (Audits: valid plan approval, R1 capacity, R2 flood window, R3 double-booking, R4 cut-off vehicle, R5 medical shelter, R6 hospital village coverage).", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 8: LIMITATIONS AND HONESTY
    # =========================================================================
    story.append(Paragraph("8. LIMITATIONS AND HONESTY", h1_style))
    story.append(Paragraph("• <b>Critic vs. Repair Asymmetry:</b> The Critic is genuinely general and audits any plan against safety invariants. The repair logic is rule-templated for the demonstration scenario. In production, a general solver like Google OR-Tools, Z3, or PuLP could replace the repair step without altering the Critic, Orchestrator, or Alert interfaces.", bullet_style))
    story.append(Paragraph("• <b>Physical Impossibility & Escalation:</b> In the Accelerated Flood scenario, two villages (Clearwater V07 with -7m margin and Fernbank V10 with -2m margin) physically cannot evacuate before water arrives. The system flags them for human commander review rather than fabricating an unsafe plan.", bullet_style))
    story.append(Paragraph("• <b>Simplified Models:</b> Evacuation windows are modeled as static scalar intervals rather than continuous dynamic simulations. Road travel uses fixed edge weights; river travel uses a Euclidean factor (1.2 * distance) rather than hydrodynamic flow models. The valley uses a schematic 0-100 Cartesian grid rather than real GIS shapefiles.", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 9: DEMO READINESS
    # =========================================================================
    story.append(Paragraph("9. DEMO READINESS", h1_style))
    story.append(Paragraph("• <b>Shortest 4-Minute Demo Click Path:</b><br/>"
                           "1. <b>(0:00-0:45) Tab 1 (Situation):</b> Show valley map, 2 blocked bridges isolating Fernbank (V10) in red. Click 'Generate situation report' to show the briefing card.<br/>"
                           "2. <b>(0:45-1:45) Sidebar & Tab 2 (Agent Run):</b> Click 'Generate Response Plan'. Point out '1.24 s' runtime KPI. Switch to Tab 2 to show 'Violations: 15 ➔ 0' convergence, red Critic audit rejection card, green repair card, and trace.<br/>"
                           "3. <b>(1:45-2:45) Tab 3 (Final Plan):</b> Toggle 'Show plan without Critic' to show side-by-side comparison. Turn toggle off; expand 'Why this?' card on V10 to show data-derived justifications. Point out template-generated civilian SMS.<br/>"
                           "4. <b>(2:45-4:00) Tab 4 (Disruption) & Tab 5 (What-If):</b> Click 'Apply Bridge Failure' (Bridge Washout ONLY; skip Accelerated Flood). Show surgical diff for V02. Switch to Tab 5, set Boats=2, Buses=2, click 'Run What-If Analysis' to show 9 R3 violations caught live.", bullet_style))
    story.append(Paragraph("• <b>Offline Verification:</b> <b>100% Offline Capable.</b> Codebase scan confirms zero outbound network calls, zero socket connections, and zero LLM API endpoints. (The only external link is an optional Google Font stylesheet in CSS that gracefully falls back to system fonts).", bullet_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 10: SCREENSHOTS
    # =========================================================================
    story.append(Paragraph("10. SCREENSHOTS FOR SLIDES", h1_style))
    screen_data = [
        [Paragraph("Slide / Screen Purpose", table_header_style), Paragraph("Tab Name", table_header_style), Paragraph("Exact Setup State Before Capturing", table_header_style)],
        [Paragraph("1. Situation Overview & Map", table_cell_bold), Paragraph("Situation", table_cell_style), Paragraph("Run plan; toggle 'Show evacuation assignments on map' ON; click 'Generate situation report'.", table_cell_style)],
        [Paragraph("2. Critic Rejection & Trace", table_cell_bold), Paragraph("Agent Run", table_cell_style), Paragraph("Run plan; scroll to top. Captures 'Violations: 15 ➔ 0' banner, red Critic rejection box, and timeline cards.", table_cell_style)],
        [Paragraph("3. Flawed vs Verified Comparison", table_cell_bold), Paragraph("Final Plan", table_cell_style), Paragraph("Run plan; toggle 'Show plan without Critic' ON. Captures side-by-side table with R1-R6 violation badges.", table_cell_style)],
        [Paragraph("4. Decision Rationale ('Why this?')", table_cell_bold), Paragraph("Final Plan", table_cell_style), Paragraph("Run plan; toggle off comparison; expand V10 (Fernbank) and V04 (Millhaven) rationale cards.", table_cell_style)],
        [Paragraph("5. Dynamic Disruption Diff", table_cell_bold), Paragraph("Disruption", table_cell_style), Paragraph("Click 'Apply Bridge Failure'. Captures surgical diff table for V02 and before/after comparative maps.", table_cell_style)],
        [Paragraph("6. Benchmark & Rule Compliance", table_cell_bold), Paragraph("Validation", table_cell_style), Paragraph("Switch to Tab 6. Captures benchmark verification table and grouped bar chart (0% naive vs 100% verified).", table_cell_style)],
    ]
    t_screen = Table(screen_data, colWidths=[140, 75, 307])
    t_screen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2236")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_screen)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 11: VIVA QUESTIONS & DEFENSE ANSWERS
    # =========================================================================
    story.append(Paragraph("11. VIVA QUESTIONS & DEFENSE ANSWERS", h1_style))

    vivas = [
        ("Q1: Where is the AI in this project? If there is no LLM, how is this an 'Agentic AI' system?",
         "FloodCommand uses symbolic, rule-based autonomous agents rather than generative LLMs. Generative LLMs hallucinate numbers and cannot guarantee hard safety invariants during disaster evacuations. Each agent possesses specialized autonomy, explicit state interfaces, and distinct operational roles. The agentic intelligence resides in the adversarial closed-loop orchestration: autonomous plan generation, automated critical auditing against domain invariants, and self-healing rework loops without human prompting."),

        ("Q2: Why use a multi-agent architecture instead of writing a single procedural script?",
         "A monolithic script tightly couples optimization with safety auditing, making it prone to shared blind spots. Decomposing the system enforces separation of concerns and adversarial tension: the Resource Agent acts as an optimizing proposer while the Red-Team Critic acts as an independent auditor. Modularity also enables surgical dynamic re-planning: when a bridge collapses, the Re-planner isolates only the affected node and re-audits it, rather than re-running a global pipeline."),

        ("Q3: How does the Resource Agent work, and why not use an exact solver like OR-Tools?",
         "The initial pass produces a baseline schedule with known flaws, built specifically to test the Critic's invariant checks. The Critic is genuinely general and can audit any plan. The current repair step is rule-templated for the demonstration. In production, a general-purpose mathematical solver like Google OR-Tools or Z3 could directly replace the repair logic without modifying the Critic, Orchestrator, or Alert interfaces."),

        ("Q4: What happens when two rules conflict (e.g. cut-off village with vulnerable people, but boat only reaches non-medical shelter)?",
         "The Critic evaluates R1 to R6 independently. If two rules conflict and no valid assignment satisfies both, the Critic rejects the plan on both rule IDs (verdict = NEEDS_REWORK). When rework reaches max rounds (3) without achieving zero violations, the orchestrator triggers an escalation protocol, logs a warning in the trace, and marks the plan for human commander override. The system prioritizes human intervention over deploying an unsafe plan."),

        ("Q5: How does the system guarantee accuracy in emergency civilian alerts?",
         "Alerts are template-generated directly from the verified plan data, so there is no model to invent numbers. AlertAgent injects the exact assigned resource ID, calculated vehicle ETA, shelter name, medical capability label, and flood arrival deadline into a standardized SMS template."),

        ("Q6: How is road cut-off reachability calculated? Does it support dynamic road changes?",
         "ImpactAnalystAgent builds an undirected adjacency list from roads.csv filtering out blocked edges. It executes Breadth-First Search (BFS) starting from each village. If BFS cannot discover a path to any designated shelter or the regional hospital hub, the node is tagged CUT_OFF. It dynamically supports real-time changes: in bridge_washout, the bridge edge between V01 and V02 is set to 'blocked' in memory, and graph reachability is immediately re-evaluated."),

        ("Q7: Why did What-If with 2 boats and 2 buses fail Critic validation if all villages were covered?",
         "Because the fleet was insufficient to service 12 villages across discrete time windows without asset re-use. The What-If simulation reallocated excess missions to the 2 available boats and 2 buses, forcing multiple evacuation missions into overlapping time windows. The Critic audited the schedule against Rule R3 and flagged 9 pairwise temporal conflicts. This proves that the Critic prioritizes physical operational feasibility over nominal population coverage."),

        ("Q8: How does the safety margin buffer work, and why did the initial plan fail R2 even with a 15-minute margin?",
         "The safety margin is a mandatory buffer added to vehicle ETA to ensure complete evacuation prior to water arrival: ETA + Margin < Deadline. In the baseline, village V04 has a flood deadline of 2.0h (120m) and was assigned a bus with ETA 105m. Even at 15m margin, 105 + 15 = 120m, which violates the strict inequality (>= 120m), triggering an R2 violation across 15m, 30m, and 60m margins. The rework loop repaired this by dispatching boat BOAT-01 with ETA 25m, establishing a safe 65-minute buffer."),
    ]

    for q, a in vivas:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(f"<b>Answer:</b> {a}", body_style))
        story.append(Spacer(1, 2))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report at: {output_path}")


if __name__ == "__main__":
    out_file = Path("c:/Users/Akshita/Documents/FAAI PROJECT/Architectural and Operational Fact Report.pdf")
    create_fact_report_pdf(out_file)
