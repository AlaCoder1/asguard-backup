import sys

from django.apps import AppConfig


class NetworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.network'

    def ready(self):
        # Skip during migrations / shell / collectstatic — only reconcile in a
        # real server process.
        if any(a in sys.argv for a in ("migrate", "makemigrations", "collectstatic",
                                       "shell", "test", "reconcile_network")):
            return

        import threading
        import time

        def _startup_reconcile():
            # Wait for NetworkManager + DB to settle after boot, then realign the
            # DB to the live system so CLI-side changes show up in the UI.
            time.sleep(12)
            try:
                from backend.network.reconcile import reconcile_network_db_from_system
                reconcile_network_db_from_system()
            except Exception:
                pass

        threading.Thread(target=_startup_reconcile, daemon=True).start()
