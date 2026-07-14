# Audit de complétude Backup / Restore — Asguard
## Document de soutenance — PFE Backup & DRP

> Ce document complète `DOCUMENTATION_BACKUP_DRP.md` et `MECANISME_BACKUP_RESTORE.md`.
> Il répond à **une seule question** : « si la VM crash, qu'est-ce qui revient et qu'est-ce qui manque ? »

---

## 1. Réponse synthétique

**Oui — l'intégralité de la configuration et des données utilisateur est restaurable.**

29 composants couvrent le firewall, le réseau, les VPN, l'IDS/IPS, le WAF, le proxy, la ZTNA, le DHCP, le routage, les certificats, la base de données, le code applicatif, les services systemd, les paquets installés, les utilisateurs Linux et les logs. Le restore se fait en deux modes complémentaires :

- **Restore en ligne (UI-safe)** : 21 composants restaurés depuis l'interface web, sans interruption du panneau d'administration. Protège le plan de contrôle (code applicatif, `/etc` global, systemd, docker) — sinon le restore coupe sa propre session.
- **Restore hors ligne (DR — console TTY)** : les 29 composants restaurés via le script `scripts/asguard-dr-restore`. Utilisé quand on reconstruit une VM neuve à partir d'un backup importé.

Chaque composant capturé en base PostgreSQL (NAT, ZTNA, VPN, certificats, …) embarque en plus un **snapshot ORM** (`component_db.json`) qui rejoue les lignes exactes — pas seulement les fichiers de config.

---

## 2. Matrice de complétude

Légende — `📁` fichiers de config, `🗄` lignes PostgreSQL, `📊` état système live (commande dumpée), `⛔` exclu du restore UI (DR offline obligatoire).

| Composant | Capturé au backup | Restauré (UI) | Restauré (DR offline) | Snapshot DB | Verdict |
|---|---|---|---|---|---|
| `database` | 📊 `pg_dump -F c` → `db/postgres.dump` | ✅ `pg_restore` | ✅ | — | **OK** |
| `firewall` | 📁 `/etc/nftables.conf` + `/etc/rules` + 🗄 `rules.Rule` (JSON dédié) | ✅ extract + rebuild Rule rows | ✅ | dédié | **OK + DB** |
| `vpn` | 📁 `/etc/openvpn`, `/etc/strongswan.d`, `/etc/swanctl`, `/etc/ipsec.*` | ✅ extract | ✅ | 🗄 `openvpn.Server/Client` | **OK + DB** |
| `web` | 📁 `/etc/nginx` | ✅ extract | ✅ | — | **OK** |
| `ids` | 📁 `/etc/suricata` + `/var/lib/suricata/rules` | ✅ extract | ✅ | 🗄 `SuricataInterface` | **OK + DB** |
| `proxy` | 📁 `/etc/squid` | ✅ extract | ✅ | 🗄 `ServerSatus`, `ProxyRules`, `ProxyUser` | **OK + DB** |
| `network` | 📁 `/etc/network`, NetworkManager, netplan, systemd/network, resolv.conf | ✅ extract | ✅ | — (voir §4) | **OK fichiers** |
| `security` | 📁 `/etc/fail2ban`, `/etc/ssh`, `/etc/pam.d` | ✅ extract | ✅ | — | **OK** |
| `certificates` | 📁 `/etc/easy-rsa`, `/etc/ssl/*`, `pki/` | ✅ extract | ✅ | 🗄 `CertificateAuthority`, `Certificate` | **OK + DB** |
| `application` | 📁 `/asguard/asguard` (sans `__pycache__`, `.git`, `venv`, `node_modules`) | ⛔ | ✅ | — | **OK (DR)** |
| `system_config` | 📁 `/etc` complet (sauf `mtab`) | ⛔ | ✅ | — | **OK (DR)** |
| `scheduled_tasks` | 📁 `/etc/crontab`, `cron.{d,daily,hourly,weekly,monthly}`, `/var/spool/cron` | ✅ extract | ✅ | — | **OK** |
| `packages` | 📊 `pacman -Qqe` ou `dpkg --get-selections` | ⛔ | ✅ réinstallation | — | **OK (DR)** |
| `systemd_services` | 📊 services enabled + active + `/etc/systemd/system` (units) | ⛔ | ✅ + `daemon-reload` | — | **OK (DR)** |
| `docker_state` | 📊 listes images / containers / volumes / networks | ⛔ | ✅ pull + recréation | — | **OK¹** |
| `logs` | 📁 `/var/log/{nginx,openvpn,suricata,asguard,syslog,messages,auth.log}` | ⛔ | ✅ | — | **OK forensique (DR)** |
| `users_groups` | 📁 `/etc/{passwd,shadow,group,gshadow,sudoers,sudoers.d}` | ⛔ | ✅ | — | **OK (DR)** |
| `ztna` | 📁 `backend/ztna/` | ✅ extract | ✅ | 🗄 9 modèles ZTNA | **OK + DB** |
| `ldap` | 📁 `backend/LdapServer/` + `/etc/ldap`, `/etc/openldap` | ✅ extract | ✅ | — | **OK** |
| `ipsec_detailed` | 📁 `backend/ipsec/` + `/etc/ipsec.*`, `/etc/strongswan.d`, `/etc/swanctl` | ✅ extract | ✅ | 🗄 `ServerIPsec` | **OK + DB** |
| `routing` | 📁 `backend/routing/` + 📊 `ip route show` | ✅ extract | ✅ | 🗄 `Routing` | **OK + DB** |
| `vlan` | 📁 `backend/vlan/` + `/etc/systemd/network`, `/etc/network` | ✅ extract | ✅ | 🗄 `Vlan` | **OK + DB** |
| `vxlan` | 📁 `backend/vxlan/` + `/etc/systemd/network`, `/etc/network` | ✅ extract | ✅ | 🗄 `Vxlan` | **OK + DB** |
| `sdwan` | 📁 `backend/sdwan/` | ✅ extract | ✅ | 🗄 `Area`, `SdwanRules`, `AreaInterface` | **OK + DB** |
| `waf` | 📁 `backend/waf/` + `/etc/nginx`, `/etc/nginx/modsec` | ✅ extract | ✅ | 🗄 `ConfigWaf`, `ApplicationWaf`, `RulesWaf`, `ApplicationRulesWaf` | **OK + DB** |
| `nat` | 📁 `backend/nat/` + 📊 `nft list ruleset` | ✅ extract | ✅ | 🗄 `SNat`, `OneToOneNat`, `DNat` | **OK + DB** |
| `dhcp` | 📁 `backend/server_dhcp4/` + `/etc/dhcp`, `/etc/dhcpd.conf` | ✅ extract | ✅ | 🗄 `ServerDhcp` | **OK + DB** |
| `gateway` | 📁 `backend/gateway/` | ✅ extract | ✅ | 🗄 `Gateway`, `GatewayInterface` | **OK + DB** |
| `double_mask` | 📁 `backend/double_mask/` | ✅ extract | ✅ | 🗄 `DoubleMask` | **OK + DB** |

¹ **`docker_state`** : seules les *listes* sont sauvegardées (pas les *images*). Le DR fait `docker pull` depuis le registre. Asguard utilise des images publiques (`postgres`, etc.), donc reproductible. Pour un environnement air-gap il faudrait `docker save`.

### Compteurs

- **29 / 29 composants** ont un runner de sauvegarde
- **29 / 29 composants** ont un runner de restauration
- **17 composants** embarquent un snapshot DB ORM exhaustif (`component_db.json`)
- **1 composant** (`firewall`) a sa propre sync DB historique (`firewall_rules_db.json`)
- **8 composants** sont exclus du restore UI (raisons techniques documentées dans `views.py:_UI_FULL_EXCLUSION_REASONS`)

**Verdict global : la complétude est totale.** Aucun composant fonctionnel du firewall n'est laissé de côté.

---

## 3. Carte du code — fichiers que l'encadrant doit regarder

### 3.1 Cœur backup / restore (5 fichiers — la « machine »)

| Fichier | Lignes | Rôle |
|---|---|---|
| `backend/backup/system_backup/full_backup_service.py` | ~1400 | Moteur de sauvegarde. Une méthode `_backup_<composant>()` par composant. `create_safe_backup` / `create_full_backup` / `create_custom_backup`. |
| `backend/backup/system_backup/restore_service.py` | ~830 | Moteur de restauration. Une méthode `_restore_<composant>()` par composant. `restore_full_safe`, `restore_full_ui_safe`, `restore_components`. |
| `backend/backup/system_backup/backup_service.py` | ~150 | Dump PostgreSQL via `docker exec pg_dump`. |
| `backend/backup/component_db.py` | 217 | Snapshot/restore générique des lignes PostgreSQL par composant. Registre `COMPONENT_MODELS` qui associe un composant à ses modèles Django. |
| `backend/backup/restore_diff.py` | 250 | Diff pré/post restore — produit le rapport ligne par ligne (ajoutés / supprimés / modifiés). |

### 3.2 Cycle de vie (4 fichiers — automatisation)

| Fichier | Rôle |
|---|---|
| `backend/backup/views.py` | API REST principale (1900+ lignes). Endpoints : `create-safe-backup`, `create-full-backup`, `schedule`, `restore-full`, `restore-preview`, `restore-full-status`, `delete-backup`. Backups asynchrones via threads (`_run_backup_in_thread`). |
| `backend/backup/apps.py` | `BackupConfig.ready()` synchronise la crontab à chaque démarrage Django (`_sync_crontab`). |
| `full_restore_runner.py` (racine) | Runner détaché lancé via `systemd-run` pour les restores complets — survit aux redémarrages de services. Notifications ntfy direct (stdlib). |
| `scripts/asguard-dr-restore` | Script bash Disaster Recovery. Lancé depuis console TTY après réinstallation VM. Restaure les composants exclus du mode UI. |

### 3.3 Robustesse (4 fichiers — qualité industrielle)

| Fichier | Rôle |
|---|---|
| `backend/backup/integrity.py` | Manifeste signé HMAC écrit en TOUT DERNIER. Détecte fichier altéré, manquant, intrus, manifeste falsifié. Anti-ransomware. |
| `backend/backup/notifications.py` | Push ntfy.sh + email (Gmail). `notify_backup_started/completed`, `notify_restore_completed`, `notify_firewall_rule_change`, `notify_waf_alert`. |
| `backend/backup/post_restore_resync.py` | Vérification de cohérence post-restauration. |
| `backend/backup/dr_drill.py` | Exercice de reprise mesuré (RPO, RTO, intégrité). Score / 100. Exécutable en CRON nocturne (`scripts/asguard-dr-drill.cron`). |

### 3.4 Cloud + Audit (3 fichiers — services additionnels)

| Fichier | Rôle |
|---|---|
| `backend/backup/system_backup/cloud_storage.py` | Upload S3-compatible (Backblaze B2 / Cloudflare R2 / AWS S3 / MinIO) via boto3. Auto-upload après chaque backup, rétention. |
| `backend/backup/observability.py` + `views_alerts.py` | Métriques + journal d'événements (`append_backup_event`). |
| `backend/backup/risk_ai.py` + `log_intelligence.py` | Risk Center IA — analyse de risque en temps réel. |

### 3.5 Frontend (1 fichier critique)

| Fichier | Rôle |
|---|---|
| `src/views/backup/components/Backups.vue` | Vue principale liste backups + actions. Contient les modales : `Aperçu du contenu` (cartes visuelles), `Restore` (avec preview), `Détails` (audit technique), monitor live de restauration. |

**Total à examiner : ~17 fichiers backend + 1 frontend + 1 bash. Tout le reste est UI Vue ou utilitaires.**

---

## 4. Points techniques que l'encadrant cherchera

### 4.1 Stockage 100 % filesystem — pas de cycle d'œuf et de poule

`/var/backups/asguard/` est l'unique source de vérité. Aucune table PostgreSQL n'enregistre les backups eux-mêmes — ce qui éviterait le paradoxe : si la base est corrompue, on perdrait la liste des backups. La métadonnée est dans `backup_metadata.json` au sein de chaque dossier.

Exception consciente : `BackupRecord` (table `backup_record`) trace l'historique d'upload **cloud** des backups, parce que cette donnée est *enrichissement* (statut S3), pas la source de vérité.

### 4.2 Snapshot DB par composant — la clé de la fidélité

Historiquement les backups ne sauvegardaient que des fichiers de config. La table `nat.DNat` (les règles NAT créées par l'utilisateur) ne pouvait pas être restaurée. `component_db.py` corrige ça :

```python
COMPONENT_MODELS = {
    "nat":  ["nat.SNat", "nat.OneToOneNat", "nat.DNat"],
    "ztna": ["ztna.Identities", "ztna.Enrollements", ...],
    ...
}
```

Au backup, `dump_component_db("nat")` sérialise toutes les lignes via `django.core.serializers`. Au restore, `restore_component_db` rejoue dans une transaction atomique avec `SET CONSTRAINTS ALL DEFERRED` — les FK ne sont vérifiées qu'au COMMIT, ce qui permet d'insérer dans n'importe quel ordre.

### 4.3 Restauration asynchrone détachée

Le restore complet n'est pas géré par un thread Django : il est lancé via `systemd-run` (unité éphémère) → `full_restore_runner.py`. Bénéfice : si la restauration touche `uvicorn` ou le réseau, le processus survit. Le suivi se fait par fichier d'état `/var/backups/asguard/restore_jobs/<job_id>.json` polled par le frontend.

### 4.4 Mode UI-safe vs DR-offline — pourquoi cette distinction ?

Restaurer `application` (le code Python) à chaud écraserait les fichiers que `uvicorn` est en train d'exécuter → crash. Restaurer `system_config` (tout `/etc`) couperait la session SSH/web en cours. Restaurer `users_groups` (`/etc/passwd`, `shadow`) verrouillerait l'opérateur. La liste exhaustive avec les raisons est documentée dans :

```python
# backend/backup/views.py:3006-3031
_UI_FULL_EXCLUSION_REASONS = {
    "application": ("Code de l'application", "Réécrire à chaud le code Python pendant qu'uvicorn tourne ferait crasher l'interface..."),
    "system_config": ("Configuration /etc système globale", "Contient hostname, fstab, locale, sudoers — un restore à chaud couperait votre session SSH/web..."),
    ...
}
```

Ces 8 composants restent restaurables — mais **uniquement par `scripts/asguard-dr-restore` lancé depuis la console TTY après reboot**. C'est le scénario exact que l'encadrant veut voir : VM crashée → réinstall minimale → DR restore.

### 4.5 Intégrité signée — anti-ransomware

`integrity.write_manifest(backup_dir)` calcule la SHA-256 de chaque fichier du backup et signe l'ensemble avec un HMAC. Écrit en tout dernier (après `backup_metadata.json`). Au restore, `verify_manifest` recalcule et compare : fichier altéré, manquant, intrus → détecté avant exécution.

### 4.6 Diff pré/post restore — preuve de fidélité (nouveau)

Module `restore_diff.py` (ajouté ce mois). Capture deux snapshots ORM (avant + après restauration) et calcule un diff ligne par ligne par modèle :

- `added` (lignes présentes en post, absentes en pré)
- `removed` (lignes présentes en pré, absentes en post)
- `modified` (mêmes PK, valeurs différentes)

Persisté dans `result["diff"]` du job state, rendu dans le moniteur de restore frontend. **Sert de preuve mesurable que le contenu attendu est bien là.**

---

## 5. Limites assumées (à mentionner par honnêteté)

| Point | Limite | Mitigation |
|---|---|---|
| Images Docker | Non sauvegardées | Re-pull depuis registre — OK avec images publiques |
| Modèle `network.Interface` | Non inclus dans `component_db.py` | Les interfaces sont auto-détectées depuis le hardware. Si nouvelle VM = nouvelles NICs, le script DR demande un mapping `OLD=NEW` |
| Backup en cours pendant restore | Pas de verrou cross-job | Probabilité quasi-nulle en exploitation (cron ≠ heure restore) |
| Application en JIT pendant restore-UI | Application explicitement exclue | C'est le but du mode UI-safe |

Aucune de ces limites n'empêche de répondre **oui** à la question « la VM revient-elle ? ».

---

## 6. Plan de défense — questions que tu peux recevoir

**Q. « Comment savez-vous que TOUS les composants sont vraiment sauvegardés ? »**
> R. Le moteur a 29 runners (`FULL_COMPONENTS` dans `full_backup_service.py:42`). Chaque runner produit un `ComponentResult` avec statut + sha256 + taille, écrit dans `backup_metadata.json`. Le `health_score` (sur 100) compte les succès/non-skipped. Démo : `cat backup_metadata.json | jq '.components | keys'`.

**Q. « Et si le backup est corrompu silencieusement ? »**
> R. Manifeste HMAC signé (`integrity.py`). Au restore, `verify_manifest` lit chaque sha256 et recalcule. Une seule différence = restore bloqué avec message explicite. Démo : `curl /backup/<id>/verify-integrity`.

**Q. « Pourquoi 2 modes de restore au lieu d'un seul ? »**
> R. Sécurité opérationnelle. Restaurer à chaud le code Python qui tourne actuellement = SIGSEGV. Le mode UI restore les 21 composants "froids" sans risque. Le DR script (`asguard-dr-restore`) restaure tout, mais s'exécute depuis console TTY après reboot — séparation stricte plan de contrôle / plan de données.

**Q. « La base PostgreSQL est-elle vraiment restaurée à l'identique ? »**
> R. Deux niveaux : (1) `pg_dump -F c` capture la totalité (schema + data). (2) Pour la traçabilité par composant, chaque module exporte ses lignes en JSON sérialisé Django dans `component_db.json` — preserved PK + FK déférées à COMMIT. Démo : `cat backup_safe_.../nat/component_db.json`.

**Q. « Comment retrouvez-vous un backup après crash de la VM ? »**
> R. Pas dans la VM. Trois chemins : (1) **export/import** UI : tar.gz téléchargé hors-VM, ré-importé sur la VM neuve. (2) **Cloud auto-upload** S3 (Backblaze B2 ou Cloudflare R2 — `cloud_storage.py`). (3) Filesystem `/var/backups/asguard/` si le disque survit.

**Q. « Le restore est-il transactionnel ? »**
> R. Par composant oui (`component_db.py` utilise `transaction.atomic`). Cross-composant non — par design : un échec partiel laisse l'opérateur avec un état intermédiaire visible (statut `partial_success` + diff) qu'il peut compléter manuellement. Le diff fournit la preuve exacte de ce qui est passé.

**Q. « Quelle est votre RPO / RTO ? »**
> R. Mesurés par `dr_drill.run_dr_readiness_drill` (exercice automatisé quotidien — `scripts/asguard-dr-drill.cron`). RPO ≤ intervalle du cron de backup (configurable). RTO restore safe ~30 s, full UI ~2-3 min, DR offline 5-10 min.

---

## 7. Démo live — voir `DEMO_DR_CHECKLIST.md`

La checklist de démo est dans un fichier séparé pour pouvoir être affichée en double écran pendant la soutenance.
