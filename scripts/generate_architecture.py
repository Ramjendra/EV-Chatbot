#!/usr/bin/env python3
"""
SHARP EV AI Chatbot — Multi-modal RAG Architecture (draw.io)
─────────────────────────────────────────────────────────────
Band 1 (top)    : OFFLINE Knowledge Indexing Pipeline (batch)
Band 2 (middle) : ONLINE Multi-modal RAG Query Pipeline (real-time)
Band 3 (bottom) : Infrastructure — Storage · Security · Auth · Monitoring
Left            : EV Vehicle + User input sources
Right           : Response output delivery
"""

# ── Colour Palette ─────────────────────────────────────────────────────────────
# AWS service colours
C_NETWORK   = "#8C4FFF"   # IoT Core, API GW, Kinesis, CloudFront
C_COMPUTE   = "#E7157B"   # Lambda, Step Functions, SQS
C_ML        = "#01A88D"   # Bedrock, SageMaker, Rekognition, Transcribe, Polly
C_STORAGE   = "#3F8624"   # S3, DynamoDB, Aurora, OpenSearch
C_SECURITY  = "#DD344C"   # Cognito, WAF, Shield, GuardDuty
C_MONITOR   = "#AF3D8F"   # CloudWatch, X-Ray, CloudTrail
C_EV        = "#1565C0"   # EV device / input boxes
C_EMBED     = "#00695C"   # Embedding model boxes (darker teal)
C_VECTOR    = "#1A237E"   # Vector store / retrieval (dark blue)
C_AUGMENT   = "#4A148C"   # Prompt augmentation (deep purple)
C_LLM       = "#BF360C"   # Multi-modal LLM (deep orange)
C_OUTPUT    = "#37474F"   # Output delivery boxes
C_DATASRC   = "#4E342E"   # Data source boxes (brown)

# Feature colours (4 chatbot modules)
F_DIAG      = "#C62828"   # Self-diagnosis        (red)
F_EV_CON    = "#1565C0"   # EV Usage Consultation (blue)
F_CHAT      = "#2E7D32"   # Chat                  (green)
F_AUTO      = "#E65100"   # General Auto Guidance (orange)

# Zone background fills
Z_OFFLINE   = "#FFF8E1"   # Offline pipeline band
Z_ONLINE    = "#E8F5E9"   # Online RAG pipeline band
Z_INFRA     = "#FFEBEE"   # Infrastructure band
Z_EV_ZONE   = "#E3F2FD"   # EV/user zone
Z_OUTPUT_Z  = "#F3E5F5"   # Output zone

Z_DATASRC   = "#FFF3E0"
Z_DOCPROC   = "#EDE7F6"
Z_EMBED_Z   = "#E0F7FA"
Z_VECSTORE  = "#E8F5E9"
Z_INPUTS    = "#E3F2FD"
Z_QEMBED    = "#E0F7FA"
Z_RETRIEVAL = "#E8EAF6"
Z_AUGMENT_Z = "#FCE4EC"
Z_LLM_Z     = "#FBE9E7"

_id = [2]
cells = []

def nid():
    v = str(_id[0]); _id[0] += 1; return v

def zone(x, y, w, h, label, fill, stroke, fc="#000000", fs=10, dashed=0, stroke_w=2):
    i = nid()
    dash = "dashed=1;" if dashed else ""
    style = (f"rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;spacingTop=6;"
             f"fillColor={fill};strokeColor={stroke};fontColor={fc};"
             f"fontSize={fs};fontStyle=1;strokeWidth={stroke_w};{dash}")
    cells.append((i, f'<mxCell id="{i}" value="{label}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def box(x, y, w, h, label, fill, stroke=None, fc="#FFFFFF", fs=8, bold=1, arc=12):
    i = nid()
    if stroke is None: stroke = fill
    style = (f"rounded=1;arcSize={arc};whiteSpace=wrap;html=1;"
             f"fillColor={fill};strokeColor={stroke};fontColor={fc};"
             f"fontSize={fs};fontStyle={bold};verticalAlign=middle;"
             f"spacingLeft=3;spacingRight=3;")
    cells.append((i, f'<mxCell id="{i}" value="{label}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def badge(x, y, w, h, text, fill):
    i = nid()
    style = (f"rounded=1;arcSize=30;whiteSpace=wrap;html=1;"
             f"fillColor={fill};strokeColor={fill};fontColor=#FFFFFF;"
             f"fontSize=7;fontStyle=1;verticalAlign=middle;")
    cells.append((i, f'<mxCell id="{i}" value="{text}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def txt(x, y, w, h, text, fs=9, fc="#333333", bold=0, align="center"):
    i = nid()
    style = (f"text;html=1;align={align};verticalAlign=middle;resizable=0;"
             f"strokeColor=none;fillColor=none;"
             f"fontSize={fs};fontStyle={bold};fontColor={fc};")
    cells.append((i, f'<mxCell id="{i}" value="{text}" style="{style}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>'))
    return i

def arrow(src, tgt, lbl="", color="#666666", thick=1.5, dashed=0,
          ex=1, ey=0.5, nx=0, ny=0.5):
    i = nid()
    dash = "dashed=1;dashPattern=8 4;" if dashed else ""
    style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
             f"strokeColor={color};strokeWidth={thick};fontSize=7;fontColor=#333333;"
             f"exitX={ex};exitY={ey};exitDx=0;exitDy=0;"
             f"entryX={nx};entryY={ny};entryDx=0;entryDy=0;{dash}")
    cells.append((i, f'<mxCell id="{i}" value="{lbl}" style="{style}" '
                  f'edge="1" source="{src}" target="{tgt}" parent="1">'
                  f'<mxGeometry relative="1" as="geometry" /></mxCell>'))
    return i

def arrow_free(src, tgt, lbl="", color="#666666", thick=1.5, dashed=0):
    i = nid()
    dash = "dashed=1;dashPattern=8 4;" if dashed else ""
    style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor={color};"
             f"strokeWidth={thick};fontSize=7;fontColor=#333333;{dash}")
    cells.append((i, f'<mxCell id="{i}" value="{lbl}" style="{style}" '
                  f'edge="1" source="{src}" target="{tgt}" parent="1">'
                  f'<mxGeometry relative="1" as="geometry" /></mxCell>'))
    return i

# =============================================================================
# PAGE TITLE
# =============================================================================
ttl = nid()
cells.append((ttl,
    f'<mxCell id="{ttl}" value="SHARP EV AI Chatbot — Multi-modal RAG Architecture (AWS)" '
    f'style="text;html=1;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#1F497D;" '
    f'vertex="1" parent="1"><mxGeometry x="350" y="8" width="1400" height="32" as="geometry" /></mxCell>'))

sub = nid()
cells.append((sub,
    f'<mxCell id="{sub}" value="Text · Voice · Image → Embedding → Vector Retrieval → Prompt Augmentation → Multi-modal LLM (Bedrock Claude 3) → Response" '
    f'style="text;html=1;align=center;verticalAlign=middle;fontSize=10;fontStyle=2;fontColor=#555;" '
    f'vertex="1" parent="1"><mxGeometry x="350" y="40" width="1400" height="18" as="geometry" /></mxCell>'))

# =============================================================================
# BAND 1 — OFFLINE KNOWLEDGE INDEXING PIPELINE
# =============================================================================
zone(18, 62, 2064, 330, "  BAND 1 — OFFLINE KNOWLEDGE BASE INDEXING PIPELINE (Batch / Scheduled)",
     Z_OFFLINE, "#F57F17", "#E65100", 10)

# ── Stage 1: Data Sources ────────────────────────────────────────────────────
zone(30, 98, 195, 278, "Data Sources", Z_DATASRC, C_DATASRC, "#3E2723", 9)
ds_manual   = box(42, 128, 171, 46, "EV Manuals&#xa;(PDF / HTML)", C_DATASRC, "#3E2723")
ds_images   = box(42, 184, 171, 46, "Vehicle Diagrams&#xa;&amp; Warning Light Images", C_DATASRC, "#3E2723")
ds_faults   = box(42, 240, 171, 46, "Fault Code Registry&#xa;(OBD-II / CAN Bus DB)", C_DATASRC, "#3E2723")
ds_auto_kb  = box(42, 296, 171, 46, "Automotive Knowledge&#xa;Base (3rd-party)", C_DATASRC, "#3E2723")
badge(38, 128, 70, 13, "EV USAGE", F_EV_CON); badge(38, 183, 70, 13, "SELF-DIAG", F_DIAG)
badge(38, 239, 70, 13, "SELF-DIAG", F_DIAG);  badge(38, 295, 70, 13, "AUTO GUIDE", F_AUTO)

# ── Stage 2: Document Processing ─────────────────────────────────────────────
zone(242, 98, 195, 278, "Document Processing", Z_DOCPROC, C_COMPUTE, "#880E4F", 9)
dp_textract = box(254, 128, 171, 46, "Amazon Textract&#xa;(PDF OCR / Table Extract)", C_COMPUTE, "#AD1457")
dp_glue     = box(254, 184, 171, 46, "AWS Glue&#xa;(ETL + Data Normalise)", C_COMPUTE, "#AD1457")
dp_chunker  = box(254, 240, 171, 46, "Lambda Chunker&#xa;(512-token splits + overlap)", C_COMPUTE, "#AD1457")
dp_s3_raw   = box(254, 296, 171, 46, "Amazon S3&#xa;(Raw Document Store)", C_STORAGE, "#2E7D32")

# ── Stage 3: Embedding Generation ────────────────────────────────────────────
zone(454, 98, 420, 278, "Multi-modal Embedding Generation", Z_EMBED_Z, C_ML, "#004D40", 9)

# Left: Text embeddings
em_titan_t  = box(466, 128, 185, 46, "Bedrock Titan Text&#xa;Embeddings v2 (1536-dim)", C_EMBED, "#00695C")
em_titan_mm = box(466, 184, 185, 46, "Bedrock Titan Multimodal&#xa;Embeddings (1024-dim)", C_EMBED, "#00695C")
em_claude3  = box(466, 240, 185, 46, "Bedrock Claude 3 Vision&#xa;(Image → Text Description)", C_ML, "#00695C")
em_cohere   = box(466, 296, 185, 46, "Cohere Embed v3&#xa;(Multilingual / Fallback)", C_ML, "#00695C")

# Right: feature mapping badges
badge(658, 132, 200, 13, "EV Manuals · Fault KB · Automotive KB", F_EV_CON)
badge(658, 188, 200, 13, "Vehicle Images · Warning Light Photos", F_DIAG)
badge(658, 244, 200, 13, "Convert image to embeddable text (SELF-DIAG)", F_DIAG)
badge(658, 300, 200, 13, "All text content · multilingual support", F_CHAT)

# ── Stage 4: Vector Index ────────────────────────────────────────────────────
zone(882, 98, 205, 278, "Vector Store (Index)", Z_VECSTORE, C_VECTOR, "#1A237E", 9)
vs_opensearch = box(894, 128, 181, 65, "Amazon OpenSearch&#xa;Serverless&#xa;(kNN Vector Index)", C_VECTOR, "#283593")
vs_metadata   = box(894, 206, 181, 40, "DynamoDB&#xa;(Chunk Metadata + Doc IDs)", C_STORAGE, "#2E7D32")
vs_s3_chunks  = box(894, 256, 181, 40, "S3 (Chunk Store +&#xa;Source Document Cache)", C_STORAGE, "#2E7D32")
vs_lambda_idx = box(894, 308, 181, 40, "Lambda Index Manager&#xa;(Incremental Updates)", C_COMPUTE, "#AD1457")

# ── Offline Pipeline Arrows ───────────────────────────────────────────────────
arrow(ds_manual,  dp_textract, "Raw PDF",     C_DATASRC, 1.5)
arrow(ds_images,  dp_glue,     "Images",      C_DATASRC, 1.5)
arrow(ds_faults,  dp_chunker,  "Structs",     C_DATASRC, 1.5)
arrow(ds_auto_kb, dp_s3_raw,   "Docs",        C_DATASRC, 1.5)

arrow(dp_textract, em_titan_t,  "Text Chunks", C_COMPUTE, 1.5)
arrow(dp_glue,     em_titan_mm, "Images",      C_COMPUTE, 1.5)
arrow(dp_chunker,  em_claude3,  "Img+Text",    C_COMPUTE, 1.5)
arrow(dp_s3_raw,   em_cohere,   "Docs",        C_COMPUTE, 1.5)

arrow(em_titan_t,  vs_opensearch, "Text Vec",      C_EMBED, 1.5)
arrow(em_titan_mm, vs_opensearch, "Image Vec",     C_EMBED, 1.5)
arrow(em_claude3,  vs_opensearch, "Desc Vec",      C_ML,    1.5)
arrow(em_cohere,   vs_metadata,   "Multi-lang Vec",C_ML,    1.5)
arrow(vs_lambda_idx, vs_opensearch, "Index",       C_COMPUTE, 1.5, 0, 0.5, 1, 0.5, 0)

# =============================================================================
# BAND 2 — ONLINE MULTI-MODAL RAG QUERY PIPELINE
# =============================================================================
zone(18, 400, 2064, 380, "  BAND 2 — ONLINE MULTI-MODAL RAG QUERY PIPELINE (Real-time)",
     Z_ONLINE, "#1B5E20", "#2E7D32", 10)

# ── Stage A: Multi-modal User Inputs ────────────────────────────────────────
zone(30, 435, 195, 328, "Multi-modal Inputs", Z_INPUTS, C_EV, "#0D47A1", 9)
in_text     = box(42, 462, 171, 42, "Text Query&#xa;(Chat · EV · Auto)", C_EV, "#0D47A1")
in_voice    = box(42, 514, 171, 42, "Voice Input&#xa;(Japanese / Multilingual)", C_EV, "#0D47A1")
in_image    = box(42, 566, 171, 42, "Image Upload&#xa;(Warning Light · Damage Photo)", C_EV, "#0D47A1")
in_telemetry= box(42, 618, 171, 42, "Vehicle Telemetry&#xa;(IoT — Fault Codes / Sensors)", C_NETWORK, "#6A1B9A")
in_stt      = box(42, 670, 171, 42, "Amazon Transcribe&#xa;(STT: Voice → Text)", C_ML, "#00695C")
badge(38, 463, 70, 12, "ALL MODULES", "#555555"); badge(38, 515, 70, 12, "ALL MODULES", "#555555")
badge(38, 567, 70, 12, "SELF-DIAG", F_DIAG);     badge(38, 619, 70, 12, "SELF-DIAG", F_DIAG)

# ── Stage B: Query Embedding ─────────────────────────────────────────────────
zone(242, 435, 205, 328, "Query Embedding", Z_QEMBED, C_ML, "#004D40", 9)
qe_api_gw   = box(254, 462, 181, 40, "Amazon API Gateway&#xa;+ AWS Lambda (Router)", C_NETWORK, "#6A1B9A")
qe_cognito  = box(254, 512, 181, 30, "Amazon Cognito Auth&#xa;(COCORO MEMBERS ID)", C_SECURITY, "#B71C1C")
qe_text_emb = box(254, 555, 181, 45, "Bedrock Titan Text Emb v2&#xa;(User text → 1536-dim vector)", C_EMBED, "#00695C")
qe_mm_emb   = box(254, 610, 181, 45, "Bedrock Titan Multimodal Emb&#xa;(Image → 1024-dim vector)", C_EMBED, "#00695C")
qe_waf      = box(254, 665, 181, 30, "AWS WAF + Rate Limiter&#xa;(Geo-block · Token Guard)", C_SECURITY, "#B71C1C")

# ── Stage C: Retrieval ────────────────────────────────────────────────────────
zone(464, 435, 220, 328, "Retrieval (kNN)", Z_RETRIEVAL, C_VECTOR, "#1A237E", 9)
rt_lambda   = box(476, 462, 196, 42, "Lambda Retriever&#xa;(Multi-modal query builder)", C_COMPUTE, "#AD1457")
rt_knn      = box(476, 516, 196, 55, "OpenSearch kNN Search&#xa;(Top-K similarity, cosine)&#xa;← same index as Band 1", C_VECTOR, "#283593")
rt_rerank   = box(476, 583, 196, 42, "Cohere Rerank v3&#xa;(Re-score Top-K results)", "#5C6BC0", "#3949AB")
rt_filter   = box(476, 637, 196, 42, "Metadata Filter&#xa;(Model / Module / Date)", "#5C6BC0", "#3949AB")
rt_hist     = box(476, 691, 196, 38, "DynamoDB&#xa;(Conversation History Lookup)", C_STORAGE, "#2E7D32")
badge(472, 516, 80, 12, "SHARED VECTOR STORE", C_VECTOR)

# ── Stage D: Prompt Augmentation ────────────────────────────────────────────
zone(701, 435, 215, 328, "Prompt Augmentation", Z_AUGMENT_Z, C_AUGMENT, "#4A148C", 9)
aug_prompt  = box(713, 462, 191, 42, "Lambda Prompt Builder&#xa;(Assemble augmented prompt)", C_AUGMENT, "#4A148C")
aug_chunks  = box(713, 516, 191, 42, "Retrieved Chunks&#xa;(Top-K passages + metadata)", "#6A1B9A", "#4A148C")
aug_sys     = box(713, 570, 191, 42, "System Prompt Templates&#xa;(Per-module instructions)", "#6A1B9A", "#4A148C")
aug_guard   = box(713, 624, 191, 42, "Amazon Bedrock Guardrails&#xa;(Input + Output safety check)", C_SECURITY, "#B71C1C")
aug_hist    = box(713, 678, 191, 38, "Conversation Context&#xa;(Last N turns injected)", "#AB47BC", "#7B1FA2")

aug_template_label = txt(713, 720, 191, 18,
    "Prompt = [System] + [History] + [Chunks] + [Query]",
    7, "#4A148C", 1)

# ── Stage E: Multi-modal LLM ─────────────────────────────────────────────────
zone(933, 435, 235, 328, "Multi-modal LLM", Z_LLM_Z, C_LLM, "#BF360C", 9)
llm_bedrock = box(945, 462, 211, 60, "Amazon Bedrock&#xa;Claude 3 Sonnet / Haiku&#xa;(Text + Image input, multi-modal)", C_LLM, "#BF360C")
llm_router  = box(945, 534, 211, 42, "Feature Router Lambda&#xa;Self-diag · EV-Usage · Chat · Auto", C_COMPUTE, "#AD1457")
llm_sm      = box(945, 588, 211, 42, "SageMaker Endpoint&#xa;(Custom fault-diagnosis model)", C_ML, "#00695C")
llm_cache   = box(945, 642, 211, 42, "Amazon ElastiCache&#xa;(Semantic response cache)", C_STORAGE, "#2E7D32")
llm_token   = box(945, 696, 211, 38, "Usage Tracker Lambda&#xa;(XX req/month quota enforcement)", C_COMPUTE, "#AD1457")
badge(941, 463, 80, 12, "GENERATOR (RAG)", C_LLM)
badge(941, 589, 80, 12, "SELF-DIAG ONLY", F_DIAG)

# ── Stage F: Output Delivery ─────────────────────────────────────────────────
zone(1185, 435, 210, 328, "Response Delivery", Z_OUTPUT_Z, "#4A148C", "#7B1FA2", 9)
out_text    = box(1197, 462, 186, 42, "Text Response&#xa;(Chat · EV Manual · Auto Guide)", "#7B1FA2", "#4A148C")
out_voice   = box(1197, 516, 186, 42, "Amazon Polly (TTS)&#xa;Voice Response Output", C_ML, "#00695C")
out_diag    = box(1197, 570, 186, 42, "Diagnosis Report&#xa;(Fault + Severity + Action)", F_DIAG, "#B71C1C")
out_ev      = box(1197, 624, 186, 42, "EV Manual Answer&#xa;(Passage + Page Ref + URL)", F_EV_CON, "#0D47A1")
out_notif   = box(1197, 678, 186, 38, "Amazon SNS&#xa;(Push Notification / Alert)", C_NETWORK, "#6A1B9A")
badge(1193, 463, 80, 12, "ALL MODULES", "#555555")
badge(1193, 517, 80, 12, "ALL MODULES", "#555555")
badge(1193, 571, 80, 12, "SELF-DIAG", F_DIAG)
badge(1193, 625, 80, 12, "EV USAGE", F_EV_CON)

# ── Online Pipeline Arrows ────────────────────────────────────────────────────
# Inputs → Query Embedding
arrow(in_text,      qe_api_gw,   "Query",      C_EV, 1.5)
arrow(in_voice,     in_stt,      "Audio",      C_ML, 1.5, 0, 1, 0.5, 0, 0.5)
arrow(in_stt,       qe_api_gw,   "Transcript", C_ML, 1.5)
arrow(in_image,     qe_api_gw,   "Image",      C_EV, 1.5)
arrow(in_telemetry, qe_api_gw,   "IoT Data",   C_NETWORK, 1.5)
arrow(qe_api_gw,    qe_cognito,  "Auth check", C_SECURITY, 1.5, 0, 1, 0.5, 0, 0.5)
arrow(qe_api_gw,    qe_text_emb, "Text→Embed", C_EMBED, 1.5)
arrow(qe_api_gw,    qe_mm_emb,   "Img→Embed",  C_EMBED, 1.5)
arrow(qe_api_gw,    qe_waf,      "Validate",   C_SECURITY, 1.5, 0, 1, 0.5, 0, 0.5)

# Query Embedding → Retrieval
arrow(qe_text_emb, rt_lambda,  "Text Vec",   C_EMBED, 1.5)
arrow(qe_mm_emb,   rt_lambda,  "Image Vec",  C_EMBED, 1.5)
arrow(rt_lambda,   rt_knn,     "kNN Query",  C_VECTOR, 2.0)
arrow(rt_knn,      rt_rerank,  "Top-K Hits", C_VECTOR, 1.5)
arrow(rt_rerank,   rt_filter,  "Re-scored",  "#5C6BC0", 1.5)
arrow(rt_filter,   rt_hist,    "Fetch Hist", C_STORAGE, 1.5, 0, 1, 0.5, 0, 0.5)

# Retrieval → Augmentation
arrow(rt_rerank,   aug_chunks, "Retrieved Chunks", C_VECTOR, 2.0)
arrow(rt_hist,     aug_hist,   "History",          C_STORAGE, 1.5)
arrow(aug_chunks,  aug_prompt, "Inject Context",   C_AUGMENT, 1.5)
arrow(aug_sys,     aug_prompt, "System Prompt",    C_AUGMENT, 1.5)
arrow(aug_hist,    aug_prompt, "History",          C_AUGMENT, 1.5)
arrow(aug_prompt,  aug_guard,  "Check Input",      C_SECURITY, 1.5)

# Augmentation → LLM
arrow(aug_guard,   llm_bedrock, "Augmented Prompt", C_LLM, 2.0)
arrow(llm_bedrock, llm_router,  "Raw Response",     C_LLM, 1.5)
arrow(llm_router,  llm_sm,      "Fault Query",      F_DIAG, 1.5)
arrow(llm_bedrock, llm_cache,   "Cache Response",   C_STORAGE, 1.5)
arrow(llm_token,   llm_router,  "Quota Check",      C_COMPUTE, 1.5, 0.5, 0, 0.5, 1)

# LLM → Output
arrow(llm_router,  out_text,  "Text",    C_LLM, 1.5)
arrow(llm_router,  out_voice, "→Polly",  C_ML,  1.5)
arrow(llm_sm,      out_diag,  "Report",  F_DIAG, 1.5)
arrow(llm_router,  out_ev,    "Answer",  F_EV_CON, 1.5)
arrow(llm_router,  out_notif, "Alert",   C_NETWORK, 1.5)

# Band-1 vector store → Band-2 retrieval (cross-band arrow)
arrow(vs_opensearch, rt_knn, "kNN Vector Index", C_VECTOR, 2.0, 0,
      0.5, 1, 0.5, 0)

# =============================================================================
# EV VEHICLE ZONE (left side, spans both bands)
# =============================================================================
zone(1408, 62, 200, 718, "EV Vehicle Layer", Z_EV_ZONE, "#1565C0", "#0D47A1", 10)
ev_sensors  = box(1420, 100, 176, 46, "EV Sensors&#xa;OBD-II · CAN Bus · BMS", C_EV, "#0D47A1")
ev_ecu      = box(1420, 158, 176, 46, "In-Vehicle ECU&#xa;+ IoT Edge Gateway", C_NETWORK, "#6A1B9A")
ev_app      = box(1420, 216, 176, 46, "SHARP EV Mobile App&#xa;(iOS / Android)", "#37474F", "#263238")
ev_browser  = box(1420, 274, 176, 42, "Web Browser&#xa;(CloudFront CDN)", "#546E7A", "#37474F")
ev_aws_iot  = box(1420, 328, 176, 46, "AWS IoT Core&#xa;(Telemetry → Cloud)", C_NETWORK, "#6A1B9A")
ev_kinesis  = box(1420, 386, 176, 46, "Amazon Kinesis&#xa;(Real-time Streaming)", C_NETWORK, "#6A1B9A")

# Link EV to ingestion (offline) and to online inputs
arrow(ev_sensors,  ds_images,    "Sensor Images", C_EV, 1.5, 1, 0, 0, 0.5)
arrow(ev_ecu,      ds_faults,    "Fault Codes",   C_EV, 1.5, 1, 0, 0, 0.5)
arrow(ev_aws_iot,  in_telemetry, "IoT Data",      C_NETWORK, 1.5, 1, 0.5, 0, 0.5)
arrow(ev_kinesis,  in_telemetry, "Streams",       C_NETWORK, 1.5, 1, 0.5, 0, 0.7)
arrow(ev_app,      in_text,      "Text Query",    "#37474F", 1.5, 1, 0.5, 0, 0.3)
arrow(ev_app,      in_voice,     "Voice",         "#37474F", 1.5, 1, 0.5, 0, 0.5)
arrow(ev_app,      in_image,     "Photo",         "#37474F", 1.5, 1, 0.5, 0, 0.7)

# =============================================================================
# OUTPUT DELIVERY BACK TO APP (right-to-left return arrows)
# =============================================================================
out_app = box(1420, 462, 176, 280, "&#xa;&#xa;&#xa;Responses&#xa;delivered back&#xa;to Mobile App&#xa;&#xa;• Text&#xa;• Voice (Polly)&#xa;• Diagnosis&#xa;• Manual Answer",
              Z_OUTPUT_Z, "#7B1FA2", "#4A148C", 9, 1)
arrow(out_text,  out_app, "Text",     "#7B1FA2", 1.5)
arrow(out_voice, out_app, "Audio",    "#7B1FA2", 1.5)
arrow(out_diag,  out_app, "Report",   "#7B1FA2", 1.5)
arrow(out_ev,    out_app, "Answer",   "#7B1FA2", 1.5)
arrow(out_notif, out_app, "Push",     "#7B1FA2", 1.5)

# =============================================================================
# BAND 3 — INFRASTRUCTURE (Security · Storage · Monitoring)
# =============================================================================
zone(18, 788, 2064, 130, "  BAND 3 — INFRASTRUCTURE: Security · Storage · Monitoring · Orchestration",
     Z_INFRA, C_SECURITY, "#B71C1C", 9)

# Security & Auth
box(30,  815, 155, 80, "Amazon Cognito&#xa;(COCORO MEMBERS ID&#xa;OAuth 2.0)", C_SECURITY, "#B71C1C")
box(198, 815, 155, 80, "AWS WAF + Shield&#xa;(DDoS · Geo-block&#xa;Rate limit · SQLi)", C_SECURITY, "#B71C1C")
box(366, 815, 155, 80, "Amazon GuardDuty&#xa;(Threat Detection&#xa;Anomaly Block)", C_SECURITY, "#B71C1C")
box(534, 815, 155, 80, "AWS Secrets Mgr&#xa;(API Keys · Certs&#xa;LLM Credentials)", "#FF7043", "#BF360C")

# Storage
box(710, 815, 155, 80, "Amazon S3&#xa;(Manuals · Images&#xa;Logs · Chunks)", C_STORAGE, "#2E7D32")
box(878, 815, 155, 80, "Amazon DynamoDB&#xa;(Conv. History&#xa;Sessions · Quota)", C_STORAGE, "#2E7D32")
box(1046,815, 155, 80, "Amazon Aurora&#xa;(Vehicle Data&#xa;Fault Registry)", C_STORAGE, "#2E7D32")

# Orchestration
box(1222,815, 155, 80, "AWS Step Fns&#xa;(Batch Index&#xa;Workflow Orchestn)", C_COMPUTE, "#AD1457")
box(1390,815, 155, 80, "Amazon SQS&#xa;(Async Queue&#xa;Retry / DLQ)", C_COMPUTE, "#AD1457")

# Monitoring
box(1558,815, 155, 80, "CloudWatch&#xa;(Metrics · Alarms&#xa;Dashboards)", C_MONITOR, "#7B1FA2")
box(1726,815, 155, 80, "AWS X-Ray&#xa;(RAG Trace&#xa;Latency per Step)", C_MONITOR, "#7B1FA2")
box(1894,815, 155, 80, "CloudTrail&#xa;(Audit · METI&#xa;Compliance Log)", C_MONITOR, "#7B1FA2")

# =============================================================================
# FEATURE LEGEND (top-right corner)
# =============================================================================
zone(1624, 62, 458, 330, "Feature Map — 4 Chatbot Modules", "#FAFAFA", "#9E9E9E", "#333", 9)

txt(1636, 88,  426, 18, "Module", 9, "#333", 1, "left")
txt(1636, 88,  240, 18, "RAG Knowledge Source", 9, "#333", 1)
txt(1636, 88,  426, 18, "LLM Mode", 9, "#333", 1)

row_y = [112, 170, 228, 286]
modules = [
    (F_DIAG,   "Self-Diagnosis",          "Fault Code DB + Vehicle Image Index",     "Claude 3 Vision + SageMaker"),
    (F_EV_CON, "EV Usage Consultation",   "EV Manual chunks (Titan Text Embed v2)",  "Claude 3 Sonnet + Kendra"),
    (F_CHAT,   "Chat (General AI)",       "Minimal retrieval — mostly generative",   "Claude 3 Haiku (generative)"),
    (F_AUTO,   "General Auto Guidance",   "Automotive KB (Titan + Cohere Embed)",    "Claude 3 Sonnet + RAG"),
]
for i, (fc, name, source, llm_mode) in enumerate(modules):
    badge(1636, row_y[i],      120, 48, name, fc)
    txt(1764,  row_y[i],       160, 24, source, 8, "#333", 0, "left")
    txt(1764,  row_y[i] + 24,  160, 24, llm_mode, 7, "#666", 2, "left")

# =============================================================================
# RAG FLOW LABEL (centre of Band 2)
# =============================================================================
txt(466, 780, 640, 18,
    "RAG Pipeline: Query Embed → kNN Retrieval → Re-rank → Prompt Augment → Claude 3 (Multi-modal) → Response",
    8, "#1B5E20", 1)

# =============================================================================
# BUILD XML OUTPUT
# =============================================================================
cell_xml = "\n        ".join(c[1] for c in cells)

xml = f'''<mxfile host="app.diagrams.net" modified="2026-06-19" agent="SHARP-EV-SA" version="21.0.0">
  <diagram name="Multi-modal RAG Architecture" id="sharp-ev-mm-rag">
    <mxGraphModel dx="2200" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="2200" pageHeight="1000" math="0" shadow="1">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {cell_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

output = "/home/ramram/Desktop/Personal/EV-Chatbot/SHARP_EV_AWS_Architecture.drawio"
with open(output, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"Saved: {output}")
print(f"Total draw.io elements: {_id[0] - 2}")
