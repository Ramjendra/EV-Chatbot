"""
Upload documents to S3 and trigger Kendra sync.

Usage:
    python ingest.py --docs ./docs/
    python ingest.py --docs ./docs/ --sync-only      # skip upload, just sync
    python ingest.py --status                         # check last sync status
"""
import argparse, boto3, os, sys, time
from pathlib import Path
from config import AWS_REGION, S3_BUCKET_NAME, S3_DOCS_PREFIX, KENDRA_INDEX_ID

s3     = boto3.client("s3",     region_name=AWS_REGION)
kendra = boto3.client("kendra", region_name=AWS_REGION)

SUPPORTED_EXTS = {".pdf", ".txt", ".html", ".docx", ".csv", ".json"}


# ── Upload docs to S3 ─────────────────────────────────────────────────────────
def upload_documents(docs_dir: str):
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"[!] Directory not found: {docs_dir}")
        sys.exit(1)

    files = [f for f in docs_path.rglob("*") if f.suffix.lower() in SUPPORTED_EXTS]
    if not files:
        print(f"[!] No supported files found in {docs_dir}")
        print(f"    Supported: {SUPPORTED_EXTS}")
        sys.exit(1)

    print(f"[→] Uploading {len(files)} file(s) to s3://{S3_BUCKET_NAME}/{S3_DOCS_PREFIX}")
    for f in files:
        key = f"{S3_DOCS_PREFIX}{f.name}"
        s3.upload_file(str(f), S3_BUCKET_NAME, key)
        print(f"    ✓  {f.name}  →  {key}")

    print(f"[✓] Upload complete: {len(files)} files\n")
    return len(files)


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

    ds_id = get_data_source_id()
    resp  = kendra.start_data_source_sync_job(IndexId=KENDRA_INDEX_ID, Id=ds_id)
    exec_id = resp["ExecutionId"]
    print(f"[→] Kendra sync started. Execution ID: {exec_id}")
    return ds_id, exec_id


def wait_for_sync(ds_id, exec_id):
    print("    Polling sync status...")
    for _ in range(60):
        jobs = kendra.list_data_source_sync_jobs(
            IndexId=KENDRA_INDEX_ID, Id=ds_id
        )["History"]

        running = next((j for j in jobs if j["ExecutionId"] == exec_id), None)
        if running:
            status = running["Status"]
            metrics = running.get("Metrics", {})
            added    = metrics.get("DocumentsAdded", 0)
            modified = metrics.get("DocumentsModified", 0)
            failed   = metrics.get("DocumentsFailed", 0)
            print(f"    Status: {status}  | Added:{added}  Modified:{modified}  Failed:{failed}", end="\r")

            if status == "SUCCEEDED":
                print(f"\n[✓] Sync complete — {added} docs added, {modified} modified, {failed} failed")
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
    print(f"Last sync:")
    print(f"  Status     : {last['Status']}")
    print(f"  Started    : {last.get('StartTime', 'N/A')}")
    print(f"  Ended      : {last.get('EndTime', 'N/A')}")
    m = last.get("Metrics", {})
    print(f"  Added      : {m.get('DocumentsAdded', 0)}")
    print(f"  Modified   : {m.get('DocumentsModified', 0)}")
    print(f"  Deleted    : {m.get('DocumentsDeleted', 0)}")
    print(f"  Failed     : {m.get('DocumentsFailed', 0)}")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into Kendra")
    parser.add_argument("--docs",      help="Path to local docs folder")
    parser.add_argument("--sync-only", action="store_true", help="Skip upload, only trigger sync")
    parser.add_argument("--status",    action="store_true", help="Show last sync status")
    args = parser.parse_args()

    if args.status:
        show_status()
        sys.exit(0)

    if not args.docs and not args.sync_only:
        parser.print_help()
        sys.exit(1)

    print("=== SHARP EV Kendra POC — Document Ingestion ===\n")

    if not args.sync_only and args.docs:
        upload_documents(args.docs)

    ds_id, exec_id = start_sync()
    wait_for_sync(ds_id, exec_id)
    print("\n✅  Documents indexed. Run: streamlit run app.py")
