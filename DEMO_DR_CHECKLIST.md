# Démo Disaster Recovery — Checklist pas-à-pas
## Soutenance PFE — sauvegarde / restauration Asguard

> **Objectif de la démo** : prouver à l'encadrant qu'après destruction d'une VM, on reconstruit l'appliance Asguard à l'identique à partir d'un seul fichier `.tar.gz` exporté.

---

## 0. Pré-flight (1 h avant la soutenance)

| Action | Commande / vérif |
|---|---|
| ☐ Backup full FRAIS créé | UI → Backups → `+ Nouveau backup` → type `Full` |
| ☐ Backup safe FRAIS créé | UI → Backups → `+ Nouveau backup` → type `Safe` |
| ☐ Backup exporté hors VM | UI → ligne du backup → `↑ Export` → télécharge `.tar.gz` |
| ☐ Backup uploadé cloud | UI → onglet Cloud Storage → vérifier upload visible |
| ☐ Intégrité vérifiée | `curl http://127.0.0.1:8000/backup/<backup_id>/verify-integrity \| jq` → attendre `"status":"ok"` |
| ☐ VM cible prête | Nouvelle VM minimale (Arch ou Debian) avec accès SSH, docker installé |
| ☐ Snapshot LVM de l'état actuel | `sudo lvcreate -L 2G -s -n asguard-presoutenance /dev/<vg>/<lv>` (sécurité retour arrière) |
| ☐ DR drill nocturne passé | `curl /backup/dr-drill/latest \| jq '.report.score'` → ≥ 80 |
| ☐ Script DR copié sur VM cible | `scp scripts/asguard-dr-restore root@<vm-cible>:/usr/local/sbin/` |

---

## 1. Scénario démo — narration

### Acte 1 — « Voici l'état initial »
**Sur la VM Asguard de référence**, montre dans l'UI :
- Onglet Backups : la liste des sauvegardes
- Clic sur **Aperçu** d'un backup `safe` récent
  - Cartes visuelles : "23 règles firewall, 5 NAT DNAT, 12 identités ZTNA, 28 règles WAF..."
  - Phrase résumé : "X éléments, identiques à l'état actuel"
- Clic sur **Détails** : sha256, taille, durée, fichiers contenus

> *« Le backup Safe contient toute la configuration métier — 17 composants, ~4.5 Mo. Le backup Full y ajoute le code applicatif, `/etc` complet, la base de données et les services systemd. »*

### Acte 2 — « Voici comment je l'exporte »
- Clic **↑ Export** sur le backup Full
- Téléchargement du `.tar.gz` (montrer la taille : ~30 Mo)

> *« Tout ce qui constitue l'appliance Asguard tient dans ce fichier. Je peux le mettre sur clé USB, le stocker en cloud — il est autonome et signé HMAC contre les altérations. »*

### Acte 3 — « Je détruis la VM » *(option déclarative ou réelle)*

**Option déclarative (recommandée si temps court)** :
> *« Imaginons que cette VM crash maintenant. Je passe à une VM neuve, fraîchement installée. »*

**Option réelle (si encadrant exige)** :
- Sur snapshot LVM, lancer `sudo shutdown -h now`
- Démarrer la VM cible neuve

### Acte 4 — « Je restaure sur VM neuve »

**Sur la VM cible**, depuis console TTY :

```bash
# 1. Importer le backup (le tar.gz exporté)
mkdir -p /var/backups/asguard
cd /var/backups/asguard
tar -xzf /path/to/asguard_backup_export_<id>.tar.gz
ls backup_*               # le dossier original est restauré

# 2. Vérifier l'intégrité AVANT toute action
ls backup_<timestamp>/backup_metadata.json
ls backup_<timestamp>/.manifest.sha256

# 3. Lancer le DR restore
sudo asguard-dr-restore /var/backups/asguard/backup_<timestamp>
```

> *« Le script demande confirmation pour chaque phase destructive — "tapez oui" — et écrit l'état précédent dans `/var/backups/asguard/dr-preflight-<timestamp>/`. »*

Phases visibles (en couleur, dans le terminal) :
```
━━━ Phase 1: Preflight ━━━
━━━ Phase 2: Locate backup ━━━
━━━ Phase 3: NIC mapping ━━━            ← prompt si interfaces changées
━━━ Phase 4: Packages ━━━
━━━ Phase 5: Stop app stack ━━━
━━━ Phase 6: Restore /etc ━━━
━━━ Phase 7: Restore systemd ━━━
━━━ Phase 8: Restore app code ━━━
━━━ Phase 9: Restore DB ━━━
━━━ Phase 10: Restore configs ━━━
━━━ Phase 11: Restore Docker ━━━
━━━ Phase 12: Apply firewall ━━━
━━━ Phase 13: Reboot ━━━
```

### Acte 5 — « Vérifications post-restauration »

Après reboot automatique :
```bash
asguard-dr-restore --verify
```

Puis dans le navigateur, ouvrir l'UI de la VM restaurée :
- **Onglet Dashboard** : services UP (uvicorn, nginx, postgres, suricata)
- **Onglet Firewall** : montrer les règles — *« exactement les mêmes IDs, descriptions, positions »*
- **Onglet NAT** : *« 5 DNAT, identiques »*
- **Onglet ZTNA** : *« 12 identités, identiques »*
- **Onglet WAF** : *« 28 règles, identiques »*
- **Onglet Backups → Historique Restores** : la ligne du restore qu'on vient de faire, avec son rapport diff (added / removed / modified)

---

## 2. Démo plus rapide (si peu de temps) — restore UI safe

Si l'encadrant ne veut PAS voir le scénario console DR complet, fais la démo dans l'UI :

1. UI → Backups → ligne backup safe → **Aperçu** : montrer les cartes visuelles
2. → **Restore** → choisir mode `complete` (UI-safe) → cocher la modale de preview
3. Cliquer "Lancer le restore" → monitor live s'affiche
4. Attendre 30 s — composants passent un par un de `pending` → `running` → `success`
5. **Rapport de changements** apparaît à la fin :
   - `+2 ajoutés / −1 supprimé / ~3 modifiés`
   - Clic sur "WAF" → tableau ligne par ligne : règle #42 ajoutée, règle #15 supprimée
6. UI → Historique Restores : la trace est conservée

> *« Le rapport diff prouve mesurablement que la restauration a remis EXACTEMENT le contenu attendu. Pas une lecture humaine d'un log — un comparatif d'état avant/après calculé par snapshot ORM. »*

---

## 3. Commandes utiles pendant la défense

| Question encadrant | Commande à taper |
|---|---|
| « Que contient ce backup ? » | `cat backup_<id>/backup_metadata.json \| jq '.components \| to_entries[] \| {name:.key, status:.value.status, size_mb:.value.size_mb}'` |
| « Le backup est-il signé ? » | `cat backup_<id>/.manifest.sha256 \| head -5` |
| « Y a-t-il la base de données ? » | `ls -lh backup_<id>/db/postgres.dump` |
| « Et les règles NAT ? » | `cat backup_<id>/nat/component_db.json \| jq '.counts'` |
| « Montrez le code de la sauvegarde firewall » | Ouvre `backend/backup/system_backup/full_backup_service.py:616` |
| « Montrez le code du restore ZTNA » | Ouvre `backend/backup/system_backup/restore_service.py` → cherche `_restore_extract_only` |
| « Comment savez-vous quels modèles sont sauvegardés ? » | Ouvre `backend/backup/component_db.py:41` → registre `COMPONENT_MODELS` |
| « Comment se lance le restore complet ? » | Ouvre `full_restore_runner.py` (racine) puis explique systemd-run |
| « Le scheduler ? » | `crontab -l \| grep asguard` + ouvre `backend/backup/apps.py` |
| « Notifications ? » | `curl https://ntfy.sh/asguard-ala-firewall-2024 --max-time 5 -d "test soutenance"` |

---

## 4. Si quelque chose plante — plans B

| Problème | Plan B |
|---|---|
| L'UI ne répond plus | `sudo systemctl restart uvicorn nginx` |
| Restore bloqué à 99 % | Montre `cat /var/backups/asguard/restore_jobs/<job_id>.json` — l'état est persisté, le job suit son cours |
| Backup création échoue | Bascule sur un backup existant (`backup_safe_2026-06-01_12-07-43`) |
| DR script demande NIC mapping | `--nic-map eth0=ens33,eth1=ens34` |
| Manifest invalide | Démontre que c'est une PROTECTION — un backup altéré DOIT être refusé. Recommence avec un backup sain |
| Pas de réseau sur VM cible | DR script supporte `--skip-packages` |

---

## 5. Points à dire à voix haute (le « pitch »)

> **« Asguard sauvegarde 29 composants — pas seulement des fichiers de config, mais aussi les lignes exactes de la base PostgreSQL pour chacun d'eux. Chaque sauvegarde est signée par un manifeste HMAC qui détecte toute altération. La restauration fonctionne dans deux modes : en ligne pour la maintenance courante sans interrompre l'interface, et hors ligne pour la reprise après sinistre complète. Un rapport de diff ligne par ligne est produit après chaque restore — pas une promesse, une preuve mesurée. »**

---

## 6. Fichiers à ouvrir dans VSCode pendant la soutenance

Ouvre ces 6 fichiers en onglets côte-à-côte, pré-positionnés sur les bonnes lignes :

1. `backend/backup/system_backup/full_backup_service.py` → l. 42 (FULL_COMPONENTS)
2. `backend/backup/system_backup/restore_service.py` → l. 261 (`_component_runners`)
3. `backend/backup/component_db.py` → l. 41 (COMPONENT_MODELS)
4. `backend/backup/restore_diff.py` → l. 178 (`diff_db_states`)
5. `backend/backup/integrity.py` → fonction `write_manifest`
6. `scripts/asguard-dr-restore` → début du fichier (header documenté)

Plus la matrice de complétude de `RAPPORT_SOUTENANCE_BACKUP_DRP.md` ouverte en preview Markdown.
