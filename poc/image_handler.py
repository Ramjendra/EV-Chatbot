"""
Image analysis handler using Amazon Rekognition.

Flow:
  Image bytes
      │
      ├──► detect_labels()   →  objects / scenes (Battery, Warning Light, Dashboard…)
      ├──► detect_text()     →  error codes, numbers (P0A80, 12V, 45%)
      └──► build_query()     →  natural language question for Kendra
"""
import boto3
from config import AWS_REGION

rekognition = boto3.client("rekognition", region_name=AWS_REGION)

# Labels we specifically care about for EV diagnosis
EV_RELEVANT_LABELS = {
    "battery", "warning", "dashboard", "gauge", "indicator",
    "light", "screen", "display", "symbol", "icon",
    "car", "vehicle", "motor", "engine", "wheel",
    "tire", "tyre", "charger", "plug", "cable",
    "thermometer", "temperature", "speedometer",
}


# ── Label detection ───────────────────────────────────────────────────────────
def detect_labels(image_bytes: bytes) -> list[dict]:
    """Detect objects and scenes in the image."""
    resp = rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MaxLabels=20,
        MinConfidence=65.0,
    )
    return [
        {
            "name":       label["Name"],
            "confidence": round(label["Confidence"], 1),
            "relevant":   label["Name"].lower() in EV_RELEVANT_LABELS,
        }
        for label in resp["Labels"]
    ]


# ── Text/code detection ───────────────────────────────────────────────────────
def detect_text(image_bytes: bytes) -> list[dict]:
    """Detect text and error codes in the image (dashboard numbers, DTC codes)."""
    resp = rekognition.detect_text(Image={"Bytes": image_bytes})
    return [
        {
            "text":       item["DetectedText"],
            "type":       item["Type"],          # LINE or WORD
            "confidence": round(item["Confidence"], 1),
        }
        for item in resp["TextDetections"]
        if item["Type"] == "LINE" and item["Confidence"] > 80
    ]


# ── Query builder ─────────────────────────────────────────────────────────────
def build_query(labels: list[dict], texts: list[dict]) -> str:
    """
    Convert Rekognition results into a natural language query for Kendra.
    Prioritises EV-relevant labels and any detected error codes.
    """
    ev_labels  = [l["name"] for l in labels if l["relevant"]]
    all_labels = [l["name"] for l in labels if not l["relevant"]]
    text_lines = [t["text"] for t in texts]

    parts = []

    # Error code patterns: P0A80, U0100, B1234, C0000 etc.
    error_codes = [
        t for t in text_lines
        if len(t) >= 4 and t[0].upper() in "PUBC" and any(c.isdigit() for c in t)
    ]

    if error_codes:
        parts.append(f"Error code detected: {', '.join(error_codes)}")
    if ev_labels:
        parts.append(f"EV components visible: {', '.join(ev_labels[:5])}")
    if text_lines and not error_codes:
        parts.append(f"Dashboard text: {', '.join(text_lines[:4])}")
    if all_labels and not ev_labels:
        parts.append(f"Items visible: {', '.join(all_labels[:5])}")

    if not parts:
        return "I took a photo of my EV dashboard. What does it show and is there anything I should be concerned about?"

    query = ". ".join(parts)
    query += ". What does this mean and what action should I take?"
    return query


# ── Full pipeline ─────────────────────────────────────────────────────────────
def analyze_image(image_bytes: bytes) -> dict:
    """
    Run full Rekognition analysis on image bytes.

    Returns:
        {
            "labels":  [{"name", "confidence", "relevant"}, ...],
            "texts":   [{"text", "type", "confidence"}, ...],
            "query":   "Natural language question for Kendra",
            "summary": "Human readable summary of what was detected"
        }
    """
    labels = detect_labels(image_bytes)
    texts  = detect_text(image_bytes)
    query  = build_query(labels, texts)

    # Build a human-readable summary for display
    top_labels    = [l["name"] for l in labels[:6]]
    detected_text = [t["text"] for t in texts[:4]]

    summary_parts = []
    if top_labels:
        summary_parts.append(f"Detected: {', '.join(top_labels)}")
    if detected_text:
        summary_parts.append(f"Text/Codes: {', '.join(detected_text)}")

    summary = " | ".join(summary_parts) if summary_parts else "No clear EV elements detected"

    return {
        "labels":  labels,
        "texts":   texts,
        "query":   query,
        "summary": summary,
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python image_handler.py <image_path>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        result = analyze_image(f.read())

    print(f"\nSummary : {result['summary']}")
    print(f"\nQuery   : {result['query']}")
    print(f"\nLabels  ({len(result['labels'])}):")
    for l in result["labels"]:
        tag = "★" if l["relevant"] else " "
        print(f"  {tag} {l['name']:30s} {l['confidence']}%")
    print(f"\nTexts   ({len(result['texts'])}):")
    for t in result["texts"]:
        print(f"    {t['text']:30s} {t['confidence']}%")
