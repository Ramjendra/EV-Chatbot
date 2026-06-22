import os
from dotenv import load_dotenv

load_dotenv()

# ── AWS ───────────────────────────────────────────────────────────────────────
AWS_REGION          = os.getenv("AWS_REGION", "ap-northeast-1")
AWS_PROFILE         = os.getenv("AWS_PROFILE", None)          # None = default credentials

# ── S3 ────────────────────────────────────────────────────────────────────────
S3_BUCKET_NAME      = os.getenv("S3_BUCKET_NAME", "sharp-ev-kendra-poc-docs")
S3_DOCS_PREFIX      = "ev-manuals/"                           # folder inside bucket

# ── Kendra ────────────────────────────────────────────────────────────────────
KENDRA_INDEX_NAME        = "sharp-ev-chatbot-index"
KENDRA_DATA_SOURCE_NAME  = "ev-manuals-s3-source"
KENDRA_EDITION           = "DEVELOPER_EDITION"                # ENTERPRISE_EDITION for prod
KENDRA_INDEX_ID          = os.getenv("KENDRA_INDEX_ID", "")  # populated after setup
KENDRA_TOP_K             = 5

# ── Bedrock ───────────────────────────────────────────────────────────────────
BEDROCK_MODEL_ID    = "anthropic.claude-3-haiku-20240307-v1:0"   # Haiku = cost-efficient POC
MAX_TOKENS          = 1024
TEMPERATURE         = 0.1                                     # low = factual answers

# ── IAM ───────────────────────────────────────────────────────────────────────
KENDRA_ROLE_NAME    = "sharp-ev-kendra-poc-role"

# ── Chatbot ───────────────────────────────────────────────────────────────────
APP_TITLE           = "SHARP EV AI Chatbot"
APP_SUBTITLE        = "Powered by Amazon Kendra + Bedrock Claude 3"

MODULES = {
    "EV Usage Consultation": {
        "icon": "⚡",
        "system_prompt": (
            "You are a helpful SHARP EV assistant. Answer questions about the EV car "
            "using only the provided document excerpts. If the answer is not in the "
            "documents, say so clearly. Be concise and accurate."
        ),
    },
    "Self-Diagnosis": {
        "icon": "🔧",
        "system_prompt": (
            "You are a SHARP EV diagnostic assistant. Analyse the user's described "
            "symptoms and use the provided technical documents to identify the likely "
            "fault, its severity (Critical / Warning / Info), and recommended action."
        ),
    },
    "General Chat": {
        "icon": "💬",
        "system_prompt": (
            "You are a friendly SHARP EV assistant. Answer general questions about "
            "electric vehicles, charging, and car maintenance. Be helpful and concise."
        ),
    },
    "Automotive Guidance": {
        "icon": "🚗",
        "system_prompt": (
            "You are an automotive expert assistant. Provide guidance on driving tips, "
            "EV best practices, and general vehicle maintenance using the provided sources."
        ),
    },
}
