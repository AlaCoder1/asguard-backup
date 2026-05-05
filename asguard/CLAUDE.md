# Asguard — Architecture Reference

Firewall/security appliance: Django 5.2 backend + Vue 3 frontend + WebSocket (Channels/Daphne).

## Stack
- **ASGI**: Daphne 4.2.1 (Django Channels) — supports WebSocket
- **Frontend**: Vue 3 + Vite, Pinia, Vue Router, Element-Plus, ag-grid
- **DB**: PostgreSQL @ localhost:5391, user=postgres, db=postgres
- **Cache/Queue**: Redis @ localhost:6379/0 (Celery broker)
- **Reverse proxy**: Nginx
- **Python**: 3.13 | **Django**: 5.2.5

## Key Config Files
| File | Purpose |
|------|---------|
| `asguard/settings.py` | Django settings (DB, apps, channels, celery) |
| `asguard/urls.py` | Root URL routing |
| `asguard/asgi.py` | ASGI + WebSocket routing |
| `.env` | DB creds, email, IP config |
| `/etc/asguard/watchdog_config.json` | Notifications (email + ntfy.sh), service watchdog |
| `/var/backups/asguard/schedule_config.json` | Backup schedule tasks + retention policy |

## Django Apps (`backend/`)
| App | Role |
|-----|------|
| `authentification` | Login, JWT, sessions |
| `dashboard` | System metrics, WebSocket consumers |
| `backup` | Backup/restore engine, scheduler, retention |
| `rules` | nftables firewall rules |
| `nat` | DNAT/SNAT/1-to-1 |
| `gateway` | Gateway policies |
| `ids_ips` | Suricata IDS/IPS |
| `waf` | ModSecurity WAF |
| `openvpn` / `openvpn_monitoring` | OpenVPN mgmt + WebSocket status |
| `ipsec` / `ipsecmonitoring` | IPsec VPN + WebSocket status |
| `proxy` | Squid proxy + logs |
| `network` | Interfaces, IP config |
| `routing` | Static routes |
| `vlan` / `vxlan` | Layer 2 tunneling |
| `sdwan` | SD-WAN policies |
| `ztna` | Zero-Trust Network Access |
| `managementUsers` | Custom User model (AUTH_USER_MODEL) |
| `managementCertificates` | PKI/CA |
| `managementLogs` | Log aggregation WebSocket |
| `server_dhcp4` | DHCPv4 server |
| `LdapServer` | LDAP/AD integration |
| `settings` | System settings |
| `subscription` | License management |
| `tasks` | Scheduled tasks, log rotation |

## Auth
- Custom user model: `managementUsers.User`
- Auth backends: Token + Session
- REST: `IsAuthenticated` default

## WebSocket Endpoints
| Path | Consumer |
|------|----------|
| `/ws/data/` | DashboardConsumer (CPU, RAM, metrics — 1s interval) |
| `/ws/vpnmonitoring/` | OpenVPN stats |
| `/ws/ipsecmonitoring/` | IPsec stats |
| `/ws/logs/` | System logs |
| `/ws/logs_suricata/` | Suricata IDS/IPS alerts |
| `/ws/logs_squid_*` | Proxy logs |
| `/ws/firewall_log/` | Firewall logs |
| `/ws/logs_ztna_*` | ZTNA logs |

## Backup Storage — 100% Filesystem (ZERO PostgreSQL)
**Root**: `/var/backups/asguard/` (238 MB total)

```
/var/backups/asguard/
  backup_safe_YYYY-MM-DD_HH-MM-SS/   ← safe backup (config only, ~4.5 MB)
    backup_metadata.json              ← schema v4.1, components status, sha256, durations
    firewall/firewall_rules.tar.gz
    vpn/vpn_configs.tar.gz
    ids/suricata.tar.gz
    proxy/squid.tar.gz
    network/network.tar.gz
    certificates/certificates.tar.gz
    routing/routing_summary.json
    nat/nat_summary.json
    dhcp/dhcp.tar.gz
    waf/waf.tar.gz
    ztna/ztna.tar.gz
    ipsec_detailed/ipsec_detailed.tar.gz
    vlan/ vxlan/ sdwan/ gateway/ double_mask/  ← each .tar.gz
  backup_YYYY-MM-DD_HH-MM-SS/          ← full backup (includes DB dump)
  asguard_db_YYYY-MM-DD_HHMMSS.dump    ← raw pg_dump output
  schedule_config.json                  ← schedule tasks + retention policy
  restore_jobs/                         ← restore job progress (JSON per job)
    {job_id}.json: {job_id, backup_id, status, components_progress, components_order, progress_pct, done, total, current_component, result}
  backup_jobs/                          ← async backup job progress (JSON per job)
    {job_id}.json: {job_id, backup_id, backup_type, status, components_progress, progress_pct, done, total, current_component, result}
  restored_logs/                        ← restore history JSON files
    restore_complete_TIMESTAMP_BACKUPID.json
    logs/
  dashboard_last_sync_summary.json     ← last config drift analysis result
```

**Safe backup components** (17 total): firewall, vpn, ids, proxy, network, certificates,
routing, nat, dhcp, waf, ztna, ipsec_detailed, vlan, vxlan, sdwan, gateway, double_mask

**Restore history**: flat JSON files in `restored_logs/` — NOT in PostgreSQL.
**Dashboard drift**: `dashboard_last_sync_summary.json` — scope: services, firewall, network, nat, vpn, ids_ips, proxy.

## Backup System
**Key constants** in `backend/backup/views.py`:
```python
SCHEDULE_CONFIG_FILE = Path("/var/backups/asguard/schedule_config.json")
_BACKUP_ROOT         = Path("/var/backups/asguard")
TASK_ENDPOINT_MAP    = {"safe_backup": "create-safe-backup", "full_backup": "create-full-backup", "db_backup": "create-db-backup"}
```

**Backup modules** (`backend/backup/system_backup/`):
- `full_backup_service.py` — `FullBackupService` (safe/full/custom backup engine)
- `backup_service.py` — `SystemBackupService.create_db_backup()` (pg_dump via Docker `app-db-container`)
- `restore_service.py` — Full restore
- `safe_restore_service.py` — Config-only restore
- `export_import_service.py` — Archive export/import
- `../notifications.py` — ntfy.sh + email alerts

**Backup API** (`/backup/`):
- `GET /backup/schedule` — fetch tasks (also triggers missed-run catchup)
- `POST /backup/schedule/task` — create task (calls `_sync_crontab`)
- `POST /backup/schedule/run/<id>` — run task (called by crontab via curl)
- `POST /backup/create-safe-backup` / `create-full-backup` — **ASYNC**: returns `{status:"queued", job_id}` immediately, runs backup in background thread writing progress to `/var/backups/asguard/backup_jobs/{job_id}.json`
- `GET /backup/progress/<job_id>` — poll backup job progress (components_progress, progress_pct, status)
- `GET /backup/restore-full-status/<job_id>` — poll restore job progress (now includes components_progress, components_order, progress_pct per component)
- `POST /backup/create-db-backup` — synchronous DB dump

**Crontab sync**: `backend/backup/apps.py` `BackupConfig.ready()` calls `_sync_crontab()` on every Django startup.

**Schedule catchup**: `_queue_due_schedule_catchups()` is called in `get_schedule` — runs missed tasks when page is loaded. **Only as fallback** — crontab is the primary trigger.

## Notification System
**Config source**: `/etc/asguard/watchdog_config.json` → `notifications`

Current config:
- **ntfy.sh**: enabled, topic = `asguard-ala-firewall-2024` → `https://ntfy.sh/asguard-ala-firewall-2024`
- **Email**: smtp.gmail.com:587, user=daasala58@gmail.com, recipients=[ala.daas@esprit.tn, daasala58@gmail.com]

**Functions** in `backend/backup/notifications.py`:
```python
notify_backup_started(backup_type, backup_id="")
notify_backup_completed(backup_type, backup_id, success, duration_s=None, message="")
notify_backup_scheduled(task_name, backup_type, cron_expr="")
notify_firewall_rule_change(action, rule_desc, interface, policy, rule_type)
notify_waf_alert(new_count, samples=None)
notify_ids_alert(new_count, sample_log="")
ntfy_test()
```

## VM Lifecycle Notifications
**Script**: `/usr/local/bin/asguard-vm-notify.sh started|stopped`
- Reads ntfy topic from `/etc/asguard/watchdog_config.json`
- Sends push notification on VM start/stop

**Systemd services** (both enabled):
- `asguard-vm-start-notify.service` — fires after `network-online.target` on boot
- `asguard-vm-stop-notify.service` — fires before `shutdown.target`

## Frontend Structure (`src/`)
```
src/
  views/          # Feature pages (backup/, dashboard/, firewall/, ipsec/, openvpn/, ...)
  components/     # Reusable UI (VButton, VInput, modals/)
  layouts/        # layout.vue, TheHeading, TheSidebar, TheFooter
  router/         # router.js (base: /asguard/, history mode)
  store/          # Pinia: modules/auth.js, modules/modal.js, notifications.js
  middleware/     # Route guards
  locales/        # i18n (en, fr)
```

## Layout Architecture
- **`layout.vue`** wraps all pages: `TheHeadingVue` (top bar) + `TheSidebarVue` + `<slot name="content">`
- **`#toolbar-status` slot** in `layout.vue` — inject a pill/badge into the grey page toolbar next to the title (used by backup/index.vue for LIVE status)
- **Vuetify `v-list-item` nesting gotcha**: never nest `v-list-item` inside `v-list-item` for custom layouts — Vuetify overrides display and breaks flex alignment. Use a plain `<div>` instead.
- **Sidebar badge pattern**: wrap `sidebarTitle + badge` in `.sidebar-title-group { display: inline-flex; align-items: center; gap: 6px; }` so badge stays adjacent to text, not pushed to edge.

## Pinia Notifications Store (`src/store/modules/notifications.js`)
- **`useNotifStore`** — shared state updated by `TheHeading.vue` every 60s from `/backup/dashboard-overview`
- Fields: `count` (alert count), `autoBackupOn` (any enabled scheduled task), `notificationsConfigured` (ntfy or email enabled in watchdog_config.json)
- Read by: `TheSidebar.vue` (badge + Monitor footer), `backup/index.vue` (LIVE pill in toolbar)

## TheSidebar.vue — Key Patterns
- Items array in `data()` — add `active: 'backup'` etc. to identify items for conditional rendering
- **Monitor actif footer**: absolute-positioned at bottom, shows LIVE clock (updated every 1s via `setInterval`) + Auto-backup ON/OFF pill
- **Rail mode** (icons only): separate `v-else` branch renders icons with badge at `top:2px right:2px`
- Clock interval started in `mounted()`, cleared in `beforeUnmount()`

## Key Backup Vue Components
| File | Role |
|------|------|
| `src/views/backup/index.vue` | Parent with 8 tabs (Dashboard, Backups, Restores, VM Snapshot, Schedule, Cloud Storage, Alertes, Logs) |
| `src/views/backup/components/BackupSchedule.vue` | Schedule CRUD, fetches on mount (triggers catchup) |
| `src/views/backup/components/BackupDashboardMonitoring.vue` | Dashboard, polls every 45s, connects `/ws/data/` |
| `src/views/backup/components/Backups.vue` | List + restore, polls 2.5s during restore |
| `src/views/backup/components/BackupCloud.vue` | Cloud Storage monitoring UI (stats, file list, sync, config, DB history) |

## BackupCloud.vue — Tab "Cloud Storage"
Sections:
- **Topbar**: connection status dot, provider name, endpoint, test + refresh + config buttons
- **Stats row**: files in cloud, total size, last upload time, auto-upload on/off
- **Config panel** (slide-in): form for provider/endpoint/keys/bucket/region/prefix/toggles
- **Cloud backups table**: filename, size, upload date, type badge (Safe/Full/DB) — from `GET /backup/cloud/backups`
- **DB History panel**: BackupRecord from PostgreSQL — `GET /backup/cloud/history`
- **Manual sync panel**: list local backups, push individually to cloud — `POST /backup/cloud/sync/<id>`

Design follows BackupSchedule.vue CSS patterns (bs-* → bc-* classes).
Build tool: `yarn build` (webpack-encore) in `/asguard/asguard/`.

## Utils (`utils/`)
- `constant_variables.py` — Standard error/success message templates
- `utils_command_system.py` — Shell command execution
- `utils_address.py` — IP address helpers
- `errors_utils.py` — Error handling

## Systemd Services
| Service | Purpose |
|---------|---------|
| `Asguard-Networking.service` | Network interface init |
| `asguard-vm-start-notify.service` | Notify on VM boot |
| `asguard-vm-stop-notify.service` | Notify on VM shutdown |

## Encryption
```python
ENCRYPT_KEY = "57-xmiMq0yop7uD7Aq3j4PNUOgZhradICh2BKBnIdB0="  # settings.py
```

## Celery
- Daily backup task: `backend.managementBackup.tasks.export_backup_task` at 02:00 UTC
- Broker + result: Redis localhost:6379/0

## Cloud Storage (S3-compatible)
**New feature** — backups auto-uploaded to cloud after every backup.

**Django models** (`backend/backup/models.py`):
- `CloudStorageConfig` (table: `backup_cloud_config`) — S3 credentials, bucket, prefix, auto_upload flag, max_cloud_copies
- `BackupRecord` (table: `backup_record`) — full backup history in PostgreSQL with cloud upload status

**Service**: `backend/backup/system_backup/cloud_storage.py` — `CloudStorageService`
- `upload_file(local_path)` — single file upload with sha256 deduplication
- `upload_backup_folder(backup_id, backup_dir)` — compress to .tar.gz then upload
- `list_cloud_backups()` — list objects in bucket
- `download_backup(cloud_key, dest_path)` — download from cloud
- `apply_cloud_retention()` — delete oldest if > max_cloud_copies
- `async_upload_after_backup(backup_id, backup_dir, backup_type, result)` — classmethod, called after every backup in daemon thread

**Supported providers** (all S3-compatible via boto3):
- Backblaze B2 — free 10 GB (recommended for PFE)
- Cloudflare R2 — free 10 GB/month
- AWS S3 — free tier 5 GB
- MinIO — self-hosted

**Cloud API endpoints** (`/backup/`):
| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `cloud/config` | Get/save cloud credentials |
| POST | `cloud/test` | Test bucket connection |
| GET | `cloud/backups` | List objects in cloud bucket |
| POST | `cloud/sync/<backup_id>` | Manual push local backup to cloud |
| GET | `cloud/history` | Backup history from PostgreSQL |

**Flow**: backup completes → `async_upload_after_backup()` in daemon thread → compresses folder → uploads → saves `BackupRecord` with `cloud_uploaded=True` → applies cloud retention.

**DB backups**: `.dump` file uploaded directly (no compression needed).
