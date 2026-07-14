"""Reconcile the DB network config from the live system (NetworkManager).

Usage:  python manage.py reconcile_network
Run after CLI-side network changes, or to verify DB ↔ system consistency.
"""
from django.core.management.base import BaseCommand

from backend.network.reconcile import reconcile_network_db_from_system


class Command(BaseCommand):
    help = "Sync DB (Interface/IP4Config/Vlan/Vxlan) from the live NM profiles."

    def handle(self, *args, **options):
        rep = reconcile_network_db_from_system()
        for k in ("created", "updated", "stale", "errors"):
            for item in rep[k]:
                tag = {"created": "＋", "updated": "～",
                       "stale": "⚠ stale", "errors": "✗"}[k]
                self.stdout.write(f"  {tag}  {item}")
        self.stdout.write(self.style.SUCCESS(
            f"reconcile done: created={len(rep['created'])} "
            f"updated={len(rep['updated'])} stale={len(rep['stale'])} "
            f"errors={len(rep['errors'])}"))
