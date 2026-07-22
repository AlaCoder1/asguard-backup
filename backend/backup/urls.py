from django.urls import path
from . import (
    views,
    views_vm_snapshot,
    views_lvm_migration,
    views_logs,
)

urlpatterns = [
    path("ping", views.ping, name="backupPing"),

    # Logs / audit timeline / system tail
    path("logs/timeline",                     views_logs.logs_timeline,          name="logsTimeline"),
    path("logs/stats",                        views_logs.logs_stats,             name="logsStats"),
    path("logs/tail",                         views_logs.logs_tail,              name="logsTail"),
    # dashboard-overview feeds the shared notification store (header badge, sidebar).
    path("dashboard-overview", views.get_dashboard_overview, name="getBackupDashboardOverview"),
    path("getAllBackups", views.get_all_backups, name="getAllBackups"),

    path("create-db-backup", views.create_db_backup, name="createDbBackup"),
    path("create-full-backup", views.create_full_backup, name="createFullBackup"),
    path("create-safe-backup", views.create_safe_backup, name="createSafeBackup"),
    path("create-custom-backup", views.create_custom_backup, name="createCustomBackup"),
    path("components", views.get_backup_components, name="getBackupComponents"),

    path("<str:backup_id>/details", views.get_backup_details, name="getBackupDetails"),

    # SAFE restore = sans application
    path("<str:backup_id>/restore", views.restore_backup, name="restoreBackup"),

    # COMPLETE restore = avec application
    path("<str:backup_id>/restore-full", views.restore_full_backup, name="restoreFullBackup"),
    path("<str:backup_id>/restore-components", views.restore_components, name="restoreComponents"),
    # Pre-restore preview: what WILL be restored vs what will be SKIPPED + why.
    path("<str:backup_id>/restore-preview", views.restore_preview, name="restorePreview"),
    # Anti-tamper: SHA-256 + HMAC integrity check of a backup before restoring it.
    path("<str:backup_id>/verify-integrity", views.verify_backup_integrity, name="verifyBackupIntegrity"),

    path("restore-full-status/<str:job_id>", views.get_restore_full_status, name="getRestoreFullStatus"),
    path("restore/active", views.restore_active, name="restoreActive"),
    # Operator recovery action offered when a restore ends degraded.
    path("system/reboot", views.system_reboot, name="systemReboot"),
    path("progress/<str:job_id>", views.get_backup_progress, name="getBackupProgress"),
    path("restore-history", views.get_restore_history, name="getRestoreHistory"),

    path("<str:backup_id>/delete", views.delete_backup, name="deleteBackup"),
    path("<str:backup_id>/export", views.export_backup, name="exportBackup"),
    path("import", views.import_backup, name="importBackup"),

    # VM Snapshots
    path("vm-snapshot/running-jobs",                  views_vm_snapshot.vm_snapshot_running_jobs,    name="vmSnapshotRunningJobs"),
    path("vm-snapshot/last-restore",                  views_vm_snapshot.vm_snapshot_last_restore,    name="vmSnapshotLastRestore"),
    path("vm-snapshot/info",                         views_vm_snapshot.vm_snapshot_info,           name="vmSnapshotInfo"),
    path("vm-snapshot/test-connection",              views_vm_snapshot.vm_snapshot_test_connection, name="vmSnapshotTestConnection"),
    path("vm-snapshot/list",                         views_vm_snapshot.vm_snapshot_list,           name="vmSnapshotList"),
    path("vm-snapshot/create",                       views_vm_snapshot.vm_snapshot_create,         name="vmSnapshotCreate"),
    path("vm-snapshot/progress/<str:job_id>",        views_vm_snapshot.vm_snapshot_progress,       name="vmSnapshotProgress"),
    path("vm-snapshot/config",                       views_vm_snapshot.vm_snapshot_config,         name="vmSnapshotConfig"),
    path("vm-snapshot/<str:snap_id>/restore",        views_vm_snapshot.vm_snapshot_restore,        name="vmSnapshotRestore"),
    path("vm-snapshot/restore-status/<str:job_id>",              views_vm_snapshot.vm_snapshot_restore_status, name="vmSnapshotRestoreStatus"),
    path("vm-snapshot/<str:snap_id>/delete",         views_vm_snapshot.vm_snapshot_delete,         name="vmSnapshotDelete"),
    path("vm-snapshot/<str:job_id>/cancel",          views_vm_snapshot.vm_snapshot_cancel,          name="vmSnapshotCancel"),

    # ─── LVM coverage migration ───────────────────────────────────────────────
    # Extends snapshot scope by bind-mounting /etc/* config paths onto the
    # snapshotable LV. This is a deployment / DR operation — only `status` and
    # `plan` are consumed by the UI (read-only previews in the VM Snapshot
    # tab). The other endpoints are intentionally kept for the asguard-dr-
    # restore script and for one-shot provisioning on a fresh appliance:
    #   - config / apply / progress  : invoked by the deployment installer
    #   - rollback / audit           : recovery hooks used by support scripts
    # Do not remove them: removing the URL without also removing the view
    # would 404 the deployment flow on a new client install.
    path("lvm-migration/status",                  views_lvm_migration.lvm_migration_status,   name="lvmMigrationStatus"),    # UI
    path("lvm-migration/plan",                    views_lvm_migration.lvm_migration_plan,     name="lvmMigrationPlan"),      # UI
    path("lvm-migration/config",                  views_lvm_migration.lvm_migration_config,   name="lvmMigrationConfig"),    # deployment
    path("lvm-migration/apply",                   views_lvm_migration.lvm_migration_apply,    name="lvmMigrationApply"),     # deployment
    path("lvm-migration/progress/<str:job_id>",   views_lvm_migration.lvm_migration_progress, name="lvmMigrationProgress"),  # deployment
    path("lvm-migration/rollback",                views_lvm_migration.lvm_migration_rollback, name="lvmMigrationRollback"),  # support
    path("lvm-migration/audit",                   views_lvm_migration.lvm_migration_audit,    name="lvmMigrationAudit"),     # support

    # In-app alerts
    path("in-app-alerts",            views.get_in_app_alerts,       name="getInAppAlerts"),
    path("in-app-alerts/mark-read",  views.mark_in_app_alerts_read, name="markInAppAlertsRead"),
]
