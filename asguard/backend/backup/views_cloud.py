"""
Cloud Storage API — S3-compatible bucket integration for backup mirroring.

Extracted from views.py during the code-review cleanup to keep the main
views file under a reviewable size. The cloud feature is self-contained:
it uses its own CloudStorageService + CloudStorageConfig/BackupRecord
models, and only depends on the shared observability helper for event
logging.

Endpoints (all under /backup/cloud/):
    GET/POST    config          — read or save provider credentials
    POST        test            — verify the bucket is reachable
    GET         backups         — list objects stored remotely
    POST        sync/<id>       — push a local backup to the cloud
    GET         history         — return BackupRecord rows from the DB
"""

import json

from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from backend.backup.observability import append_backup_event
from backend.backup.system_backup.cloud_storage import CloudStorageService

# Same root the rest of the backup module uses. Kept as a module-level
# constant rather than importing from views.py to avoid a circular import.
from pathlib import Path
_BACKUP_ROOT = Path("/var/backups/asguard")


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_config(request):
    """GET: return current cloud config. POST: save cloud config."""
    from backend.backup.models import CloudStorageConfig

    if request.method == "GET":
        cfg = CloudStorageConfig.objects.first()
        if not cfg:
            return JsonResponse({"configured": False})
        return JsonResponse({
            "configured":             True,
            "id":                     cfg.pk,
            "provider":               cfg.provider,
            "endpoint_url":           cfg.endpoint_url,
            "access_key_id":          cfg.access_key_id,
            "secret_access_key":      "••••••••",  # never returned in clear
            "bucket_name":            cfg.bucket_name,
            "region":                 cfg.region,
            "prefix":                 cfg.prefix,
            "enabled":                cfg.enabled,
            "auto_upload":            cfg.auto_upload,
            "upload_db_only_to_cloud": cfg.upload_db_only_to_cloud,
            "max_cloud_copies":       cfg.max_cloud_copies,
        })

    # POST — save config. Secret is only overwritten when the client sent a
    # non-masked value (UI submits the bullet-string back unchanged when the
    # user does not retype the secret).
    data = request.data if hasattr(request, "data") else json.loads(request.body)
    cfg  = CloudStorageConfig.objects.first() or CloudStorageConfig()
    cfg.provider        = data.get("provider", "backblaze_b2")
    cfg.endpoint_url    = data.get("endpoint_url", "")
    cfg.access_key_id   = data.get("access_key_id", "")
    cfg.bucket_name     = data.get("bucket_name", "")
    cfg.region          = data.get("region", "us-east-1")
    cfg.prefix          = data.get("prefix", "asguard-backups/")
    cfg.enabled         = bool(data.get("enabled", True))
    cfg.auto_upload     = bool(data.get("auto_upload", True))
    cfg.upload_db_only_to_cloud = bool(data.get("upload_db_only_to_cloud", False))
    cfg.max_cloud_copies = int(data.get("max_cloud_copies", 10))
    secret = data.get("secret_access_key", "")
    if secret and secret != "••••••••":
        cfg.secret_access_key = secret
    cfg.save()
    append_backup_event(
        kind="cloud",
        title="Cloud backup configuration saved",
        severity="info",
        status="success",
        source="api",
        ref_id=str(cfg.pk),
        extra={"provider": cfg.provider, "bucket": cfg.bucket_name,
               "auto_upload": cfg.auto_upload},
    )
    return JsonResponse({"status": "ok", "id": cfg.pk})


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_test(request):
    """Test connection to the configured cloud bucket."""
    from backend.backup.models import CloudStorageConfig

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "message": "No cloud storage configured."}, status=400)
    result = CloudStorageService(cfg).test_connection()
    status = 200 if result["ok"] else 400
    append_backup_event(
        kind="cloud",
        title=("Cloud backup connection test succeeded"
               if result.get("ok") else "Cloud backup connection test failed"),
        severity="success" if result.get("ok") else "error",
        status="success" if result.get("ok") else "error",
        source="api",
        detail=result.get("message", result.get("error", "")),
        extra={"provider": cfg.provider, "bucket": cfg.bucket_name},
    )
    return JsonResponse(result, status=status)


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_list(request):
    """List all backups currently stored in the cloud bucket."""
    from backend.backup.models import CloudStorageConfig

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "backups": [],
                             "message": "No cloud storage configured."})
    backups = CloudStorageService(cfg).list_cloud_backups()
    return JsonResponse({"ok": True, "backups": backups, "count": len(backups)})


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_sync(request, backup_id):
    """Manually push a local backup to cloud."""
    from backend.backup.models import CloudStorageConfig, BackupRecord
    from django.utils import timezone as tz

    cfg = CloudStorageConfig.objects.filter(enabled=True).first()
    if not cfg:
        return JsonResponse({"ok": False, "message": "No cloud storage configured."}, status=400)

    backup_dir = _BACKUP_ROOT / backup_id
    if not backup_dir.exists():
        return JsonResponse({"ok": False, "message": f"Backup {backup_id} not found locally."}, status=404)

    service = CloudStorageService(cfg)
    result  = service.upload_backup_folder(backup_id, backup_dir)

    if result.get("ok"):
        BackupRecord.objects.filter(backup_id=backup_id).update(
            cloud_uploaded=True,
            cloud_provider=cfg.provider,
            cloud_bucket=cfg.bucket_name,
            cloud_key=result.get("key", ""),
            cloud_size_mb=result.get("size_mb"),
            cloud_uploaded_at=tz.now(),
            cloud_error="",
        )

    append_backup_event(
        kind="cloud",
        title="Cloud backup sync completed" if result.get("ok") else "Cloud backup sync failed",
        severity="success" if result.get("ok") else "error",
        status="success" if result.get("ok") else "error",
        source="api",
        ref_id=backup_id,
        detail=result.get("message", result.get("error", "")),
        extra={"key": result.get("key", ""), "size_mb": result.get("size_mb"),
               "provider": cfg.provider},
    )
    return JsonResponse(result)


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def cloud_backup_history(request):
    """Return backup history from DB (BackupRecord)."""
    from backend.backup.models import BackupRecord

    records = BackupRecord.objects.all()[:50]
    return JsonResponse({"records": [r.to_dict() for r in records]})
