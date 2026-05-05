from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.backup'

    def ready(self):
        import threading

        def _sync():
            try:
                from backend.backup.views import _read_schedule_config, _sync_crontab
                config = _read_schedule_config()
                _sync_crontab(config.get("tasks", []))
            except Exception:
                pass

        threading.Thread(target=_sync, daemon=True).start()
