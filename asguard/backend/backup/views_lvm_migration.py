"""
views_lvm_migration.py — REST API for LVM coverage migration

Exposes the dry-run / status / apply / rollback / audit endpoints used by the
Backup & DRP UI to extend snapshot coverage to system configurations.
"""

import threading
import uuid
from pathlib import Path

from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .system_backup.lvm_migration_service import LVMMigrationService as Mig


# ── Status / coverage ──────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_status(request):
    """État détaillé item par item + résumé global de couverture."""
    return JsonResponse(Mig.get_global_status())


# ── Plan (dry-run) ─────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_plan(request):
    """
    Plan détaillé de ce qui SERAIT fait — aucune action n'est exécutée.
    Inclut espace requis, warnings, et étapes par item.
    """
    return JsonResponse(Mig.plan())


# ── Config ─────────────────────────────────────────────────────────────────────

@api_view(["GET", "PUT"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_config(request):
    if request.method == "GET":
        return JsonResponse(Mig.read_config())
    try:
        cfg = request.data if hasattr(request, "data") else {}
        Mig.write_config(cfg)
        return JsonResponse({"status": "saved", "config": Mig.read_config()})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=400)


# ── Apply (async) ──────────────────────────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_apply(request):
    """
    Lance la migration en arrière-plan.
    Body JSON: { "dry_run": bool, "ids": ["nftables", "openvpn", ...] }
    """
    data = request.data if hasattr(request, "data") else {}
    dry_run = bool(data.get("dry_run", True))
    ids = data.get("ids") or None

    if dry_run:
        # Synchronous — c'est juste un calcul de plan
        return JsonResponse({"dry_run": True, "plan": Mig.plan()})

    job_id = f"mig_{uuid.uuid4().hex[:10]}"

    def worker():
        try:
            Mig.apply(dry_run=False, ids=ids, job_id=job_id)
        except Exception as e:
            from .system_backup.lvm_migration_service import _write_job, JOBS_DIR
            _write_job(JOBS_DIR / f"{job_id}.json", {
                "job_id": job_id, "status": "error", "error": str(e),
            })

    t = threading.Thread(target=worker, daemon=True, name=f"lvm-mig-{job_id}")
    t.start()
    return JsonResponse({"status": "queued", "job_id": job_id})


# ── Job progress ───────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_progress(request, job_id: str):
    from .system_backup.lvm_migration_service import JOBS_DIR
    import json
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        return JsonResponse({"status": "not_found"}, status=404)
    try:
        return JsonResponse(json.loads(job_file.read_text()))
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=500)


# ── Rollback ───────────────────────────────────────────────────────────────────

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_rollback(request):
    """Body JSON: { "ids": [...] } (vide = rollback global)."""
    data = request.data if hasattr(request, "data") else {}
    ids = data.get("ids") or None
    result = Mig.rollback(ids=ids)
    return JsonResponse(result)


# ── Audit history ──────────────────────────────────────────────────────────────

@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def lvm_migration_audit(request):
    limit = int(request.GET.get("limit", 20))
    return JsonResponse({"audits": Mig.list_audits(limit=limit)})
