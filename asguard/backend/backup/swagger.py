"""
Organisation Swagger du module Backup & DRP.

Problème
--------
Sans configuration, drf_yasg place toutes les routes `/backup/*` sous un seul
tag « backup » : ~50 endpoints en vrac, impossible à lire pour un évaluateur.

Solution
--------
`BackupOrderedAutoSchema` déduit le tag de chaque endpoint à partir de son URL
et le range dans une des étapes du *cycle de vie d'une sauvegarde* :

    1. Création        →  on fabrique l'archive
    2. Catalogue       →  on liste / exporte / supprime les archives
    3. Restauration    →  on rejoue une archive sur le système
    4. Planification   →  on automatise (cron) + rétention
    5. Cloud           →  on réplique hors-site (S3)
    6. VM Snapshot/DRP →  reprise au niveau machine virtuelle
    7. Alertes         →  notifications e-mail / ntfy / telegram
    8. Logs & Audit    →  traçabilité
    9. Supervision     →  dashboard, métriques, Risk Center IA

drf_yasg trie les tags par ordre alphabétique : le préfixe numérique
(« 1. », « 2. », …) force donc l'affichage dans l'ordre réel du processus.

La classe ne touche QUE les routes `/backup/` — tout autre endpoint de
l'application conserve le comportement drf_yasg par défaut.
"""

from drf_yasg.inspectors import SwaggerAutoSchema

# Étape 1 : nom de tag affiché — préfixe numéroté pour forcer l'ordre.
_TAG_CREATE   = "Backup · 1. Création"
_TAG_CATALOG  = "Backup · 2. Catalogue & Archives"
_TAG_RESTORE  = "Backup · 3. Restauration"
_TAG_SCHEDULE = "Backup · 4. Planification & Rétention"
_TAG_CLOUD    = "Backup · 5. Cloud (hors-site)"
_TAG_VM       = "Backup · 6. VM Snapshot & DRP"
_TAG_ALERTS   = "Backup · 7. Alertes & Notifications"
_TAG_LOGS     = "Backup · 8. Logs & Audit"
_TAG_MONITOR  = "Backup · 9. Supervision & Risk Center"

# (fragment d'URL, tag) — première correspondance gagnante : l'ordre COMPTE.
# Les fragments les plus spécifiques sont placés avant les plus génériques.
_BACKUP_TAG_RULES = [
    ("/cloud/",             _TAG_CLOUD),
    ("/vm-snapshot",        _TAG_VM),
    ("/lvm-migration",      _TAG_VM),
    ("/schedule",           _TAG_SCHEDULE),
    ("/logs/",              _TAG_LOGS),
    ("/alerts/",            _TAG_ALERTS),
    ("/telegram-test",      _TAG_ALERTS),
    ("/in-app-alerts",      _TAG_ALERTS),
    ("/create-",            _TAG_CREATE),
    ("/components",         _TAG_CREATE),
    ("/progress/",          _TAG_CREATE),
    ("/verify-integrity",   _TAG_RESTORE),   # contrôle anti-falsification avant restore
    ("/restore",            _TAG_RESTORE),   # restore, restore-full, -components, -preview, -history
    ("/details",            _TAG_CATALOG),
    ("/delete",             _TAG_CATALOG),
    ("/export",             _TAG_CATALOG),
    ("/import",             _TAG_CATALOG),
    ("/getallbackups",      _TAG_CATALOG),
    ("/dashboard-overview", _TAG_MONITOR),
    ("/metrics",            _TAG_MONITOR),
    ("/events",             _TAG_MONITOR),
    ("/risk",               _TAG_MONITOR),
    ("/ping",               _TAG_MONITOR),
]


class BackupOrderedAutoSchema(SwaggerAutoSchema):
    """Tag les routes `/backup/*` par étape du cycle de vie d'une sauvegarde."""

    def get_tags(self, operation_keys=None):
        path = (self.path or "").lower()
        if "/backup/" in path:
            for fragment, tag in _BACKUP_TAG_RULES:
                if fragment in path:
                    return [tag]
        # Hors module backup : comportement drf_yasg standard.
        return super().get_tags(operation_keys)
