"""Immutable raw-snapshot storage (ADR-0003). The only place allowed to import boto3."""

import contextlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from geolens.core.config import get_settings


class ObjectStorage(Protocol):
    def put_json(self, key: str, data: dict[str, Any]) -> str: ...
    def get_json(self, uri: str) -> dict[str, Any]: ...


class LocalStorage:
    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir)

    def put_json(self, key: str, data: dict[str, Any]) -> str:
        path = self.base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return f"file://{path}"

    def get_json(self, uri: str) -> dict[str, Any]:
        path = Path(uri.removeprefix("file://"))
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result


class S3Storage:
    def __init__(self) -> None:
        import boto3
        from botocore.config import Config

        s = get_settings()
        self.bucket = s.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=s.s3_endpoint_url,
            aws_access_key_id=s.s3_access_key,
            aws_secret_access_key=s.s3_secret_key,
            region_name=s.s3_region,
            # Retries connection errors and throttling with backoff (e.g. S3 still starting).
            config=Config(retries={"max_attempts": 6, "mode": "standard"}, connect_timeout=5),
        )
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except self.client.exceptions.ClientError:
            # Several worker processes may race to create it.
            with contextlib.suppress(
                self.client.exceptions.BucketAlreadyOwnedByYou,
                self.client.exceptions.BucketAlreadyExists,
            ):
                self.client.create_bucket(Bucket=self.bucket)

    def put_json(self, key: str, data: dict[str, Any]) -> str:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=body, ContentType="application/json"
        )
        return f"s3://{self.bucket}/{key}"

    def get_json(self, uri: str) -> dict[str, Any]:
        bucket, key = uri.removeprefix("s3://").split("/", 1)
        obj = self.client.get_object(Bucket=bucket, Key=key)
        result: dict[str, Any] = json.loads(obj["Body"].read())
        return result


@lru_cache
def get_storage() -> ObjectStorage:
    s = get_settings()
    if s.storage_backend == "s3":
        return S3Storage()
    return LocalStorage(s.storage_local_dir)
