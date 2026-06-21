import os
import uuid
from pathlib import Path

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
STORAGE_LOCAL_PATH = os.getenv("STORAGE_LOCAL_PATH", "/tmp/sentinel-storage")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "sentinel")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "sentinel123")
S3_BUCKET = os.getenv("S3_BUCKET", "sentinel-uploads")

_s3_client = None


def _get_s3():
    global _s3_client
    if _s3_client is None:
        import boto3
        _s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
        )
        buckets = [b["Name"] for b in _s3_client.list_buckets().get("Buckets", [])]
        if S3_BUCKET not in buckets:
            _s3_client.create_bucket(Bucket=S3_BUCKET)
    return _s3_client


async def store_file(file_data: bytes, file_name: str, subdir: str = "uploads") -> str:
    file_id = str(uuid.uuid4())
    ext = Path(file_name).suffix if "." in file_name else ""
    stored_name = f"{file_id}{ext}"
    key = f"{subdir}/{stored_name}"

    if STORAGE_BACKEND == "local":
        dest_dir = Path(STORAGE_LOCAL_PATH) / subdir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / stored_name
        with open(dest_path, "wb") as f:
            f.write(file_data)
        return str(dest_path)

    elif STORAGE_BACKEND == "s3":
        s3 = _get_s3()
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=file_data)
        return f"s3://{S3_BUCKET}/{key}"

    raise ValueError(f"Unsupported storage backend: {STORAGE_BACKEND}")


async def read_file(storage_path: str) -> bytes:
    if STORAGE_BACKEND == "local":
        with open(storage_path, "rb") as f:
            return f.read()
    elif storage_path.startswith("s3://"):
        import re
        match = re.match(r"s3://([^/]+)/(.+)", storage_path)
        if not match:
            raise ValueError(f"Invalid S3 path: {storage_path}")
        s3 = _get_s3()
        resp = s3.get_object(Bucket=match.group(1), Key=match.group(2))
        return resp["Body"].read()
    raise ValueError(f"Unsupported storage path: {storage_path}")


async def delete_file(storage_path: str) -> None:
    if STORAGE_BACKEND == "local":
        if os.path.exists(storage_path):
            os.remove(storage_path)
    elif storage_path.startswith("s3://"):
        import re
        match = re.match(r"s3://([^/]+)/(.+)", storage_path)
        if match:
            s3 = _get_s3()
            s3.delete_object(Bucket=match.group(1), Key=match.group(2))


async def file_exists(storage_path: str) -> bool:
    if STORAGE_BACKEND == "local":
        return os.path.exists(storage_path)
    elif storage_path.startswith("s3://"):
        import re
        match = re.match(r"s3://([^/]+)/(.+)", storage_path)
        if match:
            try:
                s3 = _get_s3()
                s3.head_object(Bucket=match.group(1), Key=match.group(2))
                return True
            except Exception:
                return False
    return False
