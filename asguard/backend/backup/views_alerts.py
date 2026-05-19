"""
Alerts & Mailing — REST API
===========================
Configuration des canaux de notification (Email, ntfy, Slack, Discord) et de
la matrice d'abonnement par catégorie d'événement. Consommé par l'onglet
"Alertes & Mailing" de l'interface backup.
"""

from datetime import datetime, timezone

from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from backend.backup.notifications import (
    CATEGORIES, CATEGORY_IDS, CHANNELS,
    _alerts_block, _load_full_config, _load_notif_config, _save_notif_config,
    _send_ntfy, _send_slack, _send_twilio_sms, send_notification, _build_html,
)


def _public_notif(notif: dict) -> dict:
    """Strip secrets before returning the config to the UI."""
    safe = dict(notif)
    if safe.get("smtp_password"):
        safe["smtp_password"] = "•••••••"
    alerts = safe.get("alerts") or {}

    # Slack webhook: only confirm presence, never echo the URL.
    if alerts.get("slack", {}).get("webhook_url"):
        url = alerts["slack"]["webhook_url"]
        alerts["slack"] = dict(alerts["slack"])
        alerts["slack"]["webhook_url_masked"] = url[:32] + "…" if len(url) > 32 else url
        alerts["slack"]["has_webhook"] = True
        alerts["slack"]["webhook_url"] = ""

    # Twilio auth token: mask, keep the SID visible (it's not secret on its own).
    tw = alerts.get("twilio") or {}
    if tw.get("auth_token"):
        tw = dict(tw)
        tw["has_auth_token"] = True
        tw["auth_token_masked"] = "••••••" + tw["auth_token"][-4:] if len(tw["auth_token"]) >= 4 else "••••••"
        tw["auth_token"] = ""
        alerts["twilio"] = tw

    safe["alerts"] = alerts
    return safe


@api_view(["GET", "PUT"])
@authentication_classes([])
@permission_classes([AllowAny])
def alerts_config(request):
    """GET → current config + category catalog.
    PUT  → save merged config (only the fields the UI sends are touched).
    """
    if request.method == "GET":
        notif = _load_notif_config()
        # Ensure the alerts block exists so the UI starts with defaults.
        notif["alerts"] = _alerts_block(notif)
        return JsonResponse({
            "config":     _public_notif(notif),
            "categories": CATEGORIES,
            "channels":   CHANNELS,
        })

    # PUT — merge into existing config so partial updates are safe.
    data = request.data if hasattr(request, "data") else {}
    notif = _load_notif_config()
    alerts = _alerts_block(notif)

    # ── Email block ──────────────────────────────────────────────────────────
    if "email_enabled" in data:
        notif["email_enabled"] = bool(data["email_enabled"])
    for k in ("smtp_host", "smtp_user", "sender_name", "sender_email"):
        if k in data and isinstance(data[k], str):
            notif[k] = data[k].strip()
    if "smtp_port" in data:
        try:
            notif["smtp_port"] = int(data["smtp_port"])
        except (TypeError, ValueError):
            pass
    # Password — only overwrite when a non-empty, non-masked value is sent.
    pw = data.get("smtp_password")
    if isinstance(pw, str) and pw and not pw.startswith("•"):
        notif["smtp_password"] = pw
    if "recipients" in data and isinstance(data["recipients"], list):
        notif["recipients"] = [r.strip() for r in data["recipients"]
                               if isinstance(r, str) and r.strip()]

    # ── ntfy block ───────────────────────────────────────────────────────────
    if "ntfy" in data and isinstance(data["ntfy"], dict):
        notif_ntfy = notif.get("ntfy") or {}
        if "enabled" in data["ntfy"]:
            notif_ntfy["enabled"] = bool(data["ntfy"]["enabled"])
        if "topic" in data["ntfy"]:
            notif_ntfy["topic"] = str(data["ntfy"]["topic"]).strip()
        notif["ntfy"] = notif_ntfy

    # ── alerts: slack / twilio / severity / quiet hours / matrix ─────────────
    if "alerts" in data and isinstance(data["alerts"], dict):
        a_in = data["alerts"]

        if "slack" in a_in and isinstance(a_in["slack"], dict):
            cur = alerts.get("slack") or {}
            if "enabled" in a_in["slack"]:
                cur["enabled"] = bool(a_in["slack"]["enabled"])
            w = a_in["slack"].get("webhook_url")
            if isinstance(w, str):
                cur["webhook_url"] = w.strip()
            alerts["slack"] = cur

        if "twilio" in a_in and isinstance(a_in["twilio"], dict):
            cur = alerts.get("twilio") or {}
            tw_in = a_in["twilio"]
            if "enabled" in tw_in:
                cur["enabled"] = bool(tw_in["enabled"])
            for k in ("account_sid", "from_number"):
                if k in tw_in and isinstance(tw_in[k], str):
                    cur[k] = tw_in[k].strip()
            # auth_token: only overwrite when a non-empty, non-masked value is sent
            tok = tw_in.get("auth_token")
            if isinstance(tok, str) and tok and not tok.startswith("•"):
                cur["auth_token"] = tok.strip()
            if "recipients" in tw_in and isinstance(tw_in["recipients"], list):
                cur["recipients"] = [r.strip() for r in tw_in["recipients"]
                                     if isinstance(r, str) and r.strip()]
            if tw_in.get("min_severity") in ("info", "warning", "critical"):
                cur["min_severity"] = tw_in["min_severity"]
            alerts["twilio"] = cur

        if a_in.get("severity_threshold") in ("info", "warning", "critical"):
            alerts["severity_threshold"] = a_in["severity_threshold"]

        if "quiet_hours" in a_in and isinstance(a_in["quiet_hours"], dict):
            qh = alerts.get("quiet_hours") or {}
            qh_in = a_in["quiet_hours"]
            if "enabled" in qh_in:
                qh["enabled"] = bool(qh_in["enabled"])
            if "exempt_critical" in qh_in:
                qh["exempt_critical"] = bool(qh_in["exempt_critical"])
            for k in ("start_hour", "end_hour"):
                if k in qh_in:
                    try:
                        qh[k] = max(0, min(23, int(qh_in[k])))
                    except (TypeError, ValueError):
                        pass
            alerts["quiet_hours"] = qh

        if "subscriptions" in a_in and isinstance(a_in["subscriptions"], dict):
            subs = alerts.get("subscriptions") or {}
            for cat_id, channels in a_in["subscriptions"].items():
                if cat_id not in CATEGORY_IDS or not isinstance(channels, dict):
                    continue
                row = subs.get(cat_id) or {}
                for ch in CHANNELS:
                    if ch in channels:
                        row[ch] = bool(channels[ch])
                subs[cat_id] = row
            alerts["subscriptions"] = subs

    notif["alerts"] = alerts

    if not _save_notif_config(notif):
        return JsonResponse({"ok": False, "error": "Sauvegarde impossible"}, status=500)

    # Echo back the sanitized config so the UI refreshes consistently.
    saved = _load_notif_config()
    saved["alerts"] = _alerts_block(saved)
    return JsonResponse({"ok": True, "config": _public_notif(saved),
                         "categories": CATEGORIES, "channels": CHANNELS})


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def alerts_test_channel(request, channel: str):
    """Fire a test notification on a single channel — proves the credentials/
    webhook actually work end-to-end without waiting for a real event."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = "Asguard — Test de canal"
    body  = (f"Si vous lisez ce message, le canal « {channel} » est correctement "
             f"configuré.\nHeure : {ts}")

    if channel == "email":
        html = _build_html(
            title="Test du canal e-mail",
            color="#2563eb", badge_label="TEST", badge_color="#2563eb",
            rows=[("Statut", "Configuration valide", "#16a34a"),
                  ("Canal",  "Email SMTP", None),
                  ("Heure",  ts, None)],
            footer_note="Cette notification confirme que Asguard peut joindre votre boîte mail.",
        )
        try:
            send_notification(title, html, body)
            return JsonResponse({"ok": True, "channel": "email",
                                 "message": "Email de test envoyé"})
        except Exception as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    if channel == "ntfy":
        try:
            _send_ntfy(title=title, body=body, priority="default",
                       tags="white_check_mark,shield")
            return JsonResponse({"ok": True, "channel": "ntfy"})
        except Exception as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    if channel == "slack":
        try:
            _send_slack(title, body, severity="info")
            return JsonResponse({"ok": True, "channel": "slack"})
        except Exception as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    if channel == "twilio":
        try:
            # SMS test is intentionally tagged as 'critical' so the per-channel
            # min_severity floor never blocks it on a real test.
            _send_twilio_sms(title, body, severity="critical")
            return JsonResponse({"ok": True, "channel": "twilio",
                                 "message": "SMS de test envoyé à tous les destinataires Twilio"})
        except Exception as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    return JsonResponse({"ok": False, "error": f"Canal inconnu : {channel}"}, status=400)
