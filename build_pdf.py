# -*- coding: utf-8 -*-
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether, NextPageTemplate, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfgen import canvas as pdfcanvas

with open("sanitized.json") as f:
    DATA = json.load(f)

INK = colors.HexColor("#14181f")
INK_SOFT = colors.HexColor("#5a6270")
BORDER = colors.HexColor("#e6e3db")
BG = colors.HexColor("#f6f5f2")
GOLD = colors.HexColor("#b5790a")

def is_light(hexstr):
    hexstr = hexstr.lstrip("#")
    r, g, b = int(hexstr[0:2],16), int(hexstr[2:4],16), int(hexstr[4:6],16)
    return (0.299*r + 0.587*g + 0.114*b) > 170

PAGE_W, PAGE_H = letter
MARGIN = 0.62 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

styles = getSampleStyleSheet()

st_title = ParagraphStyle("TitleBig", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=26, leading=30, textColor=INK, spaceAfter=8, alignment=TA_LEFT)
st_eyebrow = ParagraphStyle("Eyebrow", parent=styles["Normal"], fontName="Helvetica-Bold",
                             fontSize=9.5, leading=12, textColor=GOLD, spaceAfter=10,
                             leftIndent=0)
st_objective = ParagraphStyle("Objective", parent=styles["Normal"], fontName="Helvetica",
                               fontSize=11.5, leading=17, textColor=INK_SOFT, spaceAfter=14)
st_stat_num = ParagraphStyle("StatNum", parent=styles["Normal"], fontName="Helvetica-Bold",
                              fontSize=20, leading=22, textColor=INK)
st_stat_lbl = ParagraphStyle("StatLbl", parent=styles["Normal"], fontName="Helvetica",
                              fontSize=8, leading=10, textColor=INK_SOFT)
st_meta_lbl = ParagraphStyle("MetaLbl", parent=styles["Normal"], fontName="Helvetica-Bold",
                              fontSize=9, leading=12, textColor=INK)
st_meta_val = ParagraphStyle("MetaVal", parent=styles["Normal"], fontName="Helvetica",
                              fontSize=9.5, leading=13, textColor=INK_SOFT, spaceAfter=8)

def stage_header_style(accent):
    text_color = colors.HexColor("#1a1a1a") if is_light(accent) else colors.white
    return ParagraphStyle("StageHead", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=13.5, leading=16, textColor=text_color)

st_event = ParagraphStyle("Event", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=11.5, leading=14, spaceAfter=3)
st_trigger = ParagraphStyle("Trigger", parent=styles["Normal"], fontName="Helvetica-Oblique",
                             fontSize=8.7, leading=12, textColor=INK_SOFT, spaceAfter=6)
st_field_label = ParagraphStyle("FieldLabel", parent=styles["Normal"], fontName="Helvetica-Bold",
                                 fontSize=7.6, leading=10, spaceBefore=6, spaceAfter=2,
                                 textColor=INK_SOFT)
st_body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica",
                          fontSize=9, leading=12.5, textColor=INK)
st_small = ParagraphStyle("Small", parent=styles["Normal"], fontName="Helvetica",
                           fontSize=8.4, leading=11.5, textColor=INK_SOFT)
st_celebration = ParagraphStyle("Celebration", parent=styles["Normal"], fontName="Helvetica-Bold",
                                 fontSize=8.5, leading=11, textColor=colors.HexColor("#8a5a00"))

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def field_label_colored(text, accent):
    st = ParagraphStyle("FL_%s" % accent, parent=st_field_label, textColor=colors.HexColor(accent))
    return Paragraph(text.upper(), st)

def bullet_list(items, style=st_body, bullet="•"):
    return ListFlowable(
        [ListItem(Paragraph(esc(i), style), leftIndent=10, spaceBefore=1) for i in items],
        bulletType="bullet", start=bullet, leftIndent=12, bulletFontSize=7, bulletOffsetY=1,
    )

def number_list(items, style=st_body):
    return ListFlowable(
        [ListItem(Paragraph(esc(i), style), leftIndent=10, spaceBefore=1) for i in items],
        bulletType="1", leftIndent=12, bulletFontSize=8,
    )

def who_line(who):
    parts = []
    for w in who:
        role = esc(w["role"])
        if w.get("note"):
            parts.append(f"{role} <i>({esc(w['note'])})</i>")
        else:
            parts.append(role)
    return "  &middot;  ".join(parts)

def touchpoint_flowable(col, accent):
    content = [Paragraph(esc(col["event"]), st_event)]
    if col.get("trigger"):
        content.append(Paragraph(f"<b>TRIGGER</b> &nbsp; {esc(col['trigger'])}", st_trigger))
    if col.get("objectives"):
        content.append(field_label_colored("Objectives", accent))
        content.append(bullet_list(col["objectives"]))
    if col.get("who"):
        content.append(field_label_colored("Who's involved", accent))
        content.append(Paragraph(who_line(col["who"]), st_body))
    if col.get("key_activities"):
        content.append(field_label_colored("Key activities", accent))
        content.append(number_list(col["key_activities"]))
    tags_bits = []
    if col.get("templates"):
        tags_bits.append(("Templates & collateral", ", ".join(col["templates"])))
    if col.get("systems"):
        tags_bits.append(("Systems", ", ".join(col["systems"])))
    if col.get("metrics"):
        tags_bits.append(("Success metrics", ", ".join(col["metrics"])))
    if col.get("education"):
        tags_bits.append(("Education / training", ", ".join(col["education"])))
    if col.get("digital_assets"):
        tags_bits.append(("Digital assets", col["digital_assets"]))
    for label, val in tags_bits:
        content.append(field_label_colored(label, accent))
        content.append(Paragraph(esc(val), st_small))
    if col.get("celebration"):
        content.append(Spacer(1, 4))
        content.append(Paragraph("MOMENT OF VALUE / CELEBRATION", st_celebration))

    box = Table([[content]], colWidths=[CONTENT_W])
    box.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 11),
        ("BOX", (0,0), (-1,-1), 0.6, BORDER),
        ("LINEBEFORE", (0,0), (0,0), 3, colors.HexColor(accent)),
        ("BACKGROUND", (0,0), (-1,-1), colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    return KeepTogether([box, Spacer(1, 9)])

def stage_flowables(stage):
    accent = stage["color"]
    text_color = colors.HexColor("#1a1a1a") if is_light(accent) else colors.white
    n = len(stage["columns"])
    header_para_style = ParagraphStyle("SH", parent=styles["Normal"], fontName="Helvetica-Bold",
                                        fontSize=13.5, leading=16, textColor=text_color)
    count_style = ParagraphStyle("SHC", parent=styles["Normal"], fontName="Helvetica",
                                  fontSize=8.5, textColor=text_color, alignment=2)
    header_tbl = Table(
        [[Paragraph(esc(stage["title"]), header_para_style),
          Paragraph(f"{n} touchpoint{'s' if n != 1 else ''}", count_style)]],
        colWidths=[CONTENT_W*0.75, CONTENT_W*0.25]
    )
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(accent)),
        ("LEFTPADDING", (0,0), (0,0), 12), ("RIGHTPADDING", (1,0), (1,0), 12),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    flows = [header_tbl, Spacer(1, 10)]
    for col in stage["columns"]:
        flows.append(touchpoint_flowable(col, accent))
    flows.append(Spacer(1, 6))
    return flows

def collect_stats(sheet):
    roles, systems, touch = set(), set(), 0
    for st in sheet["stages"]:
        for c in st["columns"]:
            touch += 1
            for w in c.get("who", []):
                roles.add(w["role"])
            for s in c.get("systems", []):
                systems.add(s)
    return roles, systems, touch

roles1, systems1, touch1 = collect_stats(DATA["sheet1"])
roles2, systems2, touch2 = collect_stats(DATA["sheet2"])
meta1 = DATA["sheet1"]["meta"]

def stat_cell(num, label):
    return [Paragraph(str(num), st_stat_num), Paragraph(label.upper(), st_stat_lbl)]

stats_tbl = Table(
    [[stat_cell(len(DATA["sheet1"]["stages"]), "Journey stages"),
      stat_cell(touch1 + touch2, "Mapped touchpoints"),
      stat_cell(len(roles1), "Roles orchestrated"),
      stat_cell(len(systems1), "Systems of record")]],
    colWidths=[CONTENT_W/4.0]*4
)
stats_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), BG),
    ("LEFTPADDING", (0,0), (-1,-1), 14), ("TOPPADDING", (0,0), (-1,-1), 12),
    ("BOTTOMPADDING", (0,0), (-1,-1), 12), ("RIGHTPADDING", (0,0), (-1,-1), 6),
]))

def legend_drawing(stages):
    d = Drawing(CONTENT_W, 14)
    total = sum(max(len(s["columns"]), 1) for s in stages)
    x = 0
    for s in stages:
        w = CONTENT_W * (max(len(s["columns"]), 1) / total)
        d.add(Rect(x, 0, w, 14, fillColor=colors.HexColor(s["color"]), strokeColor=None))
        x += w
    return d

cover_flows = []
cover_flows.append(Spacer(1, 6))
cover_flows.append(Paragraph("CUSTOMER SUCCESS &middot; PORTFOLIO ARTIFACT", st_eyebrow))
cover_flows.append(Paragraph(esc(meta1["doc_name"] or "Customer Lifecycle Journey Map"), st_title))
cover_flows.append(Paragraph(esc(meta1["objective"]), st_objective))
cover_flows.append(Spacer(1, 4))
cover_flows.append(stats_tbl)
cover_flows.append(Spacer(1, 12))
cover_flows.append(legend_drawing(DATA["sheet1"]["stages"]))
cover_flows.append(Spacer(1, 22))

meta_tbl = Table([
    [Paragraph("PROCESS CHAMPION", st_meta_lbl), Paragraph("CORE STAKEHOLDERS", st_meta_lbl)],
    [Paragraph(esc(meta1["champion"]), st_meta_val), Paragraph(esc(meta1["stakeholders"]), st_meta_val)],
], colWidths=[CONTENT_W/2.0]*2)
meta_tbl.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0), ("TOPPADDING",(0,0),(-1,-1),2)]))
cover_flows.append(meta_tbl)
cover_flows.append(Spacer(1, 14))
cover_flows.append(Paragraph(
    "This document maps the end-to-end customer success lifecycle across seven stages, from new "
    "sales handoff through onboarding, adoption, value management, renewal risk, and expansion. "
    "A dedicated onboarding deep-dive follows, detailing the high-touch onboarding sub-journey. "
    "Names and internal tool references have been generalized for public sharing.",
    st_objective))
cover_flows.append(PageBreak())

story = list(cover_flows)
story.append(Paragraph("FULL CUSTOMER LIFECYCLE", ParagraphStyle(
    "SectionTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15,
    textColor=INK, spaceAfter=12)))
for stage in DATA["sheet1"]["stages"]:
    story.extend(stage_flowables(stage))

story.append(PageBreak())
story.append(Paragraph("ONBOARDING DEEP-DIVE", ParagraphStyle(
    "SectionTitle2", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15,
    textColor=INK, spaceAfter=4)))
meta2 = DATA["sheet2"]["meta"]
story.append(Paragraph(esc(meta2["objective"]), st_objective))
for stage in DATA["sheet2"]["stages"]:
    story.extend(stage_flowables(stage))

def on_page(c, doc):
    c.saveState()
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(MARGIN, 0.55*inch, PAGE_W - MARGIN, 0.55*inch)
    c.setFont("Helvetica", 8)
    c.setFillColor(INK_SOFT)
    c.drawString(MARGIN, 0.38*inch, "Customer Success Lifecycle Journey Map — Portfolio Sample")
    c.drawRightString(PAGE_W - MARGIN, 0.38*inch, f"Page {doc.page}")
    c.restoreState()

doc = BaseDocTemplate("Customer_Success_Journey_Map.pdf", pagesize=letter,
                       leftMargin=MARGIN, rightMargin=MARGIN, topMargin=0.6*inch, bottomMargin=0.75*inch)
frame = Frame(MARGIN, 0.75*inch, CONTENT_W, PAGE_H - 1.35*inch, id="normal")
doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=on_page)])
doc.build(story)
print("Wrote PDF")
