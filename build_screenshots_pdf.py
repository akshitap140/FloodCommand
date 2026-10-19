"""
Script to compile all captured 16:9 real screenshots of FloodCommand into a publication-grade PDF.
Generates 'FloodCommand_Screenshots_Walkthrough.pdf' in the project root.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class SlideCanvas(canvas.Canvas):
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Top Header
        self.drawString(36, letter[0] - 25, "FloodCommand — Operations Center Visual Telemetry Walkthrough")
        self.drawRightString(letter[1] - 36, letter[0] - 25, "Real Running Dashboard Screen Captures (1080p 16:9)")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, letter[0] - 28, letter[1] - 36, letter[0] - 28)

        # Running Bottom Footer
        self.line(36, 28, letter[1] - 36, 28)
        self.setFont("Helvetica", 8)
        self.drawString(36, 18, "Educational prototype on synthetic data. Not an operational tool. | Unaltered screen captures.")
        page_str = f"Slide {self._pageNumber} of {page_count}"
        self.drawRightString(letter[1] - 36, 18, page_str)
        self.restoreState()


def build_screenshots_pdf(output_pdf_path: Path):
    # Landscape letter: 792 x 612 pt
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=34,
        bottomMargin=34,
    )

    styles = getSampleStyleSheet()

    slide_title_style = ParagraphStyle(
        "SlideTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F2236"),
    )

    slide_caption_style = ParagraphStyle(
        "SlideCaption",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
    )

    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E3A8A"),
    )

    shots = [
        {
            "file": "01_situation.png",
            "title": "Screen 1: Situation Map & Critical Indicators (01_situation.png)",
            "badge": "TAB 1: SITUATION • BASELINE OPERATIONS",
            "caption": (
                "<b>Key Numbers Visible:</b> Total Villages: <b>12</b> | People at Risk: <b>2,505</b> | Vulnerable Residents: <b>510</b> | Blocked Roads: <b>2</b> (RD-15 & RD-16 isolating Fernbank V10 in red).<br/>"
                "<b>Top KPI Strip:</b> Violations Caught: <b>15</b> | Auto-Fixed: <b>15</b> | Human Escalations: <b>0</b> | People Covered: <b>2,505 people (100%)</b> | Execution Time: <b>1.24 s</b>.<br/>"
                "<b>Map Features:</b> Shows the schematic river curve, open road network (green), blocked bridges (red dashed), and active evacuation assignment vectors."
            ),
        },
        {
            "file": "02_agent_run.png",
            "title": "Screen 2: Agent Run & Adversarial Critic Convergence (02_agent_run.png)",
            "badge": "TAB 2: AGENT RUN • ADVERSARIAL CRITIC AUDIT",
            "caption": (
                "<b>Key Numbers Visible:</b> Violations Convergence: <b>15 → 0</b> across 1 rework iteration.<br/>"
                "<b>Red Critic Audit Box:</b> Rejection detailing initial violations across R1 (S3 overflow by 390 pax), R2 (V04 bus arrival past 2h deadline), R3 (TEAM-01 double-booked on V04 & V02), R4 (bus to cut-off V10), R5 (vulnerable sent to S3 without medical), and R6 (Hospital Town V09 omitted).<br/>"
                "<b>Green Rework Box:</b> Automated resolution detailing S2 stadium diversion, high-speed boat BOAT-01 dispatch, dedicated team decoupling, and hospital transit coverage."
            ),
        },
        {
            "file": "03_naive_vs_verified.png",
            "title": "Screen 3: Naive Baseline vs. Verified Plan Comparison (03_naive_vs_verified.png)",
            "badge": "TAB 3: FINAL PLAN • SIDE-BY-SIDE AUDIT COMPARISON",
            "caption": (
                "<b>Key Numbers Visible:</b> Toggle <i>'Show plan without Critic'</i> is <b>ON</b>. Displays side-by-side comparative manifest.<br/>"
                "<b>Left Column (Initial Plan):</b> Displays color-coded Critic rejection cards for all <b>15 initial violations</b> (R1 through R6) with exact reasons and suggested repairs.<br/>"
                "<b>Right Column (Verified Plan):</b> Displays verified certified schedule with <b>100% compliance</b> and safe travel buffers across all 12 communities."
            ),
        },
        {
            "file": "04_disruption.png",
            "title": "Screen 4: Dynamic Incident Injection — Bridge Failure (04_disruption.png)",
            "badge": "TAB 4: DISRUPTION • SURGICAL RE-PLANNING DIFF",
            "caption": (
                "<b>Key Numbers Visible:</b> Active Incident: <b>BRIDGE WASHOUT</b> | Critic Re-Validation: <b>PASS (0 Violations)</b>.<br/>"
                "<b>Surgical Modification Diff:</b> Exactly <b>1 village changed: Riverbend (V02)</b>.<br/>"
                "<b>Change Action:</b> Transport Mode & Resource: <code>RESCUE_TEAM (TEAM-02)</code> ➔ <code>BOAT (BOAT-04, Slot 60-110m, ETA 25m, Margin 65m)</code>.<br/>"
                "<b>Operational Reason:</b> Arterial bridge V01–V02 collapsed; allocated secondary river craft without time conflict, leaving all 11 other communities untouched."
            ),
        },
        {
            "file": "05_validation.png",
            "title": "Screen 5: Adversarial Validation Benchmark & Compliance (05_validation.png)",
            "badge": "TAB 6: VALIDATION • 100% AUDIT BENCHMARK",
            "caption": (
                "<b>Key Numbers Visible:</b> Benchmark Table confirms <b>100% Caught</b> across all 6 planted invariant failure modes (R1 through R6).<br/>"
                "<b>Grouped Bar Chart:</b> <i>Without Critic (Naive Baseline)</i> = <b>0% compliance</b> (red bars) vs. <i>With Critic (FloodCommand)</i> = <b>100% compliance</b> (green bars) across Capacity, On-Time, No Conflict, Cut-Off, Medical, and Hospital checks."
            ),
        },
        {
            "file": "06_why_this.png",
            "title": "Screen 6: Explainable Decision Rationale — 'Why this?' (06_why_this.png)",
            "badge": "TAB 3: FINAL PLAN • DATA-DERIVED EXPLANATIONS",
            "caption": (
                "<b>Key Numbers Visible:</b> Expanded card for <b>Fernbank (V10) ➔ North Hill Fort Shelter via BOAT-05</b> (Safety Margin: <b>103m</b>).<br/>"
                "<b>Vehicle Rationale:</b> <code>CUT-OFF ISOLATED</code> status; bridges submerged; amphibious boat required (Rule R4 compliant); 60-pax payload for 160 residents (3 shuttles); ETA 35m with 103m safe margin.<br/>"
                "<b>Shelter Rationale:</b> North Hill Fort Shelter (S1) capacity 1,100 pax accommodates 160 evacuees (Rule R1 compliant); Verified Emergency Medical Facility Available."
            ),
        },
    ]

    story = []
    screenshots_dir = Path("screenshots")

    for i, shot in enumerate(shots):
        img_path = screenshots_dir / shot["file"]
        if not img_path.exists():
            print(f"Warning: {img_path} not found!")
            continue

        # Header bar for the slide
        header_table = Table(
            [
                [
                    Paragraph(f"<b>{shot['title']}</b>", slide_title_style),
                    Paragraph(f"<div align='right'><b>{shot['badge']}</b></div>", badge_style),
                ]
            ],
            colWidths=[480, 240],
        )
        header_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=6))

        # 16:9 Image scaled to fit landscape letter: width=720, height=365
        story.append(Image(str(img_path), width=720, height=365))
        story.append(Spacer(1, 6))

        # Caption box with key numbers
        caption_table = Table([[Paragraph(shot["caption"], slide_caption_style)]], colWidths=[720])
        caption_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("LINELEFT", (0, 0), (0, -1), 3.5, colors.HexColor("#2563EB")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(caption_table)

        if i < len(shots) - 1:
            story.append(PageBreak())

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"Successfully compiled walkthrough PDF: {output_pdf_path}")


if __name__ == "__main__":
    out_pdf = Path("c:/Users/Akshita/Documents/FAAI PROJECT/FloodCommand_Screenshots_Walkthrough.pdf")
    build_screenshots_pdf(out_pdf)
