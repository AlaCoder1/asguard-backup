"""
views_vm_snapshot.py — REST API for LVM snapshot management
"""

import json
import re
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from .system_backup.lvm_snapshot_service import LVMSnapshotService as Svc

LOCAL_TZ = ZoneInfo("Africa/Tunis")


def _write_job(job_file: Path, payload: dict):
    job_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = job_file.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    tmp.replace(job_file)


# ── LVM info + config ──────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_info(request):
    info = Svc.get_lvm_info()
    cfg  = Svc.read_config()
    return JsonResponse({"vm_info": info, "config": cfg})


# ── Test LVM connection ────────────────────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_test_connection(request):
    return JsonResponse(Svc.test_connection())


# ── List snapshots ─────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_list(request):
    return JsonResponse({"snapshots": Svc.list_snapshots()})


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_verify(request):
    connection = Svc.test_connection()
    snapshots  = Svc.list_snapshots()
    return JsonResponse({
        "status":     "success" if connection.get("connected") and connection.get("lv_ok") else "warning",
        "checked_at": datetime.now(LOCAL_TZ).isoformat(),
        "connection": connection,
        "snapshots":  snapshots,
        "count":      len(snapshots),
    })


# ── Create snapshot (async) ────────────────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_create(request):
    description = request.data.get("description", "").strip() or "Snapshot LVM"
    raw_name    = request.data.get("name", "").strip()
    ts          = datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
    job_id      = f"snap_job_{ts}"

    if raw_name:
        safe_name = re.sub(r"[^A-Za-z0-9_\-]+", "_", raw_name).strip("_")[:32]
        snap_id   = f"{safe_name}_{ts}" if safe_name else f"asguard_snap_{ts}"
    else:
        snap_id = f"asguard_snap_{ts}"

    job_file   = Svc.JOBS_DIR / f"{job_id}.json"
    started_at = datetime.now(LOCAL_TZ).isoformat()

    _write_job(job_file, {
        "job_id":             job_id,
        "status":             "running",
        "started_at":         started_at,
        "description":        description,
        "snap_id":            snap_id,
        "message":            "Création du snapshot LVM en cours…",
        "phase":              "lvcreate",
        "phase_label":        "Capture LVM (CoW)",
        "estimated_seconds":  Svc.estimated_snapshot_seconds(),
        "result":             None,
    })

    def _run():
        result = Svc.create_snapshot(description=description, snap_name=snap_id, job_id=job_id)
        rs = result.get("status", "error")
        payload = {
            "job_id":            job_id,
            "status":            "done" if rs == "success" else rs,
            "started_at":        started_at,
            "finished_at":       datetime.now(LOCAL_TZ).isoformat(),
            "description":       description,
            "snap_id":           result.get("snap_id"),
            "message":           result.get("message", ""),
            "error":             result.get("error", ""),
            "phase":             "completed" if rs == "success" else result.get("phase", "error"),
            "phase_label":       "Snapshot enregistré" if rs == "success" else result.get("phase_label", "Erreur LVM"),
            "duration_seconds":  result.get("duration_seconds", 0),
            "estimated_seconds": Svc.estimated_snapshot_seconds(),
            "result":            result,
        }
        # Forward the structured error fields so the UI can show an
        # actionable "free space" dialog instead of a generic toast.
        for k in ("error_type", "vg_name", "vg_free_gb", "required_gb",
                  "shortfall_gb", "existing_snapshots", "suggested_action"):
            if k in result:
                payload[k] = result[k]
        _write_job(job_file, payload)

    threading.Thread(target=_run, daemon=True).start()
    return JsonResponse({
        "status":            "queued",
        "job_id":            job_id,
        "snap_id":           snap_id,
        "started_at":        started_at,
        "estimated_seconds": Svc.estimated_snapshot_seconds(),
    }, status=202)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def vm_snapshot_progress(request, job_id):
    data = Svc.read_job(job_id)
    if data is None:
        return JsonResponse({"error": "Job introuvable"}, status=404)
    return JsonResponse(data)


# ── Restore snapshot (async) ───────────────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_restore(request, snap_id):
    ts         = datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
    job_id     = f"snap_restore_{ts}"
    job_file   = Svc.JOBS_DIR / f"{job_id}.json"
    started_at = datetime.now(LOCAL_TZ).isoformat()

    # Capture snapshot metadata BEFORE the restore — the merge step deletes
    # the metadata file, so without this snapshot the Historique Restores
    # panel would just see a job id with no human context.
    snap_meta = Svc._load_meta(snap_id) or {}
    description = snap_meta.get("description") or "—"
    created_by  = snap_meta.get("created_by")  or "manual"
    created_at  = snap_meta.get("created_at")  or ""

    # Phase timeline — fed step by step so the UI can render a vertical
    # checklist that explains exactly what the restore does (umount →
    # lvconvert --merge → deactivate/reactivate → remount).
    phases = [
        {"key": "snapshot",   "label": "Snapshot capturé",        "status": "done",    "at": created_at},
        {"key": "umount",     "label": "Démontage du volume",      "status": "pending", "at": None},
        {"key": "merge",      "label": "Fusion LVM (merge)",       "status": "pending", "at": None},
        {"key": "reactivate", "label": "Réactivation LV",          "status": "pending", "at": None},
        {"key": "remount",    "label": "Remontage filesystem",     "status": "pending", "at": None},
    ]

    _write_job(job_file, {
        "job_id":              job_id,
        "snap_id":             snap_id,
        "status":              "running",
        "started_at":          started_at,
        "description":         description,
        "created_by":          created_by,
        "snapshot_created_at": created_at,
        "phases":              phases,
        "message":             "Fusion LVM (merge) en cours…",
        "result":              None,
    })

    def _run():
        result = Svc.restore_snapshot(snap_id=snap_id)
        success = result.get("status") == "success"
        final_status = "done" if success else "error"
        finished_at = datetime.now(LOCAL_TZ).isoformat()

        # All phases either succeed together (LVM merge is atomic) or fail
        # at the merge step — there is no partial state to represent.
        if success:
            for p in phases:
                if p["status"] != "done":
                    p["status"] = "done"
                    p["at"] = finished_at
        else:
            for p in phases:
                if p["status"] == "pending":
                    p["status"] = "failed"
                    p["at"] = finished_at
                    break

        _write_job(job_file, {
            "job_id":              job_id,
            "snap_id":             snap_id,
            "status":              final_status,
            "started_at":          started_at,
            "finished_at":         finished_at,
            "description":         description,
            "created_by":          created_by,
            "snapshot_created_at": created_at,
            "phases":              phases,
            "message":             result.get("message", ""),
            "error":               result.get("error", ""),
            "result":              result,
        })

    threading.Thread(target=_run, daemon=True).start()
    return JsonResponse({"status": "queued", "job_id": job_id, "started_at": started_at}, status=202)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def vm_snapshot_restore_status(request, job_id):
    data = Svc.read_job(job_id)
    if data is None:
        return JsonResponse({"error": "Job introuvable"}, status=404)
    return JsonResponse(data)


# ── Delete ─────────────────────────────────────────────────────────────────────

@api_view(["DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_delete(request, snap_id):
    result = Svc.delete_snapshot(snap_id)
    if result.get("status") == "success":
        return JsonResponse({"msg": "Snapshot supprimé."})
    return JsonResponse({"msg": result.get("error", "Erreur suppression.")}, status=500)


# ── Config ─────────────────────────────────────────────────────────────────────

@api_view(["GET", "PUT"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_config(request):
    if request.method == "GET":
        return JsonResponse({"config": Svc.read_config()})

    data = request.data
    cfg  = Svc.read_config()

    if "auto_before_full_backup" in data:
        cfg["auto_before_full_backup"] = bool(data["auto_before_full_backup"])
    if "max_snapshots" in data:
        cfg["max_snapshots"] = max(1, min(10, int(data["max_snapshots"])))
    if "snap_size_gb" in data:
        cfg["snap_size_gb"] = max(1, min(20, int(data["snap_size_gb"])))

    Svc.write_config(cfg)
    return JsonResponse({"msg": "Configuration sauvegardée.", "config": cfg})


# ── Running jobs ───────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def vm_snapshot_running_jobs(request):
    return JsonResponse({"jobs": Svc.list_running_jobs()})


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_last_restore(request):
    data = Svc.get_last_restore(max_age_minutes=10)
    return JsonResponse({"restore": data})


# ── Cancel (kept for API compatibility) ────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vm_snapshot_cancel(request, job_id):
    job_file = Svc.JOBS_DIR / f"{job_id}.json"
    try:
        data = json.loads(job_file.read_text()) if job_file.exists() else {}
        data.update({"status": "cancelled", "error": "Annulé par l'utilisateur."})
        job_file.write_text(json.dumps(data, indent=2))
    except Exception:
        pass
    return JsonResponse({"cancelled": True})
