"""
Upload documents to S3 and trigger Kendra sync.

Usage:
    python ingest.py --docs ./docs/
    python ingest.py --docs ./docs/ --language en       # override language (default: ja)
    python ingest.py --docs ./docs/ --purge             # delete existing S3 docs first
    python ingest.py --sync-only                        # skip upload, just trigger sync
    python ingest.py --list                             # list docs currently in S3
    python ingest.py --status                           # show last sync job status
"""
import argparse, boto3, json, os, sys, time
from pathlib import Path
from config import (
    AWS_REGION, S3_BUCKET_NAME, S3_DOCS_PREFIX, KENDRA_INDEX_ID,
    KENDRA_LANGUAGE, S3_METADATA_PREFIX,
)

s3     = boto3.client("s3",     region_name=AWS_REGION)
kendra = boto3.client("kendra", region_name=AWS_REGION)

SUPPORTED_EXTS = {".pdf", ".txt", ".html", ".docx", ".csv", ".json"}


# ── Metadata upload ───────────────────────────────────────────────────────────
def _upload_language_metadata(filename: str, language: str):
    """Upload a Kendra metadata JSON so Kendra tokenizes the doc with the correct language."""
    meta_key = f"{S3_METADATA_PREFIX}{S3_DOCS_PREFIX}{filename}.metadata.json"
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=meta_key,
        Body=json.dumps({"Attributes": {"_language_code": language}}),
        ContentType="application/json",
    )


# ── Upload docs to S3 ─────────────────────────────────────────────────────────
def upload_documents(docs_dir: str, language: str = KENDRA_LANGUAGE):
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"[!] Directory not found: {docs_dir}")
        sys.exit(1)

    files = [f for f in docs_path.rglob("*") if f.suffix.lower() in SUPPORTED_EXTS]
    if not files:
        print(f"[!] No supported files found in {docs_dir}")
        print(f"    Supported: {SUPPORTED_EXTS}")
        sys.exit(1)

    total = len(files)
    print(f"[→] Uploading {total} file(s) to s3://{S3_BUCKET_NAME}/{S3_DOCS_PREFIX}  [lang={language}]")
    for i, f in enumerate(files, 1):
        key = f"{S3_DOCS_PREFIX}{f.name}"
        s3.upload_file(str(f), S3_BUCKET_NAME, key)
        _upload_language_metadata(f.name, language)
        print(f"    [{i}/{total}] ✓  {f.name}  (doc + metadata/{language})")

    print(f"[✓] Upload complete: {total} file(s)\n")
    return total


# ── Purge existing S3 docs + metadata ────────────────────────────────────────
def purge_s3():
    print(f"[→] Purging existing objects under s3://{S3_BUCKET_NAME}/")
    deleted = 0
    for prefix in [S3_DOCS_PREFIX, f"{S3_METADATA_PREFIX}{S3_DOCS_PREFIX}"]:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
            objects = page.get("Contents", [])
            if objects:
                s3.delete_objects(
                    Bucket=S3_BUCKET_NAME,
                    Delete={"Objects": [{"Key": o["Key"]} for o in objects]},
                )
                deleted += len(objects)
    print(f"[✓] Purged {deleted} object(s)\n")


# ── List S3 docs ──────────────────────────────────────────────────────────────
def list_s3_docs():
    paginator = s3.get_paginator("list_objects_v2")
    docs = []
    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=S3_DOCS_PREFIX):
        docs.extend(page.get("Contents", []))

    if not docs:
        print(f"No documents found in s3://{S3_BUCKET_NAME}/{S3_DOCS_PREFIX}")
        return

    print(f"\n{'File':<45} {'Size':>10}  {'Last Modified'}")
    print("-" * 80)
    for obj in docs:
        name = obj["Key"].replace(S3_DOCS_PREFIX, "")
        size = f"{obj['Size']:,} B"
        ts   = obj["LastModified"].strftime("%Y-%m-%d %H:%M")
        print(f"  {name:<43} {size:>10}  {ts}")
    print(f"\n  {len(docs)} file(s) in s3://{S3_BUCKET_NAME}/{S3_DOCS_PREFIX}")


# ── Trigger Kendra sync ───────────────────────────────────────────────────────
def get_data_source_id():
    sources = kendra.list_data_sources(IndexId=KENDRA_INDEX_ID)["SummaryItems"]
    if not sources:
        print("[!] No data sources found. Run setup_kendra.py first.")
        sys.exit(1)
    return sources[0]["Id"]


def start_sync():
    if not KENDRA_INDEX_ID:
        print("[!] KENDRA_INDEX_ID not set. Run setup_kendra.py first.")
        sys.exit(1)

    ds_id   = get_data_source_id()
    resp    = kendra.start_data_source_sync_job(IndexId=KENDRA_INDEX_ID, Id=ds_id)
    exec_id = resp["ExecutionId"]
    print(f"[→] Kendra sync started. Execution ID: {exec_id}")
    return ds_id, exec_id


def wait_for_sync(ds_id, exec_id):
    print("    Polling sync status every 15 s ...")
    for _ in range(60):
        jobs = kendra.list_data_source_sync_jobs(
            IndexId=KENDRA_INDEX_ID, Id=ds_id
        )["History"]

        running = next((j for j in jobs if j["ExecutionId"] == exec_id), None)
        if running:
            status   = running["Status"]
            metrics  = running.get("Metrics", {})
            added    = metrics.get("DocumentsAdded", 0)
            modified = metrics.get("DocumentsModified", 0)
            failed   = metrics.get("DocumentsFailed", 0)
            print(f"    Status: {status}  | Added:{added}  Modified:{modified}  Failed:{failed}", end="\r")

            if status == "SUCCEEDED":
                print(f"\n[✓] Sync complete — {added} added, {modified} modified, {failed} failed")
                return
            if status in ("FAILED", "INCOMPLETE"):
                err = running.get("ErrorMessage", "Unknown error")
                print(f"\n[!] Sync {status}: {err}")
                sys.exit(1)

        time.sleep(15)

    print("\n[!] Timed out waiting for sync")


def show_status():
    if not KENDRA_INDEX_ID:
        print("[!] KENDRA_INDEX_ID not set.")
        sys.exit(1)
    ds_id = get_data_source_id()
    jobs  = kendra.list_data_source_sync_jobs(IndexId=KENDRA_INDEX_ID, Id=ds_id)["History"]
    if not jobs:
        print("No sync jobs found.")
        return
    last = jobs[0]
    m    = last.get("Metrics", {})
    print(f"\nLast sync job:")
    print(f"  Status     : {last['Status']}")
    print(f"  Started    : {last.get('StartTime', 'N/A')}")
    print(f"  Ended      : {last.get('EndTime',   'N/A')}")
    print(f"  Added      : {m.get('DocumentsAdded',    0)}")
    print(f"  Modified   : {m.get('DocumentsModified', 0)}")
    print(f"  Deleted    : {m.get('DocumentsDeleted',  0)}")
    print(f"  Failed     : {m.get('DocumentsFailed',   0)}")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest EV manual documents into Amazon Kendra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--docs",      help="Path to local docs folder to upload")
    parser.add_argument("--language",  default=KENDRA_LANGUAGE,
                        help=f"Language code for Kendra tokenizer (default: {KENDRA_LANGUAGE})")
    parser.add_argument("--purge",     action="store_true",
                        help="Delete existing S3 docs + metadata before uploading")
    parser.add_argument("--sync-only", action="store_true",
                        help="Skip upload, only trigger Kendra sync")
    parser.add_argument("--list",      action="store_true",
                        help="List documents currently in S3")
    parser.add_argument("--status",    action="store_true",
                        help="Show last Kendra sync job status")
    args = parser.parse_args()

    if args.list:
        list_s3_docs()
        sys.exit(0)

    if args.status:
        show_status()
        sys.exit(0)

    if not args.docs and not args.sync_only:
        parser.print_help()
        sys.exit(1)

    print("=== SHARP EV Kendra POC — Document Ingestion ===\n")

    if args.purge:
        purge_s3()

    if not args.sync_only and args.docs:
        upload_documents(args.docs, language=args.language)

    ds_id, exec_id = start_sync()
    wait_for_sync(ds_id, exec_id)
    print("\n✅  Documents indexed. Run: streamlit run app.py")
