#!/usr/bin/env python3
"""
SHARP EV AI Chatbot — Simple High-Level Diagram (Japanese Customer)
Ultra-clean: Big icons · Minimal text · Japanese labels · 5-step flow
"""

_id = [2]
cells = []

def nid():
    v = str(_id[0]); _id[0] += 1; return v

def rect(x, y, w, h, label, fill, stroke, fc="#333333", fs=10, bold=0, arc=14, valign="middle"):
    i = nid()
    style = (f"rounded=1;arcSize={arc};whiteSpace=wrap;html=1;"
             f"fillColor={fill};strokeColor={stroke};fontColor={fc};"
             f"fontSize={fs};fontStyle={bold};verticalAlign={valign};"
             f"spacingTop=4;spacingBottom=4;")
    cells.append((i, f'<mxCell id="{i}" value="{label}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def txt(x, y, w, h, text, fs=10, fc="#333333", bold=0, align="center"):
    i = nid()
    style = (f"text;html=1;align={align};verticalAlign=middle;"
             f"strokeColor=none;fillColor=none;whiteSpace=wrap;"
             f"fontSize={fs};fontStyle={bold};fontColor={fc};")
    cells.append((i, f'<mxCell id="{i}" value="{text}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def badge(x, y, r, num, fill):
    i = nid()
    style = (f"ellipse;whiteSpace=wrap;html=1;"
             f"fillColor={fill};strokeColor=#ffffff;strokeWidth=3;"
             f"fontColor=#FFFFFF;fontSize=20;fontStyle=1;verticalAlign=middle;")
    cells.append((i, f'<mxCell id="{i}" value="{num}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{r}" height="{r}" as="geometry" /></mxCell>'))
    return i

def aws_icon(x, y, size, res_icon, fill):
    i = nid()
    style = (f"outlineConnect=0;gradientColor=none;strokeColor=none;"
             f"fillColor={fill};shape=mxgraph.aws4.resourceIcon;resIcon={res_icon};"
             f"labelPosition=none;verticalLabelPosition=none;")
    cells.append((i, f'<mxCell id="{i}" value="" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{size}" height="{size}" as="geometry" /></mxCell>'))
    return i

def arrow(src, tgt, color="#BDBDBD"):
    i = nid()
    style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;"
             f"strokeColor={color};strokeWidth=4;"
             f"endArrow=block;endFill=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
             f"entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    cells.append((i, f'<mxCell id="{i}" value="" style="{style}" '
                  f'edge="1" source="{src}" target="{tgt}" parent="1">'
                  f'<mxGeometry relative="1" as="geometry" /></mxCell>'))
    return i

# ── Colours ────────────────────────────────────────────────────────────────────
STEP_COLORS = [
    ("#E3F2FD", "#1565C0", "#1565C0"),   # 1 blue
    ("#EDE7F6", "#6A1B9A", "#6A1B9A"),   # 2 purple
    ("#E0F7FA", "#00695C", "#00695C"),   # 3 teal
    ("#E8F5E9", "#1B5E20", "#1B5E20"),   # 4 green
    ("#FFF3E0", "#E65100", "#E65100"),   # 5 orange
]
AWS_NETWORK = "#8C4FFF"
AWS_ML      = "#01A88D"
AWS_STORAGE = "#3F8624"
AWS_SEC     = "#DD344C"
AWS_COMPUTE = "#E7157B"

F_DIAG = "#C62828"; F_EV = "#1565C0"; F_CHAT = "#2E7D32"; F_AUTO = "#E65100"

# =============================================================================
# TITLE
# =============================================================================
ttl = nid()
cells.append((ttl,
    f'<mxCell id="{ttl}" '
    f'value="SHARP EV AI Chatbot  —  How It Works" '
    f'style="text;html=1;align=center;verticalAlign=middle;'
    f'fontSize=22;fontStyle=1;fontColor=#1F497D;" '
    f'vertex="1" parent="1">'
    f'<mxGeometry x="50" y="14" width="1540" height="38" as="geometry" /></mxCell>'))

sub = nid()
cells.append((sub,
    f'<mxCell id="{sub}" '
    f'value="Your Question  →  AWS Cloud  →  AI Answer" '
    f'style="text;html=1;align=center;verticalAlign=middle;'
    f'fontSize=13;fontStyle=2;fontColor=#888888;" '
    f'vertex="1" parent="1">'
    f'<mxGeometry x="50" y="52" width="1540" height="22" as="geometry" /></mxCell>'))

# =============================================================================
# 5 STEP BLOCKS  (y = 85 → 410)
# =============================================================================
BW = 268; BH = 315; GAP = 44; SY = 85
BX = [55 + i*(BW+GAP) for i in range(5)]
# 55 + 4*(268+44) = 55 + 1248 = 1303 + 268 = 1571  ✓ fits in 1640

steps = [
    # (title, subtitle, description, note, aws_icons)
    (
        "Your EV &amp; You",
        "Connect",
        "Your EV car automatically sends&#xa;sensor data to the cloud.&#xa;Open the SHARP EV App to begin.",
        "Secure login via your COCORO account",
        [("mxgraph.aws4.iot_core", AWS_NETWORK),
         ("mxgraph.aws4.cognito",  AWS_SEC)]
    ),
    (
        "Ask a Question",
        "Any Way You Like",
        "Type a message, speak out loud,&#xa;or take a photo of a warning&#xa;light or dashboard error.",
        "Voice is converted to text automatically",
        [("mxgraph.aws4.transcribe",  AWS_ML),
         ("mxgraph.aws4.rekognition", AWS_ML)]
    ),
    (
        "AI Understands",
        "Smart Processing",
        "Advanced AI (Claude 3) reads&#xa;your question and decides&#xa;exactly what to look up.",
        "Handles text, voice and images",
        [("mxgraph.aws4.bedrock",   AWS_ML),
         ("mxgraph.aws4.sagemaker", AWS_ML)]
    ),
    (
        "Find the Right Info",
        "Knowledge Search",
        "AI searches the correct source —&#xa;EV manual, fault code database,&#xa;or automotive knowledge library.",
        "Only verified information is used",
        [("mxgraph.aws4.kendra",             AWS_ML),
         ("mxgraph.aws4.opensearch_service",  AWS_ML)]
    ),
    (
        "Get Your Answer",
        "Clear Response",
        "A clear, personalised answer&#xa;arrives as text on screen,&#xa;spoken aloud, or as a report.",
        "Chat history remembered for context",
        [("mxgraph.aws4.polly",    AWS_ML),
         ("mxgraph.aws4.dynamodb", AWS_STORAGE)]
    ),
]

block_ids = []
for i, (title, subtitle, desc, note, icons) in enumerate(steps):
    fill, stroke, fc = STEP_COLORS[i]

    # Block background
    b = rect(BX[i], SY, BW, BH, "", fill, stroke, arc=16)
    block_ids.append(b)

    # Coloured top header band
    rect(BX[i], SY, BW, 50, "", stroke, stroke, "#FFFFFF", 13, 1, 8, "middle")

    # Step number badge (top-left of header)
    badge(BX[i]+8, SY+7, 36, str(i+1), "rgba(255,255,255,0.25)")

    # Title in header
    txt(BX[i]+52, SY+8, BW-60, 34, title, 13, "#FFFFFF", 1)

    # Large AWS icons (centred)
    ICON_SZ = 72
    icon_total_w = len(icons) * ICON_SZ + (len(icons)-1) * 22
    icon_start_x = BX[i] + (BW - icon_total_w) // 2
    for k, (res, col) in enumerate(icons):
        aws_icon(icon_start_x + k*(ICON_SZ+22), SY+60, ICON_SZ, res, col)

    # Subtitle tag
    txt(BX[i]+10, SY+142, BW-20, 20, subtitle, 9, stroke, 2)

    # Thin divider
    div = nid()
    cells.append((div,
        f'<mxCell id="{div}" value="" '
        f'style="line;strokeColor={stroke};fillColor=none;strokeWidth=1;opacity=40;" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="{BX[i]+20}" y="{SY+164}" width="{BW-40}" height="2" as="geometry" /></mxCell>'))

    # Description (3 lines)
    txt(BX[i]+10, SY+170, BW-20, 70, desc, 10, fc, 0)

    # Note (italic small)
    txt(BX[i]+10, SY+248, BW-20, 24, note, 8, "#888888", 2)

    # AWS service name strip at bottom
    svc_names = " · ".join(
        r.replace("mxgraph.aws4.", "").replace("_", " ").replace("opensearch service","OpenSearch").title()
        for r, _ in icons
    )
    txt(BX[i]+10, SY+275, BW-20, 32, f"AWS: {svc_names}", 7, "#AAAAAA", 0)

# Connector arrows between blocks
for i in range(4):
    arrow(block_ids[i], block_ids[i+1], STEP_COLORS[i][1])

# =============================================================================
# 4 FEATURE CARDS  (y = 415 → 530)
# =============================================================================
txt(55, 413, 1540, 22, "4 Built-in Features", 12, "#333333", 1)

FW = 371; FH = 105; FY = 437; FGap = 14
FX = [55 + i*(FW+FGap) for i in range(4)]

features = [
    (F_DIAG, "Car Problem — Self-Diagnosis",
     "Take a photo or describe the issue.",
     "AI reads your car sensor data and gives a diagnosis with recommended action.",
     "mxgraph.aws4.rekognition", AWS_ML),
    (F_EV,   "EV Manual — Usage Help",
     "Ask anything about your SHARP EV.",
     "AI searches the official EV manual and gives the exact answer with page reference.",
     "mxgraph.aws4.kendra", AWS_ML),
    (F_CHAT, "General Chat — Ask Anything",
     "Type or speak — chat freely.",
     "Claude 3 AI answers any question in a natural, conversational way.",
     "mxgraph.aws4.bedrock", AWS_ML),
    (F_AUTO, "Car Advice — Auto Guidance",
     "Ask for driving tips or EV advice.",
     "AI searches a curated automotive knowledge library for expert guidance.",
     "mxgraph.aws4.s3", AWS_STORAGE),
]

for i, (fc, name, short_desc, long_desc, res, icon_fill) in enumerate(features):
    # Card background
    rect(FX[i], FY, FW, FH, "", "#FAFAFA", fc, arc=10)
    # Coloured header
    rect(FX[i], FY, FW, 34, "", fc, fc, "#FFFFFF", 11, 1, 6, "middle")
    txt(FX[i]+8, FY+2, FW-16, 32, name, 11, "#FFFFFF", 1)
    # Description lines
    txt(FX[i]+8, FY+37, FW-72, 20, short_desc, 9, fc, 1, "left")
    txt(FX[i]+8, FY+57, FW-72, 36, long_desc,  8, "#666666", 0, "left")
    # AWS icon (right side of card)
    aws_icon(FX[i]+FW-65, FY+35, 56, res, icon_fill)

# =============================================================================
# SECURITY + FOOTER  (y = 552 → 600)
# =============================================================================
sec_bg = rect(55, 550, 1540, 48, "", "#FFEBEE", "#DD344C", "#B71C1C", 9, 0, 8)
aws_icon(62, 553, 40, "mxgraph.aws4.waf",       AWS_SEC)
aws_icon(108, 553, 40, "mxgraph.aws4.shield",   AWS_SEC)
aws_icon(154, 553, 40, "mxgraph.aws4.guardduty",AWS_SEC)
txt(200, 553, 1050, 48,
    "Security: All data encrypted in transit &amp; at rest  ·  COCORO MEMBERS ID login  ·  "
    "AWS WAF · Shield · GuardDuty  ·  METI AI Guidelines compliant  ·  Full audit logging",
    8, "#B71C1C", 0, "left")

# SHARP branding
sharp = nid()
cells.append((sharp,
    f'<mxCell id="{sharp}" value="SHARP" '
    f'style="text;html=1;align=right;verticalAlign=middle;'
    f'fontSize=28;fontStyle=1;fontColor=#CC0000;" '
    f'vertex="1" parent="1">'
    f'<mxGeometry x="1430" y="550" width="165" height="48" as="geometry" /></mxCell>'))

# =============================================================================
# BUILD XML
# =============================================================================
cell_xml = "\n        ".join(c[1] for c in cells)

xml = f'''<mxfile host="app.diagrams.net" modified="2026-06-19" agent="SHARP-EV-SA" version="21.0.0">
  <diagram name="SHARP EV Simple Overview" id="sharp-ev-simple">
    <mxGraphModel dx="1700" dy="750" grid="0" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="1660" pageHeight="640" math="0" shadow="1">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {cell_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

output = "/home/ramram/Desktop/Personal/EV-Chatbot/SHARP_EV_HighLevel_Diagram.drawio"
with open(output, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"Saved: {output}")
print(f"Total elements: {_id[0] - 2}")
