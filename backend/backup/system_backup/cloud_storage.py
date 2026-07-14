"""
Asguard Cloud Storage — S3-compatible backend.

Works with: Backblaze B2, Cloudflare R2, AWS S3, MinIO.
Intelligent features:
  - sha256 deduplication (skip if already uploaded)
  - auto-compress backup folders before upload
  - automatic cloud retention (keep N most recent)
  - background thread so backups never block
"""

import hashlib
import json
import logging
import os
import tarfile
import threading
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_COMPRESS_SUFFIX = ".tar.gz"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _compress_folder(folder: Path, dest: Path) -> Path:
    """Compress a backup folder to .tar.gz, return archive path."""
    archive = dest / (folder.name + _COMPRESS_SUFFIX)
    with tarfile.open(archive, "w:gz", compresslevel=6) as tar:
        tar.add(folder, arcname=folder.name)
    return archive


class CloudStorageService:
    """
    S3-compatible upload/download service for Asguard backups.
    All heavy operations run in daemon threads.
    """

    def __init__(self, config):
        """config: CloudStorageConfig model instance"""
        self._cfg = config

    # ── boto3 client ──────────────────────────────────────────────────────────

    def _client(self):
        import boto3
        from botocore.config import Config as BotoConfig

        kwargs = dict(
            aws_access_key_id     = self._cfg.access_key_id,
            aws_secret_access_key = self._cfg.secret_access_key,
            region_name           = self._cfg.region or "us-east-1",
            config                = BotoConfig(
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=10,
                read_timeout=120,
            ),
        )
        if self._cfg.endpoint_url:
            kwargs["endpoint_url"] = self._cfg.endpoint_url

        return boto3.client("s3", **kwargs)

    # ── Connection test ───────────────────────────────────────────────────────

    def test_connection(self) -> dict:
        try:
            client = self._client()
            client.head_bucket(Bucket=self._cfg.bucket_name)
            return {"ok": True, "message": "Connection successful."}
        except Exception as exc:
            return {"ok": False, "message": str(exc)}

    # ── Upload ────────────────────────────────────────────────────────────────

    def _object_key(self, filename: str) -> str:
        prefix = (self._cfg.prefix or "asguard-backups/").rstrip("/") + "/"
        return prefix + filename

    def upload_file(self, local_path: Path, remote_filename: str | None = None) -> dict:
        """Upload a single file. Returns dict with key, size_mb, sha256."""
        local_path = Path(local_path)
        if not local_path.exists():
            return {"ok": False, "error": f"File not found: {local_path}"}

        filename   = remote_filename or local_path.name
        object_key = self._object_key(filename)
        size_mb    = local_path.stat().st_size / (1024 * 1024)
        sha256     = _sha256_file(local_path)

        # Deduplication: check if identical file already in cloud
        try:
            client = self._client()
            head = client.head_object(Bucket=self._cfg.bucket_name, Key=object_key)
            remote_sha = head.get("Metadata", {}).get("sha256", "")
            if remote_sha == sha256:
                logger.info("cloud: skip %s (sha256 match)", filename)
                return {"ok": True, "key": object_key, "size_mb": size_mb,
                        "sha256": sha256, "skipped": True}
        except Exception:
            pass  # object doesn't exist yet

        try:
            client = self._client()
            client.upload_file(
                str(local_path),
                self._cfg.bucket_name,
                object_key,
                ExtraArgs={
                    "Metadata": {
                        "sha256":      sha256,
                        "asguard":     "true",
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    }
                },
            )
            logger.info("cloud: uploaded %s (%.2f MB)", filename, size_mb)
            return {"ok": True, "key": object_key, "size_mb": size_mb, "sha256": sha256}
        except Exception as exc:
            logger.error("cloud: upload failed for %s: %s", filename, exc)
            return {"ok": False, "error": str(exc)}

    def upload_backup_folder(self, backup_id: str, backup_dir: Path) -> dict:
        """
        Compress backup_dir to .tar.gz and upload.
        Temp archive is created in /tmp and deleted after upload.
        """
        tmp_dir = Path("/tmp")
        archive = None
        try:
            logger.info("cloud: compressing %s …", backup_id)
            archive = _compress_folder(Path(backup_dir), tmp_dir)
            result  = self.upload_file(archive, archive.name)
            return result
        except Exception as exc:
            logger.error("cloud: compress/upload failed for %s: %s", backup_id, exc)
            return {"ok": False, "error": str(exc)}
        finally:
            if archive and archive.exists():
                archive.unlink()

    # ── List ──────────────────────────────────────────────────────────────────

    def list_cloud_backups(self) -> list[dict]:
        """Return list of backup objects in cloud bucket (sorted newest first)."""
        prefix = (self._cfg.prefix or "asguard-backups/").rstrip("/") + "/"
        try:
            client   = self._client()
            paginator = client.get_paginator("list_objects_v2")
            objects  = []
            for page in paginator.paginate(Bucket=self._cfg.bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key == prefix:
                        continue
                    objects.append({
                        "key":          key,
                        "filename":     key.split("/")[-1],
                        "size_mb":      round(obj["Size"] / (1024 * 1024), 3),
                        "last_modified": obj["LastModified"].isoformat(),
                    })
            objects.sort(key=lambda x: x["last_modified"], reverse=True)
            return objects
        except Exception as exc:
            logger.error("cloud: list failed: %s", exc)
            return []

    # ── Download ──────────────────────────────────────────────────────────────

    def download_backup(self, cloud_key: str, dest_path: Path) -> dict:
        """Download object at cloud_key to dest_path."""
        try:
            client = self._client()
            dest_path = Path(dest_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            client.download_file(self._cfg.bucket_name, cloud_key, str(dest_path))
            size_mb = dest_path.stat().st_size / (1024 * 1024)
            logger.info("cloud: downloaded %s → %s (%.2f MB)", cloud_key, dest_path, size_mb)
            return {"ok": True, "path": str(dest_path), "size_mb": size_mb}
        except Exception as exc:
            logger.error("cloud: download failed %s: %s", cloud_key, exc)
            return {"ok": False, "error": str(exc)}

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_cloud_backup(self, cloud_key: str) -> dict:
        try:
            client = self._client()
            client.delete_object(Bucket=self._cfg.bucket_name, Key=cloud_key)
            logger.info("cloud: deleted %s", cloud_key)
            return {"ok": True}
        except Exception as exc:
            logger.error("cloud: delete failed %s: %s", cloud_key, exc)
            return {"ok": False, "error": str(exc)}

    # ── Smart retention ───────────────────────────────────────────────────────

    def apply_cloud_retention(self):
        """Keep only the N most recent backups in cloud. Delete the rest."""
        max_copies = self._cfg.max_cloud_copies or 10
        objects    = self.list_cloud_backups()
        if len(objects) <= max_copies:
            return
        to_delete = objects[max_copies:]
        for obj in to_delete:
            self.delete_cloud_backup(obj["key"])
            logger.info("cloud retention: deleted %s", obj["filename"])

    # ── Async helpers ─────────────────────────────────────────────────────────

    @classmethod
    def async_upload_after_backup(cls, backup_id: str, backup_dir: str | None,
                                   backup_type: str, result: dict):
        """
        Called in a daemon thread after every backup.
        Saves BackupRecord to DB, uploads to cloud if configured.
        """
        def _run():
            try:
                import django
                from backend.backup.models import BackupRecord, CloudStorageConfig
                from django.utils import timezone as tz

                metadata = result.get("metadata", {})
                totals   = metadata.get("totals", {})

                record, _ = BackupRecord.objects.get_or_create(
                    backup_id=backup_id,
                    defaults={
                        "backup_type":        backup_type,
                        "backup_scope":       metadata.get("backup_scope", ""),
                        "created_at":         tz.now(),
                        "status":             result.get("status", "error"),
                        "health_score":       metadata.get("health_score"),
                        "size_mb":            totals.get("size_mb"),
                        "components_success": totals.get("components_success", 0),
                        "components_failed":  totals.get("components_failed", 0),
                        "components_skipped": totals.get("components_skipped", 0),
                        "message":            result.get("message", ""),
                        "local_path":         backup_dir or result.get("file", ""),
                    },
                )

                # Cloud upload
                cfg_qs = CloudStorageConfig.objects.filter(enabled=True, auto_upload=True)
                if not cfg_qs.exists() or not backup_dir:
                    return

                cfg     = cfg_qs.first()
                service = cls(cfg)

                # For DB backup (.dump file) upload the file directly
                if backup_type == "db_backup":
                    db_file = Path(result.get("file", ""))
                    if db_file.exists():
                        upload_result = service.upload_file(db_file)
                    else:
                        return
                else:
                    upload_result = service.upload_backup_folder(backup_id, backup_dir)

                if upload_result.get("ok"):
                    record.cloud_uploaded    = True
                    record.cloud_provider    = cfg.provider
                    record.cloud_bucket      = cfg.bucket_name
                    record.cloud_key         = upload_result.get("key", "")
                    record.cloud_size_mb     = upload_result.get("size_mb")
                    record.cloud_uploaded_at = tz.now()
                    record.cloud_error       = ""
                    record.save()
                    service.apply_cloud_retention()
                else:
                    record.cloud_error = upload_result.get("error", "Unknown error")
                    record.save()

            except Exception as exc:
                logger.error("async_upload_after_backup failed: %s", exc)

        threading.Thread(target=_run, daemon=True).start()
