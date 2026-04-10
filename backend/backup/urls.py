from django.urls import path
from . import views

urlpatterns = [
    path("ping", views.ping, name="backupPing"),
    path("getAllBackups", views.get_all_backups, name="getAllBackups"),

    path("create-db-backup", views.create_db_backup, name="createDbBackup"),

    path("create-full-backup", views.create_full_backup, name="createFullBackup"),
    path("create-safe-backup", views.create_safe_backup, name="createSafeBackup"),

    path("<str:backup_id>/details", views.get_backup_details, name="getBackupDetails"),

    path("<str:backup_id>/restore", views.restore_backup, name="restoreBackup"),
    path("<str:backup_id>/restore-full", views.restore_full_backup, name="restoreFullBackup"),
    path("restore-full-status/<str:job_id>", views.get_restore_full_status, name="getRestoreFullStatus"),

    path("<str:backup_id>/delete", views.delete_backup, name="deleteBackup"),
    path("<str:backup_id>/export", views.export_backup, name="exportBackup"),
    path("import", views.import_backup, name="importBackup"),
]