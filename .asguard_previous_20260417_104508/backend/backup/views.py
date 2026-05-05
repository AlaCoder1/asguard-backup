import json
import logging
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from .system_backup.backup_service import SystemBackupService
from .system_backup.full_backup_service import FullBackupService
from .system_backup.restore_service import RestoreService
from .system_backup.export_import_service import ExportImportService

logger = logging.getLogger(__name__)

BACKUP_DIR = Path("/var/backups/asguard")
BACKUP_PATTERNS = ["asguard_backup_*.dump", "asguard_db_*.dump"]

RESTORE_JOBS_DIR = BACKUP_DIR / "restore_jobs"
FULL_RESTORE_RUNNER = Path("/asguard/asguard/full_restore_runner.py")
PYTHON_BIN = "/usr/bin/python"


COMPONENTS_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["components"],
    properties={
        "components": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            example=["firewall", "vpn", "certificates"],
        )
    },
)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="PING BACKUP MODULE")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def ping(request):
    return JsonResponse({"status": "ok", "module": "backup"})


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE DATABASE BACKUP (LEGACY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_db_backup(request):
    result = SystemBackupService.create_db_backup()
    return JsonResponse(result)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE FULL BACKUP (DISASTER RECOVERY)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_full_backup(request):
    result = FullBackupService.create_full_backup()
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="CREATE SAFE BACKUP (ADMIN UI)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_safe_backup(request):
    result = FullBackupService.create_safe_backup()
    status_code = 200 if result["status"] == "ok" else (400 if result["status"] == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema(
    method="post",
    operation_summary="CREATE CUSTOM BACKUP (ONE OR MORE COMPONENTS)",
    request_body=COMPONENTS_REQUEST_SCHEMA,
    responses={200: "OK"},
)
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def create_components_backup(request):
    try:
        payload = request.data if hasattr(request, "data") else {}
    except Exception:
        payload = {}

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse(
            {"status": "error", "message": "'components' must be a JSON array."},
            status=400,
        )

    result = FullBackupService.create_components_backup(components)
    status_code = 200 if result.get("status") == "ok" else (400 if result.get("status") == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="LIST ALL BACKUPS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_all_backups(request):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for d in BACKUP_DIR.glob("backup_*"):
        if d.is_dir():
            meta_file = d / "backup_metadata.json"
            if meta_file.exists():
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)

                    backup_scope = meta.get("backup_scope", "unknown")

                    if backup_scope == "safe_restore_ui":
                        backup_type = "safe"
                    elif backup_scope == "selected_components":
                        backup_type = "custom"
                    else:
                        backup_type = "full"

                    results.append({
                        "type": backup_type,
                        "scope": backup_scope,
                        "id": d.name,
                        "filename": d.name,
                        "modified_at": meta.get("created_at", datetime.fromtimestamp(d.stat().st_mtime).isoformat()),
                        "metadata": meta,
                    })
                except Exception:
                    logger.warning("Could not read metadata for backup %s", d.name)

    for pattern in BACKUP_PATTERNS:
        for p in BACKUP_DIR.glob(pattern):
            st = p.stat()
            results.append({
                "type": "database_only",
                "scope": "legacy_database_only",
                "id": p.name,
                "filename": p.name,
                "size_bytes": st.st_size,
                "modified_at": datetime.fromtimestamp(st.st_mtime).isoformat(),
            })

    results.sort(key=lambda x: x["modified_at"], reverse=True)
    return JsonResponse({"count": len(results), "results": results})


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET BACKUP DETAILS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_backup_details(request, backup_id):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    metadata_file = backup_dir / "backup_metadata.json"
    if not metadata_file.exists():
        return JsonResponse({"status": "error", "message": "backup_metadata.json not found."}, status=404)

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        files = []
        total_size = 0
        for p in backup_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(backup_dir))
                size = p.stat().st_size
                total_size += size
                files.append({
                    "path": rel,
                    "size_bytes": size,
                    "modified_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                })

        return JsonResponse({
            "status": "ok",
            "backup_id": backup_id,
            "backup_dir": str(backup_dir),
            "total_size_bytes": total_size,
            "metadata": metadata,
            "files": files,
        })
    except Exception as e:
        logger.exception("Failed to read backup details for %s", backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="SAFE FULL RESTORE (WITHOUT APPLICATION)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="safe")


@swagger_auto_schema("POST", responses={202: "Accepted"}, operation_summary="FULL RESTORE COMPLETE (WITH APPLICATION)")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_full_backup(request, backup_id):
    return _launch_detached_restore(backup_id=backup_id, mode="complete")


@swagger_auto_schema(
    method="post",
    operation_summary="RESTORE SELECTED COMPONENTS (SAFE, WITHOUT APPLICATION)",
    request_body=COMPONENTS_REQUEST_SCHEMA,
    responses={200: "OK"},
)
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_components_backup(request, backup_id):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    try:
        payload = request.data if hasattr(request, "data") else {}
    except Exception:
        payload = {}

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse(
            {"status": "error", "message": "'components' must be a JSON array."},
            status=400,
        )

    result = RestoreService.restore_components_safe(backup_id, components)
    status_code = 200 if result.get("status") == "success" else (400 if result.get("status") == "error" else 207)
    return JsonResponse(result, status=status_code)


@swagger_auto_schema(
    method="post",
    operation_summary="RESTORE SELECTED COMPONENTS (COMPLETE, APPLICATION ALLOWED)",
    request_body=COMPONENTS_REQUEST_SCHEMA,
    responses={200: "OK"},
)
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def restore_components_complete_backup(request, backup_id):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    try:
        payload = request.data if hasattr(request, "data") else {}
    except Exception:
        payload = {}

    components = payload.get("components", [])
    if not isinstance(components, list):
        return JsonResponse(
            {"status": "error", "message": "'components' must be a JSON array."},
            status=400,
        )

    result = RestoreService.restore_components_complete(backup_id, components)
    status_code = 200 if result.get("status") == "success" else (400 if result.get("status") == "error" else 207)
    return JsonResponse(result, status=status_code)


def _launch_detached_restore(backup_id: str, mode: str):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    metadata_file = backup_dir / "backup_metadata.json"
    if not metadata_file.exists():
        return JsonResponse({"status": "error", "message": "backup_metadata.json not found."}, status=404)

    RESTORE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    (RESTORE_JOBS_DIR / "logs").mkdir(parents=True, exist_ok=True)

    job_id = f"restore_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_id}"
    state_file = RESTORE_JOBS_DIR / f"{job_id}.json"
    log_file = RESTORE_JOBS_DIR / "logs" / f"{job_id}.log"

    initial_state = {
        "job_id": job_id,
        "backup_id": backup_id,
        "mode": mode,
        "status": "queued",
        "started_at": None,
        "finished_at": None,
        "log_file": str(log_file),
        "result": None,
    }

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(initial_state, f, indent=2)

    unit_name = f"asguard-restore-{mode}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    shell_cmd = (
        f"exec {shlex.quote(PYTHON_BIN)} "
        f"{shlex.quote(str(FULL_RESTORE_RUNNER))} "
        f"{shlex.quote(backup_id)} "
        f"{shlex.quote(job_id)} "
        f"{shlex.quote(mode)} "
        f">> {shlex.quote(str(log_file))} 2>&1"
    )

    cmd = [
        "sudo",
        "-n",
        "systemd-run",
        "--unit", unit_name,
        "--description", f"Asguard {mode} restore {backup_id}",
        "--property=WorkingDirectory=/asguard/asguard",
        "/usr/bin/bash",
        "-lc",
        shell_cmd,
    ]

    try:
        launch = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
            check=False,
        )

        if launch.returncode != 0:
            logger.error(
                "systemd-run failed rc=%s output=%s",
                launch.returncode,
                launch.stdout.strip(),
            )
            return JsonResponse({
                "status": "error",
                "message": "Failed to launch detached restore unit.",
                "returncode": launch.returncode,
                "launcher_output": launch.stdout.strip(),
                "unit_name": unit_name,
                "mode": mode,
            }, status=500)

        logger.info("%s restore unit started: %s | output=%s", mode, unit_name, launch.stdout.strip())

        return JsonResponse({
            "status": "started",
            "message": f"{mode} restore launched in detached systemd unit.",
            "backup_id": backup_id,
            "job_id": job_id,
            "mode": mode,
            "state_file": str(state_file),
            "log_file": str(log_file),
            "unit_name": unit_name,
            "launcher_output": launch.stdout.strip(),
        }, status=202)

    except Exception as e:
        logger.exception("Failed to launch %s restore for %s", mode, backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET FULL RESTORE JOB STATUS")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_restore_full_status(request, job_id):
    state_file = RESTORE_JOBS_DIR / f"{job_id}.json"
    if not state_file.exists():
        return JsonResponse({"status": "error", "message": f"Restore job {job_id} not found."}, status=404)

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return JsonResponse(payload, status=200)
    except Exception as e:
        logger.exception("Failed to read restore job status %s", job_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("DELETE", responses={200: "OK"}, operation_summary="DELETE BACKUP")
@api_view(["DELETE"])
@require_http_methods(["DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def delete_backup(request, backup_id):
    backup_dir = BACKUP_DIR / backup_id
    if not backup_dir.exists() or not backup_dir.is_dir():
        return JsonResponse({"status": "error", "message": f"Backup {backup_id} not found."}, status=404)

    try:
        import shutil
        shutil.rmtree(backup_dir)
        return JsonResponse({"status": "success", "message": f"Backup {backup_id} deleted."})
    except Exception as e:
        logger.exception("Failed to delete backup %s", backup_id)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="EXPORT BACKUP")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def export_backup(request, backup_id):
    export_path = ExportImportService.export_backup(backup_id)
    if not export_path:
        return JsonResponse(
            {"status": "error", "message": "Backup export failed or not found."},
            status=404
        )

    response = FileResponse(open(export_path, "rb"), content_type="application/gzip")
    response["Content-Disposition"] = f'attachment; filename="asguard_export_{backup_id}.tar.gz"'
    return response


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="IMPORT BACKUP")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def import_backup(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "No file uploaded."}, status=400)

    result = ExportImportService.import_backup(uploaded_file)
    status_code = 200 if result.get("status") == "success" else 400
    return JsonResponse(result, status=status_code)