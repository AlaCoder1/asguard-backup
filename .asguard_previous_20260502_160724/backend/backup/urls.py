from django.urls import path
from . import views

urlpatterns = [
    path("ping", views.ping, name="backupPing"),
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

    path("restore-full-status/<str:job_id>", views.get_restore_full_status, name="getRestoreFullStatus"),
    path("restore-history", views.get_restore_history, name="getRestoreHistory"),

    path("<str:backup_id>/delete", views.delete_backup, name="deleteBackup"),
    path("<str:backup_id>/export", views.export_backup, name="exportBackup"),
    path("import", views.import_backup, name="importBackup"),

    # Schedule & Retention
    path("schedule", views.get_schedule, name="getSchedule"),
    path("schedule/task", views.save_schedule_task, name="saveScheduleTask"),
    path("schedule/task/<str:task_id>", views.delete_schedule_task, name="deleteScheduleTask"),
    path("schedule/run/<str:task_id>", views.run_scheduled_task, name="runScheduledTask"),
    path("schedule/retention", views.update_retention, name="updateRetention"),
    path("schedule/apply-retention", views.apply_retention_now, name="applyRetentionNow"),

    path("telegram-test", views.test_telegram, name="telegramTest"),

    # Cloud Storage
    path("cloud/config",                  views.cloud_config,         name="cloudConfig"),
    path("cloud/test",                    views.cloud_test,           name="cloudTest"),
    path("cloud/backups",                 views.cloud_list,           name="cloudList"),
    path("cloud/sync/<str:backup_id>",    views.cloud_sync,           name="cloudSync"),
    path("cloud/history",                 views.cloud_backup_history, name="cloudBackupHistory"),
]
