"""
Auto-Pilot — REST API
=====================
Toggle + status + intervention journal for the autonomous remediation engine
(backend/backup/autopilot.py). Consumed by the AI Risk Center.
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from backend.backup import autopilot


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def autopilot_status(request):
    try:
        return JsonResponse(autopilot.status(), status=200)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=200)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def autopilot_config(request):
    data = request.data if isinstance(request.data, dict) else {}
    try:
        cfg = autopilot.save_config(data)
        return JsonResponse({"ok": True, "config": cfg}, status=200)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=200)
