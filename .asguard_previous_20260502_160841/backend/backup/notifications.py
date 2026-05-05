"""
Asguard — Notification helper
Email (critiques) + Telegram (temps réel) pour tous les événements firewall/backup.
Config dans /etc/asguard/watchdog_config.json → clé "notifications".
"""

import json
import logging
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

logger = logging.getLogger(__name__)

_WD_CONFIG = Path("/etc/asguard/watchdog_config.json")
_ENV_FILE  = Path("/asguard/asguard/.env")


# ── Config helpers ─────────────────────────────────────────────────────────────

def _load_notif_config():
    try:
        cfg = json.loads(_WD_CONFIG.read_text())
        return cfg.get("notifications", {})
    except Exception:
        return {}


def _env_vars():
    env = {}
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


# ── Email ──────────────────────────────────────────────────────────────────────

def _build_html(title, color, badge_label, badge_color, rows, footer_note=""):
    rows_html = ""
    for label, value, val_color in rows:
        vc = f"color:{val_color};font-weight:600;" if val_color else "color:#374151;"
        rows_html += f"""
        <tr>
          <td style="padding:8px 16px;color:#6b7280;font-size:13px;border-bottom:1px solid #f3f4f6;white-space:nowrap;">{label}</td>
          <td style="padding:8px 16px;font-size:13px;{vc}border-bottom:1px solid #f3f4f6;">{value}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 0;">
    <tr><td align="center">
      <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <tr>
          <td style="background:{color};padding:26px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
              <td>
                <div style="color:rgba(255,255,255,0.8);font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Asguard</div>
                <div style="color:#fff;font-size:22px;font-weight:700;">{title}</div>
              </td>
              <td align="right" style="font-size:36px;line-height:1;">🛡</td>
            </tr></table>
          </td>
        </tr>

        <tr>
          <td style="padding:20px 32px 8px;">
            <span style="background:{badge_color}18;color:{badge_color};border:1px solid {badge_color}33;
                         font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
                         padding:4px 12px;border-radius:20px;">{badge_label}</span>
          </td>
        </tr>

        <tr>
          <td style="padding:12px 32px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border:1px solid #f3f4f6;border-radius:8px;overflow:hidden;">
              {rows_html}
            </table>
          </td>
        </tr>

        <tr>
          <td style="background:#f9fafb;padding:14px 32px;border-top:1px solid #f3f4f6;">
            <p style="margin:0;font-size:11px;color:#9ca3af;">
              {footer_note or "Généré automatiquement par Asguard. Ne pas répondre."}
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


def _get_admin_emails():
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return list(
            User.objects.filter(is_active=True, is_staff=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )
    except Exception:
        return []


def send_notification(subject, html, plain, extra_recipients=None):
    """Send email — reserved for critical events only."""
    notif = _load_notif_config()
    if not notif.get("email_enabled"):
        return

    recipients = list(notif.get("recipients", []))
    for email in _get_admin_emails():
        if email not in recipients:
            recipients.append(email)
    if extra_recipients:
        for email in extra_recipients:
            if email and email not in recipients:
                recipients.append(email)
    if not recipients:
        return

    env = _env_vars()
    smtp_host    = notif.get("smtp_host")     or env.get("EMAIL_HOST", "smtp.office365.com")
    smtp_port    = int(notif.get("smtp_port") or env.get("EMAIL_PORT", 587))
    smtp_user    = notif.get("smtp_user")     or env.get("EMAIL_HOST_USER", "")
    smtp_pass    = notif.get("smtp_password") or env.get("EMAIL_HOST_PASSWORD", "")
    sender_name  = notif.get("sender_name",  "Asguard Watchdog")
    sender_email = notif.get("sender_email", smtp_user)

    if not smtp_user or not smtp_pass:
        logger.warning("Notifications email: identifiants SMTP manquants")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Asguard] {subject}"
        msg["From"]    = f"{sender_name} <{sender_email}>"
        msg["To"]      = ", ".join(recipients)
        msg.set_content(plain)
        msg.add_alternative(html, subtype="html")
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.ehlo()
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        logger.info(f"Email envoyé : {subject} → {recipients}")
    except Exception as exc:
        logger.error(f"Échec email : {exc}")


# ── ntfy.sh ────────────────────────────────────────────────────────────────────

def _send_ntfy(title: str, body: str, priority: str = "default", tags: str = "shield"):
    """Send a push notification via ntfy.sh (free, no account needed)."""
    import requests as _req
    notif = _load_notif_config()
    nt = notif.get("ntfy", {})
    if not nt.get("enabled"):
        return
    topic = nt.get("topic", "").strip()
    if not topic:
        logger.warning("ntfy: topic manquant dans watchdog_config.json")
        return
    try:
        safe_title = title.encode("ascii", "replace").decode("ascii")
        _req.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title":    safe_title,
                "Priority": priority,
                "Tags":     tags,
            },
            timeout=10,
        )
        logger.info(f"ntfy notification envoyée : {title}")
    except Exception as exc:
        logger.error(f"ntfy notification échouée : {exc}")


def ntfy_test():
    """Send a test notification to verify ntfy setup."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    _send_ntfy(
        title="Asguard — Test de connexion",
        body=f"ntfy est correctement configuré.\nHeure : {ts}",
        priority="default",
        tags="white_check_mark,shield",
    )


# ── Backup events ──────────────────────────────────────────────────────────────

def notify_backup_started(backup_type, backup_id=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"Sauvegarde démarrée — {label}",
        body=f"Type : {label}\nID : {backup_id or '—'}\nHeure : {ts}",
        priority="default",
        tags="arrows_counterclockwise,shield",
    )
    html = _build_html(
        title=f"🔄 {label} démarrée",
        color="#2563eb",
        badge_label="SAUVEGARDE EN COURS",
        badge_color="#2563eb",
        rows=[
            ("Type",   label,            None),
            ("ID",     backup_id or "—", None),
            ("Heure",  ts,               None),
            ("Statut", "En cours...",    "#2563eb"),
        ],
    )
    send_notification(f"{label} démarrée", html, f"Sauvegarde démarrée\nType: {label}\nHeure: {ts}")


def notify_backup_completed(backup_type, backup_id, success, duration_s=None, message=""):
    ts      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label   = type_labels.get(backup_type, backup_type)
    ok      = success
    color   = "#16a34a" if ok else "#dc2626"
    badge   = "SUCCÈS" if ok else "ÉCHEC"
    status  = "✓ Terminée avec succès" if ok else "✗ Échec de la sauvegarde"
    dur_str = f"{int(duration_s)}s" if duration_s else "—"

    body = f"Type : {label}\nID : {backup_id or '—'}\nDurée : {dur_str}\nHeure : {ts}"
    if not ok and message:
        body += f"\nErreur : {message[:200]}"
    _send_ntfy(
        title=f"Sauvegarde {'réussie' if ok else 'ÉCHOUÉE'} — {label}",
        body=body,
        priority="default" if ok else "high",
        tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
    )

    rows = [
        ("Type",   label,            None),
        ("ID",     backup_id or "—", None),
        ("Statut", status,           "#16a34a" if ok else "#dc2626"),
        ("Durée",  dur_str,          None),
        ("Heure",  ts,               None),
    ]
    if message:
        rows.append(("Détail", message, None))
    html = _build_html(
        title=f"{'✓' if ok else '✗'} {label} {'réussie' if ok else 'échouée'}",
        color=color, badge_label=badge, badge_color=color, rows=rows,
    )
    send_notification(
        f"{label} {'réussie ✓' if ok else 'échouée ✗'}",
        html,
        f"Sauvegarde {'réussie' if ok else 'échouée'}\nType: {label}\nStatut: {status}\nHeure: {ts}",
    )


def notify_backup_scheduled(task_name, backup_type, cron_expr=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"Backup automatique déclenché — {label}",
        body=f"Tâche : {task_name}\nType : {label}\nCron : {cron_expr or '—'}\nHeure : {ts}",
        priority="low",
        tags="alarm_clock,shield",
    )
    html = _build_html(
        title="⏰ Sauvegarde automatique déclenchée",
        color="#7c3aed",
        badge_label="PLANIFIÉE",
        badge_color="#7c3aed",
        rows=[
            ("Tâche",         task_name,        None),
            ("Type",          label,            None),
            ("Planification", cron_expr or "—", None),
            ("Déclenchée à",  ts,               None),
        ],
    )
    send_notification(
        f"Sauvegarde automatique : {task_name}",
        html,
        f"Sauvegarde automatique déclenchée\nTâche: {task_name}\nType: {label}\nHeure: {ts}",
    )


# ── Firewall events ────────────────────────────────────────────────────────────

def notify_firewall_rule_change(action, rule_desc="", interface="", policy="", rule_type=""):
    """Called when a firewall rule is added, updated, or deleted."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map    = {"ajoutée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    tags_map     = {"ajoutée": "white_check_mark,lock", "supprimée": "wastebasket,lock", "modifiée": "pencil,lock"}
    color = color_map.get(action.lower(), "#2563eb")

    _send_ntfy(
        title=f"Firewall — Règle {action}",
        body=f"{rule_desc or '—'}\nInterface : {interface or '—'}\nPolitique : {policy or '—'} | {rule_type or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags_map.get(action.lower(), "lock,shield"),
    )
    html = _build_html(
        title=f"🔒 Règle firewall {action}",
        color=color,
        badge_label=f"RÈGLE {action.upper()}",
        badge_color=color,
        rows=[
            ("Action",      action,           color),
            ("Description", rule_desc or "—", None),
            ("Interface",   interface or "—", None),
            ("Politique",   policy or "—",    None),
            ("Direction",   rule_type or "—", None),
            ("Heure",       ts,               None),
        ],
    )
    send_notification(
        f"Firewall – Règle {action}",
        html,
        f"Règle firewall {action} : {rule_desc} sur {interface} à {ts}",
    )


# ── WAF events ─────────────────────────────────────────────────────────────────

def notify_waf_alert(new_count, samples=None):
    """Called when WAF synchronization finds new violations."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [f"{new_count} violation(s) ModSecurity détectée(s)"]
    if samples:
        for i, s in enumerate(samples[:3], 1):
            src = s.get("source") or "?"
            msg = (s.get("message") or "—")[:80]
            lines.append(f"{i}. {src} — {msg}")
    lines.append(f"Heure : {ts}")
    _send_ntfy(
        title=f"Alerte WAF — {new_count} violation(s)",
        body="\n".join(lines),
        priority="high",
        tags="warning,shield",
    )

    rows = [
        ("Nouvelles violations", str(new_count), "#dc2626"),
        ("Heure de détection",   ts,             None),
    ]
    if samples:
        for i, s in enumerate(samples[:3], 1):
            src = s.get("source") or "—"
            msg = (s.get("message") or "—")[:80]
            rows.append((f"Alerte #{i}", f"{src} — {msg}", "#dc2626"))
    html = _build_html(
        title="⚠ Alerte WAF – Violations détectées",
        color="#dc2626", badge_label="ALERTE WAF", badge_color="#dc2626", rows=rows,
    )
    send_notification(
        f"WAF : {new_count} violation(s) détectée(s)",
        html,
        f"WAF : {new_count} nouvelles violation(s) détectée(s) à {ts}",
    )


# ── IDS/IPS events ─────────────────────────────────────────────────────────────

def notify_ids_alert(new_count, sample_log=""):
    """Called when IDS/IPS (Suricata) detects new alert lines."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    body = f"{new_count} alerte(s) Suricata détectée(s)\nMoteur : Suricata IDS/IPS\nHeure : {ts}"
    if sample_log:
        body += f"\n---\n{sample_log[:200]}"
    _send_ntfy(
        title=f"Alerte IDS/IPS — {new_count} alerte(s) Suricata",
        body=body,
        priority="urgent",
        tags="rotating_light,shield",
    )

    rows = [
        ("Nouvelles alertes", str(new_count),     "#f59e0b"),
        ("Moteur",            "Suricata IDS/IPS", None),
        ("Heure",             ts,                 None),
    ]
    if sample_log:
        rows.append(("Extrait", sample_log[:120], "#f59e0b"))
    html = _build_html(
        title="🔍 Alerte IDS/IPS – Suricata",
        color="#f59e0b", badge_label="ALERTE IDS/IPS", badge_color="#f59e0b", rows=rows,
    )
    send_notification(
        f"IDS/IPS Suricata : {new_count} alerte(s)",
        html,
        f"Suricata : {new_count} alerte(s) IDS/IPS détectée(s) à {ts}",
    )
