from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
sec = doc.sections[0]
sec.top_margin    = Cm(1.8)
sec.bottom_margin = Cm(1.8)
sec.left_margin   = Cm(2.0)
sec.right_margin  = Cm(2.0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def cell_bg(cell, hex_color):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def cell_border(cell, color='000000', sz='4'):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top', 'left', 'bottom', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), sz)
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), color)
        tcBorders.append(b)
    tcPr.append(tcBorders)

def set_col_widths(table, widths_cm):
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths_cm):
                cell.width = Cm(widths_cm[i])

def add_text(cell, text, bold=False, fs=9.5,
             align=WD_ALIGN_PARAGRAPH.LEFT, italic=False):
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run(text)
    r.bold   = bold
    r.italic = italic
    r.font.size = Pt(fs)
    r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

# =============================================================================
# TITLE
# =============================================================================
title = doc.add_heading('SHARP EV AI Chatbot', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

sub = doc.add_heading('Top 5 Assumptions, Risks & Dependencies', 2)
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = meta.add_run(
    'Prepared for: SHARP Business & Client Team   |   '
    'Date: 2026-06-23   |   Version: 1.0')
r.font.size = Pt(9)
r.font.italic = True

doc.add_paragraph()

# Purpose line
p = doc.add_paragraph()
r = p.add_run('Purpose: ')
r.bold = True; r.font.size = Pt(9.5)
r2 = p.add_run(
    'This document outlines the top 5 assumptions, risks, and dependencies '
    'that must be confirmed and managed to ensure successful delivery of the '
    'SHARP EV AI Chatbot project. Each item requires acknowledgement and '
    'action from SHARP before development begins.')
r2.font.size = Pt(9.5)

doc.add_paragraph()

# =============================================================================
# MAIN TABLE
# =============================================================================
data = [
    (
        '1',
        'EV Manual Quality',
        'SHARP provides EV manuals in clean, readable digital format.',
        'Poor quality documents cause the AI to give wrong or incomplete answers to customers.',
        'Confirm document format before project starts. If scanned images only, treat as a blocker before AI development begins.',
    ),
    (
        '2',
        'Vehicle Sensor Data Connection',
        'SHARP EV cars can send real-time data (battery level, fault codes, warnings) to the cloud.',
        'Self-Diagnosis feature cannot be built. Feature will be removed from Version 1 and pushed to a later release.',
        'Confirm if vehicle data connection exists. If not available, Self-Diagnosis will be image-only in Version 1.',
    ),
    (
        '3',
        'AI Service Approval',
        'Amazon AI services (Claude AI, Titan Embeddings) are approved and active on AWS Japan before development starts.',
        'All 4 chatbot features are blocked at the same time. No backup option is available in the current design.',
        'Submit AI service approval request at project start. Confirm activation before development begins.',
    ),
    (
        '4',
        'Open RFQ Values',
        'SHARP confirms all unanswered values from the RFQ — response accuracy, speed, number of users, usage limits, and answer length.',
        'System is built for the wrong scale. Rebuilding in the final weeks causes delays and extra cost.',
        'All open values must be confirmed in writing by SHARP before development starts.',
    ),
    (
        '5',
        'COCORO Login System',
        'SHARP provides COCORO MEMBERS ID login system technical details and test access before integration begins.',
        'Chatbot cannot go live without a working login. All user testing is blocked. SHARP security team will not approve go-live.',
        'Share COCORO technical specification and test credentials at project start. This is a hard requirement for launch.',
    ),
]

HEADERS  = ['#', 'Topic', 'Assumption', 'Risk if Not Met', 'Mitigation']
COL_W    = [0.7, 3.2, 4.0, 4.2, 4.1]

tbl = doc.add_table(rows=1 + len(data), cols=5)
tbl.style     = 'Table Grid'
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
set_col_widths(tbl, COL_W)

# Header row — light grey background, bold black text
hrow = tbl.rows[0]
for i, h in enumerate(HEADERS):
    c = hrow.cells[i]
    cell_bg(c, 'D9D9D9')
    cell_border(c, '000000', '6')
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    add_text(c, h, bold=True, fs=10, align=WD_ALIGN_PARAGRAPH.CENTER)

# Data rows — alternating white / very light grey
for ri, (num, topic, assumption, risk, mitigation) in enumerate(data):
    row  = tbl.rows[ri + 1]
    bg   = 'FFFFFF' if ri % 2 == 0 else 'F2F2F2'
    vals = [num, topic, assumption, risk, mitigation]

    for ci, val in enumerate(vals):
        c = row.cells[ci]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell_bg(c, bg)
        cell_border(c, '000000', '4')

        if ci == 0:
            add_text(c, val, bold=True, fs=11,
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        elif ci == 1:
            add_text(c, val, bold=True, fs=9.5)
        else:
            add_text(c, val, fs=9.5)

doc.add_paragraph()

# =============================================================================
# ACTION REQUIRED TABLE
# =============================================================================
h2 = doc.add_heading('Action Required from SHARP', 2)

actions = [
    ('1', 'EV Manuals',            'Provide digital PDF files with readable text'),
    ('2', 'Vehicle Data',          'Confirm if vehicle sensor data connection exists and share technical details'),
    ('3', 'AI Service Approval',   'Submit and confirm AWS Japan AI service activation'),
    ('4', 'Open RFQ Values',       'Provide written confirmation of all unanswered requirement items'),
    ('5', 'COCORO Login Details',  'Share COCORO MEMBERS ID specification and test credentials'),
]

act_tbl = doc.add_table(rows=1 + len(actions), cols=3)
act_tbl.style     = 'Table Grid'
act_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
set_col_widths(act_tbl, [0.7, 3.5, 12.0])

for i, h in enumerate(['#', 'Item', 'Action Required']):
    c = act_tbl.rows[0].cells[i]
    cell_bg(c, 'D9D9D9')
    cell_border(c, '000000', '6')
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    add_text(c, h, bold=True, fs=10, align=WD_ALIGN_PARAGRAPH.CENTER)

for ri, (num, item, action) in enumerate(actions):
    row = act_tbl.rows[ri + 1]
    bg  = 'FFFFFF' if ri % 2 == 0 else 'F2F2F2'
    for ci, val in enumerate([num, item, action]):
        c = row.cells[ci]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell_bg(c, bg)
        cell_border(c, '000000', '4')
        is_bold  = ci in [0, 1]
        is_center = ci == 0
        add_text(c, val, bold=is_bold, fs=9.5,
                 align=WD_ALIGN_PARAGRAPH.CENTER if is_center else WD_ALIGN_PARAGRAPH.LEFT)

# Footer
doc.add_paragraph()
fp = doc.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run(
    'All 5 items must be confirmed before development begins  '
    '|  SHARP EV AI Chatbot  |  Confidential')
r.font.size = Pt(8)
r.font.italic = True

# Save
output = '/home/ramram/Desktop/Personal/EV-Chatbot/archive/documents/SHARP_EV_Assumptions_Risks_Dependencies.docx'
doc.save(output)
print(f'Saved: {output}')
