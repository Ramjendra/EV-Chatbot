"""
One-time infrastructure setup:
  1. Create S3 bucket
  2. Create IAM role for Kendra
  3. Create Kendra Developer index
  4. Create S3 data source
  5. Save KENDRA_INDEX_ID to .env
"""
import boto3, json, time, sys
from botocore.exceptions import ClientError
from config import (
    AWS_REGION, S3_BUCKET_NAME, S3_DOCS_PREFIX,
    KENDRA_INDEX_NAME, KENDRA_DATA_SOURCE_NAME, KENDRA_EDITION,
    KENDRA_ROLE_NAME,
)

iam     = boto3.client("iam",    region_name=AWS_REGION)
s3      = boto3.client("s3",     region_name=AWS_REGION)
kendra  = boto3.client("kendra", region_name=AWS_REGION)
sts     = boto3.client("sts",    region_name=AWS_REGION)


# ── 1. S3 bucket ──────────────────────────────────────────────────────────────
def create_s3_bucket():
    try:
        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=S3_BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
            )
        print(f"[✓] S3 bucket created: {S3_BUCKET_NAME}")
    except ClientError as e:
        if e.response["Error"]["Code"] in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"[~] S3 bucket already exists: {S3_BUCKET_NAME}")
        else:
            raise


# ── 2. IAM role for Kendra ────────────────────────────────────────────────────
def create_kendra_role():
    account_id = sts.get_caller_identity()["Account"]

    trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "kendra.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    }

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["cloudwatch:PutMetricData"],
                "Resource": "*",
                "Condition": {"StringEquals": {"cloudwatch:namespace": "AWS/Kendra"}},
            },
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogGroup", "logs:DescribeLogGroups"],
                "Resource": f"arn:aws:logs:{AWS_REGION}:{account_id}:log-group:/aws/kendra/*",
            },
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents",
                           "logs:DescribeLogStreams"],
                "Resource": f"arn:aws:logs:{AWS_REGION}:{account_id}:log-group:/aws/kendra/*:log-stream:*",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{S3_BUCKET_NAME}",
                    f"arn:aws:s3:::{S3_BUCKET_NAME}/*",
                ],
            },
        ],
    }

    try:
        role = iam.create_role(
            RoleName=KENDRA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust),
            Description="Kendra index role for SHARP EV POC",
        )
        role_arn = role["Role"]["Arn"]
        print(f"[✓] IAM role created: {role_arn}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            role_arn = iam.get_role(RoleName=KENDRA_ROLE_NAME)["Role"]["Arn"]
            print(f"[~] IAM role already exists: {role_arn}")
        else:
            raise

    iam.put_role_policy(
        RoleName=KENDRA_ROLE_NAME,
        PolicyName="KendraS3Access",
        PolicyDocument=json.dumps(policy),
    )
    print("[✓] IAM inline policy attached")

    # Wait for IAM propagation
    time.sleep(10)
    return role_arn


# ── 3. Kendra index ───────────────────────────────────────────────────────────
def create_kendra_index(role_arn):
    try:
        resp = kendra.create_index(
            Name=KENDRA_INDEX_NAME,
            Edition=KENDRA_EDITION,
            RoleArn=role_arn,
            Description="SHARP EV Chatbot knowledge index — POC",
        )
        index_id = resp["Id"]
        print(f"[✓] Kendra index creation started: {index_id}")
    except ClientError as e:
        if "already exists" in str(e).lower():
            indexes = kendra.list_indices()["IndexConfigurationSummaryItems"]
            index_id = next(i["Id"] for i in indexes if i["Name"] == KENDRA_INDEX_NAME)
            print(f"[~] Kendra index already exists: {index_id}")
            return index_id
        raise

    # Wait until ACTIVE
    print("    Waiting for index to become ACTIVE (this takes ~30 min for first time)...")
    for _ in range(120):
        status = kendra.describe_index(Id=index_id)["Status"]
        print(f"    Status: {status}", end="\r")
        if status == "ACTIVE":
            print(f"\n[✓] Kendra index ACTIVE: {index_id}")
            return index_id
        if status == "FAILED":
            raise RuntimeError("Kendra index creation FAILED")
        time.sleep(30)

    raise TimeoutError("Timed out waiting for Kendra index")


# ── 4. S3 data source ─────────────────────────────────────────────────────────
def create_data_source(index_id, role_arn):
    try:
        resp = kendra.create_data_source(
            IndexId=index_id,
            Name=KENDRA_DATA_SOURCE_NAME,
            Type="S3",
            RoleArn=role_arn,
            Configuration={
                "S3Configuration": {
                    "BucketName": S3_BUCKET_NAME,
                    "InclusionPrefixes": [S3_DOCS_PREFIX],
                }
            },
            Description="EV manuals from S3",
        )
        ds_id = resp["Id"]
        print(f"[✓] Data source created: {ds_id}")
        return ds_id
    except ClientError as e:
        if "already exists" in str(e).lower():
            sources = kendra.list_data_sources(IndexId=index_id)["SummaryItems"]
            ds_id = next(s["Id"] for s in sources if s["Name"] == KENDRA_DATA_SOURCE_NAME)
            print(f"[~] Data source already exists: {ds_id}")
            return ds_id
        raise


# ── 5. Save to .env ───────────────────────────────────────────────────────────
def save_index_id(index_id):
    env_path = ".env"
    lines = []
    try:
        with open(env_path) as f:
            lines = [l for l in f.readlines() if not l.startswith("KENDRA_INDEX_ID")]
    except FileNotFoundError:
        pass
    lines.append(f"KENDRA_INDEX_ID={index_id}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)
    print(f"[✓] KENDRA_INDEX_ID saved to .env")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== SHARP EV Kendra POC — Infrastructure Setup ===\n")
    create_s3_bucket()
    role_arn  = create_kendra_role()
    index_id  = create_kendra_index(role_arn)
    ds_id     = create_data_source(index_id, role_arn)
    save_index_id(index_id)
    print(f"\n✅  Setup complete.")
    print(f"    Index ID      : {index_id}")
    print(f"    Data Source ID: {ds_id}")
    print(f"    S3 Bucket     : {S3_BUCKET_NAME}/{S3_DOCS_PREFIX}")
    print(f"\nNext: python ingest.py --docs ./docs/")
