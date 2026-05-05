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


def notify_missed_backup_catchup(task_name, backup_type, missed_at=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    type_labels = {
        "safe_backup": "Sauvegarde Safe",
        "full_backup": "Sauvegarde Full DR",
        "db_backup":   "Sauvegarde Base de données",
    }
    label = type_labels.get(backup_type, backup_type)

    _send_ntfy(
        title=f"⚠️ Sauvegarde manquée — Récupération déclenchée",
        body=f"Tâche : {task_name}\nType : {label}\nHeure prévue manquée : {missed_at or '—'}\nRécupération lancée à : {ts}",
        priority="high",
        tags="warning,arrows_counterclockwise,shield",
    )
    html = _build_html(
        title="⚠️ Sauvegarde manquée — Récupération en cours",
        color="#d97706",
        badge_label="MANQUÉE — RÉCUPÉRATION",
        badge_color="#d97706",
        rows=[
            ("Tâche",            task_name,       None),
            ("Type",             label,           None),
            ("Heure manquée",    missed_at or "—", "#d97706"),
            ("Récupération à",   ts,              None),
            ("Cause probable",   "VM arrêtée ou non démarrée à l'heure planifiée", None),
        ],
    )
    send_notification(
        f"⚠️ Sauvegarde manquée : {task_name}",
        html,
        f"Sauvegarde manquée détectée\nTâche: {task_name}\nType: {label}\nHeure manquée: {missed_at}\nRécupération lancée à: {ts}",
    )


# ── Restore events ────────────────────────────────────────────────────────────

def notify_restore_started(backup_id: str, mode: str = "safe"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_label = "Full DR" if mode == "complete" else "Safe"
    _send_ntfy(
        title=f"Restauration démarrée — {mode_label}",
        body=f"Backup : {backup_id}\nMode : {mode_label}\nHeure : {ts}\nL'interface sera indisponible ~2-3 min.",
        priority="high",
        tags="arrows_counterclockwise,rotating_light,shield",
    )
    html = _build_html(
        title=f"🔄 Restauration {mode_label} démarrée",
        color="#d97706",
        badge_label="RESTAURATION EN COURS",
        badge_color="#d97706",
        rows=[
            ("Backup",   backup_id,   None),
            ("Mode",     mode_label,  None),
            ("Heure",    ts,          None),
            ("Statut",   "En cours — interface temporairement indisponible", "#d97706"),
        ],
    )
    send_notification(
        f"Restauration {mode_label} démarrée",
        html,
        f"Restauration démarrée\nBackup: {backup_id}\nMode: {mode_label}\nHeure: {ts}",
    )


def notify_restore_completed(backup_id: str, mode: str, success: bool,
                              duration_s=None, components_ok=0, components_failed=0):
    ts      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_label = "Full DR" if mode == "complete" else "Safe"
    ok      = success
    color   = "#16a34a" if ok else "#dc2626"
    badge   = "RESTAURATION RÉUSSIE" if ok else "RESTAURATION ÉCHOUÉE"
    status  = "✓ Système restauré et opérationnel" if ok else "✗ Erreur durant la restauration"
    dur_str = f"{int(duration_s)}s" if duration_s else "—"

    _send_ntfy(
        title=f"Restauration {'réussie' if ok else 'ÉCHOUÉE'} — {mode_label}",
        body=(
            f"Backup : {backup_id}\nMode : {mode_label}\n"
            f"Composants OK : {components_ok} | Échecs : {components_failed}\n"
            f"Durée : {dur_str}\nHeure : {ts}"
        ),
        priority="default" if ok else "urgent",
        tags="white_check_mark,shield" if ok else "x,shield,rotating_light",
    )
    html = _build_html(
        title=f"{'✓' if ok else '✗'} Restauration {mode_label} {'réussie' if ok else 'échouée'}",
        color=color, badge_label=badge, badge_color=color,
        rows=[
            ("Backup",           backup_id,             None),
            ("Mode",             mode_label,            None),
            ("Statut",           status,                color),
            ("Composants OK",    str(components_ok),    "#16a34a"),
            ("Composants KO",    str(components_failed), "#dc2626" if components_failed else None),
            ("Durée",            dur_str,               None),
            ("Heure",            ts,                    None),
        ],
    )
    send_notification(
        f"Restauration {mode_label} {'réussie ✓' if ok else 'échouée ✗'}",
        html,
        f"Restauration {'réussie' if ok else 'échouée'}\nBackup: {backup_id}\nStatut: {status}\nHeure: {ts}",
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


# ── Service events ─────────────────────────────────────────────────────────────

def notify_service_action(service_name: str, action: str, success: bool, display_name: str = ""):
    """Called when a service is started, stopped, restarted, enabled or disabled."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    label = display_name or service_name
    action_labels = {
        "start": "démarré", "stop": "arrêté", "restart": "redémarré",
        "enable": "activé", "disable": "désactivé",
    }
    action_fr = action_labels.get(action.lower(), action)
    ok = success
    color = "#16a34a" if ok else "#dc2626"
    badge = f"SERVICE {action_fr.upper()}" if ok else f"ÉCHEC {action_fr.upper()}"
    icon_map = {
        "start": "▶", "stop": "⏹", "restart": "↺", "enable": "✓", "disable": "✗",
    }
    icon = icon_map.get(action.lower(), "⚙")
    priority = "default" if ok else "high"
    tags = "gear,white_check_mark" if ok else "gear,x"

    _send_ntfy(
        title=f"Service {label} — {action_fr}",
        body=f"Service : {label}\nAction : {action_fr}\nStatut : {'Succès' if ok else 'Échec'}\nHeure : {ts}",
        priority=priority,
        tags=tags,
    )
    html = _build_html(
        title=f"{icon} Service {label} {action_fr}",
        color=color, badge_label=badge, badge_color=color,
        rows=[
            ("Service", label,                           None),
            ("Action",  action_fr,                       color),
            ("Statut",  "✓ Succès" if ok else "✗ Échec", color),
            ("Heure",   ts,                              None),
        ],
    )
    send_notification(
        f"Service {label} {action_fr}",
        html,
        f"Service {label} {action_fr} — {'Succès' if ok else 'Échec'} — {ts}",
    )


# ── Auth events ────────────────────────────────────────────────────────────────

def notify_user_login(username: str, ip: str = "", success: bool = True, action: str = "login"):
    """Called on user login or logout."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    action_map = {"login": "connecté", "logout": "déconnecté", "failed": "tentative échouée"}
    action_fr = action_map.get(action, action)
    ok = success
    color = "#16a34a" if ok else "#dc2626"
    badge = f"AUTH — {action_fr.upper()}"
    priority = "default" if ok else "high"
    tags = "key,white_check_mark" if ok else "key,warning"

    _send_ntfy(
        title=f"Asguard — Utilisateur {action_fr}",
        body=f"Utilisateur : {username}\nAction : {action_fr}\nIP : {ip or '—'}\nHeure : {ts}",
        priority=priority,
        tags=tags,
    )
    html = _build_html(
        title=f"🔑 Utilisateur {action_fr}",
        color=color, badge_label=badge, badge_color=color,
        rows=[
            ("Utilisateur", username,              None),
            ("Action",      action_fr,             color),
            ("IP source",   ip or "—",             None),
            ("Heure",       ts,                    None),
        ],
    )
    send_notification(
        f"Auth — {username} {action_fr}",
        html,
        f"Utilisateur {username} {action_fr} depuis {ip or '?'} à {ts}",
    )


# ── User management events ─────────────────────────────────────────────────────

def notify_user_change(action: str, username: str, changed_by: str = ""):
    """Called when a user account is created, deleted or modified."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    action_map = {"créé": "#16a34a", "supprimé": "#dc2626", "modifié": "#f59e0b"}
    color = action_map.get(action, "#2563eb")
    tags_map = {"créé": "bust_in_silhouette,white_check_mark", "supprimé": "bust_in_silhouette,wastebasket", "modifié": "bust_in_silhouette,pencil"}
    tags = tags_map.get(action, "bust_in_silhouette")

    _send_ntfy(
        title=f"Gestion utilisateurs — Compte {action}",
        body=f"Utilisateur : {username}\nAction : {action}\nPar : {changed_by or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"👤 Compte utilisateur {action}",
        color=color, badge_label=f"UTILISATEUR {action.upper()}", badge_color=color,
        rows=[
            ("Utilisateur", username,          None),
            ("Action",      action,            color),
            ("Par",         changed_by or "—", None),
            ("Heure",       ts,                None),
        ],
    )
    send_notification(
        f"Utilisateur {action} : {username}",
        html,
        f"Compte utilisateur {action} : {username} — par {changed_by or '?'} à {ts}",
    )


# ── Certificate events ─────────────────────────────────────────────────────────

def notify_certificate_change(action: str, cert_name: str, cert_type: str = ""):
    """Called when a certificate or CA is created, deleted or revoked."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créé": "#16a34a", "supprimé": "#dc2626", "révoqué": "#f59e0b", "non-révoqué": "#2563eb"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créé": "lock,white_check_mark", "supprimé": "lock,wastebasket", "révoqué": "lock,warning", "non-révoqué": "lock"}
    tags = tags_map.get(action, "lock")

    _send_ntfy(
        title=f"Certificat {action} — {cert_name}",
        body=f"Certificat : {cert_name}\nType : {cert_type or '—'}\nAction : {action}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"🔐 Certificat {action}",
        color=color, badge_label=f"CERTIFICAT {action.upper()}", badge_color=color,
        rows=[
            ("Certificat", cert_name,      None),
            ("Type",       cert_type or "—", None),
            ("Action",     action,         color),
            ("Heure",      ts,             None),
        ],
    )
    send_notification(
        f"Certificat {action} : {cert_name}",
        html,
        f"Certificat {action} : {cert_name} ({cert_type or '?'}) à {ts}",
    )


# ── IPSec events ───────────────────────────────────────────────────────────────

def notify_ipsec_change(action: str, tunnel_name: str = "", details: str = ""):
    """Called when an IPSec tunnel is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créé": "#16a34a", "supprimé": "#dc2626", "modifié": "#f59e0b"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créé": "shield,white_check_mark", "supprimé": "shield,wastebasket", "modifié": "shield,pencil"}
    tags = tags_map.get(action, "shield")

    _send_ntfy(
        title=f"IPSec — Tunnel {action}",
        body=f"Tunnel : {tunnel_name or '—'}\nAction : {action}\n{('Détail : ' + details) if details else ''}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    rows = [
        ("Tunnel", tunnel_name or "—", None),
        ("Action", action,             color),
        ("Heure",  ts,                 None),
    ]
    if details:
        rows.insert(2, ("Détail", details, None))
    html = _build_html(
        title=f"🛡 IPSec — Tunnel {action}",
        color=color, badge_label=f"IPSEC {action.upper()}", badge_color=color, rows=rows,
    )
    send_notification(
        f"IPSec — Tunnel {action} : {tunnel_name}",
        html,
        f"IPSec tunnel {action} : {tunnel_name} à {ts}",
    )


# ── NAT events ─────────────────────────────────────────────────────────────────

def notify_nat_change(action: str, rule_type: str = "", rule_desc: str = ""):
    """Called when a NAT rule (DNAT/SNAT/1-to-1) is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")
    tags_map = {"créée": "arrows_counterclockwise,white_check_mark", "supprimée": "arrows_counterclockwise,wastebasket", "modifiée": "arrows_counterclockwise,pencil"}
    tags = tags_map.get(action, "arrows_counterclockwise")

    _send_ntfy(
        title=f"NAT — Règle {action}",
        body=f"Type : {rule_type or '—'}\nRègle : {rule_desc or '—'}\nHeure : {ts}",
        priority="default",
        tags=tags,
    )
    html = _build_html(
        title=f"↔ Règle NAT {action}",
        color=color, badge_label=f"NAT {action.upper()}", badge_color=color,
        rows=[
            ("Type",   rule_type or "—",  None),
            ("Règle",  rule_desc or "—",  None),
            ("Action", action,            color),
            ("Heure",  ts,                None),
        ],
    )
    send_notification(
        f"NAT — Règle {action} ({rule_type})",
        html,
        f"Règle NAT {action} ({rule_type}) : {rule_desc or '?'} à {ts}",
    )


# ── Routing events ─────────────────────────────────────────────────────────────

def notify_routing_change(action: str, dest: str = "", gateway: str = ""):
    """Called when a static route is created, deleted or updated."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"créée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")

    _send_ntfy(
        title=f"Routage — Route {action}",
        body=f"Destination : {dest or '—'}\nPasserelle : {gateway or '—'}\nHeure : {ts}",
        priority="default",
        tags="arrows_counterclockwise,shield",
    )
    html = _build_html(
        title=f"🗺 Route statique {action}",
        color=color, badge_label=f"ROUTAGE {action.upper()}", badge_color=color,
        rows=[
            ("Destination", dest or "—",    None),
            ("Passerelle",  gateway or "—", None),
            ("Action",      action,         color),
            ("Heure",       ts,             None),
        ],
    )
    send_notification(
        f"Routage — Route {action}",
        html,
        f"Route statique {action} : {dest or '?'} via {gateway or '?'} à {ts}",
    )


# ── Network/Interface events ───────────────────────────────────────────────────

def notify_network_change(action: str, interface: str = "", details: str = ""):
    """Called when a network interface is configured or deleted."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    color_map = {"configurée": "#16a34a", "supprimée": "#dc2626", "modifiée": "#f59e0b"}
    color = color_map.get(action, "#2563eb")

    _send_ntfy(
        title=f"Réseau — Interface {action}",
        body=f"Interface : {interface or '—'}\n{('Détail : ' + details) if details else ''}\nHeure : {ts}",
        priority="default",
        tags="satellite,shield",
    )
    rows = [
        ("Interface", interface or "—", None),
        ("Action",    action,           color),
        ("Heure",     ts,               None),
    ]
    if details:
        rows.insert(2, ("Détail", details, None))
    html = _build_html(
        title=f"🌐 Interface réseau {action}",
        color=color, badge_label=f"RÉSEAU {action.upper()}", badge_color=color, rows=rows,
    )
    send_notification(
        f"Réseau — Interface {action} : {interface}",
        html,
        f"Interface réseau {action} : {interface} à {ts}",
    )
