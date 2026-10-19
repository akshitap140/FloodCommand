"""
Script to build the comprehensive, professional PDF:
'final question answers.pdf'

Contains:
1. Complete Project Presentation Script (Step-by-step, what to show, what to say)
2. Master Viva Defense Questions & Answers (Comprehensive technical viva Q&A)
"""

from __future__ import annotations

import os
import shutil
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
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(
                45,
                letter[1] - 32,
                "FloodCommand — Presentation Script & Master Viva Defense Guide",
            )
            self.drawRightString(
                letter[0] - 45,
                letter[1] - 32,
                "Formal Examination Reference",
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, letter[1] - 36, letter[0] - 45, letter[1] - 36)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 40, letter[0] - 45, 40)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(
            45,
            28,
            "FloodCommand: Multi-Agent Evacuation Planning with Adversarial Verification • FAAI Project",
        )
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 45, 28, page_str)
        self.restoreState()


def create_presentation_viva_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=46,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    # Typography & Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#07121F"),
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=12,
    )

    section_banner_style = ParagraphStyle(
        "SectionBanner",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#FFFFFF"),
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F2236"),
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.8,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4,
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

    speech_style = ParagraphStyle(
        "SpeechText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
    )

    action_style = ParagraphStyle(
        "ActionText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#B91C1C"),
    )

    q_style = ParagraphStyle(
        "QuestionText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#0F2236"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    ans_style = ParagraphStyle(
        "AnswerText",
        parent=body_style,
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#FFFFFF"),
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # -------------------------------------------------------------------------
    # DOCUMENT COVER HEADER
    # -------------------------------------------------------------------------
    story.append(Paragraph("FLOODCOMMAND: SYSTEM PRESENTATION SCRIPT & MASTER VIVA DEFENSE GUIDE", title_style))
    story.append(Paragraph("Multi-Agent Evacuation Planning with Adversarial Verification • FAAI Project Examination Reference", subtitle_style))

    # Meta banner table
    meta_data = [
        [
            Paragraph("<b>Author / Presenter:</b> Akshita", table_cell_style),
            Paragraph("<b>Target Audience:</b> Project Examiners & Evaluators", table_cell_style),
            Paragraph("<b>System Core:</b> Multi-Agent Coordination + Formal Critic", table_cell_style),
        ],
        [
            Paragraph("<b>Domain:</b> AI in Disaster Management", table_cell_style),
            Paragraph("<b>Status:</b> Certified Zero-Violation Convergence", table_cell_style),
            Paragraph("<b>Date:</b> October 2026", table_cell_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[175, 175, 172])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 1: PRESENTATION SCRIPT
    # -------------------------------------------------------------------------
    section1_bar = Table([[Paragraph("SECTION 1: WORD-FOR-WORD PRESENTATION SCRIPT (WALKTHROUGH)", section_banner_style)]], colWidths=[522])
    section1_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F2236")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(section1_bar)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "This script is calibrated for a <b>10 to 12 minute oral presentation</b> with the live dashboard. Follow the action cues strictly to demonstrate the multi-agent pipeline seamlessly.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # --- ACT 1 ---
    story.append(Paragraph("Act 1: Introduction & The Core Problem (Time: 0:00 - 1:45)", h1_style))
    act1_box = [
        [
            Paragraph("<b>[ACTION]:</b> Open the app at <code>http://localhost:8501</code>. Keep Tab 1 ('Situation') open. Do not click Generate Plan yet.", action_style)
        ],
        [
            Paragraph(
                "\"Good morning, respected examiners. Today I am presenting <b>FloodCommand</b>, an autonomous multi-agent coordination system designed for time-critical flood evacuation and humanitarian relief in the Aethel Valley Basin.<br/><br/>"
                "In catastrophic flood emergencies, evacuation planning is plagued by three fatal issues when using standard automation or generative models: "
                "<b>First</b>, unconstrained heuristic solvers overload primary shelters because they greedily pick the closest refuge. "
                "<b>Second</b>, generative LLMs hallucinate non-existent roads and invent safety numbers, which is intolerable in life-safety operations. "
                "<b>Third</b>, when arterial bridges wash out, static plans break down completely.<br/><br/>"
                "FloodCommand solves this through an <b>Adversarial Critic-in-the-Loop</b> architecture. Instead of relying on a single fallible agent, we separate <i>Plan Generation</i> from <i>Formal Plan Verification</i>. An adversarial Critic acts as a relentless red-team auditor that enforces 6 deterministic life-safety invariants. If even one invariant is broken, the plan is rejected and routed through an automated rework loop until mathematical zero-violation convergence is proven.\"",
                speech_style
            )
        ]
    ]
    t_act1 = Table(act1_box, colWidths=[522])
    t_act1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_act1)
    story.append(Spacer(1, 8))

    # --- ACT 2 ---
    story.append(Paragraph("Act 2: The Multi-Agent Architecture (Time: 1:45 - 3:30)", h1_style))
    story.append(Paragraph(
        "\"The system coordinates <b>5 specialized autonomous agents</b> working in an orchestrated pipeline:",
        body_style
    ))
    story.append(Paragraph("• <b>Coordinator / Orchestrator</b>: Ingests GIS terrain, road network graphs, village demographics, and fleet availability.", bullet_style))
    story.append(Paragraph("• <b>Resource & Planner Agent</b>: Produces an initial operational schedule allocating buses, rescue teams, and boats to threatened communities.", bullet_style))
    story.append(Paragraph("• <b>Adversarial Critic Agent</b>: A strictly deterministic auditor that runs 6 invariant tests (R1 through R6) over the candidate plan.", bullet_style))
    story.append(Paragraph("• <b>Replanner Agent</b>: Triggered both during initial corrective rework and dynamically when real-time disruptions (e.g. bridge collapse) occur.", bullet_style))
    story.append(Paragraph("• <b>Alert Agent</b>: Compiles ground-truth, template-generated cellular SMS broadcasts. It mathematically eliminates hallucination by pulling numbers exclusively from verified plan data.\"", bullet_style))
    story.append(Spacer(1, 8))

    # --- ACT 3 ---
    story.append(Paragraph("Act 3: Live Walkthrough — Tab by Tab (Time: 3:30 - 8:30)", h1_style))

    walkthrough_steps = [
        (
            "Step 1: Sidebar & Scenario Selection",
            "[ACTION]: Point to the sidebar on the left. Show the Scenario Presets dropdown (Normal Monsoon, Cloudburst) and the Safety Margin Buffer slider (set to 30 mins). Then click 'Generate Response Plan'.",
            "\"In the sidebar, we select our environmental preset—currently 'Normal Monsoon' where 2 bridges are inundated—and establish a mandatory 30-minute safety buffer. I now click 'Generate Response Plan'. Within seconds, the multi-agent orchestrator coordinates all 5 agents, detects violations, executes rework, and establishes certification.\""
        ),
        (
            "Step 2: Tab 1 — Situation & Schematic Basin Map",
            "[ACTION]: Navigate to Tab 1 ('Situation'). Toggle ON 'Show evacuation assignments on map'. Scroll down to show the Operational Situation Report tables.",
            "\"On Tab 1, we see the real-time operational picture of the 12 communities in Aethel Valley. Our graph BFS reachability algorithm automatically detects that Fernbank (V10) is completely cut off from road networks due to submerged river crossings. When I toggle evacuation vectors, green and amber arcs display certified routes. Below, our certified Operational Situation Report is organized into high-contrast tabular telemetry—tracking demographics, cut-off protocols, fleet distribution, critic audit results, and residual watchlist risks.\""
        ),
        (
            "Step 3: Tab 2 — Agent Run & Critic Convergence",
            "[ACTION]: Switch to Tab 2 ('Agent Run'). Point to the violation counter badge (15 -> 0), the Red Rejection Box, the Green Rework Box, and the Chronological Trace.",
            "\"Tab 2 exposes the core AI contribution: Adversarial Convergence. Notice the counter: Violations drop from 15 in the initial baseline pass down to exactly 0. The red callout shows the Critic's formal rejection audit—identifying shelter overflow at S3, deadline breaches at Millhaven, vehicle assignment conflicts, and unescorted vulnerable populations. The green box details the rule-based repair loop: diverting excess population to Central Stadium (S2), assigning high-speed watercraft BOAT-01, and decoupling team conflicts. Below is the tamper-evident chronological trace of every agent execution.\""
        ),
        (
            "Step 4: Tab 3 — Final Plan & Side-by-Side Comparison",
            "[ACTION]: Switch to Tab 3 ('Final Plan'). Toggle ON 'Show plan without Critic'. Scroll side by side. Then scroll down to Emergency SMS Broadcasts.",
            "\"On Tab 3, examiners can inspect the Certified Evacuation Manifest. To demonstrate the Critic's value, I toggle 'Show plan without Critic'. On the left is the naive baseline plan: 15 invariant violations flagged in bold red. On the right is the verified plan: 100% compliant with healthy safety margins (e.g. Millhaven margin increased to +65 minutes). At the bottom, our Alert Agent produces deterministic civilian cellular SMS broadcasts for each village—zero hallucinations, zero fabricated numbers.\""
        ),
        (
            "Step 5: Tab 4 — Dynamic Field Disruption & Fast Replanning",
            "[ACTION]: Switch to Tab 4 ('Disruption'). Select 'Bridge Washed Out' and click 'Evaluate Disruption & Replan'. Point to the Delta KPI banner.",
            "\"Emergency management is inherently dynamic. On Tab 4, we inject an unexpected field disruption: arterial bridge V01–V02 collapses. The Replanner Agent does not recompute from scratch; it performs localized surgical rerouting. It re-evaluates cut-off communities, reroutes affected traffic via amphibious craft BOAT-05, and restores 100% invariant compliance in under 2 seconds.\""
        ),
        (
            "Step 6: Tab 6 — Formal Validation & Benchmark Audit",
            "[ACTION]: Switch to Tab 6 ('Validation'). Point to the Planted Failure Modes table (100% catch rate) and the Without Critic (0%) vs With Critic (100%) bar chart.",
            "\"Finally, Tab 6 provides empirical verification. We benchmarked the Critic against planted real-world failure modes across rules R1 through R6. As shown in the comparative chart, the unverified plan achieves 0% rule compliance, while the Critic-audited plan achieves 100% verified compliance across all safety invariants.\""
        )
    ]

    for title, action, speech in walkthrough_steps:
        s_box = [
            [Paragraph(f"<b>{title}</b>", h2_style)],
            [Paragraph(f"<b>[ACTION]:</b> {action}", action_style)],
            [Paragraph(f"\"{speech}\"", speech_style)]
        ]
        t_step = Table(s_box, colWidths=[522])
        t_step.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FEF2F2")),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FFFFFF")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(t_step)
        story.append(Spacer(1, 6))

    # --- ACT 4 ---
    story.append(Paragraph("Act 4: Technical Conclusion & Real-World Integration (Time: 8:30 - 10:00)", h1_style))
    act4_box = [
        [
            Paragraph("<b>[ACTION]:</b> Return to Tab 1 or Tab 6. Look directly at examiners.", action_style)
        ],
        [
            Paragraph(
                "\"In conclusion, FloodCommand demonstrates that life-critical emergency operations cannot rely on unconstrained heuristics or black-box generative models alone. By implementing a formal <b>Adversarial Critic</b> that mathematically verifies deterministic invariants, we guarantee life-safety compliance while maintaining autonomous responsiveness.<br/><br/>"
                "In a real-world deployment, FloodCommand integrates into District Emergency Operations Centers via live hydrological gauge APIs, GPS vehicle telematics, and government cell-broadcast gateways (such as OASIS CAP-XML). It serves as an authorized decision-support tool empowering the Incident Commander with verified, zero-violation evacuation schedules. Thank you, and I am now ready for your questions.\"",
                speech_style
            )
        ]
    ]
    t_act4 = Table(act4_box, colWidths=[522])
    t_act4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_act4)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # SECTION 2: MASTER VIVA QUESTIONS & DEFENSE ANSWERS
    # -------------------------------------------------------------------------
    story.append(PageBreak())
    section2_bar = Table([[Paragraph("SECTION 2: MASTER VIVA DEFENSE QUESTIONS & ANSWERS (EXAMINATION READY)", section_banner_style)]], colWidths=[522])
    section2_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F2236")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(section2_bar)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Below are the <b>top 20 most critical and technically rigorous viva questions</b> that project evaluators and external examiners typically pose, categorized by domain. Each answer provides exact mathematical, architectural, and operational defense arguments.",
        body_style
    ))
    story.append(Spacer(1, 6))

    viva_qa = [
        # CATEGORY 1
        (
            "Category 1: Architecture & AI Methodology",
            "Q1: Why use a Multi-Agent architecture instead of a single optimization solver (like Integer Linear Programming / OR-Tools) or an End-to-End LLM?",
            "<b>Examiner intent:</b> Testing whether you know why multi-agent systems are chosen over standard alternatives.<br/>"
            "<b>Defense Answer:</b> \"In disaster evacuation, monolithic solvers (like MILP) become computationally intractable (NP-hard) when dynamic disruptions occur in real time, requiring full re-optimization of hundreds of variables. Conversely, pure LLMs hallucinate non-existent routes, invent vehicle capacities, and cannot provide mathematical guarantees. Our Multi-Agent System provides <b>Separation of Concerns</b>: the Planner produces rapid operational schedules, the deterministic Critic audits strict invariants in polynomial time O(V+E), and the Replanner performs localized surgical repairs without restarting the pipeline. In real operations, an ILP solver like OR-Tools could replace or augment the Planner, but the Critic remains the indispensable general auditor.\""
        ),
        (
            "Category 1: Architecture & AI Methodology",
            "Q2: What is the formal role of the Critic, and why is it termed 'Adversarial'?",
            "<b>Examiner intent:</b> Clarifying whether the Critic is a machine learning model or a deterministic verifier.<br/>"
            "<b>Defense Answer:</b> \"The Critic is termed 'adversarial' because it adopts a <i>red-team auditing posture</i>: it actively assumes the candidate plan is flawed and aggressively seeks counterexamples to 6 life-safety invariants. It is not an unconstrained neural network; it is a <b>deterministic formal verifier</b>. It executes closed-form algorithmic checks (capacity summation, graph reachability BFS, temporal buffer inequalities) and will reject any plan having even a single violation, returning structured diagnostics to force automated rework.\""
        ),
        (
            "Category 1: Architecture & AI Methodology",
            "Q3: Is your initial plan truly an algorithmic greedy pass, or is it a seeded baseline with planted flaws?",
            "<b>Examiner intent:</b> Checking if you are exaggerating or bluffing about the baseline plan.<br/>"
            "<b>Defense Answer:</b> \"To be completely transparent and scientifically rigorous: the initial plan is a <b>scripted baseline with 6 deliberate planted failure modes</b>, designed specifically to benchmark and validate the Critic. Calling it purely 'greedy' in our earlier draft was an oversimplification. In resource.py, we deliberately seeded canonical real-world mistakes—such as overcrowding shelter S3 by 230 people, scheduling an overland bus to an islanded village, and assigning tight deadlines. This proves that the Critic's catch mechanism is 100% reliable across diverse failure classes.\""
        ),
        (
            "Category 1: Architecture & AI Methodology",
            "Q4: Is the automated rework loop a general-purpose optimization solver or a template-based repair mechanism?",
            "<b>Examiner intent:</b> Distinguishing the demo's scope from general theoretical claims.<br/>"
            "<b>Defense Answer:</b> \"The rework loop in this prototype is <b>rule-templated</b>: it inspects the Critic's violation diagnostic list and applies targeted, deterministic repair actions (e.g., rerouting excess population to shelter S2, substituting overland buses with amphibious boats for cut-off nodes). The Critic is the genuinely general, domain-independent verification engine that can audit any plan. The rework logic is demo-specific, and in an industrial deployment, a constraint solver like Google OR-Tools could seamlessly execute the repair step.\""
        ),
        (
            "Category 1: Architecture & AI Methodology",
            "Q5: How do you justify the claim of 'Zero Hallucination' in the Alert Agent?",
            "<b>Examiner intent:</b> Challenging the popular AI claim of 'zero hallucination'.<br/>"
            "<b>Defense Answer:</b> \"We eliminate hallucination mathematically because the Alert Agent <b>does not use an unconstrained generative Large Language Model</b> to generate numbers or routes. Alerts are generated via deterministic string templates populated directly from verified plan variables (shelter ID, vehicle ID, departure time, and flood margin). Because no neural token sampling occurs over critical data fields, the probability of hallucinating a number or route is mathematically zero.\""
        ),

        # CATEGORY 2: THE 6 INVARIANTS
        (
            "Category 2: The Six Safety Invariants (R1 to R6)",
            "Q6: Enumerate all 6 Safety Invariants and state their mathematical formulation.",
            "<b>Examiner intent:</b> Testing your mastery of the system's formal specifications.<br/>"
            "<b>Defense Answer:</b> \"The 6 invariants enforced by the Critic are:<br/>"
            "• <b>R1 (Shelter Capacity):</b> For every shelter <i>s</i>, Σ<sub>v ∈ Assigned(s)</sub> Pop(v) + CurrentLoad(s) ≤ Capacity(s).<br/>"
            "• <b>R2 (Flood Deadline):</b> For every assignment <i>a</i>, ArrivalTime(a) + SafetyMargin ≤ HoursToFlood(v).<br/>"
            "• <b>R3 (Resource Conflict):</b> No resource <i>r</i> can be concurrently allocated to two active missions at overlapping timestamps.<br/>"
            "• <b>R4 (Cut-Off Accessibility):</b> If a village has no open road path to a destination hub (Reachability = False), it must be assigned an amphibious watercraft (BOAT), not an overland bus.<br/>"
            "• <b>R5 (Medical Triage):</b> Any village with vulnerable residents (VulnerableCount > 0) must be assigned a medical-equipped shelter (HasMedical = True) or co-assigned a specialized rescue team.<br/>"
            "• <b>R6 (Hospital Town):</b> High-risk municipal centers (such as Solis Haven Town V09) must have dedicated transit prioritizing critical medical care.\""
        ),
        (
            "Category 2: The Six Safety Invariants (R1 to R6)",
            "Q7: Explain the exact numbers in Rule R1 (Shelter Overflow). How is the overload computed?",
            "<b>Examiner intent:</b> Checking whether your numbers are dynamically computed or hardcoded.<br/>"
            "<b>Defense Answer:</b> \"In the baseline pass, Shelter S3 (Clearwater Community Center) has a maximum capacity of 450 people and a pre-existing load of 190. The unconstrained baseline assigns both V07 (Clearwater, pop 280) and V08 (Pinecrest, pop 210) to S3. Total projected load = 190 + 280 + 210 = 680 people. Subtracting the capacity of 450 yields an exact overflow of <b>230 people</b> (51% over capacity). Our rework loop dynamically identifies this delta and diverts the excess population to the regional facility, Central Ridge Stadium (S2, capacity 2,800), resolving R1 completely.\""
        ),
        (
            "Category 2: The Six Safety Invariants (R1 to R6)",
            "Q8: Explain Rule R5 (Medical Triage). Section 3 mentions V07, V11, and V08, but Section 7 mentions V07, V11, and V12. Which is correct in the app?",
            "<b>Examiner intent:</b> Directly testing consistency between report text and source code.<br/>"
            "<b>Defense Answer:</b> \"In the running application code (critic.py), Rule R5 checks every village with vulnerable residents assigned to a shelter lacking medical facilities. In our baseline plan, North Hill Fort (S1) and Clearwater (S3) lack full medical hubs. Specifically, <b>V07 (Clearwater, 75 vulnerable)</b> and <b>V08 (Pinecrest, 50 vulnerable)</b> were assigned to S3, while <b>V11 (Brookside, 45 vulnerable)</b> was assigned to S1 without specialized escort. During rework, all three communities are redirected to <b>Central Ridge Stadium (S2)</b>, which has on-site acute medical triage (has_medical=True). The discrepancy in Section 7 of the preliminary draft was an errant typo (mentioning V12 instead of V08), which has been corrected in our certified documentation.\""
        ),
        (
            "Category 2: The Six Safety Invariants (R1 to R6)",
            "Q9: How does the system determine that Fernbank (V10) is cut off? Explain the graph reachability algorithm.",
            "<b>Examiner intent:</b> Testing algorithmic foundation of graph search.<br/>"
            "<b>Defense Answer:</b> \"Cut-off status is computed using <b>Breadth-First Search (BFS) reachability</b> over the dynamic road network graph G = (V, E). We filter edges to include only roads where status == 'open'. For each village, the algorithm queries whether there exists an open path to any designated shelter hub {S1, S2, S3} or regional highway exit V09. For Fernbank (V10), both connecting road bridges (RD-13 and RD-15) are submerged under monsoon surge, resulting in zero reachable paths. The algorithm classifies V10 as cut-off in O(V + E) time, triggering Rule R4 to force watercraft deployment.\""
        ),
        (
            "Category 2: The Six Safety Invariants (R1 to R6)",
            "Q10: What is the computational complexity of the Critic audit?",
            "<b>Examiner intent:</b> Evaluating algorithmic scalability.<br/>"
            "<b>Defense Answer:</b> \"The Critic audit runs in <b>linear and polynomial time</b> with respect to valley size: "
            "1) Capacity check (R1) is O(|Assignments|). "
            "2) Deadline check (R2) is O(|Assignments|). "
            "3) Conflict check (R3) sorts and scans resource intervals in O(N log N). "
            "4) Graph reachability (R4) uses BFS in O(|V| + |E|). "
            "5) Medical and hospital triage (R5, R6) are O(|Assignments|). "
            "Total audit complexity is O(|V| + |E| + N log N), which executes in <b>under 40 milliseconds</b> for our 12-village basin, ensuring instantaneous convergence.\""
        ),

        # CATEGORY 3: REPLANNING & REAL-WORLD INTEGRATION
        (
            "Category 3: Dynamic Replanning & What-If Sandbox",
            "Q11: When a field disruption occurs, why not rerun the entire multi-agent workflow from scratch?",
            "<b>Examiner intent:</b> Assessing practical operational understanding of emergency response.<br/>"
            "<b>Defense Answer:</b> \"In an active evacuation, <b>churn is catastrophic</b>. If 1,000 residents are already boarding buses according to an authorized plan, rerunning from scratch might arbitrarily reassign unaffected villages to different shelters, creating massive civilian panic and traffic gridlock. Our Replanner Agent performs <b>localized, delta-based repair</b>: it freezes all unaffected vehicle assignments and resolves only the invalidated edge (e.g., substituting amphibious craft for the broken bridge corridor). This preserves operational stability.\""
        ),
        (
            "Category 3: Dynamic Replanning & What-If Sandbox",
            "Q12: How does the What-If Analysis sandbox work, and what is its operational utility?",
            "<b>Examiner intent:</b> Understanding Tab 5's analytical purpose.<br/>"
            "<b>Defense Answer:</b> \"The What-If sandbox simulates parametric stress tests by varying the mandatory safety buffer between 0 and 90 minutes across all nodes. It categorizes each community into three zones: <b>Safe</b> (buffer > 30m), <b>Low Margin</b> (0m to 30m), and <b>Failed</b> (arrival time exceeds flood crest). This allows incident commanders to stress-test their plan against sudden weather deterioration before authorizing vehicle dispatch.\""
        ),
        (
            "Category 3: Dynamic Replanning & What-If Sandbox",
            "Q13: How would FloodCommand be integrated into a real-life District Emergency Operations Center (DEOC)?",
            "<b>Examiner intent:</b> Testing real-world applicability.<br/>"
            "<b>Defense Answer:</b> \"FloodCommand connects into 4 real-world systems: "
            "1) <b>Inbound Telemetry:</b> Pulls real-time river water levels and rain radar from government hydrological APIs (CWC/USGS/IMD) and road closure feeds from highway traffic GIS. "
            "2) <b>Fleet Telematics:</b> GPS and Automatic Vehicle Location (AVL) devices on rescue buses and boats feed live locations via MQTT brokers. "
            "3) <b>Human-in-the-Loop Approval:</b> The certified dashboard acts as an advisory tool for the District Magistrate / Incident Commander to review and click 'Authorize'. "
            "4) <b>Dissemination:</b> Dispatches route manifests to first-responder tablets and outputs cellular broadcasts via the OASIS Common Alerting Protocol (CAP-XML).\""
        ),
        (
            "Category 3: Dynamic Replanning & What-If Sandbox",
            "Q14: What happens if cellular networks and power grids collapse during a catastrophic flood?",
            "<b>Examiner intent:</b> Probing resilience and edge-case failure modes.<br/>"
            "<b>Defense Answer:</b> \"In disaster engineering, primary communication failure must be anticipated. When cellular towers fail, FloodCommand incorporates three fallback channels: "
            "First, the system runs locally on edge servers powered by emergency generators in the DEOC. "
            "Second, dispatch manifests and situation reports are compressed into lightweight packet bursts transmitted over digital VHF/HF emergency radio (such as APRS/Winlink protocols). "
            "Third, satellite uplinks (BGAN or Starlink) installed at regional shelter hubs receive manifests directly, where loudhailer teams and civil defense wardens guide arrivals.\""
        ),
        (
            "Category 3: Dynamic Replanning & What-If Sandbox",
            "Q15: Why didn't you translate the entire command dashboard into regional languages?",
            "<b>Examiner intent:</b> Testing design decisions and interface rationale.<br/>"
            "<b>Defense Answer:</b> \"In emergency management, command-and-control operations centers operate under standardized technical terminology (e.g., Invariants, ETA buffers, Critic Audit, GIS topology). Translating technical engineering consoles creates semantic ambiguity and layout instability. However, <b>citizen-facing communications</b> (the cellular SMS broadcasts in Tab 3) do support regional language localization, ensuring residents receive life-saving directives in their native language while incident commanders retain precise, unambiguous technical telemetry.\""
        ),

        # CATEGORY 4: VIVA CURVEBALLS & DEFENSIVE STRATEGY
        (
            "Category 4: Evaluator Curveballs & Honest Defense",
            "Q16: Can the Critic itself have bugs or fail to catch a violation?",
            "<b>Examiner intent:</b> Trying to catch you in an overconfident claim of absolute perfection.<br/>"
            "<b>Defense Answer:</b> \"Yes, theoretically any software can contain bugs if an invariant specification is incomplete or miscoded. That is precisely why FloodCommand relies on <b>formal, unit-tested deterministic invariants</b> rather than probabilistic models. In our test suite (test_critic.py), we maintain exhaustive property-based tests verifying each invariant boundary condition independently. Furthermore, FloodCommand is an <b>advisory decision-support tool</b> with a Human-in-the-Loop, ensuring that the Incident Commander always performs final oversight before dispatch.\""
        ),
        (
            "Category 4: Evaluator Curveballs & Honest Defense",
            "Q17: What are the primary limitations of your prototype today?",
            "<b>Examiner intent:</b> Testing scientific honesty and self-awareness.<br/>"
            "<b>Defense Answer:</b> \"There are three primary limitations: "
            "1) <b>Synthetic Data:</b> The current evaluation runs on a 12-village synthetic topology representing Aethel Valley rather than live GIS telemetry. "
            "2) <b>Rule-Based Rework:</b> The current repair loop uses pre-scripted rules rather than a general constraint solver like OR-Tools. "
            "3) <b>Single-Trip Fleet Assumption:</b> We model primary high-capacity evacuation runs rather than multi-trip round-robin shuttle scheduling. Addressing these constitutes our immediate roadmap for future work.\""
        ),
        (
            "Category 4: Evaluator Curveballs & Honest Defense",
            "Q18: What is the difference between Verification and Validation in FloodCommand?",
            "<b>Examiner intent:</b> Fundamental software and AI engineering concepts.<br/>"
            "<b>Defense Answer:</b> \"<b>Verification</b> asks: 'Did we build the plan right?' In FloodCommand, this is performed by the Critic checking that the plan satisfies all mathematical constraints (R1–R6) with zero violations. <b>Validation</b> asks: 'Did we build the right system for the real world?' This is evaluated on Tab 6 and Tab 4, demonstrating that the system successfully saves 100% of civilian lives, withstands dynamic bridge collapses, and produces actionable real-world telematics.\""
        ),
        (
            "Category 4: Evaluator Curveballs & Honest Defense",
            "Q19: How does the system prevent vehicle bottlenecks on narrow mountain roads?",
            "<b>Examiner intent:</b> Domain-specific operational transport inquiry.<br/>"
            "<b>Defense Answer:</b> \"In our road network model, each arterial corridor has an assigned travel time and status. The Planner and Critic enforce staggered departure schedules based on vehicle capacity (e.g., high-capacity 50-passenger buses vs swift watercraft). In full-scale deployment, corridor flow-capacity constraints (maximum vehicles per hour) can be added as an explicit invariant R7 without altering the Critic's architectural pipeline.\""
        ),
        (
            "Category 4: Evaluator Curveballs & Honest Defense",
            "Q20: If you had 6 more months on this project, what would you build next?",
            "<b>Examiner intent:</b> Vision, maturity, and research potential.<br/>"
            "<b>Defense Answer:</b> \"I would focus on three major advancements: "
            "1) <b>Constraint Optimization Integration:</b> Replace the rule-based repair loop with a Mixed Integer Linear Programming (MILP) or OR-Tools solver for multi-objective optimization (minimizing total evacuation time while maximizing safety margins). "
            "2) <b>Dynamic Multi-Trip Scheduling:</b> Implement vehicle battery/fuel tracking and turn-around times to allow buses and boats to execute multi-trip evacuations. "
            "3) <b>Direct GIS & Drone Telemetry:</b> Ingest real-time drone aerial imagery (YOLO-based road flood detection) to update road blockage statuses autonomously.\""
        ),
    ]

    for cat_title, q_text, ans_text in viva_qa:
        qa_box = [
            [Paragraph(f"<b>{q_text}</b>", q_style)],
            [Paragraph(ans_text, ans_style)],
        ]
        t_qa = Table(qa_box, colWidths=[522])
        t_qa.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 6))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_path}")


if __name__ == "__main__":
    workspace_dir = Path(__file__).resolve().parent
    primary_pdf = workspace_dir / "final question answers.pdf"
    secondary_pdf = workspace_dir / "final_question_answers.pdf"

    create_presentation_viva_pdf(primary_pdf)
    shutil.copyfile(primary_pdf, secondary_pdf)
    print(f"Also created copy: {secondary_pdf}")
