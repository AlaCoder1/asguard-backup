import json
import subprocess
import threading
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render
from backend.dashboard.functions import get_system_infomations, service_action, update_sevice_DB
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from backend.backup.notifications import notify_service_action

_WD_CONFIG   = Path("/etc/asguard/watchdog_config.json")
_WD_INCIDENTS = Path("/var/log/asguard/watchdog_incidents.json")

_DEFAULT_WD_CONFIG = {
    "enabled": True,
    "check_interval_seconds": 30,
    "services": [
        {"name": "uvicorn",        "display": "API Uvicorn",         "critical": True,  "restart_count": 0},
        {"name": "nginx",          "display": "Nginx Web",           "critical": True,  "restart_count": 0},
        {"name": "UpApp",          "display": "Docker Services",     "critical": False, "restart_count": 0},
        {"name": "sshd",           "display": "SSH Daemon",          "critical": False, "restart_count": 0},
        {"name": "NetworkManager", "display": "Network Manager",     "critical": True,  "restart_count": 0},
        {"name": "nftables",       "display": "Firewall (nftables)", "critical": True,  "restart_count": 0},
    ],
    "notifications": {
        "email_enabled": False,
        "smtp_host": "",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_password": "",
        "recipients": [],
        "alert_on_failure": True,
        "alert_on_recovery": True,
    },
}


def _wd_read_config():
    if not _WD_CONFIG.exists():
        _wd_write_config(_DEFAULT_WD_CONFIG)
        return json.loads(json.dumps(_DEFAULT_WD_CONFIG))
    try:
        return json.loads(_WD_CONFIG.read_text())
    except Exception:
        return json.loads(json.dumps(_DEFAULT_WD_CONFIG))


def _wd_write_config(cfg):
    _WD_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    _WD_CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))


def _service_active(name):
    r = subprocess.run(["systemctl", "is-active", name],
                       capture_output=True, text=True)
    return r.stdout.strip() == "active"


def _watchdog_daemon_active():
    return _service_active("asguard-watchdog")
@swagger_auto_schema(
    method='PUT',
    operation_summary="API to update service action",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'service': openapi.Schema(type=openapi.TYPE_STRING,
                                      enum=['sshd','dhclient@','suricata','squid',
                                            'nftables','NetworkManager','openvpn',
                                            'ipsec','clamv','Asguard-Networking'],default="sshd"),
            'action': openapi.Schema(type=openapi.TYPE_STRING,enum=["enable","disable","start","stop"]),
        },
        required=['service', 'action'],
    ),
    responses={
        200: openapi.Response(
            description='Service action performed successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'msg': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['msg'],
            ),
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'msg': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['msg'],
            ),
        ),
    },
)
# API to set actions service
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def set_actions_service(request):
    if (request.method == 'PUT'):
        data_in=request.data
        service=data_in.get('service',None)
        action=data_in.get('action',None)
        if action is not None and service is not None:
            match action.lower():
                case "enable":
                    data={
                        "status_enabled":True
                    }
                    msg_suc=_('The service has enabled successfully!')
                    msg_err=_('Failed to enable the service!')
                case "disable":
                    data={
                        "status_enabled":False
                    }
                    msg_suc=_('The service has disabled successfully!')
                    msg_err=_('Failed to disable the service!')
                case "start":
                    data={
                        "status_started":True
                    }
                    msg_suc=_('The service has started successfully!')
                    msg_err=_('Failed to start the service!')
                case "stop":
                    data={
                        "status_started":False
                    }
                    msg_suc=_('The service has stopped successfully!')
                    msg_err=_('Failed to stop the service!')
                case "restart":
                    data={
                        "status_started":True
                    }
                    msg_suc=_('The service has restarted successfully!')
                    msg_err=_('Failed to restart the service!')
        aux=service_action(service, action)
        if aux.get("ok") is True:
           state = aux.get("state", {})
           data["status_started"] = state.get("status_started", data.get("status_started", False))
           data["status_enabled"] = state.get("status_enabled", data.get("status_enabled", False))
           data["status_install"] = state.get("status_install", True)
           db_update = update_sevice_DB(service,data)
           if db_update is True:
               msg=msg_suc
               status=200
           else:
               msg=db_update
               status=400
           threading.Thread(target=notify_service_action, args=(service, action, db_update is True), daemon=True).start()
        else:
            state = aux.get("state", {})
            if state:
                data["status_started"] = state.get("status_started", False)
                data["status_enabled"] = state.get("status_enabled", False)
                data["status_install"] = state.get("status_install", True)
                update_sevice_DB(service, data)
            error_detail = aux.get("error")
            msg=f"{msg_err} {error_detail}".strip()
            status=400
            threading.Thread(target=notify_service_action, args=(service, action, False), daemon=True).start()

        return JsonResponse({"msg": msg}, status=status)


# ── Watchdog API ──────────────────────────────────────────────────────────────

@swagger_auto_schema("GET", responses={200: "OK"}, operation_summary="GET watchdog status")
@api_view(["GET"])
@require_http_methods(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def get_watchdog_status(request):
    cfg       = _wd_read_config()
    daemon_ok = _watchdog_daemon_active()

    services_status = []
    for svc in cfg.get("services", []):
        name = svc["name"]
        services_status.append({
            "name":          name,
            "display":       svc.get("display", name),
            "critical":      svc.get("critical", False),
            "active":        _service_active(name),
            "restart_count": svc.get("restart_count", 0),
        })

    incidents = []
    if _WD_INCIDENTS.exists():
        try:
            all_inc = json.loads(_WD_INCIDENTS.read_text())
            incidents = list(reversed(all_inc[-20:]))
        except Exception:
            pass

    notif = cfg.get("notifications", {})
    safe_notif = {k: v for k, v in notif.items() if k != "smtp_password"}

    return JsonResponse({
        "daemon_active":    daemon_ok,
        "enabled":          cfg.get("enabled", True),
        "check_interval":   cfg.get("check_interval_seconds", 30),
        "services":         services_status,
        "notifications":    safe_notif,
        "recent_incidents": incidents,
    })


@swagger_auto_schema("PUT", responses={200: "OK"}, operation_summary="UPDATE watchdog config")
@api_view(["PUT"])
@require_http_methods(["PUT"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def update_watchdog_config(request):
    data = request.data
    cfg  = _wd_read_config()

    if "enabled" in data:
        cfg["enabled"] = bool(data["enabled"])
    if "check_interval_seconds" in data:
        cfg["check_interval_seconds"] = max(10, int(data["check_interval_seconds"]))

    if "notifications" in data:
        notif = cfg.setdefault("notifications", {})
        for key in ("email_enabled", "smtp_host", "smtp_port", "smtp_user",
                    "smtp_password", "recipients", "alert_on_failure", "alert_on_recovery"):
            if key in data["notifications"]:
                notif[key] = data["notifications"][key]

    _wd_write_config(cfg)
    return JsonResponse({"msg": "Configuration watchdog mise à jour"})


@swagger_auto_schema("POST", responses={200: "OK"}, operation_summary="Toggle watchdog daemon")
@api_view(["POST"])
@require_http_methods(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def toggle_watchdog_daemon(request):
    action = request.data.get("action", "start")
    if action not in ("start", "stop", "restart", "enable", "disable"):
        return JsonResponse({"msg": "Action invalide"}, status=400)

    r = subprocess.run(["systemctl", action, "asguard-watchdog"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return JsonResponse({"msg": r.stderr.strip() or "Erreur systemctl"}, status=500)

    return JsonResponse({"msg": f"Watchdog daemon: {action} OK",
                         "active": _watchdog_daemon_active()})

