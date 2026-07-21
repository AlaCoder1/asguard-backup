# Asguard — Module Sauvegarde & Reprise après sinistre (DR)

Module de **sauvegarde, restauration et reprise après sinistre** pour l'appliance
de sécurité Asguard (pare-feu / firewall). Cette version livre le mécanisme de
backup/restore ; les modules complémentaires ont été retirés.

## Fonctionnalités

L'interface expose quatre onglets :

| Onglet | Rôle |
|--------|------|
| **Backups** | Création de sauvegardes (safe / full / DB) et restauration |
| **Historique Restores** | Journal des restaurations avec rapport de différences (avant/après) |
| **Snapshot** | Points de restauration LVM (retour arrière quasi instantané) |
| **Logs** | Timeline d'audit et journal système |

Points clés du mécanisme :

- **Trois types de sauvegarde** : `safe` (configuration seule, ~4,5 Mo),
  `full` (configuration + dump PostgreSQL + code applicatif + `/etc` + services
  systemd) et `db` (dump PostgreSQL brut).
- **Sauvegarde par composant** : 17 composants (firewall, VPN, IDS, proxy, NAT,
  routing, DHCP, WAF, ZTNA, VLAN, etc.) — fichiers de configuration **et** lignes
  correspondantes en base de données.
- **Restauration honnête** : un rapport de différences ligne par ligne
  (`ajoutés / supprimés / modifiés`) est produit après chaque restauration,
  calculé par comparaison de l'état de la base avant/après.
- **Anti-altération** : chaque sauvegarde est signée par un manifeste
  SHA-256 + HMAC, vérifié avant toute restauration.
- **Reprise après sinistre** : le script `scripts/asguard-dr-restore` reconstruit
  une appliance complète sur une VM neuve à partir d'une sauvegarde `full`.
- **Resynchronisation automatique** : après une restauration et à chaque
  démarrage, l'état de la base (règles nftables, NAT, routes) est réappliqué au
  noyau (`asguard-resync.service`).

## Stack technique

- **Backend** : Django 5.2 (Python 3.13), Django Channels / Daphne (WebSocket)
- **Frontend** : Vue 3, Vuetify, Element-Plus, ag-grid — build via webpack (`yarn build`)
- **Base de données** : PostgreSQL (conteneur Docker, port `5391`)
- **Reverse proxy** : Nginx

## Démarrage rapide

> Testé sur Arch Linux. Sur Arch, `pip install` direct est refusé
> (`externally-managed-environment`) — utiliser un environnement virtuel, ou
> l'option `--break-system-packages` comme dans la séquence complète ci-dessous.

```bash
git clone https://github.com/AlaCoder1/asguard-backup.git
cd asguard-backup

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d          # PostgreSQL (port 5391)
python manage.py migrate

yarn install
yarn build                    # génère le dossier static/

python manage.py runserver    # ou daphne / uvicorn en production
```

L'interface backup est accessible sur `http://127.0.0.1:8000/asguard/backup`
(le routeur front est monté sous la base `/asguard/`).

## Intégration dans une appliance Asguard existante

Si l'appliance Asguard (firewall) tourne déjà et qu'on veut simplement **y
ajouter le module de sauvegarde**, il n'est pas nécessaire de repartir de zéro.
Les autres applications (rules, nat, vlan, ipsec, proxy, ztna…) sont déjà
présentes — le module s'appuie dessus.

### 1. Copier les fichiers du module

```
backend/backup/                     → backend/backup/
src/views/backup/                   → src/views/backup/
src/store/modules/notifications.js  → src/store/modules/notifications.js
scripts/asguard-dr-restore          → scripts/ (script DR console)
scripts/asguard-resync.service      → scripts/ (unit systemd)
```

### 2. Câbler le backend (`asguard/settings.py`)

```python
INSTALLED_APPS = [
    # …
    'backend.backup',
]

REST_FRAMEWORK = {
    # …
    'DEFAULT_AUTO_SCHEMA_CLASS': 'backend.backup.swagger.BackupOrderedAutoSchema',
}

DATABASES = {
    'default': {
        # …
        'OPTIONS': {'connect_timeout': 15},   # évite un faux 500 pendant un snapshot LVM
    }
}
```

### 3. Câbler les routes (`asguard/urls.py`)

```python
from views.views import backup_page          # sert la page (SPA Vue)

urlpatterns = [
    # …
    path("backup/", backup_page),
    path("backup/", include("backend.backup.urls")),
]
```

Ajouter aussi la vue `backup_page` dans `views/views.py` (elle rend le template
qui charge l'application Vue).

### 4. Câbler le frontend

`src/router/router.js` :
```js
import BackupComponent from '../views/backup/index.vue';
// …
{ path: '/backup', component: BackupComponent },
```

`src/layouts/TheSidebar.vue` — ajouter l'entrée de menu :
```js
{ title: "sideBar.backup", href: "/backup", active: "backup" }
```

### 5. Dépendances Python (`requirements.txt`)

Le module ajoute deux paquets par rapport au firewall de base :

```
psutil==7.0.0
boto3==1.43.2
```

### 6. Appliquer

```bash
pip install psutil boto3
python manage.py migrate backup      # crée les tables du module
yarn build                           # recompile le frontend
```

> Les correctifs apportés à d'autres applications (`backend/vlan/functions.py`,
> `backend/ipsec/list_ipsec.py`, `backend/proxy/views.py`) sont des corrections
> firewall **optionnelles** — utiles mais non requises pour le module backup.

## Structure du dépôt

```
backend/          # Applications Django
  backup/         # Moteur de sauvegarde/restauration
    system_backup/  # Services : full_backup, restore, safe_restore, cloud, LVM…
    views.py        # API REST /backup/*
    urls.py         # Routes
  ...             # rules, nat, vlan, ipsec, proxy, ztna, network…
src/              # Frontend Vue 3
  views/backup/   # Interface du module (index.vue + components/)
asguard/          # Paquet Django (settings.py, urls.py, asgi.py, wsgi.py)
scripts/          # asguard-dr-restore, asguard-resync.service…
manage.py
docker-compose.yml
requirements.txt
```

## Stockage des sauvegardes

Les sauvegardes vivent sur le système de fichiers sous `/var/backups/asguard/`
(aucune dépendance à PostgreSQL pour les stocker). Chaque sauvegarde est un
dossier horodaté contenant `backup_metadata.json`, le manifeste signé et une
archive `.tar.gz` par composant.

## API principale (`/backup/`)

| Méthode | Route | Rôle |
|---------|-------|------|
| POST | `create-safe-backup` / `create-full-backup` | Sauvegarde asynchrone (retourne un `job_id`) |
| GET | `progress/<job_id>` | Progression d'une sauvegarde |
| GET | `getAllBackups` | Liste des sauvegardes |
| GET | `<id>/verify-integrity` | Vérification SHA-256 + HMAC |
| GET | `<id>/restore-preview` | Aperçu de ce qui sera restauré |
| POST | `<id>/restore` / `<id>/restore-full` | Restauration (safe / complète) |
| GET | `restore-full-status/<job_id>` | Progression d'une restauration |
| GET | `restore-history` | Historique des restaurations |
| GET / POST | `schedule` … | Planification et rétention |
| GET / POST | `vm-snapshot/*` | Snapshots LVM |

---

## Annexe — Initialisation complète de l'appliance

Séquence d'initialisation d'origine (génération de l'ISO / première mise en
service de l'appliance complète).

```bash
pip install -r requirements.txt --break-system-packages
yarn install
yarn build
docker-compose up -d
python manage.py makemigrations
python manage.py migrate

# collecte des fichiers statiques (Swagger UI) en production, avec DEBUG=False
python manage.py collectstatic

python manage.py create_wheel_group
python manage.py init_roles_db
python manage.py generate_user -u root -p root -r admin
python manage.py init_ASGUARD
python manage.py init_organisation -o Asguard
```

### Souscription

```bash
python manage.py init_features_for_subscription
python manage.py init_subscription
python manage.py add_feature_in_subscription -f <feature_name> -p <feature_price>
```

### Services

```bash
python manage.py init_services

# Squid
python manage.py create_files_squid
python manage.py init_conf_squid
python manage.py init_squid_conf_bd
iptables --flush

# NAT
python manage.py init_rules_nat

# IPsec
python manage.py start_ipsec

# Suricata
python manage.py init_suricata_file
sudo suricata-update
sudo python manage.py init_config_suricata

# Routing / réglages
python manage.py init_routing
python manage.py init_timezone_bd
python manage.py init_generale_settings_bd

# WAF
python manage.py init_waf_config

# Logs
python manage.py init_logs
python manage.py init_logrotate_script
python manage.py init_logrotate
python manage.py init_logrotate_timer
python manage.py init_log_firewall

# Interface réseau + réglages généraux
python manage.py init_interface_settings
python manage.py init_settings
```
