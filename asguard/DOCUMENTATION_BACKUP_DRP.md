# Documentation du module Backup & DRP - Asguard

Date de suivi : 8 mai 2026  
Projet : Asguard Firewall / Plateforme de securite et continuite  
Module : Backup, Restore, DRP, Monitoring, Alerting et Risk Center IA

## 1. Objectif du module

Le module **Backup & DRP** a pour objectif d'assurer la continuite de service de la plateforme Asguard en couvrant trois besoins principaux :

1. Sauvegarder les donnees et configurations critiques du firewall.
2. Restaurer rapidement l'etat du systeme apres incident, erreur humaine ou panne.
3. Superviser l'etat de la machine, des services et des sauvegardes afin d'anticiper les risques.

Le module ne se limite pas a une simple creation d'archives. Il fournit une interface complete de **gestion de reprise apres sinistre**, avec monitoring, alertes, planification, retention, cloud, snapshots VMware et une couche d'analyse intelligente via **AI Risk Center**.

## 2. Perimetre fonctionnel

Le module est integre dans l'interface **Backup & Restore** et contient les onglets suivants :

| Onglet | Role |
| --- | --- |
| Dashboard & Monitoring | Vue globale de l'etat backup, services, machine, stockage, synchronisation et alertes. |
| AI Risk Center | Analyse intelligente du risque en temps reel : VM, systeme, backup, services, firewall, intrusion. |
| Backups | Creation, listing, details, export, import, suppression et restore des backups. |
| Historique Restores | Historique des operations de restauration. |
| VM Snapshot | Gestion des snapshots VMware et retour arriere VM. |
| Schedule | Planification automatique des backups et politique de retention. |
| Cloud Storage | Synchronisation vers stockage compatible S3. |
| Alertes & Mailing | Configuration des notifications et alertes. |
| Logs | Espace reserve au suivi des logs du module. |

## 3. Architecture technique

### 3.1 Frontend

Le frontend est developpe en **Vue 3** avec **Vuetify**, **ApexCharts** et **Axios**.

Fichiers principaux :

| Fichier | Description |
| --- | --- |
| `src/views/backup/index.vue` | Conteneur principal du module Backup & DRP et gestion des onglets. |
| `src/views/backup/components/BackupDashboardMonitoring.vue` | Dashboard de monitoring, sante machine, services, sync et analytics. |
| `src/views/backup/components/BackupRiskCenter.vue` | Analyse IA du risque en temps reel. |
| `src/views/backup/components/Backups.vue` | Creation, listing, details, restore, import/export et suppression. |
| `src/views/backup/components/VmSnapshot.vue` | Interface de gestion des snapshots VMware. |
| `src/views/backup/components/BackupSchedule.vue` | Planification et retention. |
| `src/views/backup/components/BackupCloud.vue` | Configuration et synchronisation cloud. |
| `src/views/backup/components/BackupAlertsMailing.vue` | Configuration alerting. |
| `src/middleware/backup.js` | Point d'entree Vue du module. |

### 3.2 Backend

Le backend est base sur **Django** et expose des endpoints REST dedies au module backup.

Fichiers principaux :

| Fichier | Description |
| --- | --- |
| `backend/backup/urls.py` | Declaration des routes API du module. |
| `backend/backup/views.py` | Endpoints principaux : dashboard, backup, restore, schedule, cloud, alertes. |
| `backend/backup/views_vm_snapshot.py` | Endpoints specifiques aux snapshots VMware. |
| `backend/backup/models.py` | Modeles cloud et historique backup. |
| `backend/backup/notifications.py` | Notifications email, ntfy, Telegram et alertes in-app. |
| `backend/backup/system_backup/backup_service.py` | Service de backup standard. |
| `backend/backup/system_backup/full_backup_service.py` | Service de backup complet. |
| `backend/backup/system_backup/restore_service.py` | Restore complet. |
| `backend/backup/system_backup/safe_restore_service.py` | Restore safe sans partie applicative sensible. |
| `backend/backup/system_backup/export_import_service.py` | Export/import d'archives. |
| `backend/backup/system_backup/cloud_storage.py` | Integration S3-compatible. |
| `backend/backup/system_backup/snapshot_service.py` | Operations VMware snapshot. |

### 3.3 Communication temps reel

Deux mecanismes sont utilises :

1. **Polling HTTP** : rafraichissement periodique des donnees via `/backup/dashboard-overview`.
2. **WebSocket** : recuperation live des metriques machine via `/ws/data/`.

Cela permet d'afficher en quasi temps reel :

- CPU
- RAM
- uptime
- load average
- statut VM
- etat des services critiques
- etat des disques
- alertes actives

## 4. Fonctionnalites detaillees

## 4.1 Dashboard & Monitoring

Le dashboard fournit une vue de pilotage du module DRP.

Fonctionnalites :

- Etat du dernier backup.
- Score de sante du dernier backup.
- Nombre total de backups.
- Stockage utilise et espace restant.
- Prochain backup planifie.
- Services critiques actifs/inactifs.
- Etat de la machine : CPU, RAM, load average, uptime, disques.
- Etat de la VM : detection VMware/KVM/VirtualBox/Hyper-V ou machine physique.
- Analyse de synchronisation entre systeme reel et base de donnees.
- Alertes actives avec priorisation.

Endpoint principal :

```http
GET /backup/dashboard-overview
```

Cet endpoint construit un payload global contenant :

- `cards` : indicateurs backup, services, stockage, prochaine execution.
- `integrity` : integrite du dernier backup.
- `sync` : verification de coherence systeme/base.
- `charts` : donnees graphiques.
- `live_metrics` : metriques machine.
- `services` : etat des services et checks runtime.
- `resources` : disques systeme et backup.
- `alerts` : alertes actives.

## 4.2 Creation de backups

Le module supporte plusieurs types de sauvegardes.

| Type | Description |
| --- | --- |
| DB Backup | Sauvegarde de la base de donnees. |
| Safe Backup | Sauvegarde des composants d'administration et de securite sans partie applicative complete. |
| Full Backup | Sauvegarde complete du systeme Asguard. |
| Custom Backup | Sauvegarde selective de composants choisis. |

Endpoints :

```http
POST /backup/create-db-backup
POST /backup/create-safe-backup
POST /backup/create-full-backup
POST /backup/create-custom-backup
GET  /backup/components
GET  /backup/progress/<job_id>
```

Techniques utilisees :

- Creation de jobs asynchrones.
- Suivi de progression par job id.
- Decoupage par composants.
- Generation de metadonnees pour chaque archive.
- Calcul d'integrite et de statut par composant.
- Affichage UI du composant courant et du resultat final.

## 4.3 Listing, details, export/import et suppression

L'onglet **Backups** permet :

- Lister toutes les sauvegardes.
- Filtrer et paginer.
- Voir les details d'un backup.
- Voir l'etat des composants sauvegardes.
- Exporter une archive.
- Importer une archive externe.
- Supprimer un backup.

Endpoints :

```http
GET    /backup/getAllBackups
GET    /backup/<backup_id>/details
GET    /backup/<backup_id>/export
POST   /backup/import
DELETE /backup/<backup_id>/delete
```

Caracteristiques techniques :

- Normalisation des metadonnees.
- Verification des composants reussis, echoues ou ignores.
- Support d'archives importees.
- Export pour transfert ou conservation hors machine.

## 4.4 Restore

Le module propose trois modes de restauration.

| Mode | Description |
| --- | --- |
| Safe Restore | Restauration controlee des composants critiques sans restaurer l'application complete. |
| Full Restore | Restauration complete avec suivi de job. |
| Custom Restore | Restauration selective des composants choisis. |

Endpoints :

```http
POST /backup/<backup_id>/restore
POST /backup/<backup_id>/restore-full
POST /backup/<backup_id>/restore-components
GET  /backup/restore-full-status/<job_id>
GET  /backup/restore-history
```

Techniques utilisees :

- Jobs asynchrones pour eviter de bloquer l'interface.
- Polling de progression.
- Verification post-restore.
- Resume des composants restaures, echoues ou ignores.
- Stabilisation systeme apres restore.
- Historique des restaurations.

Le restore est accompagne d'une verification finale afin de confirmer que les composants sont bien revenus dans un etat exploitable.

## 4.5 VM Snapshot

L'onglet **VM Snapshot** ajoute une couche DRP au niveau virtualisation.

Fonctionnalites :

- Detection de l'environnement VMware.
- Test de connexion.
- Liste des snapshots.
- Verification des snapshots.
- Creation de snapshot manuel.
- Creation de snapshot avant backup complet.
- Restore d'une VM depuis snapshot.
- Suppression de snapshot.
- Annulation de job snapshot.
- Suivi des jobs en cours.

Endpoints :

```http
GET    /backup/vm-snapshot/info
POST   /backup/vm-snapshot/test-connection
GET    /backup/vm-snapshot/list
POST   /backup/vm-snapshot/verify
POST   /backup/vm-snapshot/create
GET    /backup/vm-snapshot/progress/<job_id>
PUT    /backup/vm-snapshot/config
POST   /backup/vm-snapshot/<snap_id>/restore
GET    /backup/vm-snapshot/restore-status/<job_id>
DELETE /backup/vm-snapshot/<snap_id>/delete
POST   /backup/vm-snapshot/<job_id>/cancel
```

Techniques utilisees :

- Service backend dedie `snapshot_service.py`.
- Jobs asynchrones.
- Cache et verification explicite.
- Estimation du temps de creation.
- Gestion du cas ou la VM redemarre pendant un restore.
- Interface de progression dediee.

## 4.6 Planification et retention

L'onglet **Schedule** permet d'automatiser les backups.

Fonctionnalites :

- Creation de taches planifiees.
- Choix du type de backup.
- Execution manuelle d'une tache.
- Suppression d'une tache.
- Gestion du fuseau horaire.
- Application d'une politique de retention.
- Nettoyage des anciennes sauvegardes.

Endpoints :

```http
GET    /backup/schedule
POST   /backup/schedule/task
DELETE /backup/schedule/task/<task_id>
POST   /backup/schedule/run/<task_id>
PUT    /backup/schedule/retention
POST   /backup/schedule/apply-retention
PUT    /backup/schedule/timezone
```

Techniques utilisees :

- Configuration persistante JSON.
- Calcul de prochaine execution.
- Detection de taches manquees.
- Rattrapage automatique si la machine etait indisponible.
- Retention basee sur nombre, age et importance des backups.

## 4.7 Cloud Storage

Le module supporte la synchronisation vers des stockages compatibles S3.

Providers prevus :

- Backblaze B2
- Cloudflare R2
- AWS S3
- MinIO
- Custom S3-compatible

Fonctionnalites :

- Configuration des credentials.
- Test de connexion.
- Upload automatique apres backup.
- Synchronisation manuelle d'un backup.
- Listing des backups cloud.
- Historique cloud.
- Option DB backup cloud-only.
- Limitation du nombre de copies cloud.

Endpoints :

```http
GET/PUT /backup/cloud/config
POST    /backup/cloud/test
GET     /backup/cloud/backups
POST    /backup/cloud/sync/<backup_id>
GET     /backup/cloud/history
```

Techniques utilisees :

- API S3-compatible.
- Service dedie `cloud_storage.py`.
- Mode auto-upload.
- Historisation dans le modele `BackupRecord`.
- Gestion des erreurs cloud.

## 4.8 Alertes et notifications

Le module dispose d'un systeme d'alerte multi-canal.

Canaux :

- In-app alerts.
- Toasts UI.
- Badge de notification.
- Email.
- ntfy.
- Telegram test endpoint.

Types d'alertes :

- Backup demarre.
- Backup termine.
- Backup echoue.
- Backup planifie.
- Backup manque puis rattrape.
- Restore demarre.
- Restore termine.
- Snapshot VM restore.
- Risque ressources VM.
- Service critique arrete.

Endpoints :

```http
GET  /backup/in-app-alerts
POST /backup/in-app-alerts/mark-read
POST /backup/telegram-test
```

Technique importante :

Les alertes in-app sont persistees dans un fichier JSON afin d'etre visibles dans l'interface meme apres rafraichissement. Le header de l'application lit ces alertes et affiche un badge/notification.

## 4.9 AI Risk Center

L'onglet **AI Risk Center** est la couche intelligente du module.

Objectif :

Transformer les signaux techniques du module Backup & DRP en un score de risque lisible, explicable et exploitable.

Signaux utilises :

- CPU live.
- RAM live.
- Load average.
- Disque systeme `/`.
- Disque backup.
- Uptime.
- Etat VM.
- Services critiques.
- Alertes actives.
- Sante du dernier backup.
- Drift/synchronisation entre systeme reel et base.

Sources :

```http
GET /backup/dashboard-overview
WS  /ws/data/
```

Le Risk Center effectue :

- Un refresh HTTP toutes les 15 secondes.
- Une ecoute WebSocket pour les metriques live.
- Un recalcul automatique du score.
- Une visualisation radar des familles de risques.
- Une courbe temporelle CPU/RAM/Risk VM.
- Une surface d'exposition par categorie.
- Une explication du score.
- Un playbook d'actions recommandees.

Scores calcules :

| Score | Donnees utilisees |
| --- | --- |
| VM crash | CPU, RAM, disque systeme, load average. |
| Systeme | Ratio services OK / services critiques. |
| Backup/DRP | Health du dernier backup, statut, espace disque backup. |
| Firewall/Intrusion | Alertes actives, drift de synchronisation, coherence systeme/base. |
| Global Risk Score | Combinaison ponderee des scores precedents. |

Important :

Le modele est actuellement un **modele heuristique explicable**, pas encore un modele ML entraine sur dataset. Il est volontairement transparent pour le PFE : chaque score peut etre justifie par une metrique visible.

Exemple :

Si la VM est confortable avec CPU 1%, RAM 62%, disque 59% et charge legere, le score VM doit rester faible. Si le score global est eleve, le Risk Center explique que le risque vient d'un autre signal : backup degrade, service arrete, stockage, alerte active ou drift de synchronisation.

## 5. Monitoring et detection proactive

Le monitoring du module repose sur plusieurs couches :

1. **Metriques machine live**
   - CPU
   - RAM
   - uptime
   - load average

2. **Checks runtime**
   - Detection de virtualisation.
   - Etat du filesystem `/`.
   - Etat du volume backup.
   - Services systemd critiques.

3. **Verification DRP**
   - Dernier backup.
   - Integrite.
   - Couverture des composants critiques.
   - Stockage disponible.

4. **Verification de coherence**
   - Comparaison entre base de donnees et systeme reel.
   - Firewall/nftables.
   - NAT.
   - VPN.
   - IDS/IPS.
   - Proxy.
   - Services.
   - Reseau.

5. **Risk Center**
   - Agregation intelligente.
   - Score global.
   - Explication.
   - Actions recommandees.

## 6. Techniques et technologies utilisees

| Categorie | Technologies / techniques |
| --- | --- |
| Backend | Django, Django REST, endpoints HTTP, jobs asynchrones, fichiers JSON de configuration. |
| Frontend | Vue 3, Vuetify, Axios, ApexCharts, composants modulaires. |
| Temps reel | WebSocket `/ws/data/`, polling HTTP, refresh automatique. |
| Backup | Archives par composants, metadonnees, hash, progress jobs. |
| Restore | Safe restore, full restore, custom restore, verification post-restore. |
| Cloud | API S3-compatible, Backblaze B2, Cloudflare R2, AWS S3, MinIO. |
| VM DRP | VMware snapshot, restore snapshot, jobs asynchrones, verification. |
| Monitoring | CPU, RAM, uptime, load average, disques, services systemd. |
| Alerting | Email, ntfy, Telegram test, in-app alerts, toast UI, badges. |
| IA | Score heuristique explicable, aggregation multi-signaux, playbook intelligent. |

## 7. Endpoints principaux

### Dashboard

```http
GET /backup/dashboard-overview
```

### Backup

```http
GET  /backup/getAllBackups
POST /backup/create-db-backup
POST /backup/create-full-backup
POST /backup/create-safe-backup
POST /backup/create-custom-backup
GET  /backup/components
GET  /backup/progress/<job_id>
```

### Restore

```http
POST /backup/<backup_id>/restore
POST /backup/<backup_id>/restore-full
POST /backup/<backup_id>/restore-components
GET  /backup/restore-full-status/<job_id>
GET  /backup/restore-history
```

### Gestion des archives

```http
GET    /backup/<backup_id>/details
GET    /backup/<backup_id>/export
POST   /backup/import
DELETE /backup/<backup_id>/delete
```

### Schedule

```http
GET    /backup/schedule
POST   /backup/schedule/task
DELETE /backup/schedule/task/<task_id>
POST   /backup/schedule/run/<task_id>
PUT    /backup/schedule/retention
POST   /backup/schedule/apply-retention
PUT    /backup/schedule/timezone
```

### Cloud

```http
GET/PUT /backup/cloud/config
POST    /backup/cloud/test
GET     /backup/cloud/backups
POST    /backup/cloud/sync/<backup_id>
GET     /backup/cloud/history
```

### VM Snapshot

```http
GET    /backup/vm-snapshot/info
POST   /backup/vm-snapshot/test-connection
GET    /backup/vm-snapshot/list
POST   /backup/vm-snapshot/verify
POST   /backup/vm-snapshot/create
GET    /backup/vm-snapshot/progress/<job_id>
PUT    /backup/vm-snapshot/config
POST   /backup/vm-snapshot/<snap_id>/restore
GET    /backup/vm-snapshot/restore-status/<job_id>
DELETE /backup/vm-snapshot/<snap_id>/delete
POST   /backup/vm-snapshot/<job_id>/cancel
```

### Alertes

```http
GET  /backup/in-app-alerts
POST /backup/in-app-alerts/mark-read
POST /backup/telegram-test
```

## 8. Scenarios de demonstration pour la reunion

### Scenario 1 : supervision rapide

1. Ouvrir **Backup & DRP > Dashboard & Monitoring**.
2. Montrer l'etat du dernier backup.
3. Montrer la sante machine : CPU, RAM, disques, load average.
4. Montrer les services critiques.
5. Montrer les alertes actives.

### Scenario 2 : creation backup

1. Aller dans **Backups**.
2. Lancer un safe backup ou full backup.
3. Montrer le suivi de progression.
4. Ouvrir les details du backup.
5. Expliquer les composants et le score de sante.

### Scenario 3 : restore

1. Selectionner un backup.
2. Ouvrir le restore.
3. Expliquer les modes : safe, complete, custom.
4. Lancer un restore de demonstration si l'environnement le permet.
5. Montrer le monitoring de progression et verification finale.

### Scenario 4 : AI Risk Center

1. Ouvrir **AI Risk Center**.
2. Montrer le score global.
3. Montrer que le score est base sur les vraies metriques live.
4. Expliquer la partie VM : CPU/RAM/load/disques.
5. Expliquer le radar et les actions recommandees.

### Scenario 5 : VMware snapshot

1. Ouvrir **VM Snapshot**.
2. Tester la connexion.
3. Lister les snapshots.
4. Creer un snapshot.
5. Expliquer le restore snapshot comme mecanisme DRP rapide.

## 9. Points forts du module

- Module complet de continuite de service.
- Interface unifiee pour backup, restore, monitoring et alerting.
- Gestion de plusieurs types de backup.
- Restore progressif et verifie.
- Integration cloud compatible S3.
- Gestion VMware snapshot.
- Monitoring temps reel via WebSocket.
- Alertes multi-canal.
- AI Risk Center explicable, utile pour decision rapide.
- Architecture modulaire, separant UI, API, services backend et stockage.

## 10. Limites actuelles et ameliorations possibles

### Limites

- Le Risk Center utilise actuellement un modele heuristique explicable, pas encore un modele ML entraine.
- Les logs ont un onglet dedie mais peuvent etre enrichis avec recherche avancee.
- Le restore complet depend de l'environnement systeme et doit etre teste avec prudence.
- Les snapshots VMware necessitent une configuration correcte de l'hote et de `vmrun`.

### Evolutions proposees

1. Ajouter un dataset historique pour entrainer un modele ML.
2. Ajouter une prediction de panne basee sur series temporelles CPU/RAM/load.
3. Ajouter un scoring par criticite metier des services.
4. Ajouter une exportation PDF automatique des rapports DRP.
5. Ajouter une matrice RTO/RPO.
6. Ajouter un simulateur d'incident pour tester le plan de reprise.
7. Ajouter une page d'audit de conformite backup.

## 11. Resume pour l'encadrant

Le module Backup & DRP d'Asguard assure la sauvegarde, la restauration et la supervision proactive de la plateforme. Il combine des mecanismes classiques de backup/restore avec des fonctions avancees : monitoring live, alerting, snapshots VMware, stockage cloud, planification, retention et Risk Center IA.

La contribution principale est l'integration d'un workflow DRP complet dans une interface unique, avec une couche intelligente capable de transformer les metriques techniques en score de risque comprehensible et actionnable.

Le module est donc a la fois :

- un outil de sauvegarde,
- un outil de restauration,
- un tableau de bord de supervision,
- un systeme d'alerte,
- et un assistant d'analyse de risque pour anticiper les incidents.

