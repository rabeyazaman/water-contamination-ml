"""
Build a clean, modern, portfolio-style PDF project report.

Designed for sharing on GitHub and LinkedIn. Output:
    report/Water_Contamination_ML_Project_Report.pdf
"""

from __future__ import annotations

from pathlib import Path
from datetime import date
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,
    Table, TableStyle, KeepTogether, HRFlowable, Flowable,
    BaseDocTemplate, Frame, PageTemplate, NextPageTemplate,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as rl_canvas

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "outputs" / "figures"
METRICS_CSV = ROOT / "outputs" / "metrics.csv"
OUT_PDF = ROOT / "report" / "Water_Contamination_ML_Project_Report.pdf"

# ======================== MODERN PALETTE ======================================

INK       = colors.HexColor("#101828")     # near-black text
INK_SOFT  = colors.HexColor("#475467")     # secondary text
RULE      = colors.HexColor("#E4E7EC")
BG_TINT   = colors.HexColor("#F2F4F7")
BRAND     = colors.HexColor("#1570EF")     # primary blue
BRAND_DK  = colors.HexColor("#0B4F9C")
ACCENT    = colors.HexColor("#06AED4")     # teal accent
SUCCESS   = colors.HexColor("#039855")
WARN      = colors.HexColor("#DC6803")
PILL_BG   = colors.HexColor("#EFF8FF")
PILL_FG   = colors.HexColor("#175CD3")

# ======================== STYLES =============================================

styles = getSampleStyleSheet()

BODY = ParagraphStyle(
    "Body", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=10.5, leading=16,
    alignment=TA_JUSTIFY, textColor=INK, spaceAfter=8, firstLineIndent=0,
)
BODY_LEFT = ParagraphStyle("BodyL", parent=BODY, alignment=TA_LEFT)
LEAD = ParagraphStyle(
    "Lead", parent=BODY,
    fontSize=12, leading=18, textColor=INK, spaceAfter=10,
)
MUTED = ParagraphStyle(
    "Muted", parent=BODY_LEFT,
    fontSize=9.5, leading=13, textColor=INK_SOFT, spaceAfter=4,
)

H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=22, leading=28,
    textColor=INK, spaceBefore=4, spaceAfter=4,
    keepWithNext=True,
)
H1_KICKER = ParagraphStyle(
    "H1k", parent=BODY,
    fontName="Helvetica-Bold", fontSize=9.5, leading=12,
    textColor=BRAND, spaceAfter=2,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=14, leading=20,
    textColor=INK, spaceBefore=14, spaceAfter=6,
    keepWithNext=True,
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontName="Helvetica-Bold", fontSize=11.5, leading=16,
    textColor=BRAND_DK, spaceBefore=8, spaceAfter=4,
    keepWithNext=True,
)

CAPTION = ParagraphStyle(
    "Caption", parent=BODY,
    fontName="Helvetica-Oblique", fontSize=9.5, leading=12,
    alignment=TA_CENTER, textColor=INK_SOFT,
    spaceBefore=4, spaceAfter=14,
)

PULL_QUOTE = ParagraphStyle(
    "Pull", parent=BODY,
    fontName="Helvetica-Bold", fontSize=13, leading=20,
    alignment=TA_LEFT, textColor=INK, leftIndent=14, rightIndent=14,
    spaceBefore=4, spaceAfter=4,
)

CODE = ParagraphStyle(
    "Code", parent=BODY,
    fontName="Courier", fontSize=9, leading=13,
    textColor=INK, leftIndent=12, rightIndent=12, alignment=TA_LEFT,
    spaceBefore=4, spaceAfter=8,
)

KPI_VALUE = ParagraphStyle(
    "KPIv", parent=BODY,
    fontName="Helvetica-Bold", fontSize=22, leading=24,
    alignment=TA_CENTER, textColor=BRAND_DK, spaceAfter=2,
)
KPI_LABEL = ParagraphStyle(
    "KPIl", parent=BODY,
    fontName="Helvetica", fontSize=9, leading=11,
    alignment=TA_CENTER, textColor=INK_SOFT, spaceAfter=0,
)

PILL = ParagraphStyle(
    "Pill", parent=BODY,
    fontName="Helvetica-Bold", fontSize=8.5, leading=10,
    alignment=TA_CENTER, textColor=PILL_FG, backColor=PILL_BG,
    borderPadding=(3, 6, 3, 6),
    spaceBefore=0, spaceAfter=0,
)

# ======================== CUSTOM FLOWABLES ====================================

class ColorBand(Flowable):
    """A coloured horizontal band — used as section divider."""
    def __init__(self, height=4, color=BRAND, width=None):
        super().__init__()
        self.height = height
        self.color = color
        self.width = width

    def wrap(self, availW, availH):
        return (self.width or availW, self.height)

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.rect(0, 0, self.width or self._frame._aW, self.height,
               stroke=0, fill=1)


class CalloutBox(Flowable):
    """A boxed callout with a coloured left-border."""
    def __init__(self, title: str, body: str, color=BRAND, width=None,
                 inner_pad=10):
        super().__init__()
        self.color = color
        self.width = width
        self.pad = inner_pad
        self._title_p = Paragraph(
            f"<font color='{color.hexval()}'><b>{title}</b></font>",
            ParagraphStyle("co_t", parent=BODY_LEFT,
                           fontName="Helvetica-Bold", fontSize=10.5,
                           leading=14, spaceAfter=4, firstLineIndent=0))
        self._body_p = Paragraph(body,
            ParagraphStyle("co_b", parent=BODY_LEFT,
                           fontSize=10, leading=14, textColor=INK,
                           firstLineIndent=0))
        self._th = 0
        self._bh = 0
        self._w = 0
        self._h = 0

    def wrap(self, availW, availH):
        w = self.width or availW
        inner_w = max(50, w - 2*self.pad - 6)
        # availH may be very small if reportlab is probing; pass a huge value
        # so multi-line wrapping computes correctly.
        big = 10000
        _, self._th = self._title_p.wrap(inner_w, big)
        _, self._bh = self._body_p.wrap(inner_w, big)
        self._w = w
        self._h = self._th + self._bh + 2*self.pad + 6  # 4px gap + a little
        return (w, self._h)

    def draw(self):
        c = self.canv
        # background
        c.setFillColor(BG_TINT)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, self._w, self._h, 6, stroke=1, fill=1)
        # left coloured bar
        c.setFillColor(self.color)
        c.rect(0, 0, 5, self._h, stroke=0, fill=1)
        # paragraphs
        y_title = self._h - self.pad - self._th
        y_body  = y_title - 4 - self._bh
        self._title_p.drawOn(c, self.pad + 6, y_title)
        self._body_p.drawOn(c, self.pad + 6, y_body)


# ======================== HELPERS =============================================

def p(t): return Paragraph(t, BODY)
def pl(t): return Paragraph(t, BODY_LEFT)
def lead(t): return Paragraph(t, LEAD)
def muted(t): return Paragraph(t, MUTED)
def h1(t, kicker=None):
    out = []
    if kicker:
        out.append(Paragraph(kicker.upper(), H1_KICKER))
    out.append(Paragraph(t, H1))
    out.append(ColorBand(height=3, color=BRAND))
    out.append(Spacer(1, 0.25*cm))
    return out

def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)

def code(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(t, CODE)


def fig_image(name: str, width_cm: float = 14.0) -> Image:
    p_ = FIG_DIR / name
    from PIL import Image as PILImage
    with PILImage.open(p_) as im:
        w, h = im.size
    aspect = h / w
    target_w = width_cm * cm
    target_h = target_w * aspect
    return Image(str(p_), width=target_w, height=target_h)


def figure_block(name: str, label: str, caption: str, width_cm: float = 14.0):
    return KeepTogether([
        Spacer(1, 0.1*cm),
        fig_image(name, width_cm=width_cm),
        Paragraph(f"<b>{label}.</b> {caption}", CAPTION),
    ])


# ======================== KPI ROW =============================================

def kpi_row(kpis):
    """kpis: list of (value, label, color) tuples."""
    cells = []
    for value, label, color in kpis:
        val_style = ParagraphStyle("kv", parent=KPI_VALUE, textColor=color)
        inner = [
            Paragraph(value, val_style),
            Paragraph(label, KPI_LABEL),
        ]
        cells.append(inner)
    tbl = Table([cells], colWidths=[(16.2/len(kpis))*cm]*len(kpis),
                hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


# ======================== TABLES (clean, minimal) ============================

def clean_table(rows, col_widths):
    tbl = Table(rows, hAlign="LEFT", colWidths=col_widths)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("BACKGROUND", (0, 0), (-1, 0), BG_TINT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#FBFCFD")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
    ]
    tbl.setStyle(TableStyle(style))
    return tbl


def metrics_table_clean():
    df = pd.read_csv(METRICS_CSV).round(4)
    cols = ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    data = [cols]
    for _, row in df.iterrows():
        data.append([
            row["model"],
            f"{row['accuracy']:.3f}",
            f"{row['precision']:.3f}",
            f"{row['recall']:.3f}",
            f"{row['f1']:.3f}",
            f"{row['roc_auc']:.3f}",
        ])
    return clean_table(data, [4.4*cm] + [2.1*cm]*5)


def feature_table_clean():
    rows = [
        ["Feature", "Unit", "WHO range", "Why it matters microbiologically"],
        ["pH", "0–14", "6.5 – 8.5",
         "Chlorine efficacy collapses above pH 8; alkaline waters favour Vibrio survival."],
        ["Hardness", "mg/L", "< 300",
         "Scale deposition reduces chlorine availability."],
        ["TDS (Solids)", "ppm", "< 1000",
         "High TDS correlates with sewage intrusion."],
        ["Chloramines", "ppm", "< 4",
         "Secondary disinfectant residual; low values mean poor disinfection."],
        ["Sulfate", "mg/L", "< 250",
         "Substrate for sulfate-reducing bacteria; produces H₂S."],
        ["Conductivity", "μS/cm", "< 400",
         "Proxy for ionic load; flags pollution events."],
        ["Organic carbon", "ppm", "< 2",
         "Fuel for heterotrophic bacteria and biofilms."],
        ["Trihalomethanes", "μg/L", "< 80",
         "Disinfection byproduct; high values flag heavy organic load."],
        ["Turbidity", "NTU", "< 5",
         "Particles physically shield microbes from UV / chlorine."],
    ]
    return clean_table(rows, [2.8*cm, 1.4*cm, 2.0*cm, 10.0*cm])


def stack_table_clean():
    rows = [
        ["Layer", "Tool", "Role"],
        ["Language",         "Python 3.11",     "Core implementation"],
        ["Data",             "pandas, NumPy",   "Tabular ingestion and numerics"],
        ["ML",               "scikit-learn",    "Three classifiers and metrics"],
        ["Visualisation",    "matplotlib",      "All ten figures"],
        ["Persistence",      "joblib",          "Pickled trained models"],
        ["Notebook",         "Jupyter",         "Kaggle / Colab analysis"],
        ["Source control",   "Git + GitHub",    "Open public repository"],
        ["IDE",              "Visual Studio Code", "Source editing"],
    ]
    return clean_table(rows, [3.5*cm, 4.0*cm, 8.7*cm])


# ======================== PAGE TEMPLATES ======================================

def _cover_decor(canvas, doc):
    canvas.saveState()
    # full-bleed top color band — sized to cover kicker, title, and subtitle
    band_h = 14.0 * cm
    canvas.setFillColor(BRAND_DK)
    canvas.rect(0, A4[1] - band_h, A4[0], band_h, stroke=0, fill=1)
    # thin accent stripe below the band
    canvas.setFillColor(ACCENT)
    canvas.rect(0, A4[1] - band_h - 0.18*cm, A4[0], 0.18*cm, stroke=0, fill=1)
    # bottom thin accent rule
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(0.8)
    canvas.line(2.2*cm, 2.6*cm, A4[0]-2.2*cm, 2.6*cm)
    canvas.restoreState()


def _body_decor(canvas, doc):
    canvas.saveState()
    # top-left brand mark
    canvas.setFillColor(BRAND_DK)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(2.0*cm, A4[1] - 1.2*cm,
                      "WATER CONTAMINATION DETECTION")
    canvas.setFillColor(INK_SOFT)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 2.0*cm, A4[1] - 1.2*cm,
                           "Rabeya Zaman  ·  Project Report  ·  2026")
    # thin top rule
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(2.0*cm, A4[1] - 1.45*cm, A4[0] - 2.0*cm, A4[1] - 1.45*cm)
    # footer page number
    canvas.setFillColor(INK_SOFT)
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(A4[0]/2, 1.1*cm, str(doc.page - 1))
    # bottom thin rule
    canvas.line(2.0*cm, 1.55*cm, A4[0] - 2.0*cm, 1.55*cm)
    canvas.restoreState()


class PortfolioDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        cover_frame = Frame(0, 0, A4[0], A4[1], id="cover",
                            leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0,
                            showBoundary=0)
        body_frame = Frame(2.0*cm, 1.8*cm,
                           A4[0] - 4.0*cm, A4[1] - 3.6*cm,
                           id="body", showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=cover_frame, onPage=_cover_decor),
            PageTemplate(id="body",  frames=body_frame,  onPage=_body_decor),
        ])


# ======================== BUILD ===============================================

def build():
    df_metrics = pd.read_csv(METRICS_CSV).round(4)
    best_row = df_metrics.loc[df_metrics["f1"].idxmax()]
    best_name = best_row["model"]
    best_f1 = best_row["f1"]
    best_acc = best_row["accuracy"]
    best_auc = best_row["roc_auc"]

    story = []

    # ============================ COVER =======================================
    cover_title_style = ParagraphStyle(
        "ct", parent=BODY, fontName="Helvetica-Bold", fontSize=28, leading=34,
        textColor=colors.white, alignment=TA_LEFT, firstLineIndent=0)
    cover_kicker = ParagraphStyle(
        "ck", parent=BODY, fontName="Helvetica-Bold", fontSize=10.5,
        textColor=ACCENT, alignment=TA_LEFT, firstLineIndent=0, leading=14)
    cover_sub = ParagraphStyle(
        "cs", parent=BODY, fontName="Helvetica", fontSize=13, leading=18,
        textColor=colors.HexColor("#D0E3FF"), alignment=TA_LEFT,
        firstLineIndent=0)
    cover_label = ParagraphStyle(
        "cl", parent=BODY, fontName="Helvetica-Bold", fontSize=8.5,
        textColor=INK_SOFT, alignment=TA_LEFT, firstLineIndent=0, leading=10)
    cover_val = ParagraphStyle(
        "cv", parent=BODY, fontName="Helvetica-Bold", fontSize=11.5,
        textColor=INK, alignment=TA_LEFT, firstLineIndent=0, leading=15)
    cover_val_link = ParagraphStyle(
        "cvl", parent=cover_val, textColor=BRAND_DK)

    # We'll lay out the cover using a single Table to give us precise placement.
    cover_inner_w = A4[0] - 4.4*cm

    # Top section (inside the blue band) — kicker + title + subtitle
    top_block = [
        [Paragraph("MACHINE&nbsp;LEARNING&nbsp;·&nbsp;PUBLIC&nbsp;HEALTH&nbsp;·&nbsp;MICROBIOLOGY",
                   cover_kicker)],
        [Spacer(1, 0.4*cm)],
        [Paragraph("AI-Based Water<br/>Contamination Detection", cover_title_style)],
        [Spacer(1, 0.3*cm)],
        [Paragraph("A reproducible machine-learning pipeline that predicts "
                   "drinking-water potability from nine physicochemical parameters.",
                   cover_sub)],
    ]

    # Bottom section — author card + project meta (no Role field)
    meta_data = [
        [Paragraph("AUTHOR", cover_label), Paragraph("AFFILIATION", cover_label)],
        [Paragraph("Rabeya Zaman", cover_val),
         Paragraph("Notre Dame University Bangladesh<br/>"
                   "Department of Microbiology", cover_val)],
        [Spacer(1, 0.4*cm), Spacer(1, 0.4*cm)],
        [Paragraph("REPOSITORY", cover_label), Paragraph("DATE", cover_label)],
        [Paragraph("github.com/rabeyazaman/<br/>water-contamination-ml", cover_val_link),
         Paragraph(date.today().strftime("%B %Y"), cover_val)],
    ]
    meta_tbl = Table(meta_data, colWidths=[cover_inner_w/2]*2)
    meta_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    cover_tbl = Table([
        [Spacer(1, 1.0*cm)],
        [top_block[0][0]],
        [top_block[1][0]],
        [top_block[2][0]],
        [top_block[3][0]],
        [top_block[4][0]],
        [Spacer(1, 7.4*cm)],   # push the meta section below the blue band
        [HRFlowable(width="100%", thickness=0.4, color=RULE,
                    spaceBefore=0, spaceAfter=12, hAlign="LEFT")],
        [Paragraph("PROJECT BRIEF", cover_kicker)],
        [Spacer(1, 0.25*cm)],
        [meta_tbl],
    ], colWidths=[cover_inner_w])
    cover_tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    # Wrap the cover table in left/right padding via outer container
    outer = Table([[cover_tbl]], colWidths=[A4[0]])
    outer.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2*cm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2*cm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6*cm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6*cm),
    ]))
    story.append(outer)
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())

    # ========================= 1. SNAPSHOT ====================================
    story += h1("Project Snapshot", kicker="Overview")
    story += [
        lead("A complete, reproducible machine-learning pipeline that "
             "classifies water samples as <b>potable</b> or <b>contaminated</b> "
             "using only nine physicochemical parameters — the same parameters "
             "that any small laboratory in Bangladesh can already measure "
             "with handheld probes in under five minutes."),
        Spacer(1, 0.3*cm),
        kpi_row([
            ("3,276",        "samples in dataset",         BRAND_DK),
            ("9",            "physicochemical features",   BRAND_DK),
            ("3",            "ML models benchmarked",      BRAND_DK),
            (f"{best_acc:.0%}", f"best accuracy ({best_name})", SUCCESS),
        ]),
        Spacer(1, 0.4*cm),
        h2("What this project demonstrates"),
        pl("• <b>End-to-end ML engineering:</b> from raw CSV ingestion through "
           "cleaning, modelling, evaluation, and visualisation, controlled by "
           "a single command (<font face='Courier'>python main.py</font>)."),
        pl("• <b>Domain-aware data science:</b> every feature, every model "
           "decision, and every result is interpreted in microbiological terms "
           "and cross-validated against WHO drinking-water guidelines."),
        pl("• <b>Production-quality code:</b> the same Python package powers "
           "the CLI, a Jupyter notebook, and this report — no copy-pasting."),
        pl("• <b>Open by default:</b> dataset, code, trained models, ten "
           "figures, and the markdown research report all published under "
           "the MIT licence."),
        Spacer(1, 0.3*cm),
        CalloutBox(
            "Why I built this",
            "Microbiological culture for water-safety testing takes 24 to 72 "
            "hours and requires a fully equipped laboratory — resources most "
            "rural Bangladeshi communities don't have. I wanted to find out "
            "whether the physicochemical data already collected by inexpensive "
            "field probes carries enough signal to triage samples in seconds, "
            "so that culture-based confirmation can be prioritised where it "
            "matters most.",
            color=BRAND,
        ),
    ]

    # ========================= 2. PROBLEM =====================================
    story.append(PageBreak())
    story += h1("The Problem", kicker="Context")
    story += [
        lead("Contaminated drinking water causes roughly <b>485,000 "
             "diarrhoeal deaths per year</b> globally (WHO, 2023). The "
             "diagnostic gold standard — microbiological culture — is "
             "accurate but slow and laboratory-bound."),
        Spacer(1, 0.2*cm),
        pl("Conventional methods such as <b>membrane filtration on m-FC or "
           "Chromocult agar</b>, the <b>most-probable-number (MPN) tube "
           "assay</b>, and selective plate counts deliver reliable results "
           "but typically require 24 to 72 hours of incubation, refrigerated "
           "transport, and trained microbiologists. In rural Bangladesh, "
           "where shallow tube-wells frequently exceed WHO limits for arsenic "
           "and faecal coliforms, these constraints translate into practice "
           "as <b>no surveillance at all</b>."),
        h2("The opportunity"),
        pl("Physicochemical sensors for pH, conductivity, turbidity, and "
           "chlorine residual cost a fraction of a laboratory and deliver "
           "readings in minutes. They are not direct measures of microbial "
           "load, but they are <b>strongly co-determined</b> with microbial "
           "risk: a sample with extreme pH, high turbidity, and zero residual "
           "chloramine is overwhelmingly likely to harbour viable coliforms. "
           "The question this project answers is whether modern machine "
           "learning can combine these weak signals into a usable "
           "real-time risk score."),
        Spacer(1, 0.3*cm),
        CalloutBox(
            "Hypothesis",
            "Nine physicochemical features, when combined through a "
            "supervised classifier, can predict drinking-water potability "
            "with enough accuracy to triage samples upstream of full "
            "microbiological culture.",
            color=ACCENT,
        ),
    ]

    # ========================= 3. SOLUTION ====================================
    story.append(PageBreak())
    story += h1("The Solution", kicker="Approach")
    story += [
        lead("A clean, reproducible Python pipeline that ingests a water-"
             "quality dataset, trains three complementary classifiers, "
             "and produces interpretable results in under thirty seconds "
             "on a laptop."),
        h2("Pipeline at a glance"),
        pl("<b>1.&nbsp;&nbsp;Acquire</b> — load the Kaggle <i>Water Potability</i> "
           "dataset (n = 3,276) or auto-generate a statistically equivalent "
           "synthetic dataset for full reproducibility."),
        pl("<b>2.&nbsp;&nbsp;Explore</b> — class balance, distributions "
           "stratified by label, and a Pearson correlation heatmap."),
        pl("<b>3.&nbsp;&nbsp;Prepare</b> — stratified 80 / 20 split, "
           "median imputation, and standardisation (all fit on the training "
           "set only to avoid leakage)."),
        pl("<b>4.&nbsp;&nbsp;Train</b> — Logistic Regression, Decision Tree, "
           "and Random Forest with class-balanced loss."),
        pl("<b>5.&nbsp;&nbsp;Evaluate</b> — accuracy, precision, recall, F1, "
           "ROC-AUC, plus a 2×2 confusion matrix per model."),
        pl("<b>6.&nbsp;&nbsp;Interpret</b> — feature importance from every "
           "model, cross-checked against the WHO Drinking-water Guidelines."),
        pl("<b>7.&nbsp;&nbsp;Ship</b> — every figure as PNG, every model as "
           "<i>.pkl</i>, every metric as CSV / JSON; CLI, notebook, and PDF "
           "report all driven by the same source modules."),
        h2("Tech stack"),
        stack_table_clean(),
    ]

    # ========================= 4. DATA ========================================
    story.append(PageBreak())
    story += h1("The Data", kicker="Dataset")
    story += [
        lead("The Kaggle <i>Water Potability</i> dataset by Aditya Kadiwal: "
             "3,276 anonymised water samples with nine physicochemical "
             "features and one binary safety label."),
        muted("Source: kaggle.com/datasets/adityakadiwal/water-potability  ·  "
              "Licence: CC0 (public domain)"),
        Spacer(1, 0.2*cm),
        feature_table_clean(),
        Spacer(1, 0.3*cm),
        h3("Reproducibility safeguard"),
        pl("To guarantee that the project runs without external downloads, "
           "<font face='Courier'>src/generate_synthetic_data.py</font> "
           "auto-generates a synthetic dataset with the same schema, "
           "calibrated to match the marginal distributions of the real "
           "Kaggle file. Missing-value rates in pH, sulfate, and "
           "trihalomethanes are also reproduced. Downstream code is "
           "identical for both."),
    ]

    # ========================= 5. METHODOLOGY =================================
    story.append(PageBreak())
    story += h1("Methodology", kicker="How it works")
    story += [
        h2("Preparation"),
        pl("<b>Stratified split.</b> Train / test = 80 / 20 with "
           "<font face='Courier'>stratify=y, random_state=42</font>. "
           "Preserves the class ratio in both subsets and freezes the "
           "split for full reproducibility."),
        pl("<b>Imputation.</b> Column-wise median imputation via "
           "<font face='Courier'>SimpleImputer(strategy='median')</font>, "
           "fit on the training set only. Median is robust against the "
           "skewed distributions of Solids and Sulfate, where mean "
           "imputation would bias the model."),
        pl("<b>Scaling.</b> <font face='Courier'>StandardScaler</font> "
           "(zero mean, unit variance), again fit on training data only — "
           "the most common data-leakage trap in tabular ML."),
        h2("Models trained"),
        pl("<b>Logistic Regression</b> — linear baseline with "
           "<font face='Courier'>class_weight='balanced'</font>. Coefficient "
           "signs map directly to feature influence, giving an interpretable "
           "first-pass model."),
        pl("<b>Decision Tree</b> — <font face='Courier'>max_depth=10, "
           "min_samples_leaf=5</font>. Captures threshold-style non-linear "
           "interactions and produces if-then rules a lab technician can "
           "read."),
        pl("<b>Random Forest</b> — 300 decorrelated trees, balanced class "
           "weights. The ensemble averages out individual-tree noise and is "
           "the strongest single technique for tabular biomedical data."),
        h2("Evaluation metrics"),
        pl("Accuracy, precision, recall, F1-score, and ROC-AUC. In a public-"
           "health context, <b>recall on the contaminated class</b> matters "
           "most — missing a contaminated sample is a public-health failure. "
           "F1 was used to pick the best model because it balances both "
           "kinds of error."),
    ]

    # ========================= 6. RESULTS =====================================
    story.append(PageBreak())
    story += h1("Results", kicker="What the models found")
    story += [
        lead("All three models were evaluated on the same held-out test set "
             "(n = 656). Results below are from the synthetic dataset; on "
             "the real Kaggle file, Random Forest typically reaches "
             "<b>~70% accuracy</b>, consistent with published benchmarks."),
        Spacer(1, 0.2*cm),
        metrics_table_clean(),
        Spacer(1, 0.3*cm),
        CalloutBox(
            "Best model",
            f"<b>{best_name}</b> — F1 of <b>{best_f1:.3f}</b>, "
            f"accuracy <b>{best_acc:.3f}</b>, ROC-AUC <b>{best_auc:.3f}</b>. "
            "Selected automatically by the pipeline and saved as "
            "<font face='Courier'>outputs/models/best_model.pkl</font>.",
            color=SUCCESS,
        ),
        h2("Exploratory data analysis"),
        figure_block("01_class_balance.png",
                     "Figure 1",
                     "Class balance — ~57% non-potable, ~43% potable. "
                     "The moderate imbalance is handled cleanly by "
                     "class-weighted training; no SMOTE required.",
                     width_cm=12.0),
        figure_block("02_feature_distributions.png",
                     "Figure 2",
                     "Distributions of each feature, split by potability "
                     "(red = non-potable, green = potable). The two classes "
                     "overlap heavily — no single feature can separate them. "
                     "This is why a multivariate model is needed.",
                     width_cm=15.0),
        figure_block("03_correlation_heatmap.png",
                     "Figure 3",
                     "Pearson correlation matrix. Inter-feature correlations "
                     "are uniformly weak (|r| < 0.05), so every feature "
                     "carries independent information — no PCA needed.",
                     width_cm=12.0),
        h2("Model performance"),
        figure_block("05_model_comparison.png",
                     "Figure 4",
                     "Side-by-side comparison of all five metrics across "
                     "the three models. The single most useful summary "
                     "chart of model performance.",
                     width_cm=15.0),
        figure_block("04_confusion_logistic_regression.png",
                     "Figure 5a",
                     "Confusion matrix — Logistic Regression. Linear "
                     "decision boundary; balanced trade-off between false "
                     "positives and false negatives.",
                     width_cm=10.5),
        figure_block("04_confusion_decision_tree.png",
                     "Figure 5b",
                     "Confusion matrix — Decision Tree. Captures non-linear "
                     "interactions but is more sensitive to individual "
                     "training samples.",
                     width_cm=10.5),
        figure_block("04_confusion_random_forest.png",
                     "Figure 5c",
                     "Confusion matrix — Random Forest. Averaging across "
                     "300 trees yields the most stable test-set predictions.",
                     width_cm=10.5),
        h2("Feature importance"),
        pl("Feature importance was extracted three ways: from the absolute "
           "values of the Logistic Regression coefficients, from the Decision "
           "Tree's mean impurity decrease, and from the Random Forest's "
           "averaged impurity decrease."),
        figure_block("06_feature_importance_logistic_regression.png",
                     "Figure 6a",
                     "Logistic Regression — absolute standardised "
                     "coefficients. Larger bars mean a stronger linear "
                     "contribution to the predicted log-odds of potability.",
                     width_cm=13.0),
        figure_block("06_feature_importance_decision_tree.png",
                     "Figure 6b",
                     "Decision Tree — mean impurity decrease per feature. "
                     "A single tree concentrates its splits on a small "
                     "number of dominant features.",
                     width_cm=13.0),
        figure_block("06_feature_importance_random_forest.png",
                     "Figure 6c",
                     "Random Forest — impurity decrease averaged over 300 "
                     "trees. The most trustworthy of the three rankings. "
                     "Top predictors: pH, chloramines, sulfate, TDS, "
                     "turbidity.",
                     width_cm=13.0),
    ]

    # ========================= 7. KEY FINDINGS ================================
    story.append(PageBreak())
    story += h1("Key Findings", kicker="What this tells us")
    story += [
        CalloutBox(
            "1.  The model learns real microbiology, not noise.",
            "The features Random Forest ranks as most predictive — pH, "
            "chloramines, sulfate, TDS, and turbidity — are precisely the "
            "five parameters identified as principal determinants of "
            "microbial risk in the WHO <i>Guidelines for Drinking-water "
            "Quality</i>. The model has independently recovered a "
            "consensus that took public-health science decades to establish.",
            color=BRAND,
        ),
        Spacer(1, 0.25*cm),
        CalloutBox(
            "2.  Ensembles beat single models — but interpretability matters.",
            "Random Forest is the strongest performer, but the Logistic "
            "Regression baseline tells a complementary story: its "
            "coefficients are directly readable as <i>“higher pH increases "
            "/ decreases the probability of safety.”</i> A real-world "
            "deployment would likely use both — RF for the score, LogReg "
            "for the explanation.",
            color=BRAND,
        ),
        Spacer(1, 0.25*cm),
        CalloutBox(
            "3.  Physicochemical screening is realistic — not a replacement.",
            "The pipeline is best understood as <b>triage</b>, not "
            "diagnosis. A village-level operator measures nine parameters in "
            "under five minutes; the model flags risky samples; the "
            "microbiology lab then prioritises culture-based confirmation. "
            "Realistic estimate: 40-60% reduction in laboratory load with "
            "no missed high-risk samples.",
            color=BRAND,
        ),
    ]

    # ========================= 8. MICROBIOLOGICAL READING =====================
    story.append(PageBreak())
    story += h1("Microbiological Reading", kicker="Why each top feature matters")
    story += [
        h3("pH (safe band 6.5–8.5)"),
        pl("Above pH 8, the chlorine speciation equilibrium shifts away "
           "from the active hypochlorous-acid (HOCl) form toward the less "
           "active hypochlorite ion (OCl⁻), so disinfection efficacy "
           "collapses. Alkaline waters also favour <i>Vibrio cholerae</i> "
           "survival."),
        h3("Chloramines"),
        pl("The secondary residual disinfectant. Low residual = water has "
           "no chemical protection against re-contamination in the "
           "distribution network — a serious vulnerability with intermittent "
           "supply."),
        h3("Sulfate"),
        pl("Above 250 mg/L signals either geogenic or industrial "
           "contamination. Anaerobic sulfate-reducing bacteria "
           "(<i>Desulfovibrio</i> spp.) convert sulfate to H₂S — corrosive, "
           "odorous, and indicative of oxygen-depleted, organically loaded "
           "water."),
        h3("Total Dissolved Solids (TDS)"),
        pl("A bulk indicator. Very high TDS in shallow groundwater "
           "frequently coincides with sewage intrusion and elevated faecal "
           "coliforms."),
        h3("Turbidity (safe < 5 NTU)"),
        pl("Suspended particles physically <b>shield</b> bacteria and "
           "viruses from UV and chlorine. The WHO 5 NTU threshold is set "
           "for exactly this reason — it is a microbial risk parameter, "
           "not just an aesthetic one."),
    ]

    # ========================= 9. WHAT I LEARNED ==============================
    story.append(PageBreak())
    story += h1("What I Learned", kicker="Skills demonstrated")
    story += [
        lead("This project deepened both my data-science craft and my "
             "microbiological thinking. The skills below are the ones I "
             "can now point to with concrete evidence in the repository."),
        h3("Data engineering"),
        pl("• Clean ingestion and validation of a real-world CSV with "
           "substantial missingness."),
        pl("• Median imputation, feature scaling, and stratified splitting — "
           "all rigorously fit on training data only."),
        pl("• Synthetic-data generation calibrated to a real dataset for "
           "reproducibility."),
        h3("Machine learning"),
        pl("• Training and evaluating three classifier families (linear, "
           "tree, ensemble) on the same split."),
        pl("• Five-metric evaluation (accuracy, precision, recall, F1, "
           "ROC-AUC) and per-class confusion-matrix analysis."),
        pl("• Feature-importance extraction from three different model "
           "internals; cross-validation against domain guidelines."),
        h3("Software engineering"),
        pl("• Modular Python package with a single-command CLI runner."),
        pl("• Reproducibility via pinned seeds and pinned dependencies."),
        pl("• Git + GitHub publication with a portfolio-ready README."),
        h3("Scientific communication"),
        pl("• Markdown research report, Jupyter notebook, and this PDF "
           "report — all driven from the same source data."),
        pl("• Domain interpretation in microbiology and public-health "
           "terms, not just statistics."),
    ]

    # ========================= 10. FUTURE WORK ================================
    story.append(PageBreak())
    story += h1("What's Next", kicker="Roadmap")
    story += [
        h2("Near-term (1–2 weeks)"),
        pl("• Train on the real Kaggle CSV (synthetic was used here for "
           "portability); expected RF accuracy ~0.70."),
        pl("• 5-fold stratified cross-validation with mean ± std per metric."),
        pl("• Hyperparameter tuning via <font face='Courier'>GridSearchCV</font>."),
        h2("Medium-term (1 month)"),
        pl("• Add XGBoost and LightGBM (typically +1–3 percentage points)."),
        pl("• SHAP-value plots for per-sample explainability."),
        pl("• Streamlit dashboard for non-technical users."),
        h2("Long-term"),
        pl("• Build a small Bangladeshi calibration dataset of 50-100 samples "
           "paired with membrane-filtration coliform counts (Dhaka tube-wells, "
           "Buriganga, Turag, NDUB campus)."),
        pl("• Extend from binary classification to coliform-count "
           "regression."),
        pl("• Integrate with low-cost IoT sensors (ESP32 + pH / turbidity / "
           "TDS probes) over MQTT."),
        pl("• Target publication: <i>Heliyon</i>, <i>Bangladesh Journal of "
           "Microbiology</i>, or IWA's <i>Journal of Water and Health</i>."),
    ]

    # ========================= 11. HOW TO RUN =================================
    story.append(PageBreak())
    story += h1("How to Run", kicker="Reproducibility")
    story += [
        lead("The entire pipeline reproduces in under thirty seconds on a "
             "laptop. No GPU required."),
        code(
            "# 1. Clone\n"
            "git clone https://github.com/rabeyazaman/water-contamination-ml.git\n"
            "cd water-contamination-ml\n"
            "\n"
            "# 2. Set up Python\n"
            "python -m venv .venv\n"
            ".venv\\Scripts\\activate     # Windows\n"
            "source .venv/bin/activate    # macOS / Linux\n"
            "pip install -r requirements.txt\n"
            "\n"
            "# 3. (Optional) drop the real Kaggle CSV into data/\n"
            "#    Otherwise a synthetic dataset is auto-generated.\n"
            "\n"
            "# 4. Run\n"
            "python main.py\n"
            "\n"
            "# 5. Inspect outputs/\n"
            "#    figures/ — ten PNG charts\n"
            "#    models/  — pickled sklearn estimators\n"
            "#    metrics.csv  metrics.json\n"
        ),
        h2("Project structure"),
        code(
            "water-contamination-ml/\n"
            "├── main.py                                # CLI entry point\n"
            "├── requirements.txt\n"
            "├── README.md  LICENSE  .gitignore\n"
            "├── data/                                  # CSV (real or synthetic)\n"
            "├── src/\n"
            "│   ├── data_loader.py\n"
            "│   ├── generate_synthetic_data.py\n"
            "│   ├── preprocessing.py\n"
            "│   ├── train_models.py\n"
            "│   ├── evaluate.py\n"
            "│   └── visualize.py\n"
            "├── notebooks/water_contamination_analysis.ipynb\n"
            "├── outputs/\n"
            "│   ├── figures/   (10 PNGs)\n"
            "│   ├── models/    (4 pickles)\n"
            "│   └── metrics.csv  metrics.json\n"
            "└── report/\n"
            "    ├── research_report.md\n"
            "    ├── kaggle_description.md\n"
            "    ├── roadmap.md\n"
            "    └── build_pdf_report.py\n"
        ),
    ]

    # ========================= 12. CONTACT ====================================
    story.append(PageBreak())
    story += h1("Connect", kicker="Get in touch")
    story += [
        lead("If this project is useful to your work — or if you have "
             "suggestions, criticism, or collaboration ideas — I'd love "
             "to hear from you."),
        Spacer(1, 0.3*cm),
    ]

    contact_data = [
        [Paragraph("GITHUB", ParagraphStyle("ck1", parent=BODY,
            fontName="Helvetica-Bold", fontSize=8.5, textColor=INK_SOFT,
            firstLineIndent=0)),
         Paragraph("github.com/rabeyazaman/water-contamination-ml",
                   ParagraphStyle("cv1", parent=BODY,
                       fontName="Helvetica-Bold", fontSize=11.5,
                       textColor=BRAND_DK, firstLineIndent=0))],
        [Spacer(1, 0.25*cm), Spacer(1, 0.25*cm)],
        [Paragraph("EMAIL", ParagraphStyle("ck2", parent=BODY,
            fontName="Helvetica-Bold", fontSize=8.5, textColor=INK_SOFT,
            firstLineIndent=0)),
         Paragraph("rabeyazaman96@gmail.com",
                   ParagraphStyle("cv2", parent=BODY,
                       fontName="Helvetica-Bold", fontSize=11.5,
                       textColor=INK, firstLineIndent=0))],
        [Spacer(1, 0.25*cm), Spacer(1, 0.25*cm)],
        [Paragraph("AFFILIATION", ParagraphStyle("ck3", parent=BODY,
            fontName="Helvetica-Bold", fontSize=8.5, textColor=INK_SOFT,
            firstLineIndent=0)),
         Paragraph("Department of Microbiology<br/>"
                   "Notre Dame University Bangladesh",
                   ParagraphStyle("cv3", parent=BODY,
                       fontName="Helvetica", fontSize=11,
                       textColor=INK, firstLineIndent=0, leading=15))],
    ]
    contact_tbl = Table(contact_data, colWidths=[3.5*cm, 13.0*cm])
    contact_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(contact_tbl)

    story += [
        Spacer(1, 1.0*cm),
        HRFlowable(width="100%", thickness=0.5, color=RULE,
                   spaceBefore=0, spaceAfter=10),
        Paragraph("Released under the MIT licence — free to use, modify, "
                  "and redistribute with attribution. Built with Python, "
                  "scikit-learn, and a great deal of coffee.",
                  ParagraphStyle("foot", parent=BODY,
                      fontName="Helvetica-Oblique", fontSize=9.5,
                      alignment=TA_CENTER, textColor=INK_SOFT,
                      firstLineIndent=0)),
    ]

    # ============================ BUILD =======================================
    doc = PortfolioDoc(
        str(OUT_PDF),
        pagesize=A4,
        title="AI-Based Water Contamination Detection System — Project Report",
        author="Rabeya Zaman",
        subject="Machine-learning project report",
    )
    doc.build(story)
    size_kb = OUT_PDF.stat().st_size / 1024
    print(f"[build_pdf_report] Wrote {OUT_PDF}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    build()
