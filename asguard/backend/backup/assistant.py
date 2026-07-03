"""
Asguard Assistant — offline, rule-based advisory engine (NO LLM, zero cost).

Answers three kinds of operator questions without any external service, so it
keeps working even when the appliance has lost internet:

  1. "Which backup fits my need?"  → recommend_backup()  (matches the need to
     the components each backup carries + the right backup type / restore mode)
  2. "What does this backup contain / what's missing?" → review_backup()
  3. "How do I block X / add a user / make a VLAN?"    → knowledge base

`answer(message)` is the single entry point: it detects intent from keywords
(FR + EN) and dispatches. Everything is read-only.
"""
import json
import re
from pathlib import Path

_BACKUP_ROOT = Path("/var/backups/asguard")

# Full set of components a backup may carry, with a human label + which operator
# "need" each one serves. Used for both recommendation and review.
_COMPONENTS = {
    "firewall":        ("Règles firewall (nftables)",      ["firewall", "pare-feu", "règle", "regle", "rule", "bloquer", "port", "nftables"]),
    "nat":             ("NAT (DNAT/SNAT/1-to-1)",          ["nat", "redirection", "port forwarding", "dnat", "snat"]),
    "gateway":         ("Passerelles",                     ["gateway", "passerelle"]),
    "routing":         ("Routes statiques",                ["route", "routing", "routage"]),
    "network":         ("Interfaces & IP",                 ["interface", "réseau", "reseau", "ip", "network", "carte"]),
    "vlan":            ("VLAN",                            ["vlan"]),
    "vxlan":           ("VXLAN",                           ["vxlan"]),
    "vpn":             ("OpenVPN",                         ["vpn", "openvpn"]),
    "ipsec_detailed":  ("IPsec",                           ["ipsec"]),
    "ids":             ("IDS/IPS (Suricata)",              ["ids", "ips", "suricata", "intrusion"]),
    "waf":             ("WAF (ModSecurity)",               ["waf", "modsecurity", "web application"]),
    "proxy":           ("Proxy (Squid)",                   ["proxy", "squid"]),
    "ztna":            ("ZTNA (Zero-Trust)",               ["ztna", "zero-trust", "zero trust"]),
    "certificates":    ("Certificats / PKI",               ["certificat", "pki", "ca", "tls", "ssl"]),
    "dhcp":            ("Serveur DHCP",                    ["dhcp", "bail", "lease"]),
    "sdwan":           ("SD-WAN",                          ["sdwan", "sd-wan"]),
    "double_mask":     ("Double Mask",                     ["double mask", "double_mask"]),
    "database":        ("Base de données (users, règles…)", ["base", "database", "données", "donnees", "utilisateur", "user", "compte", "login"]),
    "application":     ("Code de l'application",           ["application", "code", "app"]),
    "system_config":   ("Configuration système (/etc)",    ["système", "systeme", "hostname", "fstab"]),
}


# ── knowledge base (how-to) ──────────────────────────────────────────────────
# Each entry: keywords → (titre, réponse, où_dans_l_UI).
_HOWTO = [
    (["bloquer", "block", "interdire", "refuser port", "fermer port"],
     "Bloquer un port ou une IP",
     "Va dans **Rules firewall** (menu 10 / onglet Firewall). Crée une règle sur "
     "l'interface concernée (ex. WAN ens34), type **inbound**, action **drop**, et "
     "précise le port/protocole ou l'IP source. La règle est écrite dans la table "
     "nftables `filter_<interface>` puis persistée en base."),
    (["accepter", "autoriser", "allow", "ouvrir port", "accept"],
     "Autoriser un flux / ouvrir un port",
     "Dans **Rules firewall**, crée une règle **accept** (inbound ou outbound) sur "
     "l'interface voulue, avec le port/protocole. Place les règles accept avant les "
     "drop génériques — l'ordre compte dans nftables."),
    (["ajouter user", "ajouter utilisateur", "add user", "créer compte", "creer compte", "nouvel utilisateur"],
     "Ajouter un utilisateur",
     "Onglet **Gestion des utilisateurs** (managementUsers). Les comptes applicatifs "
     "sont stockés en base → ils sont inclus dans un backup **full** (composant "
     "`database`), pas dans un backup safe."),
    (["vlan"],
     "Créer un VLAN",
     "Menu **6. VLAN** (ou onglet VLAN). Choisis l'interface parente (ex. ens33), un "
     "tag numérique (1–4094) et une priorité. Ça crée un profil NetworkManager "
     "`vlanXXX` — capturé dans le composant réseau du backup."),
    (["nat", "redirection", "port forwarding", "dnat"],
     "Faire une redirection de port (NAT)",
     "Onglet **NAT** → DNAT : IP/port externe → IP/port interne. Le NAT est dans la "
     "table `ip nat` (prerouting/postrouting) et sauvegardé dans le composant `nat`."),
    (["restaurer", "restore", "dr", "clone", "reprise"],
     "Restaurer / cloner la machine",
     "Pour un **clone identique** (même IP, même config) après un sinistre : fais un "
     "backup **FULL**, puis un **restore COMPLETE** sur la nouvelle VM (2 cartes), puis "
     "reboot. L'original doit être éteint (une seule machine par IP). Pour juste "
     "revenir en arrière sur une config, restaure le **composant** concerné."),
]

_BACKUP_TYPES = (
    "Types de sauvegarde",
    "• **Safe** = configuration seule (firewall, VPN, réseau, certificats… ~4,5 Mo), "
    "sans base ni code. Idéal pour figer une config avant un changement.\n"
    "• **Full** = safe + **base de données** (règles, users, historique) + code app. "
    "Nécessaire pour un clone ou pour restaurer des données.\n"
    "• **Custom** = tu choisis les composants (ex. `network` + `database`).\n\n"
    "Pour restaurer : **COMPLETE** = clone exact de toute la VM (même IP) ; par "
    "**composant** = ne remet qu'une partie (ex. juste le réseau)."
)


def _norm(text: str) -> str:
    return (text or "").lower().strip()


def _load_backups():
    """Return [{id, date, type, components:{name:status}}] newest first."""
    out = []
    if not _BACKUP_ROOT.exists():
        return out
    for d in _BACKUP_ROOT.iterdir():
        if not d.is_dir() or not d.name.startswith("backup_"):
            continue
        meta_f = d / "backup_metadata.json"
        if not meta_f.exists():
            continue  # control dirs (backup_jobs, …) aren't real backups
        comps, btype, date = {}, "full" if "custom" not in d.name else "custom", ""
        if True:
            try:
                meta = json.loads(meta_f.read_text())
                comps = {k: (v.get("status", "unknown") if isinstance(v, dict) else "present")
                         for k, v in (meta.get("components") or {}).items()}
                date = meta.get("created_at", "")
                btype = meta.get("backup_type") or meta.get("type") or btype
            except Exception:
                pass
        if "safe" in d.name:
            btype = "safe"
        out.append({"id": d.name, "date": date, "type": btype, "components": comps})
    return sorted(out, key=lambda b: b["date"] or b["id"], reverse=True)


def _need_to_components(text: str):
    """Map the free-text need to the set of components that serve it."""
    t = _norm(text)
    matched = []
    for comp, (label, kws) in _COMPONENTS.items():
        if any(kw in t for kw in kws):
            matched.append(comp)
    return matched


def recommend_backup(text: str) -> dict:
    needs = _need_to_components(text)
    backups = _load_backups()
    t = _norm(text)
    wants_clone = any(w in t for w in ("clone", "identique", "dr", "sinistre", "tout", "complet", "complète", "complete"))

    if not backups:
        return {"reply": "Aucune sauvegarde disponible pour l'instant. Lance d'abord "
                         "un backup (Full pour un clone, Safe pour la config seule).",
                "refs": []}

    # Score each backup by how many of the needed components it carries (present).
    scored = []
    for b in backups:
        ok = sum(1 for c in needs if b["components"].get(c) in ("success", "present", "ok"))
        scored.append((ok, b))
    scored.sort(key=lambda x: (x[0], x[1]["date"]), reverse=True)
    best = scored[0][1]

    need_labels = [_COMPONENTS[c][0] for c in needs] or ["(besoin non précisé)"]
    lines = [f"Ton besoin : {', '.join(need_labels)}."]
    if wants_clone:
        full = next((b for b in backups if b["type"] in ("full", "custom")), best)
        lines.append(f"→ Pour un **clone identique**, prends un backup **FULL** et fais un "
                     f"**restore COMPLETE**. Le plus récent adapté : **{full['id']}**.")
        best = full
    else:
        lines.append(f"→ Backup conseillé : **{best['id']}** (type {best['type']}). "
                     f"Restaure le **composant** correspondant si tu ne veux pas tout remettre.")
    if needs:
        missing = [_COMPONENTS[c][0] for c in needs
                   if best["components"].get(c) not in ("success", "present", "ok")]
        if missing:
            lines.append(f"⚠️ Ce backup ne contient pas : {', '.join(missing)}. "
                         f"Prends-en un qui les inclut ou refais un backup.")
    return {"reply": "\n".join(lines), "refs": [best["id"]]}


def review_backup(backup_id: str = "") -> dict:
    backups = _load_backups()
    if not backups:
        return {"reply": "Aucune sauvegarde à analyser.", "refs": []}
    target = next((b for b in backups if b["id"] == backup_id), None) if backup_id else backups[0]
    if target is None:
        target = backups[0]

    present, missing = [], []
    for comp, (label, _) in _COMPONENTS.items():
        st = target["components"].get(comp)
        if st in ("success", "present", "ok"):
            present.append(label)
        elif comp in ("firewall", "network", "vpn", "database", "certificates"):
            # only flag "missing" for the components a full backup should carry
            if comp not in target["components"]:
                missing.append(label)
    reply = [f"**{target['id']}** (type {target['type']})",
             f"✅ Contient ({len(present)}) : {', '.join(present) if present else '—'}"]
    if missing:
        reply.append(f"⚠️ Absent : {', '.join(missing)}")
    reply.append("Pour un clone complet, ce backup doit être de type **full** et "
                 "restauré en mode **COMPLETE**.")
    return {"reply": "\n".join(reply), "refs": [target["id"]]}


def _howto(text: str):
    t = _norm(text)
    if any(w in t for w in ("type de backup", "types de backup", "safe ou full", "safe vs full")):
        title, body = _BACKUP_TYPES
        return {"reply": f"**{title}**\n{body}", "refs": []}
    for kws, title, body in _HOWTO:
        if any(kw in t for kw in kws):
            return {"reply": f"**{title}**\n{body}", "refs": []}
    return None


_HELP = ("Je suis l'assistant Asguard (hors-ligne). Je peux :\n"
         "• **conseiller un backup** selon ton besoin — ex. « quel backup pour le firewall ? »\n"
         "• **analyser un backup** — ex. « que contient le dernier backup ? »\n"
         "• **expliquer le firewall** — ex. « comment bloquer un port ? », « ajouter un user »\n"
         "• expliquer les **types de backup** et la **restauration / DR**.")


# Short definitions so "c'est quoi X" gets an EXPLANATION (not a backup reco).
_GLOSSARY = {
    ("firewall", "pare-feu", "pare feu", "nftables"):
        "Un **firewall** (pare-feu) filtre le trafic réseau : il autorise ou bloque les connexions selon des règles "
        "(par interface, port, protocole, IP). Sur Asguard il repose sur **nftables**, plus NAT, VPN, IDS/IPS, WAF, proxy…",
    ("nat", "dnat", "snat"):
        "Le **NAT** traduit les adresses IP. **DNAT** = rediriger un port externe vers une machine interne (ouvrir un service) ; "
        "**SNAT** = masquer les IP internes derrière l'IP publique pour sortir sur internet.",
    ("vlan",):
        "Un **VLAN** découpe un réseau physique en réseaux logiques isolés (par tag 1-4094). Utile pour séparer les flux "
        "(ex. bureautique / serveurs / invités) sur une même carte.",
    ("vpn", "openvpn"):
        "Un **VPN** crée un tunnel chiffré. Asguard fait de l'**OpenVPN** (accès nomade/serveur) et de l'**IPsec** (site-à-site).",
    ("ipsec",):
        "**IPsec** = VPN chiffré, surtout pour relier deux sites (tunnel site-à-site) de façon sécurisée.",
    ("ids", "ips", "suricata"):
        "L'**IDS/IPS** (Suricata) surveille le trafic : il **détecte** (IDS) et peut **bloquer** (IPS) les attaques/intrusions.",
    ("waf", "modsecurity"):
        "Le **WAF** (ModSecurity) protège les applications web (injections SQL, XSS…) en filtrant les requêtes HTTP.",
    ("proxy", "squid"):
        "Le **proxy** (Squid) relaie et filtre les accès web des utilisateurs (cache, contrôle, logs).",
    ("ztna", "zero-trust", "zero trust"):
        "Le **ZTNA** (Zero-Trust) n'accorde l'accès qu'après vérification de l'identité et du contexte — « ne jamais faire confiance par défaut ».",
    ("dhcp",):
        "Le **DHCP** attribue automatiquement les adresses IP aux machines du réseau.",
    ("backup", "sauvegarde"):
        "Un **backup** = une copie de ta configuration/données pour pouvoir revenir en arrière ou reconstruire la machine. "
        "3 types : safe (config), full (config+base+code), custom (au choix).",
    ("dr", "disaster", "reprise", "sinistre"):
        "Le **DR** (reprise après sinistre) = pouvoir reconstruire la machine à l'identique après une panne : "
        "backup FULL → restore COMPLETE sur une nouvelle VM (même IP), original éteint.",
}

_DEFINE_TRIGGERS = ("c'est quoi", "cest quoi", "qu'est-ce", "quest-ce", "quest ce", "qu'est ce",
                    "c quoi", "définition", "definition", "explique", "explication",
                    "à quoi sert", "a quoi sert", "que fait", "ça sert", "ca sert", "what is")


def _definition_reply(t: str):
    if not any(trig in t for trig in _DEFINE_TRIGGERS):
        return None
    for terms, txt in _GLOSSARY.items():
        if any(term in t for term in terms):
            return txt
    return None


def _rule_answer(message: str) -> dict:
    """Rule-based fallback. Returns {intent, reply, refs}."""
    t = _norm(message)
    if not t:
        return {"intent": "help", "reply": _HELP, "refs": []}

    # 1) definitional question ("c'est quoi X") → EXPLAIN, never recommend a backup
    d = _definition_reply(t)
    if d:
        return {"intent": "define", "reply": d, "refs": []}

    # 2) review a specific/last backup
    if any(w in t for w in ("contient", "que contient", "review", "analyse", "qu'y a", "manque")):
        m = re.search(r"(backup[\w\-]+)", t)
        r = review_backup(m.group(1) if m else "")
        return {"intent": "review", **r}

    # 3) how-to knowledge base (before recommend, so "comment bloquer un port" explains)
    ho = _howto(message)
    if ho:
        return {"intent": "howto", **ho}

    # 4) recommend — only for explicit backup/restore intent
    if any(w in t for w in ("quel backup", "quelle sauvegarde", "recommand", "conseil",
                            "restaur", "sauvegarde", "backup", "je veux")):
        r = recommend_backup(message)
        return {"intent": "recommend", **r}

    return {"intent": "help", "reply": _HELP, "refs": []}


# ── DR Readiness audit + Restore impact/risk ────────────────────────────────
from datetime import datetime

# Per-component restore risk (curated, accurate). level: ÉLEVÉ / MOYEN / FAIBLE.
_RESTORE_RISKS = {
    "database":      ("ÉLEVÉ", "Remplace TOUTE la base (users, règles, réseau, certificats, historique). Tu perds ce qui a été créé depuis le backup ; brève coupure. Atomique (rollback si échec)."),
    "application":   ("MOYEN", "Réécrit le code de l'app. À restaurer AVEC la database, sinon code et données désynchronisés."),
    "system_config": ("ÉLEVÉ", "/etc (hostname, fstab, sudoers). Restore à chaud = coupe la session ; fstab cassé = boot en échec. Mode COMPLETE/offline seulement."),
    "users_groups":  ("MOYEN", "Remet le mot de passe root et les comptes Linux du backup."),
    "network":       ("MOYEN", "Remet les profils réseau ; en COMPLETE remet l'IP source (peut couper ta session / créer un conflit d'IP si l'original tourne)."),
}
_LOW_RISK_HINT = ("FAIBLE", "Config remplacée + service rechargé — coupure brève du service.")


def _days_since_iso(iso):
    try:
        dt = datetime.fromisoformat((iso or "").replace("Z", ""))
        if dt.tzinfo:
            dt = dt.astimezone().replace(tzinfo=None)
        return (datetime.now() - dt).days
    except Exception:
        return None


def _last_restore_days():
    d = _BACKUP_ROOT / "restored_logs"
    newest = None
    try:
        for f in d.glob("*.json"):
            m = f.stat().st_mtime
            newest = m if newest is None else max(newest, m)
    except Exception:
        pass
    if newest is None:
        return None
    return int((datetime.now().timestamp() - newest) // 86400)


def dr_readiness() -> dict:
    """Audit the disaster-recovery posture from real data → score + checklist."""
    checks, score = [], 0

    def add(cid, label, status, weight, detail, reco=""):
        nonlocal score
        score += weight if status == "ok" else (weight // 2 if status == "warn" else 0)
        checks.append({"id": cid, "label": label, "status": status, "detail": detail, "reco": reco})

    backups = _load_backups()
    fulls = [b for b in backups if b["type"] == "full"]
    if fulls:
        age = _days_since_iso(fulls[0]["date"])
        if age is not None and age <= 7:
            add("full", "Backup FULL récent", "ok", 25, f"Dernier full il y a {age} j")
        elif age is not None and age <= 30:
            add("full", "Backup FULL récent", "warn", 25, f"Dernier full il y a {age} j",
                "Refais un backup FULL (idéalement < 7 jours).")
        else:
            add("full", "Backup FULL récent", "fail", 25, "Full ancien ou daté",
                "Fais un backup FULL maintenant.")
    else:
        add("full", "Backup FULL récent", "fail", 25, "Aucun backup full",
            "Fais un backup FULL — indispensable pour un clone DR.")

    cloud_ok, cloud_detail = False, "Aucune copie hors-site"
    try:
        from backend.backup.models import BackupRecord
        n = BackupRecord.objects.filter(cloud_uploaded=True).count()
        if n:
            cloud_ok, cloud_detail = True, f"{n} backup(s) dans le cloud"
    except Exception:
        pass
    add("cloud", "Copie hors-site (cloud)", "ok" if cloud_ok else "fail", 20, cloud_detail,
        "" if cloud_ok else "Active l'upload cloud (onglet Cloud Storage) — évite le point de défaillance unique.")

    sched_ok, ret_ok, sdetail = False, False, "Aucune tâche active"
    try:
        sc = json.loads((_BACKUP_ROOT / "schedule_config.json").read_text())
        on = [t for t in sc.get("tasks", []) if t.get("enabled")]
        if on:
            sched_ok, sdetail = True, f"{len(on)} tâche(s) active(s)"
        ret_ok = bool(sc.get("retention"))
    except Exception:
        pass
    add("schedule", "Backups planifiés", "ok" if sched_ok else "fail", 15, sdetail,
        "" if sched_ok else "Programme un backup automatique (onglet Schedule).")
    add("retention", "Politique de rétention", "ok" if ret_ok else "warn", 10,
        "Configurée" if ret_ok else "Non configurée",
        "" if ret_ok else "Définis une rétention (GFS) pour ne pas saturer le disque.")

    lr = _last_restore_days()
    if lr is None:
        add("restore_test", "Test de restauration", "fail", 20, "Jamais testé",
            "Teste une restauration — un backup jamais restauré est un faux filet de sécurité.")
    elif lr <= 30:
        add("restore_test", "Test de restauration", "ok", 20, f"Dernier test il y a {lr} j")
    else:
        add("restore_test", "Test de restauration", "warn", 20, f"Dernier test il y a {lr} j",
            "Refais un test de restauration (recommandé < 30 j).")

    net_ok, ndetail = False, "Interfaces DR non standard"
    try:
        from backend.network.models import Interface
        names = {i.ifname for i in Interface.objects.all()}
        if {"ens33", "ens34"} <= names:
            net_ok, ndetail = True, "2 cartes (ens33 LAN + ens34 WAN)"
    except Exception:
        pass
    add("network", "Réseau DR (2 NIC)", "ok" if net_ok else "warn", 10, ndetail,
        "" if net_ok else "Le standard DR = 2 cartes ens33 (LAN) + ens34 (WAN).")

    level = "ready" if score >= 80 else ("partial" if score >= 50 else "at_risk")
    return {"score": score, "level": level, "checks": checks}


_READY_LEVELS = {
    "ready":   ("✅ PRÊT", "Ta reprise après sinistre est bien couverte."),
    "partial": ("🟠 PARTIEL", "Reprise possible, mais des lacunes à combler."),
    "at_risk": ("🔴 À RISQUE", "Ta reprise après sinistre n'est pas garantie."),
}
_STATUS_ICON = {"ok": "✅", "warn": "🟠", "fail": "🔴"}


def _readiness_reply() -> str:
    r = dr_readiness()
    lab, msg = _READY_LEVELS[r["level"]]
    lines = [f"**Préparation au sinistre (DR) : {r['score']}/100 — {lab}**", msg, ""]
    for c in r["checks"]:
        lines.append(f"{_STATUS_ICON[c['status']]} **{c['label']}** — {c['detail']}")
        if c["reco"] and c["status"] != "ok":
            lines.append(f"   → {c['reco']}")
    return "\n".join(lines)


def _readiness_summary() -> str:
    r = dr_readiness()
    gaps = [c["label"] for c in r["checks"] if c["status"] == "fail"]
    s = f"Préparation DR : {r['score']}/100 ({r['level']})"
    return s + (f" — manque : {', '.join(gaps)}" if gaps else " — aucune lacune critique")


def restore_impact(backup_id: str = "") -> str:
    """Explain, for a backup, WHAT will change vs the current state + the RISK of
    each component. Reuses the restore-preview diff when available."""
    backups = _load_backups()
    if not backups:
        return "Aucune sauvegarde à analyser."
    b = next((x for x in backups if x["id"] == backup_id), None) if backup_id else backups[0]
    if b is None:
        b = backups[0]
    comps = [c for c, s in b["components"].items() if s in ("success", "present", "ok")]

    lines = [f"**Impact d'une restauration de `{b['id']}`** (type {b['type']})", ""]

    # What actually differs vs the current machine (from the restore-preview engine).
    try:
        import json as _json
        from pathlib import Path as _P
        from backend.backup.views import _preview_system_section
        bdir = _P("/var/backups/asguard") / b["id"]
        meta = _json.loads((bdir / "backup_metadata.json").read_text())
        sec = _preview_system_section(bdir, meta.get("components", {}))
        diff = sec.get("diff", {})
        d_lines = []
        if diff.get("root_password", {}).get("changes") is True:
            d_lines.append("- Mot de passe root : **différent** → sera remplacé")
        h = diff.get("hostname", {})
        if h.get("changes"):
            d_lines.append(f"- Nom d'hôte : {h.get('current')} → « {h.get('backup')} »")
        u = diff.get("users", {})
        if u.get("added") or u.get("removed"):
            d_lines.append(f"- Comptes : +{', '.join(u.get('added') or []) or '—'} / −{', '.join(u.get('removed') or []) or '—'}")
        mc = diff.get("packages", {}).get("missing_count")
        if mc:
            d_lines.append(f"- Paquets : {mc} manquant(s) réinstallé(s)")
        if d_lines:
            lines.append("**Ce qui changera au niveau système vs maintenant :**")
            lines.extend(d_lines)
        else:
            lines.append("Au niveau système : identique à l'état actuel (aucun changement détecté).")
        lines.append("")
    except Exception:
        pass

    # Per-component risk.
    risky = [c for c in comps if c in _RESTORE_RISKS]
    if risky:
        lines.append("**⚠️ Composants sensibles (préviens avant de restaurer) :**")
        for c in risky:
            lvl, why = _RESTORE_RISKS[c]
            lines.append(f"- **{c}** — risque {lvl} : {why}")
    lines.append("")
    lines.append("💡 Fais un backup « safe » AVANT de restaurer. Pour ne pas tout remettre, "
                 "restaure **par composant**. Pour un clone (même IP), c'est COMPLETE + reboot, original éteint.")
    return "\n".join(lines)


# ── Local LLM (Ollama) layer ─────────────────────────────────────────────────
# Free, offline, runs on the appliance. If Ollama isn't reachable we fall back
# to the deterministic rule engine above, so the assistant never fully breaks.
import os
import urllib.request

_OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")

_ASGUARD_KNOWLEDGE = """Tu es l'assistant d'Asguard, un pare-feu / appliance de sécurité (Django + Vue).
Réponds en français, de façon claire et concise, comme un expert réseau/sécurité.
Si tu n'es pas sûr, dis-le — n'invente jamais de commande ou de chemin.

CONNAISSANCES ASGUARD :
- C'est un firewall : il filtre le trafic réseau (règles nftables), fait du NAT, VPN (OpenVPN/IPsec),
  IDS/IPS (Suricata), WAF (ModSecurity), proxy (Squid), ZTNA, DHCP, VLAN/VXLAN, routage, PKI/certificats.
- Interfaces standard : ens33 = LAN, ens34 = WAN.
- SAUVEGARDE : 3 types. « Safe » = config seule (firewall, VPN, réseau, certificats…), sans base ni code.
  « Full » = safe + base de données (règles, users, historique) + code de l'app. « Custom » = composants au choix.
- RESTAURATION : « COMPLETE » = clone exact de toute la VM (même IP, même config) — pour un plan de reprise (DR)
  après sinistre. Par « composant » = ne remet qu'une partie (ex. juste le réseau).
- DR : pour cloner la machine, faire un backup FULL puis un restore COMPLETE sur une nouvelle VM (2 cartes réseau),
  puis reboot. Une seule machine par IP à la fois (l'original doit être éteint).
- FIREWALL : bloquer un port/IP → onglet « Rules firewall », choisir l'interface (LAN ens33 ou WAN ens34),
  chaîne inbound, action « drop », préciser protocole+port ou IP source. Autoriser → action « accept ».
  L'ordre compte : les « accept » spécifiques avant les « drop » génériques.
- NAT / redirection de port → onglet « NAT » → DNAT : IP:port externe (WAN) vers IP:port interne (LAN).
- OUVRIR un service depuis l'extérieur = 2 étapes : une règle NAT (DNAT) + une règle firewall « accept » sur le WAN.
- OpenVPN → onglet OpenVPN (serveur, clients, certificats). IPsec → onglet IPsec (site-à-site / nomade).
- Ajouter un utilisateur → « Gestion des utilisateurs » (stocké en base → inclus dans un backup full).
- Créer un VLAN → onglet VLAN (interface parente + tag 1-4094). VXLAN → onglet VXLAN.
- BACKUP PLANIFIÉ → onglet Schedule : tâche safe/full/db à une heure cron, avec rétention.
- BONNES PRATIQUES : fais un backup « safe » AVANT tout changement de config ; un « full » régulier pour le DR ;
  vérifie l'aperçu avant de restaurer.

RISQUES DE RESTAURATION (préviens toujours l'utilisateur avant qu'il restaure un composant sensible) :
- database : pg_restore REMPLACE TOUTE la base (users, règles, réseau, certificats, historique) — pas juste une app.
  Atomique (rollback si échec) mais tu PERDS tout ce qui a été créé depuis le backup + brève coupure. Risque ÉLEVÉ.
- application : réécrit le code de l'app. À restaurer AVEC la database (sinon code et données désynchronisés). Risque MOYEN.
- system_config (/etc) : hostname, fstab, sudoers — un restore à chaud coupe la session SSH/web ; un mauvais fstab peut
  empêcher le boot. Mode COMPLETE/offline seulement. Risque ÉLEVÉ.
- users_groups : remet le mot de passe root et les comptes Linux du backup. Risque MOYEN.
- network : remet les profils réseau ; en COMPLETE, remet l'IP source (peut couper ta session, ou créer un conflit
  d'IP si l'original tourne encore). Risque MOYEN-ÉLEVÉ.
- firewall / nat / vpn / ids / proxy / etc. : config remplacée + service rechargé — coupure brève du service concerné. Risque FAIBLE.
- Restauration COMPLETE : clone TOUTE la VM (même IP, root, users) → reboot requis, l'original doit être ÉTEINT (conflit IP). Risque ÉLEVÉ (mais c'est le but du DR).
CONSEIL : toujours faire un backup « safe » AVANT de restaurer, et vérifier l'Aperçu (ce qui va changer) avant de lancer.

Tu peux conseiller QUEL backup restaurer, analyser ce qu'un backup contient, expliquer CE QUI VA CHANGER et les RISQUES,
évaluer la préparation au sinistre (DR Readiness), et guider pas à pas.
Le contexte ci-dessous donne l'ÉTAT RÉEL de cette machine — appuie-toi dessus."""


def _live_context() -> str:
    """Inject the REAL, current state of the machine so the model always knows
    what exists — no retraining. Read fresh on every prompt: interfaces, VLANs,
    firewall rule count, and the available backups. Whatever the operator adds
    shows up here automatically on the next question."""
    parts = ["ÉTAT ACTUEL DE LA MACHINE (à jour, lu maintenant) :"]

    try:
        from backend.network.models import Interface, IP4Config
        ip_by_if = {c.interface_id: (c.typeip4, c.ip_address, c.netmask)
                    for c in IP4Config.objects.all()}
        rows = []
        for i in Interface.objects.all():
            if not i.ifname:
                continue
            ip = ip_by_if.get(i.id)
            addr = f"{ip[1]}/{ip[2]} ({ip[0]})" if ip and ip[1] else (f"{ip[0]}" if ip else "sans IP")
            rows.append(f"{i.name_interface or i.ifname} [{i.ifname}] = {addr}")
        if rows:
            parts.append("Interfaces : " + " ; ".join(rows))
    except Exception:
        pass
    try:
        from backend.vlan.models import Vlan
        vl = list(Vlan.objects.select_related("parent_interface").all())
        if vl:
            parts.append("VLAN : " + ", ".join(
                f"tag {v.vlan_tag} sur {getattr(v.parent_interface, 'ifname', '?')}" for v in vl))
        else:
            parts.append("VLAN : aucun (il n'y a AUCUN VLAN configuré)")
    except Exception:
        pass
    try:
        from backend.rules.models import Rule
        parts.append(f"Règles firewall en base : {Rule.objects.count()}")
    except Exception:
        pass
    try:
        sched = _BACKUP_ROOT / "schedule_config.json"
        if sched.exists():
            cfg = json.loads(sched.read_text())
            tasks = cfg.get("tasks", []) if isinstance(cfg, dict) else []
            on = [t for t in tasks if t.get("enabled")]
            parts.append(f"Backups planifiés : {len(on)} tâche(s) active(s)" if on
                         else "Backups planifiés : aucun (aucune tâche active)")
    except Exception:
        pass

    backups = _load_backups()[:6]
    if backups:
        parts.append("Sauvegardes présentes (récente en premier) :")
        for b in backups:
            present = sum(1 for s in b["components"].values() if s in ("success", "present", "ok"))
            parts.append(f"- {b['id']} (type {b['type']}, {present} composants)")
    else:
        parts.append("Aucune sauvegarde présente.")
    try:
        parts.append(_readiness_summary())
    except Exception:
        pass
    return "\n".join(parts)


def _is_readiness(t: str) -> bool:
    if any(w in t for w in ("readiness", "sinistre", "suis-je prêt", "suis je pret", "es-tu prêt")):
        return True
    if any(w in t for w in ("prêt", "pret", "préparé", "prepar", "reprise")) and \
       any(w in t for w in ("dr", "sinistre", "reprise", "restaur", "backup", "sauvegarde", "disaster")):
        return True
    if "audit" in t and any(w in t for w in ("dr", "backup", "sauvegarde")):
        return True
    return False


def _is_impact(t: str) -> bool:
    ctx = any(w in t for w in ("restaur", "restore", "backup", "sauvegarde", "db", "database", "application", "composant"))
    trig = any(w in t for w in ("risque", "danger", "impact", "abim", "endommag", "casser", "grave",
                                "ce qui change", "qui change", "différe", "differe", "difference",
                                "version précédente", "version precedente", "avant/après", "sensible"))
    return ctx and trig


_RISK_COMP_KW = {
    "database":      ["database", "base de donnée", "base de donnees", "données", "donnees", " db ", "la db", "postgres"],
    "application":   ["application", "le code", "app "],
    "system_config": ["système", "systeme", "/etc", "hostname", "fstab"],
    "network":       ["réseau", "reseau", "interface", "profils réseau"],
    "users_groups":  ["utilisateur", "compte", "mot de passe root", "root"],
}


def _risk_of_component(t: str):
    """If the user names a specific sensitive component, explain ITS risk."""
    padded = f" {t} "
    for comp, kws in _RISK_COMP_KW.items():
        if any(k in padded for k in kws):
            lvl, why = _RESTORE_RISKS[comp]
            return (f"**Restaurer le composant « {comp} » — risque {lvl}**\n{why}\n\n"
                    "💡 Fais un backup « safe » AVANT, et vérifie l'Aperçu (ce qui va changer). "
                    "Restaure par composant pour limiter l'impact.")
    return None


def _special_intent(message: str):
    """DR-readiness / restore-impact intents → deterministic, exact replies
    (score & risks must be reliable, not left to the small model)."""
    t = _norm(message)
    if _is_readiness(t):
        return _readiness_reply()
    if _is_impact(t):
        comp = _risk_of_component(t)
        if comp:
            return comp
        m = re.search(r"(backup[\w\-]+)", t)
        return restore_impact(m.group(1) if m else "")
    return None


def _payload(message: str, stream: bool) -> dict:
    return {
        "model": _OLLAMA_MODEL,
        "stream": stream,
        # keep the model hot for 30 min so follow-up questions are instant; small
        # context + capped output keep CPU latency low.
        "keep_alive": "2m",
        "options": {"temperature": 0.3, "num_ctx": 1536, "num_predict": 400},
        "messages": [
            {"role": "system", "content": _ASGUARD_KNOWLEDGE + "\n\n" + _live_context()
             + "\n\nRÈGLES : base-toi STRICTEMENT sur « ÉTAT ACTUEL DE LA MACHINE » ci-dessus. "
               "Si un élément (VLAN, interface, backup…) n'y figure PAS, réponds clairement qu'il "
               "n'existe pas / qu'il n'y en a pas — n'invente jamais. Réponds de façon BRÈVE et directe."},
            {"role": "user", "content": message},
        ],
    }


def _ollama_chat(message: str, timeout: int = 60) -> str | None:
    """Non-streaming call. Returns reply text or None on failure."""
    try:
        req = urllib.request.Request(
            f"{_OLLAMA_URL}/api/chat",
            data=json.dumps(_payload(message, False)).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return ((data.get("message") or {}).get("content", "").strip()) or None
    except Exception:
        return None


def stream_answer(message: str):
    """Generator yielding reply text chunks (for a live, ChatGPT-style stream).
    Falls back to the rule engine if Ollama can't be reached at all."""
    t = _norm(message)
    if not t:
        yield _HELP
        return
    special = _special_intent(message)
    if special is not None:
        yield special
        return
    try:
        req = urllib.request.Request(
            f"{_OLLAMA_URL}/api/chat",
            data=json.dumps(_payload(message, True)).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        resp = urllib.request.urlopen(req, timeout=120)
    except Exception:
        yield _rule_answer(message)["reply"]
        return
    got = False
    try:
        for raw in resp:
            line = raw.decode("utf-8", "ignore").strip()
            if not line:
                continue
            obj = json.loads(line)
            chunk = (obj.get("message") or {}).get("content", "")
            if chunk:
                got = True
                yield chunk
            if obj.get("done"):
                break
    except Exception:
        pass
    if not got:  # Ollama answered but empty → deterministic fallback
        yield _rule_answer(message)["reply"]


def prewarm():
    """Load the model into RAM at startup so the first user question is fast."""
    try:
        req = urllib.request.Request(
            f"{_OLLAMA_URL}/api/chat",
            data=json.dumps({"model": _OLLAMA_MODEL, "stream": False, "keep_alive": "2m",
                             "options": {"num_predict": 1},
                             "messages": [{"role": "user", "content": "ok"}]}).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=120).read()
    except Exception:
        pass


def answer(message: str) -> dict:
    """Non-streaming entry point (kept for compatibility). Tries the LLM, falls
    back to the rule engine."""
    t = _norm(message)
    if not t:
        return {"intent": "help", "reply": _HELP, "refs": []}
    special = _special_intent(message)
    if special is not None:
        return {"intent": "dr", "reply": special, "refs": []}
    reply = _ollama_chat(message)
    if reply:
        return {"intent": "llm", "reply": reply, "refs": []}
    return _rule_answer(message)
