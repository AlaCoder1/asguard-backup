# Mécanisme Backup & Restore — Asguard

Document technique préparé pour la revue de code.
Il répond précisément à quatre questions :

1. Comment une sauvegarde est-elle fabriquée, étape par étape, dans le code ?
2. Comment une restauration rejoue-t-elle cet état ?
3. Les configurations système (nginx, base de données, `/etc`) sont-elles toutes restaurables ?
4. Si une VM est détruite, comment reconstruit-on le même appareil sur une autre VM ?

---

## 0. Où le code est centralisé

| Rôle | Fichier |
|------|---------|
| **Moteur de sauvegarde** | `backend/backup/system_backup/full_backup_service.py` |
| **Moteur de restauration** | `backend/backup/system_backup/restore_service.py` |
| **Dump base de données** | `backend/backup/system_backup/backup_service.py` |
| **Snapshot DB par composant** | `backend/backup/component_db.py` |
| **Re-synchronisation post-restore** | `backend/backup/post_restore_resync.py` |
| **API REST (point d'entrée HTTP)** | `backend/backup/views.py` + `views_*.py` |
| **Routes** | `backend/backup/urls.py` |
| **Script de reprise après sinistre** | `scripts/asguard-dr-restore` |

Tout le stockage est **sur disque**, jamais en base : racine `/var/backups/asguard/`.

---

## 1. Comment se fait une sauvegarde

### 1.1 Trois portées possibles

| Type | Méthode (entrée) | Contenu |
|------|------------------|---------|
| **Safe** | `FullBackupService.create_safe_backup()` | 17 composants de configuration uniquement (firewall, vpn, nat…). Léger (~4,5 Mo). |
| **Full** | `FullBackupService.create_full_backup()` | 29 composants : safe + base de données + `/etc` complet + application + systemd + paquets + docker. |
| **Custom** | `FullBackupService.create_custom_backup(components)` | Sous-ensemble choisi par l'utilisateur. |

### 1.2 Les étapes, dans le code

`full_backup_service.py` :

1. **Création du dossier horodaté** — `create_full_backup()` (l.95) crée
   `/var/backups/asguard/backup_<AAAA-MM-JJ_HH-MM-SS>/` et un sous-dossier par composant.

2. **Exécution des « runners »** — `_run_backup_runners()` (l.279) parcourt la liste
   des composants. Chaque composant a sa fonction `_backup_<nom>()` qui renvoie un
   `ComponentResult` (statut, fichier produit, taille, sha256, durée).

3. **Capture de chaque composant** — selon le composant :
   - **Fichiers de config** → archive `tar.gz`. Exemples :
     - `firewall` → `/etc/nftables.conf` + `/etc/rules` (`_backup_firewall`, l.605)
     - `web` (nginx) → `/etc/nginx` en entier (`_backup_web`, l.686)
     - `vpn` → `/etc/openvpn`, `/etc/strongswan.d`, `/etc/swanctl`… (`_backup_vpn`, l.669)
     - `system_config` → **tout `/etc`** (`_backup_system_config`, l.791)
   - **Base de données** → `_backup_database()` (l.572) lance
     `pg_dump -F c` **dans le conteneur Docker `app-db-container`**, puis `docker cp`
     pour sortir le `.dump`.
   - **Données métier (lignes en base)** → après chaque runner, `_run_backup_runners`
     appelle `dump_component_db()` (`component_db.py`) et écrit un `component_db.json`
     par composant. C'est ce qui permet de restaurer *les règles NAT, routes, serveurs
     VPN…* telles qu'elles sont en base, pas seulement les fichiers.

4. **Finalisation** — `_finalize_backup()` (l.339) écrit `backup_metadata.json` :
   version de schéma, liste des composants avec statut/sha256/durée, statut global.
   Ce fichier est la « carte » que la restauration lira.

5. **Asynchrone côté API** — l'endpoint `POST /backup/create-full-backup`
   (`views.py`) ne bloque pas : il renvoie aussitôt `{status:"queued", job_id}` et
   lance le backup dans un thread. La progression est écrite dans
   `/var/backups/asguard/backup_jobs/<job_id>.json` et lue par
   `GET /backup/progress/<job_id>`.

**Résultat** : un dossier autonome contenant des `.tar.gz`, le dump SQL, les
`component_db.json` et `backup_metadata.json`. Il peut être copié, exporté, ou

---

## 2. Comment se fait une restauration

### 2.1 Quatre modes

| Mode | Méthode | Usage |
|------|---------|-------|
| **Safe** | `RestoreService.restore_full_safe()` | Rejoue les configs **sans** toucher à l'application Django. |
| **Complete** | `RestoreService.restore_full_complete()` | Rejoue tout, application incluse. |
| **UI-safe** | `RestoreService.restore_full_ui_safe()` | Restore depuis l'interface en excluant les composants « moteur » (`application`, `system_config`, `systemd_services`, `packages`, `docker_state`…) pour ne pas tuer l'appli pendant qu'elle tourne. Voir `UI_FULL_EXCLUDED_COMPONENTS` (l.24). |
| **Custom** | `RestoreService.restore_components(components)` | Sous-ensemble choisi. |

Tous convergent vers `_restore_full()` (l.67).

### 2.2 Les étapes, dans le code

`restore_service.py` — `_restore_full()` :

1. **Lecture de la carte** — ouvre `backup_metadata.json`, vérifie l'existence du
   backup, construit la liste des composants à rejouer (selon le mode).

2. **Restauration composant par composant** — pour chaque composant, appelle
   `_restore_<nom>()` :
   - **Vérification d'intégrité** — `_verify_component_file()` (l.302) compare le
     sha256 du fichier au sha256 noté dans la metadata.
   - **Extraction** — l'archive `tar.gz` est ré-extraite vers `/`.
   - **Validation avant activation** — exemples :
     - `web` → `nginx -t` avant de recharger nginx (`_restore_web`, l.627)
     - `firewall` → `nft -c -f` (validation) puis **`nft flush ruleset`** puis
       `nft -f` (`_restore_firewall`, l.480). Le `flush` évite la duplication des
       règles dans le noyau.
   - **Rechargement du service** — `_service_reload_if_exists()` / `_restart`.

3. **Restauration de la base** — `_restore_database()` (l.442) : `docker cp` du
   `.dump` dans le conteneur, puis `pg_restore -c` (`-c` = *clean* : supprime les
   objets existants avant de recréer). Le `-c` garantit qu'une donnée ajoutée
   **après** la sauvegarde disparaît bien à la restauration.

4. **Restauration des données métier** — `_restore_component_db()` (l.536) rejoue
   le `component_db.json` du composant : il vide les tables concernées puis recrée
   les lignes avec leurs clés primaires d'origine (`component_db.py`).

5. **Progression** — écrite dans `/var/backups/asguard/restore_jobs/<job_id>.json`,
   lue par `GET /backup/restore-full-status/<job_id>`.

6. **Aperçu préalable** — `GET /backup/<id>/restore-preview` indique, **avant** de
   lancer, ce qui sera restauré et ce qui sera ignoré (et pourquoi).

**Principe clé** : la restauration rejoue à la fois **les fichiers** (`/etc/*`) **et
la base** (dump SQL + `component_db.json`). Une règle ajoutée après le backup est
donc réellement supprimée — fichiers et base reviennent à l'état sauvegardé.

---

## 3. Les configs système sont-elles restaurables ? (question de l'évaluateur)

**Oui — vérifiable composant par composant :**

| Config | Sauvegarde | Restauration | Restaurable ? |
|--------|-----------|--------------|---------------|
| **nginx** (`/etc/nginx`) | `_backup_web` (l.686), dossier complet | `_restore_web` (l.627) : extraction → `nginx -t` → reload | ✅ Oui, avec test de validité |
| **Base de données** (contenu PostgreSQL) | `_backup_database` : `pg_dump -F c` | `_restore_database` : `pg_restore -c` | ✅ Oui, restauration propre (clean) |
| **`/etc` complet** | `_backup_system_config` (l.791) : `tar` de tout `/etc` | extraction vers `/` | ✅ Oui (mode Full/DR) |
| **Règles firewall** (`/etc/nftables.conf`, `/etc/rules`) | `_backup_firewall` + export DB `firewall_rules_db.json` | `_restore_firewall` : flush + reload + `_restore_firewall_rules_db` | ✅ Oui, fichiers **et** base |
| **VPN / IPsec** (`/etc/openvpn`, `/etc/swanctl`…) | `_backup_vpn` | `_restore_vpn` | ✅ Oui |
| **Services systemd personnalisés** | `_backup_systemd_services` | `_restore_systemd_services` | ✅ Oui |

Nuance honnête à présenter à l'évaluateur :
- Le **contenu** de la base PostgreSQL est intégralement sauvegardé/restauré.
- La **configuration du serveur PostgreSQL** (`postgresql.conf`, `pg_hba.conf`)
  vit dans le conteneur Docker `app-db-container` ; elle est couverte par le
  composant `docker_state` (images + volumes), pas par le dump SQL. Pour un
  appareil reconstruit, c'est le conteneur Docker qui réapplique sa config.

---

## 4. Reprise après sinistre — VM détruite ou crashée

Question de l'évaluateur : *« si une VM crashe, comment obtenir le même appareil
sur une autre VM ? »*

Trois niveaux de protection, du plus rapide au plus complet :

### Niveau 1 — Snapshot VMware (`views_vm_snapshot.py`)
Retour arrière de la **VM entière** en quelques secondes. Idéal pour annuler une
mauvaise manipulation. Limite : ne protège pas si l'hyperviseur lui-même tombe.

### Niveau 2 — Snapshot LVM
Snapshot bloc (Copy-on-Write) du volume logique de données. Permet de revenir à
un état figé sans dépendre de VMware.

### Niveau 3 — Reconstruction sur une VM neuve (le vrai DRP)

C'est la réponse à « la VM est détruite ». Procédure :

1. **Les sauvegardes ont survécu** — parce qu'elles sont répliquées **hors-site**
   VM disparaît, le dossier `backup_<TS>` est récupérable.

   dossier `backup_<TS>` dans `/var/backups/asguard/`.

3. **Lancer le script `scripts/asguard-dr-restore`** — il reconstruit l'appareil
   à l'identique en 13 phases :

   | Phase | Action |
   |-------|--------|
   | 1 | Preflight (droits, espace disque) |
   | 2 | Vérification d'intégrité (sha256) |
   | 3 | Mapping des interfaces réseau (la nouvelle VM peut avoir d'autres NIC) |
   | 4 | Réinstallation des paquets système |
   | 5 | Arrêt du stack applicatif (uvicorn, nginx, PostgreSQL) |
   | 6 | Restauration de `/etc` (`system_config`) |
   | 7 | Restauration des services systemd |
   | 8 | Restauration de l'application `/asguard/asguard` |
   | 9 | Restauration de la base PostgreSQL |
   | 10 | Restauration des configs appliance (firewall, vpn, …) |
   | 11 | Restauration Docker (images + volumes) |
   | 12 | Réapplication des règles firewall runtime |
   | 13 | Redémarrage |
   | 14 | `--verify` : contrôle post-restore après reboot |

   À la fin, la nouvelle VM **est** l'ancienne : mêmes règles, mêmes VPN, même
   base, mêmes services. La phase 3 gère le cas réaliste où la nouvelle VM n'a
   pas les mêmes noms d'interfaces réseau.

**Résumé pour l'évaluateur** : un appareil détruit se reconstruit à partir d'une
`asguard-dr-restore`. C'est ce qui fait du module un vrai **plan de reprise
après sinistre**, pas un simple outil d'archivage.

---

## 5. Organisation des API dans Swagger

Les ~70 endpoints `/backup/` étaient affichés en un seul bloc « backup » non trié.
Ils sont désormais regroupés par **étape du cycle de vie d'une sauvegarde**
(`backend/backup/swagger.py` + `SWAGGER_SETTINGS` dans `asguard/settings.py`) :

1. Création — 2. Catalogue & Archives — 3. Restauration —
4. VM Snapshot & DRP — 5. Logs & Audit.

Le préfixe numéroté force Swagger à les afficher dans l'ordre réel du processus.
La règle de classement est centralisée et automatique (déduite de l'URL) — aucun
décorateur à maintenir endpoint par endpoint.
