# Prep entretien technique — Backup & DRP / Asguard

> Fiche de révision orale. Pour chaque question : **réponse courte à dire**, puis détail si on creuse.
> Ne récite pas — comprends la logique. L'expert teste si tu connais *pourquoi* tu as fait tes choix.

---

## A. Architecture Asguard (mise en contexte)

**Q1 — C'est quoi Asguard en une phrase ?**
> Une appliance firewall/sécurité : backend Django 5.2 (ASGI/Daphne avec WebSocket via Channels), frontend Vue 3, PostgreSQL, Redis+Celery, derrière Nginx. Elle gère firewall nftables, NAT, VPN (OpenVPN/IPsec), IDS/IPS Suricata, WAF ModSecurity, proxy Squid, ZTNA, DHCP, etc.

**Q2 — Pourquoi Daphne/ASGI et pas WSGI classique ?**
> Parce qu'on a besoin de **WebSocket** pour le monitoring temps réel (CPU/RAM toutes les 1s, logs Suricata/Squid live, statut VPN). WSGI est synchrone et ne gère pas les connexions persistantes ; ASGI oui.

**Q3 — Où s'insère ton module dans cette archi ?**
> C'est l'app Django `backup`. Elle expose une API REST sous `/backup/`, un moteur de sauvegarde/restore dans `system_backup/`, et un frontend Vue (8 onglets) dans `src/views/backup/`. Elle interagit avec PostgreSQL (pg_dump), le filesystem, systemd, Docker (conteneur DB), LVM et le cloud S3.

**Q4 — Celery sert à quoi ici ?**
> Tâche planifiée quotidienne d'export backup à 02:00 UTC, broker Redis. Mais attention — le **scheduling principal des backups passe par crontab système**, pas Celery (voir section Scheduling).

---

## B. Backup (Safe / Full / DB)

**Q5 — Quels sont tes 3 modes de backup et la différence ?**
> - **Safe** (~4.5 MB) : config uniquement — 17 composants (firewall, vpn, ids, proxy, network, certificats, routing, nat, dhcp, waf, ztna, ipsec, vlan, vxlan, sdwan, gateway, double_mask). Rapide, non intrusif.
> - **Full** : safe + dump PostgreSQL complet (`pg_dump -F c`) + code applicatif. C'est la base d'un vrai DRP.
> - **DB** : juste le dump PostgreSQL, synchrone.

**Q6 — Où sont stockés les backups ? Pourquoi pas en base ?**
> 100 % filesystem sous `/var/backups/asguard/`. **Zéro PostgreSQL pour le stockage** — volontaire : si la base est corrompue, je dois quand même pouvoir lire mes backups. Mettre les backups dans la base qu'on sauvegarde serait une dépendance circulaire. Chaque backup a un `backup_metadata.json` (schéma v4.1 : statut des composants, sha256, durées).

**Q7 — Comment garantis-tu l'intégrité d'un backup ?**
> sha256 par composant stocké dans les métadonnées + endpoint `verify-integrity` qui recalcule et compare. À la restauration, on vérifie avant de rejouer.

**Q8 — Le backup bloque-t-il l'interface pendant qu'il tourne ?**
> Non. `create-safe-backup` / `create-full-backup` sont **asynchrones** : l'API renvoie immédiatement `{status:"queued", job_id}`, le backup tourne dans un thread de fond qui écrit sa progression dans `backup_jobs/{job_id}.json`. Le front poll `GET /backup/progress/<job_id>` pour la barre de progression par composant.

**Q9 — Pourquoi un thread et pas Celery pour le backup async ?**
> Choix pragmatique : le backup est I/O-bound (tar, pg_dump), pas CPU. Un daemon thread suffit, ça évite la dépendance à un worker Celery actif et la sérialisation de gros objets. Le suivi de progression est un simple fichier JSON, donc lisible même après redémarrage d'uvicorn.

**Q10 — Que se passe-t-il si pg_dump échoue au milieu d'un full backup ?**
> Le composant `database` est marqué `failed` dans les métadonnées, les autres composants restent valides. Le backup n'est pas atomique tout-ou-rien au niveau global, mais chaque composant a son statut — on sait exactement quoi a réussi.

---

## C. Restore & DRP (la zone la plus questionnée)

**Q11 — Différence entre restore Safe (UI) et restore Complet (DR) ?**
> - **Restore en ligne / UI-safe** : restaure la config sans couper le panneau d'admin. On **protège le plan de contrôle** (code applicatif, `/etc` global, systemd, docker) — sinon le restore tuerait sa propre session HTTP. ~21 composants.
> - **Restore complet / DR offline** : reconstruit une VM neuve à l'identique depuis un backup importé, via console TTY (`scripts/asguard-dr-restore`). 29 composants, y compris IP réseau, profils NetworkManager, mot de passe root, users Linux.

**Q12 — "Restore complet = clone exact de la VM source", explique.**
> Le mode COMPLETE reproduit la VM source **à l'identique** : IP/profils réseau NM, mot de passe root, utilisateurs. C'est le modèle DR — on remonte un sinistre sur une VM vierge. Donc on NE préserve PAS l'IP de la machine cible, c'est voulu. (Pour le restore UI au contraire on préserve le réseau host.)

**Q13 — Comment restaures-tu plus que des fichiers ? (le piège ORM)**
> Chaque composant capturé en base (NAT, ZTNA, VPN, certs…) embarque un **snapshot ORM** `component_db.json` qui rejoue les **lignes exactes** PostgreSQL, pas seulement les fichiers de config. Donc on restaure l'état applicatif réel, pas juste `/etc`.

**Q14 — VM Snapshot : c'est quoi la couche LVM ?**
> Avant un restore risqué, on prend un **snapshot LVM** du volume logique → rollback instantané si le restore foire. `/var/backups` est sur le LV snapshotable.

**Q15 — [PIÈGE CLASSIQUE] Si `/var/backups` est sur le LV que tu restaures, tu n'effaces pas tes propres backups ?**
> Excellente question — c'est un bug que j'ai eu et corrigé. Oui, le restore aurait écrasé `/var/backups`. La solution : je **stage les backups + le schedule hors du LV** avant le restore, plus un lock du scheduler hors-LV. Comme ça les backups survivent au restore.

**Q16 — [PIÈGE] Le restore complet a-t-il déjà cassé le boot ?**
> Oui, vécu : le full restore écrasait `/etc/fstab` avec la layout LVM de la VM **source** → la cible ne bootait plus si elle n'avait pas le 2e disque. Corrigé : on **préserve le fstab de l'hôte** et on strippe les lignes LVM quand il n'y a pas de 2e disque (mode natif).

**Q17 — [PIÈGE] "VM lente/qui rame après un restore", pourquoi ?**
> Amplification d'écriture LVM : N snapshots × copy-on-write → la VM devient I/O-bound (pas un problème RAM/CPU). Solution : `lvremove` des vieux snapshots pour soulager les I/O.

**Q18 — Que se passe-t-il si le restore est tué en plein milieu (kill -9, reboot) ?**
> J'ai un mécanisme de **self-heal** : un restore SIGKILL pendant la stabilisation laisse le job bloqué en "running" (bannière coincée). Le self-heal détecte ça dans le statut/active/history et le résout, avec un checkpoint précoce et un overlay plein écran côté UI. La progression est trackée dans des fichiers JSON donc elle **survit au reload, à la fermeture du navigateur et au redémarrage d'uvicorn**.

**Q19 — [PIÈGE] node_modules : pourquoi un cas spécial ?**
> Les backups **excluent node_modules** (trop volumineux). Mais un restore complet écraserait le dossier app et perdrait node_modules. Fix : un **symlink stable `/asguard/node_modules`** recréé par `_restore_application`, qui survit au restore.

**Q20 — Comment l'admin sait-il ce qui a été restauré ?**
> Historique des restores en **fichiers JSON plats** dans `restored_logs/` (pas en base, même logique d'indépendance). Format `restore_complete_TIMESTAMP_BACKUPID.json`.

---

## D. Cloud & Scheduling

**Q21 — Comment marche la planification des backups ?**
> Le déclencheur **principal est le crontab système** (cronie). À chaque démarrage Django, `BackupConfig.ready()` appelle `_sync_crontab()` pour synchroniser les tâches. Le cron fait un `curl` vers `POST /backup/schedule/run/<id>`. En **fallback**, quand on charge la page schedule, `_queue_due_schedule_catchups()` rattrape les runs manqués.

**Q22 — [PIÈGE] Pourquoi pas juste Celery beat pour le scheduling ?**
> Celery beat suppose un worker + beat toujours vivants. Le crontab système est plus robuste pour une appliance : il survit aux redémarrages applicatifs. Celery reste pour la tâche d'export cloud quotidienne.

**Q23 — [PIÈGE vécu] Un backup planifié a été silencieusement manqué, pourquoi ?**
> Bug de timezone : **cronie ignore la variable `TZ=` pour le scheduling**, plus un retry `{{}}` cassé et des tâches dupliquées dans le crontab root. Corrigé. C'est pour ça que j'ai ajouté le mécanisme de catchup en fallback.

**Q24 — Le cloud, comment ça marche ?**
> Après chaque backup, `async_upload_after_backup()` (classmethod, daemon thread) compresse le dossier en .tar.gz et l'upload vers un stockage **S3-compatible** via boto3. Providers supportés : Backblaze B2, Cloudflare R2, AWS S3, MinIO. Dédup par sha256, puis `apply_cloud_retention()` supprime les plus vieux au-delà de `max_cloud_copies`.

**Q25 — Où sont les credentials cloud ? C'est sécurisé ?**
> Dans le modèle `CloudStorageConfig` (table `backup_cloud_config`). Historique d'upload dans `BackupRecord`. [À vérifier/mentionner : chiffrement de la clé secrète — il y a un `ENCRYPT_KEY` dans settings.py.]

**Q26 — Retention : locale ET cloud ?**
> Oui, deux politiques. Locale via `schedule_config.json` (retention policy). Cloud via `max_cloud_copies`. Indépendantes.

**Q27 — Notifications ?**
> Deux canaux : **ntfy.sh** (push, topic dédié) et **email SMTP** (Gmail). Fonctions dans `notifications.py` : backup started/completed/scheduled, alertes firewall/WAF/IDS. Plus des notifs de cycle de vie VM (start/stop) via services systemd.

---

## E. Questions transverses / pièges de jury

**Q28 — Quelle est la partie la plus dure que tu as développée ?**
> Le restore complet en mode DR. Parce que ce n'est pas "copier des fichiers" : il faut gérer fstab, LVM, le réseau, node_modules, ne pas se couper soi-même (plan de contrôle), survivre à un kill en plein milieu, et tout ça sans casser le boot. Chaque cas limite a été un bug réel que j'ai reproduit et corrigé.

**Q29 — Comment tu testes un DRP ? Tu as cassé une vraie VM ?**
> Oui — checklist `DEMO_DR_CHECKLIST.md` : backup full frais → export .tar.gz hors VM → destruction VM → reconstruction sur VM vierge via `asguard-dr-restore`. Plus un **DR drill nocturne** automatisé avec un score (`/backup/dr-drill/latest`, seuil ≥ 80). Snapshot LVM de sécurité avant chaque test pour rollback.

**Q30 — Si je te dis "ton backup est inutile sans test de restore", tu réponds ?**
> Totalement d'accord, c'est exactement pourquoi j'ai le DR drill automatisé + la vérification d'intégrité sha256 + l'historique de restore. Un backup non testé est une hypothèse, pas une garantie.

**Q31 — Limites / améliorations possibles ?** (montre du recul)
> - Backup pas atomique au niveau global (par-composant seulement).
> - Pas encore de chiffrement at-rest des archives locales (seulement transport cloud).
> - Le thread async n'a pas de file d'attente : 2 backups simultanés possibles.
> - Pistes : backup incrémental/différentiel, signature GPG des archives, restore point-in-time DB via WAL.

---

## F. Déroulé de démo (15-20 min)

1. **Contexte** (1 min) : "Asguard est un firewall ; mon module garantit la continuité de service — backup, restore, DRP, monitoring, cloud."
2. **Dashboard backup** : état machine, services, dernière sauvegarde, alertes. Montre le WebSocket live (CPU/RAM bougent).
3. **Créer un backup** : type Safe → barre de progression par composant (prouve l'async + le job tracking).
4. **Aperçu d'un backup** : cartes "23 règles firewall, 5 NAT, 12 ZTNA, 28 WAF…" → prouve que ce sont des données réelles, pas juste des fichiers.
5. **Intégrité** : `verify-integrity` → status ok (sha256).
6. **Schedule** : montre une tâche planifiée + retention.
7. **Cloud** : onglet Cloud Storage, backup visible côté S3/B2.
8. **LE moment fort — Restore** : restaure un backup, montre l'overlay de progression, parle du self-heal ("même si je ferme le navigateur / reboot, le restore continue et le statut se rétablit").
9. **(Si tu oses) DR complet** : narration de la reconstruction sur VM vierge depuis le .tar.gz exporté.

> **Conseil démo** : prépare un backup frais AVANT la soutenance (cf. DEMO_DR_CHECKLIST.md, section pré-flight 1h avant). Ne crée jamais un full restore en live sans snapshot LVM de sécurité.

---

## H. Compléments — angles d'attaque experts (à maîtriser absolument)

**Q32 — [TRÈS PROBABLE] C'est quoi ton RPO et ton RTO ?**
> - **RPO (Recovery Point Objective)** = perte de données max tolérée = mon **intervalle de planification**. Avec un backup planifié quotidien, RPO = 24h ; je peux le descendre à l'heure via crontab. Le full backup contient le dump PostgreSQL, donc je perds au pire les données depuis le dernier backup.
> - **RTO (Recovery Time Objective)** = temps de remise en service. Restore en ligne (UI-safe) : quelques minutes, sans reboot. DR complet sur VM vierge : ~15-30 min (import .tar.gz + rejeu des 29 composants + stabilisation). Le snapshot LVM permet un rollback quasi-instantané si le restore échoue.
> Message clé : RPO piloté par la fréquence de schedule, RTO par le mode de restore choisi.

**Q33 — [FORCE sous-exploitée] Tes backups résistent-ils à un ransomware / une falsification ?**
> Oui, et c'est volontaire (`backend/backup/integrity.py`). À chaque backup j'écris un **manifeste signé** :
> - `MANIFEST.sha256` : un sha256 par fichier.
> - `MANIFEST.sig` : un **HMAC-SHA256** du manifeste, signé avec le secret de l'appliance (`ENCRYPT_KEY`).
> Un attaquant qui modifie un fichier puis régénère un faux manifeste **ne peut pas produire de signature valide sans le secret**. Donc avant tout restore je détecte : fichier altéré (hash différent), disparu, intrus, ou manifeste falsifié (HMAC invalide). Restaurer depuis un backup compromis propagerait l'attaque — je le bloque avant. C'est plus fort qu'un simple checksum : le checksum détecte la corruption accidentelle, le HMAC détecte la falsification **intentionnelle**.

**Q34 — [PIÈGE SÉCU — assume, ne bluffe pas] Tes secrets sont-ils chiffrés ? Le mot de passe DB ?**
> Réponse honnête + recul (le jury valorise la lucidité, pas le déni) :
> - La **clé secrète cloud S3** (`CloudStorageConfig.secret_access_key`) est aujourd'hui stockée **en clair** dans la table — c'est une limitation connue. Piste : la chiffrer avec Fernet en utilisant `ENCRYPT_KEY`.
> - Le **mot de passe PostgreSQL** est en clair dans `docker-compose.yml` — acceptable en dev/PFE, à externaliser dans un `.env` / secret Docker en prod.
> - Les **archives de backup ne sont pas chiffrées at-rest** localement (seulement intègres via HMAC) ; le transport cloud, lui, est en TLS.
> Ce que je NE dis pas : « tout est sécurisé ». Je montre que je connais mes trous et la remédiation. (Voir aussi Q31.)

**Q35 — [HISTOIRE DE ROBUSTESSE — vécu/corrigé] Après un restore, l'appli affichait "connection refused" sur PostgreSQL. Pourquoi ?**
> Course au démarrage (race condition). PostgreSQL tourne dans un conteneur Docker (`app-db-container`, port 5391). Un restore complet fait un **rollback du volume LVM** qui héberge les données pgdb et redémarre les services. Le runner post-restore relançait bien uvicorn + nginx, mais **pas le conteneur DB** ; et sa restart policy était `no`. Au login, le menu CLI interrogeait 5391 avant que la DB soit prête → "Connection refused".
> Fix en deux temps : (1) `restart: always` sur le conteneur → redémarrage auto au boot ; (2) une fonction **`force_db_recovery()`** dans `full_restore_runner.py`, appelée AVANT la reprise uvicorn, qui démarre le conteneur, ré-applique la policy, et **attend `pg_isready`** avant de continuer. La DB est désormais garantie up à la fin de tout restore.
> Leçon : « j'ai géré uvicorn et nginx mais j'avais oublié que ma DB est conteneurisée et dépend de Docker — l'ordre de dépendance au démarrage compte ».

**Q36 — [PIÈGE ATOMICITÉ] Si le restore de la DB est interrompu en plein milieu, je me retrouve avec une base à moitié vide ?**
> Non. Le `pg_restore` tourne en **`--single-transaction`** avec `--if-exists` : tout le drop+recreate est **une seule transaction**. Une interruption (restart conteneur, stall I/O) fait un **rollback** vers la base précédente au lieu de laisser une base à moitié droppée. Donc le restore DB est atomique tout-ou-rien — contrairement au backup global qui est, lui, par-composant (cf. Q10).

**Q37 — [CONCURRENCE] Que se passe-t-il si deux restores (ou deux backups) sont lancés en même temps ?**
> Pour le restore : un **lock de scheduler hors-LV** + le tracking par job_id évitent le chaos, et l'UI bloque pendant un restore en cours (overlay plein écran). Limitation assumée côté backup : le thread async n'a pas de file d'attente, donc 2 backups simultanés sont théoriquement possibles — c'est dans mes pistes d'amélioration (Q31). En pratique l'UI désactive le bouton pendant un job actif.

**Q38 — [POURQUOI DOCKER] Pourquoi PostgreSQL dans un conteneur et pas en natif sur l'appliance ?**
> Isolation + portabilité de version + le `pg_dump`/`pg_restore` se font proprement via `docker exec` avec la bonne version, indépendamment de la version pg de l'hôte. Le revers (que j'ai documenté) : ça ajoute une dépendance au démarrage à gérer après restore (cf. Q35). Les **données** vivent sur un volume bind-monté depuis le LV LVM, donc elles sont bien dans le périmètre snapshot/restore.

---

## G. Vocabulaire à manier avec assurance
RPO/RTO · DRP (Disaster Recovery Plan) · snapshot LVM copy-on-write · pg_dump format custom (`-F c`) · ASGI/WSGI · daemon thread · idempotence du restore · plan de contrôle vs plan de données · S3-compatible · retention policy · sha256 / intégrité · self-heal / reprise sur incident.
