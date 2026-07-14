#!/bin/bash
# =============================================================================
# Asguard — Notification de cycle de vie VM + DÉTECTION DE CRASH / GEL
# =============================================================================
# Appelé par deux unités systemd :
#   asguard-vm-stop-notify.service   ->  "stopped"  (Before=shutdown.target)
#   asguard-vm-start-notify.service  ->  "started"  (au démarrage)
#
# Détection de crash / gel
# ------------------------
# Un arrêt PROPRE passe toujours par le chemin "stopped", qui dépose un
# marqueur /var/lib/asguard/clean_shutdown juste avant l'extinction.
# Au démarrage suivant, le chemin "started" cherche ce marqueur :
#
#   - marqueur présent  -> arrêt précédent propre   -> "VM démarrée" (normal)
#   - marqueur absent   -> arrêt précédent ANORMAL  -> ALERTE URGENTE
#                          (crash, gel/freeze, reset forcé, coupure secteur)
#                          avec l'heure de dernière activité et la durée
#                          d'indisponibilité estimée.
#
# Une VM gelée ne PEUT PAS notifier pendant qu'elle est gelée — c'est physique.
# Ce script le signale dès qu'elle redémarre : c'est le plus tôt où la VM
# elle-même peut savoir qu'elle a eu un incident. Pour une détection PENDANT
# la panne, voir le watchdog hôte « asguard-vmware-watchdog.ps1 ».
# =============================================================================

EVENT="${1:-started}"                      # "started" | "stopped"
CONFIG="/etc/asguard/watchdog_config.json"
STATE_DIR="/var/lib/asguard"
CLEAN_MARKER="$STATE_DIR/clean_shutdown"    # déposé par un arrêt propre
INIT_MARKER="$STATE_DIR/.vm_notify_initialized"

mkdir -p "$STATE_DIR"

[ -f "$CONFIG" ] || exit 0

# Topic ntfy lu depuis la config watchdog.
TOPIC=$(python3 -c "
import json
try:
    d = json.load(open('$CONFIG'))
    t = d.get('notifications', {}).get('ntfy', {})
    if t.get('enabled') and t.get('topic'):
        print(t['topic'])
except Exception:
    pass
" 2>/dev/null)

[ -z "$TOPIC" ] && exit 0

HOSTNAME=$(hostname)
TS=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

# send <title> <priority> <tags> <body>
send() {
    curl -s -X POST "https://ntfy.sh/${TOPIC}" \
        -H "Title: $1" \
        -H "Priority: $2" \
        -H "Tags: $3" \
        --data-binary "$4" \
        --max-time 15 > /dev/null 2>&1 || true
}

# ── Arrêt : on enregistre qu'il est PROPRE ───────────────────────────────────
if [ "$EVENT" = "stopped" ]; then
    echo "$TS" > "$CLEAN_MARKER"
    send "Asguard — VM arrêtée" "default" "stop_sign,computer" \
"La VM '$HOSTNAME' s'arrête proprement.
Heure : $TS"
    exit 0
fi

# ── Démarrage ────────────────────────────────────────────────────────────────

# Tout premier démarrage après installation du script : aucun historique.
if [ ! -f "$INIT_MARKER" ]; then
    touch "$INIT_MARKER"
    send "Asguard — VM démarrée" "default" "white_check_mark,computer" \
"La VM '$HOSTNAME' vient de démarrer (première initialisation du détecteur).
Heure : $TS"
    exit 0
fi

# Arrêt précédent propre : le marqueur existe.
if [ -f "$CLEAN_MARKER" ]; then
    LAST_STOP=$(cat "$CLEAN_MARKER" 2>/dev/null)
    rm -f "$CLEAN_MARKER"
    send "Asguard — VM démarrée" "default" "white_check_mark,computer" \
"La VM '$HOSTNAME' vient de démarrer.
Arrêt précédent : propre ($LAST_STOP)
Heure : $TS"
    exit 0
fi

# Pas de marqueur d'arrêt propre -> ARRÊT ANORMAL.
# On estime l'heure du gel via le dernier log du boot précédent.
FROZE_EPOCH=$(journalctl -b -1 -n1 -o short-unix 2>/dev/null | awk '{print int($1)}')
NOW_EPOCH=$(date +%s)
if [ -n "$FROZE_EPOCH" ] && [ "$FROZE_EPOCH" -gt 0 ] 2>/dev/null; then
    FROZE_AT=$(date -u -d "@$FROZE_EPOCH" '+%Y-%m-%d %H:%M:%S UTC' 2>/dev/null)
    DOWN_MIN=$(( (NOW_EPOCH - FROZE_EPOCH) / 60 ))
    DOWN_LINE="Dernière activité détectée : $FROZE_AT
Indisponibilité estimée : ${DOWN_MIN} min"
else
    DOWN_LINE="Durée d'indisponibilité : inconnue (pas de journal du boot précédent)"
fi

send "Asguard — REDÉMARRAGE ANORMAL" "urgent" "rotating_light,warning,computer" \
"⚠️ La VM '$HOSTNAME' a redémarré après un ARRÊT ANORMAL.

Aucun arrêt propre n'a été enregistré : crash, gel (freeze), reset forcé ou
coupure d'alimentation.

$DOWN_LINE
Redémarrage : $TS

À vérifier : ressources de l'hôte VMware, snapshots en cours, état du datastore."
exit 0
