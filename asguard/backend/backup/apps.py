from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.backup'

    def ready(self):
        import threading
        import time

        def _startup_sync_and_catchup():
            # Give uvicorn/Django a moment to fully initialize before running
            time.sleep(8)
            try:
                from backend.backup.views import (
                    _read_schedule_config,
                    _sync_crontab,
                    _queue_due_schedule_catchups,
                )
                config = _read_schedule_config()
                from backend.backup.views import _get_schedule_tz
                # Re-sync crontab entries on every startup (regenerates retry-aware commands)
                _sync_crontab(config.get("tasks", []), _get_schedule_tz(config))
                # Run missed backup catchup on startup — don't wait for user to open the page
                _queue_due_schedule_catchups(config)
            except Exception:
                pass

        threading.Thread(target=_startup_sync_and_catchup, daemon=True).start()
