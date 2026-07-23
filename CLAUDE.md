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

## Django Apps (`backend/`)
| App | Role |
|-----|------|
| `authentification` | Login, JWT, sessions |
| `dashboard` | System metrics, WebSocket consumers |
| `backup` | Backup / restore / LVM snapshot engine |
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
**Key constant** in `backend/backup/views.py`:
```python
_BACKUP_ROOT = Path("/var/backups/asguard")
```

**Backup modules** (`backend/backup/system_backup/`):
- `full_backup_service.py` — `FullBackupService` (safe/full/custom backup engine)
- `backup_service.py` — `SystemBackupService.create_db_backup()` (pg_dump via Docker `app-db-container`)
- `restore_service.py` — Restore engine (`restore_full_complete` / `restore_full_ui_safe` / `restore_full_safe`)
- `export_import_service.py` — Archive export/import
- `lvm_snapshot_service.py` — LVM snapshot create/list/restore/delete
- `service_diagnostics.py` — `_diagnose_service_failure` (used by the Logs tab "Cause technique" banner)

**Backup API** (`/backup/`):
- `POST /backup/create-safe-backup` / `create-full-backup` / `create-custom-backup` — **ASYNC**: returns `{status:"queued", job_id}` immediately, runs backup in a background thread writing progress to `/var/backups/asguard/backup_jobs/{job_id}.json`
- `GET /backup/progress/<job_id>` — poll backup job progress (components_progress, progress_pct, status)
- `GET /backup/restore-full-status/<job_id>` — poll restore job progress (components_progress, components_order, progress_pct per component)
- `POST /backup/<id>/restore` / `restore-full` / `restore-components` — safe / complete / per-component restore
- `GET /backup/<id>/restore-preview` — pre-restore diff · `GET /backup/<id>/verify-integrity` — SHA-256 + HMAC check
- `GET /backup/vm-snapshot/*` — LVM snapshots · `GET /backup/logs/*` — audit timeline / stats / tail

> This version ships the backup/restore mechanism only — the automation (cron
> scheduling), cloud upload, notifications, dashboard and AI modules were removed.

## Frontend Structure (`src/`)
```
src/
  views/          # Feature pages (backup/, dashboard/, firewall/, ipsec/, openvpn/, ...)
  components/     # Reusable UI (VButton, VInput, modals/)
  layouts/        # layout.vue, TheHeading, TheSidebar, TheFooter
  router/         # router.js (base: /asguard/, history mode)
  store/          # Pinia: modules/auth.js, modules/modal.js
  middleware/     # Route guards
  locales/        # i18n (en, fr)
```

## Layout Architecture
- **`layout.vue`** wraps all pages: `TheHeadingVue` (top bar) + `TheSidebarVue` + `<slot name="content">`
- **`#toolbar-status` slot** in `layout.vue` — inject a pill/badge into the grey page toolbar next to the title (available for page toolbars)
- **Vuetify `v-list-item` nesting gotcha**: never nest `v-list-item` inside `v-list-item` for custom layouts — Vuetify overrides display and breaks flex alignment. Use a plain `<div>` instead.
- **Sidebar badge pattern**: wrap `sidebarTitle + badge` in `.sidebar-title-group { display: inline-flex; align-items: center; gap: 6px; }` so badge stays adjacent to text, not pushed to edge.

## TheSidebar.vue — Key Patterns
- Items array in `data()` — add `active: 'backup'` etc. to identify items for conditional rendering
- **Sidebar backup entry**: `active: 'backup'` marks the menu item (used for conditional rendering)
- **Rail mode** (icons only): separate `v-else` branch renders icons with badge at `top:2px right:2px`
- Clock interval started in `mounted()`, cleared in `beforeUnmount()`

## Key Backup Vue Components
| File | Role |
|------|------|
| `src/views/backup/index.vue` | Parent with 4 tabs (Backups, Historique Restores, Snapshot, Logs) |
| `src/views/backup/components/Backups.vue` | List + create + restore, polls during restore |
| `src/views/backup/components/RestoreHistory.vue` | Restore history + before/after diff report |
| `src/views/backup/components/VmSnapshot.vue` | LVM snapshots (create / restore / delete) |
| `src/views/backup/components/BackupLogs.vue` | Audit timeline, stats, service log tail |

## Utils (`utils/`)
- `constant_variables.py` — Standard error/success message templates
- `utils_command_system.py` — Shell command execution
- `utils_address.py` — IP address helpers
- `errors_utils.py` — Error handling

## Systemd Services
| Service | Purpose |
|---------|---------|
| `Asguard-Networking.service` | Network interface init |
| `asguard-resync.service` | Re-apply firewall/NAT/routing from DB to kernel at boot |

## Encryption
```python
ENCRYPT_KEY = "57-xmiMq0yop7uD7Aq3j4PNUOgZhradICh2BKBnIdB0="  # settings.py
```

## Celery
- Daily backup task: `backend.managementBackup.tasks.export_backup_task` at 02:00 UTC
- Broker + result: Redis localhost:6379/0

