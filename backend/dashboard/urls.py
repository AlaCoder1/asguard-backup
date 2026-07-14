from django.urls import path
from . import views

urlpatterns = [
    path("action",                   views.set_actions_service,    name="action"),
    path("watchdog",                 views.get_watchdog_status,    name="watchdogStatus"),
    path("watchdog/config",          views.update_watchdog_config, name="watchdogConfig"),
    path("watchdog/daemon",          views.toggle_watchdog_daemon, name="watchdogDaemon"),
]
