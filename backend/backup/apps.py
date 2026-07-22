from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.backup'

    def ready(self):
        import threading
        import time

        def _background_resource_monitor():
            """
            Permanent background thread — checks RAM/CPU every 60s and sends
            alert notifications regardless of whether any user has the dashboard open.
            """
            time.sleep(15)
            while True:
                try:
                    import psutil, os
                    from backend.backup.views import (
                        _resource_risk_alert,
                        _maybe_notify_resource_risk,
                    )
                    try:
                        load_values = os.getloadavg()
                        load_average = ", ".join(f"{v:.2f}" for v in load_values)
                    except Exception:
                        load_average = ""

                    live_metrics = {
                        "cpu_percentage":    psutil.cpu_percent(interval=2),
                        "memory_percentage": psutil.virtual_memory().percent,
                        "load_average":      load_average,
                    }
                    _maybe_notify_resource_risk(_resource_risk_alert(live_metrics), live_metrics)
                except Exception:
                    pass
                time.sleep(60)

        # NOTE: assistant prewarm intentionally removed — loading the local LLM at
        # boot pushed the hardened appliance into instability (guest CPU-disabled
        # crashes). The assistant now stays on the safe rule-based engine unless the
        # (capped) Ollama service is deliberately re-enabled.

        threading.Thread(target=_background_resource_monitor, daemon=True).start()
