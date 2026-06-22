"""
Kendra + Bedrock RAG pipeline.

Flow:
  User Query
      │
      ▼
  Kendra.query()  ──►  Top-K document excerpts + scores
      │
      ▼
  build_prompt()  ──►  System + Sources + User Question
      │
      ▼
  Bedrock Claude 3  ──►  Streamed answer
"""
import boto3, json
from typing import Iterator
from config import (
    AWS_REGION, KENDRA_INDEX_ID, KENDRA_TOP_K,
    BEDROCK_MODEL_ID, MAX_TOKENS, TEMPERATURE,
)

kendra  = boto3.client("kendra",          region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


# ── Kendra query ──────────────────────────────────────────────────────────────
def query_kendra(query: str, top_k: int = KENDRA_TOP_K) -> list[dict]:
    """Return top-K results from Kendra with title, excerpt, score, URL."""
    if not KENDRA_INDEX_ID:
        raise ValueError("KENDRA_INDEX_ID not set. Run setup_kendra.py first.")

    resp = kendra.query(
        IndexId=KENDRA_INDEX_ID,
        QueryText=query,
        PageSize=top_k,
        QueryResultTypeFilter="DOCUMENT",   # DOCUMENT | QUESTION_ANSWER | ANSWER
    )

    results = []
    for item in resp.get("ResultItems", []):
        excerpt = ""
        if item.get("DocumentExcerpt"):
            excerpt = item["DocumentExcerpt"].get("Text", "")

        source_uri = ""
        for attr in item.get("DocumentAttributes", []):
            if attr["Key"] == "_source_uri":
                source_uri = attr["Value"].get("StringValue", "")

        results.append({
            "title":       item.get("DocumentTitle", {}).get("Text", "Unknown"),
            "excerpt":     excerpt,
            "score":       item.get("ScoreAttributes", {}).get("ScoreConfidence", "LOW"),
            "source_uri":  source_uri,
            "result_id":   item.get("Id", ""),
        })

    return results


# ── Prompt builder ────────────────────────────────────────────────────────────
def build_prompt(query: str, sources: list[dict], system_prompt: str) -> list[dict]:
    """Build Bedrock Messages API payload."""
    context_blocks = []
    for i, src in enumerate(sources, 1):
        context_blocks.append(
            f"[Source {i}] {src['title']}\n{src['excerpt']}"
        )

    context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."

    user_message = (
        f"Use the following document excerpts to answer the question.\n\n"
        f"--- SOURCES ---\n{context_text}\n--- END SOURCES ---\n\n"
        f"Question: {query}\n\n"
        f"Answer based only on the sources above. If the answer is not in the sources, "
        f"say \"I could not find this information in the available documents.\""
    )

    return [{"role": "user", "content": user_message}]


# ── Bedrock streaming call ────────────────────────────────────────────────────
def stream_bedrock(messages: list[dict], system_prompt: str) -> Iterator[str]:
    """Yield text chunks from Bedrock Claude 3 via streaming."""
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens":  MAX_TOKENS,
        "temperature": TEMPERATURE,
        "system":      system_prompt,
        "messages":    messages,
    }

    resp = bedrock.invoke_model_with_response_stream(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
    )

    for event in resp["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk.get("type") == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                yield delta.get("text", "")


# ── Non-streaming call (for testing) ─────────────────────────────────────────
def invoke_bedrock(messages: list[dict], system_prompt: str) -> str:
    """Return full response text (non-streaming)."""
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens":  MAX_TOKENS,
        "temperature": TEMPERATURE,
        "system":      system_prompt,
        "messages":    messages,
    }
    resp = bedrock.invoke_model(modelId=BEDROCK_MODEL_ID, body=json.dumps(body))
    result = json.loads(resp["body"].read())
    return result["content"][0]["text"]


# ── Full RAG pipeline ─────────────────────────────────────────────────────────
def rag_stream(query: str, system_prompt: str) -> tuple[Iterator[str], list[dict]]:
    """
    Returns (text_stream, sources).
    Caller iterates text_stream to get answer tokens.
    """
    sources  = query_kendra(query)
    messages = build_prompt(query, sources, system_prompt)
    stream   = stream_bedrock(messages, system_prompt)
    return stream, sources


def rag_answer(query: str, system_prompt: str) -> tuple[str, list[dict]]:
    """Non-streaming version. Returns (answer_text, sources)."""
    sources  = query_kendra(query)
    messages = build_prompt(query, sources, system_prompt)
    answer   = invoke_bedrock(messages, system_prompt)
    return answer, sources


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from config import MODULES
    query  = "What is the maximum range of the SHARP EV on a full charge?"
    system = MODULES["EV Usage Consultation"]["system_prompt"]
    print(f"Query: {query}\n")
    answer, sources = rag_answer(query, system)
    print(f"Answer:\n{answer}\n")
    print(f"Sources ({len(sources)}):")
    for s in sources:
        print(f"  [{s['score']}] {s['title']}")
        print(f"          {s['excerpt'][:120]}...")
