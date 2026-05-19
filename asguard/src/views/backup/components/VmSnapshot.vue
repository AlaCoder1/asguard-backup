<template>
  <div class="lvm-wrap">

    <!-- Post-restore success banner -->
    <Transition name="lvm-fade">
      <div class="lvm-restore-banner" v-if="lastRestoreBanner">
        <div class="lvm-banner-icon-wrap">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div class="lvm-banner-text">
          <strong>Système restauré avec succès</strong>
          <span>Votre Asguard est revenu à l'état du point <code>{{ lastRestoreBanner.snap_id }}</code></span>
        </div>
        <button class="lvm-banner-close" @click="lastRestoreBanner = null">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </Transition>

    <!-- ════════ HERO PROTECTION CARD ════════ -->
    <div class="lvm-hero">
      <div class="lvm-hero-bg"></div>
      <div class="lvm-hero-content">

        <div class="lvm-hero-left">
          <!-- Big shield icon with status -->
          <div class="lvm-shield" :class="protectionLevel">
            <svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <polyline v-if="protectionLevel === 'protected'" points="9 12 11 14 15 10"/>
              <line v-else-if="protectionLevel === 'warning'" x1="12" y1="8" x2="12" y2="13"/>
              <circle v-else-if="protectionLevel === 'warning'" cx="12" cy="16" r="0.5" fill="currentColor"/>
              <line v-else x1="9" y1="9" x2="15" y2="15"/>
              <line v-if="protectionLevel === 'unprotected'" x1="15" y1="9" x2="9" y2="15"/>
            </svg>
            <div class="lvm-shield-pulse"></div>
          </div>

          <div class="lvm-hero-text">
            <div class="lvm-hero-status">
              <span class="lvm-hero-dot" :class="protectionLevel"></span>
              {{ protectionStatusLabel }}
            </div>
            <h1 class="lvm-hero-title">{{ protectionHeadline }}</h1>
            <p class="lvm-hero-sub">{{ protectionSubtitle }}</p>
          </div>
        </div>

        <div class="lvm-hero-right">
          <button class="lvm-hero-cta" @click="openCreateDialog" :disabled="creating || !lvmOk">
            <div class="lvm-hero-cta-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            </div>
            <div class="lvm-hero-cta-text">
              <strong>Créer un point de restauration</strong>
              <span>Sauvegarde instantanée · ~{{ vmInfo.snapshot_estimated_seconds || 8 }}s · sans interruption</span>
            </div>
            <svg class="lvm-hero-cta-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          </button>

          <div class="lvm-hero-mini-actions">
            <button class="lvm-mini-btn" @click="testConnection" title="Vérifier que le système de sauvegarde fonctionne">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Diagnostic
            </button>
            <button class="lvm-mini-btn" @click="showAdvanced = !showAdvanced" :class="{ active: showAdvanced }" title="Afficher les détails techniques">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              {{ showAdvanced ? 'Mode simple' : 'Mode expert' }}
            </button>
            <button class="lvm-mini-btn" @click="showConfig = !showConfig" title="Configurer le système">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              Réglages
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════ INSIGHT ROW (3 friendly cards) ════════ -->
    <div class="lvm-insight-row">
      <div class="lvm-insight-card">
        <div class="lvm-insight-icon teal">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="lvm-insight-body">
          <div class="lvm-insight-val">{{ lastSnapshotAge }}</div>
          <div class="lvm-insight-lbl">Dernier point de restauration</div>
        </div>
      </div>

      <div class="lvm-insight-card">
        <div class="lvm-insight-icon purple">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        </div>
        <div class="lvm-insight-body">
          <div class="lvm-insight-val">{{ snapshots.length }} <span class="lvm-insight-max">/ {{ config.max_snapshots || 3 }}</span></div>
          <div class="lvm-insight-lbl">Points enregistrés</div>
        </div>
      </div>

      <div class="lvm-insight-card">
        <div class="lvm-insight-icon green">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </div>
        <div class="lvm-insight-body">
          <div class="lvm-insight-val">{{ vmInfo.vg?.vg_free || '—' }}</div>
          <div class="lvm-insight-lbl">Espace disponible</div>
        </div>
      </div>

      <div class="lvm-insight-card">
        <div class="lvm-insight-icon blue">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="lvm-insight-body">
          <div class="lvm-insight-val">~{{ vmInfo.snapshot_estimated_seconds || 8 }}s</div>
          <div class="lvm-insight-lbl">Temps de sauvegarde</div>
        </div>
      </div>
    </div>

    <!-- ════════ COVERAGE CARD (what's actually protected) ════════ -->
    <div class="lvm-coverage-card" :class="'cov-' + coverageLevel">
      <div class="lvm-cov-head">
        <div class="lvm-cov-title-wrap">
          <div class="lvm-cov-icon" :class="'cov-' + coverageLevel">
            <svg v-if="coverageLevel === 'full'"    width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
            <svg v-else-if="coverageLevel === 'partial'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          </div>
          <div>
            <div class="lvm-cov-title">Couverture du point de restauration</div>
            <div class="lvm-cov-sub">{{ coverageHeadline }}</div>
          </div>
        </div>
        <div class="lvm-cov-actions">
          <span class="lvm-cov-pill" :class="'cov-' + coverageLevel">
            {{ coverage.migrated || 0 }} / {{ coverage.applicable || 0 }} modules
            <span v-if="coverage.coverage_pct != null"> · {{ coverage.coverage_pct }}%</span>
          </span>
          <button class="lvm-mini-btn" @click="toggleCoverageDetails" :class="{ active: showCoverageDetails }">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            {{ showCoverageDetails ? 'Masquer' : 'Détails' }}
          </button>
          <button class="lvm-btn-primary" @click="openPlanModal" :disabled="coverageLevel === 'full'">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Étendre la couverture
          </button>
        </div>
      </div>

      <div class="lvm-cov-bar">
        <div class="lvm-cov-bar-fill" :class="'cov-' + coverageLevel"
             :style="{ width: (coverage.coverage_pct || 0) + '%' }"></div>
      </div>

      <Transition name="lvm-slide">
        <div class="lvm-cov-items" v-if="showCoverageDetails">
          <div v-for="it in coverage.items" :key="it.id"
               class="lvm-cov-item"
               :class="'state-' + it.state">
            <div class="lvm-cov-item-icon">
              <svg v-if="it.state === 'migrated'"        width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><polyline points="20 6 9 17 4 12"/></svg>
              <svg v-else-if="it.state === 'not_migrated'"  width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <svg v-else-if="it.state === 'not_applicable'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
            <div class="lvm-cov-item-body">
              <div class="lvm-cov-item-id">{{ coverageItemLabel(it.id) }}</div>
              <div class="lvm-cov-item-src mono">{{ it.source }}</div>
            </div>
            <div class="lvm-cov-item-state">
              <span class="lvm-cov-state-pill" :class="'state-' + it.state">
                {{ coverageStateLabel(it.state) }}
              </span>
              <span v-if="it.size_bytes" class="lvm-cov-size">{{ humanBytes(it.size_bytes) }}</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- ════════ MIGRATION PLAN MODAL (dry-run preview) ════════ -->
    <Transition name="lvm-fade">
      <div class="lvm-modal-overlay" v-if="showPlanModal" @click.self="showPlanModal = false">
        <div class="lvm-modal lvm-modal-wide">
          <div class="lvm-modal-head">
            <div>
              <div class="lvm-modal-title">Plan d'extension de couverture</div>
              <div class="lvm-modal-sub">Aperçu en mode simulation — aucune modification ne sera appliquée tant que vous ne confirmez pas.</div>
            </div>
            <button class="lvm-modal-close" @click="showPlanModal = false">×</button>
          </div>

          <div class="lvm-plan-body" v-if="migrationPlan">
            <!-- Plan summary -->
            <div class="lvm-plan-summary">
              <div class="lvm-plan-stat">
                <span class="lvm-plan-stat-val">{{ migrationPlan.summary.to_migrate }}</span>
                <span class="lvm-plan-stat-lbl">À migrer</span>
              </div>
              <div class="lvm-plan-stat">
                <span class="lvm-plan-stat-val">{{ migrationPlan.summary.already_done }}</span>
                <span class="lvm-plan-stat-lbl">Déjà fait</span>
              </div>
              <div class="lvm-plan-stat">
                <span class="lvm-plan-stat-val">{{ migrationPlan.summary.not_applicable }}</span>
                <span class="lvm-plan-stat-lbl">Non applicable</span>
              </div>
              <div class="lvm-plan-stat">
                <span class="lvm-plan-stat-val">{{ humanBytes(migrationPlan.estimated_size_bytes) }}</span>
                <span class="lvm-plan-stat-lbl">Données à déplacer</span>
              </div>
              <div class="lvm-plan-stat">
                <span class="lvm-plan-stat-val">{{ humanBytes(migrationPlan.lv_free_bytes) }}</span>
                <span class="lvm-plan-stat-lbl">Espace libre LV</span>
              </div>
            </div>

            <!-- Warnings -->
            <div v-if="migrationPlan.warnings && migrationPlan.warnings.length" class="lvm-plan-warnings">
              <div class="lvm-plan-warn-title">⚠ Avertissements</div>
              <ul>
                <li v-for="(w, i) in migrationPlan.warnings" :key="i">{{ w }}</li>
              </ul>
            </div>

            <!-- Safety net -->
            <div class="lvm-plan-safety">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <span><strong>Filet de sécurité automatique :</strong> {{ migrationPlan.pre_safety_net.step }}</span>
            </div>

            <!-- Per-item actions -->
            <div class="lvm-plan-actions-list">
              <div v-for="a in migrationPlan.actions" :key="a.id"
                   class="lvm-plan-action"
                   :class="'decision-' + a.decision">
                <div class="lvm-plan-action-head">
                  <div class="lvm-plan-action-id">
                    <strong>{{ coverageItemLabel(a.id) }}</strong>
                    <span class="lvm-plan-decision" :class="'decision-' + a.decision">{{ planDecisionLabel(a.decision) }}</span>
                  </div>
                  <span v-if="a.size_bytes" class="lvm-cov-size">{{ humanBytes(a.size_bytes) }}</span>
                </div>
                <div class="lvm-plan-action-src mono">{{ a.source }} → {{ a.target }}</div>
                <div v-if="a.reason" class="lvm-plan-reason">{{ a.reason }}</div>
                <details v-if="a.steps && a.steps.length" class="lvm-plan-steps">
                  <summary>Voir les étapes ({{ a.steps.length }})</summary>
                  <ol>
                    <li v-for="(s, i) in a.steps" :key="i" class="mono">{{ s }}</li>
                  </ol>
                </details>
              </div>
            </div>
          </div>
          <div v-else class="lvm-plan-loading">Calcul du plan…</div>

          <div class="lvm-modal-foot">
            <span class="lvm-plan-note">Mode build + dry-run uniquement — la migration réelle est désactivée dans cette release.</span>
            <button class="lvm-btn-ghost" @click="showPlanModal = false">Fermer</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ════════ JOB PROGRESS BANNER (in-page, for create jobs) ════════ -->
    <Transition name="lvm-fade">
      <div class="lvm-progress-banner" v-if="activeJob && !restoring">
        <div class="lvm-progress-left">
          <div class="lvm-spinner"></div>
          <div>
            <div class="lvm-progress-title">{{ activeJob.phase_label || 'Opération en cours…' }}</div>
            <div class="lvm-progress-sub">Veuillez patienter — votre système reste accessible</div>
          </div>
        </div>
        <div class="lvm-progress-bar-wrap">
          <div class="lvm-progress-bar-fill" :style="{ width: jobProgressPct + '%' }"></div>
        </div>
        <span class="lvm-progress-pct">{{ jobProgressPct }}%</span>
      </div>
    </Transition>

    <!-- ════════ FULL-SCREEN RESTORE OVERLAY ════════ -->
    <!-- Restore stops PostgreSQL for ~30s while the LVM merge runs. ANY page
         that talks to the DB during that window will 500. This overlay takes
         over the screen so the user sees a controlled progress UI instead of
         Django error pages, then auto-reloads when the job finishes. -->
    <Teleport to="body">
      <Transition name="lvm-fade">
        <div class="lvm-restore-overlay" v-if="restoring">
          <div class="lvm-restore-overlay-card">
            <div class="lvm-restore-overlay-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 12 A 16 16 0 1 1 8 36" />
                <path d="M8 12 L 8 4 L 16 4" />
                <path d="M24 16 L 24 24 L 30 28" />
              </svg>
            </div>
            <div class="lvm-restore-overlay-title">Restauration LVM en cours</div>
            <div class="lvm-restore-overlay-sub">
              Snapshot <code>{{ activeJob?.snap_id || lastRestoreBanner?.snap_id || '—' }}</code> en cours de réapplication.
              <br/>
              L'interface est momentanément indisponible pendant la fusion du volume
              (PostgreSQL est arrêté ~30 s pour garantir l'intégrité). Ne fermez pas l'onglet.
            </div>

            <div class="lvm-restore-overlay-bar">
              <div class="lvm-restore-overlay-bar-fill" :style="{ width: restoreOverlayPct + '%' }"></div>
            </div>
            <div class="lvm-restore-overlay-pct">{{ restoreOverlayPct }}%</div>

            <div class="lvm-restore-overlay-phases">
              <div v-for="p in restoreOverlayPhases" :key="p.key"
                   class="lvm-restore-overlay-phase"
                   :class="{ 'done': p.done, 'active': p.active }">
                <span class="lvm-restore-overlay-phase-dot"></span>
                <span>{{ p.label }}</span>
              </div>
            </div>

            <div class="lvm-restore-overlay-footer" v-if="restorePollErrors > 0">
              ⏳ Connexion à la base interrompue (normal) — {{ restorePollErrors }} tentative(s) de reprise…
            </div>
            <div class="lvm-restore-overlay-footer" v-else>
              La page se rechargera automatiquement à la fin.
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ════════ SPACE ERROR MODAL — actionable, lists snapshots to delete ════════ -->
    <Transition name="lvm-fade">
      <div class="lvm-space-modal-backdrop" v-if="spaceError" @click.self="dismissSpaceError">
        <div class="lvm-space-modal" role="dialog" aria-modal="true">
          <div class="lvm-space-modal-head">
            <div class="lvm-space-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                   stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 22h20L12 2z"/>
                <line x1="12" y1="9" x2="12" y2="14"/>
                <line x1="12" y1="17" x2="12" y2="17.5"/>
              </svg>
            </div>
            <div class="lvm-space-head-body">
              <div class="lvm-space-title">Espace insuffisant pour créer le snapshot</div>
              <div class="lvm-space-sub">{{ spaceError.error }}</div>
            </div>
          </div>

          <div class="lvm-space-stats">
            <div class="lvm-space-stat">
              <span class="lvm-space-stat-lbl">Espace libre</span>
              <span class="lvm-space-stat-val warn">{{ formatSnapSize(spaceError.vg_free_gb) }}</span>
            </div>
            <div class="lvm-space-stat">
              <span class="lvm-space-stat-lbl">Espace requis</span>
              <span class="lvm-space-stat-val">{{ formatSnapSize(spaceError.required_gb) }}</span>
            </div>
            <div class="lvm-space-stat">
              <span class="lvm-space-stat-lbl">À libérer</span>
              <span class="lvm-space-stat-val danger">{{ formatSnapSize(spaceError.shortfall_gb) }}</span>
            </div>
          </div>

          <div class="lvm-space-action-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16v.5"/></svg>
            Libérez de l'espace en supprimant un snapshot existant
          </div>

          <div class="lvm-space-list" v-if="spaceError.existing_snapshots && spaceError.existing_snapshots.length">
            <div
              v-for="(s, idx) in spaceError.existing_snapshots"
              :key="s.snap_id"
              class="lvm-space-snap"
              :class="{ 'lvm-space-snap--suggested': idx === 0 }"
            >
              <div class="lvm-space-snap-left">
                <div class="lvm-space-snap-name">
                  <span class="lvm-space-snap-id">{{ s.snap_id }}</span>
                  <span v-if="idx === 0" class="lvm-space-snap-tag">Plus ancien · suggéré</span>
                </div>
                <div class="lvm-space-snap-meta">
                  <span v-if="s.description">{{ s.description }}</span>
                  <span v-if="s.created_at">· Créé le {{ new Date(s.created_at).toLocaleString('fr-FR') }}</span>
                </div>
              </div>
              <div class="lvm-space-snap-right">
                <span class="lvm-space-snap-size">{{ formatSnapSize(s.size_gb) }}</span>
                <button
                  class="lvm-space-snap-del"
                  :disabled="deletingSnapId === s.snap_id"
                  @click="deleteAndRetry(s.snap_id)"
                >
                  <svg v-if="deletingSnapId === s.snap_id" width="13" height="13" viewBox="0 0 50 50" class="lvm-mini-spin">
                    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="80" stroke-linecap="round"/>
                  </svg>
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
                  {{ deletingSnapId === s.snap_id ? 'Suppression…' : 'Supprimer et réessayer' }}
                </button>
              </div>
            </div>
          </div>
          <div v-else class="lvm-space-empty">
            Aucun snapshot existant à supprimer. Réduisez la taille dans
            <strong>Réglages → Espace réservé par point</strong>, ou agrandissez
            le Volume Group.
          </div>

          <div class="lvm-space-modal-foot">
            <button class="lvm-btn-ghost" @click="dismissSpaceError">Fermer</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ════════ ADVANCED TECHNICAL PANEL (collapsible) ════════ -->
    <Transition name="lvm-slide">
      <div class="lvm-tech-panel" v-if="showAdvanced">
        <div class="lvm-tech-header">
          <div class="lvm-tech-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            Détails techniques LVM
          </div>
          <span class="lvm-tech-pill" :class="lvmOk ? 'online' : 'offline'">
            <span class="lvm-dot" :class="lvmOk ? 'green' : 'red'"></span>
            {{ lvmOk ? 'LVM opérationnel' : 'LVM indisponible' }}
          </span>
        </div>
        <div class="lvm-vol-grid">
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">Volume Group</span>
            <span class="lvm-vol-val mono">{{ vmInfo.vg?.vg_name || 'asguard-vg' }}</span>
          </div>
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">Logical Volume</span>
            <span class="lvm-vol-val mono">{{ vmInfo.lv?.lv_name || 'asguard-data' }}</span>
          </div>
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">Taille du volume</span>
            <span class="lvm-vol-val">{{ vmInfo.lv?.lv_size || '—' }}</span>
          </div>
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">Espace libre VG</span>
            <span class="lvm-vol-val">{{ vmInfo.vg?.vg_free || '—' }}</span>
          </div>
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">Point de montage</span>
            <span class="lvm-vol-val mono">{{ vmInfo.mount_point || '/var/asguard_data' }}</span>
          </div>
          <div class="lvm-vol-item">
            <span class="lvm-vol-lbl">CPU / RAM</span>
            <span class="lvm-vol-val">{{ vmInfo.vcpus || '—' }} CPU · {{ vmInfo.ram_gb || '—' }} GB</span>
          </div>
        </div>
        <div class="lvm-disk-bar-wrap" v-if="vmInfo.disk_usage?.use_percent">
          <div class="lvm-disk-bar-header">
            <span>Utilisation du volume {{ vmInfo.mount_point || '/var/asguard_data' }}</span>
            <span class="lvm-disk-pct">{{ vmInfo.disk_usage.used }} / {{ vmInfo.disk_usage.total }} ({{ vmInfo.disk_usage.use_percent }})</span>
          </div>
          <div class="lvm-disk-bar">
            <div class="lvm-disk-fill" :style="{ width: vmInfo.disk_usage.use_percent }" :class="diskBarClass"></div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ════════ CONFIG PANEL ════════ -->
    <Transition name="lvm-slide">
      <div class="lvm-config-panel" v-if="showConfig">
        <div class="lvm-config-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/></svg>
          Réglages des points de restauration
        </div>
        <div class="lvm-config-grid">
          <div class="lvm-config-field">
            <label>Espace réservé par point (Go)</label>
            <input type="number" v-model.number="editConfig.snap_size_gb" min="1" max="20" class="lvm-input"/>
            <span class="lvm-config-hint">Taille maximale des modifications stockées (Copy-on-Write)</span>
          </div>
          <div class="lvm-config-field">
            <label>Nombre maximum de points</label>
            <input type="number" v-model.number="editConfig.max_snapshots" min="1" max="10" class="lvm-input"/>
            <span class="lvm-config-hint">Au-delà, les plus anciens sont supprimés automatiquement</span>
          </div>
          <div class="lvm-config-field lvm-config-toggle">
            <div>
              <label>Sauvegarde automatique avant Full Backup</label>
              <span class="lvm-config-hint">Crée un point juste avant chaque sauvegarde complète</span>
            </div>
            <div class="lvm-toggle-wrap">
              <input type="checkbox" v-model="editConfig.auto_before_full_backup" id="lvm-auto" class="lvm-toggle-cb"/>
              <label for="lvm-auto" class="lvm-toggle-label"></label>
            </div>
          </div>
        </div>
        <div class="lvm-config-actions">
          <button class="lvm-btn-primary" @click="saveConfig">Enregistrer</button>
          <button class="lvm-btn-ghost" @click="showConfig = false">Annuler</button>
        </div>
      </div>
    </Transition>

    <!-- ════════ TIMELINE OF SNAPSHOTS ════════ -->
    <div class="lvm-timeline-card">
      <div class="lvm-timeline-header">
        <div class="lvm-timeline-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
          Vos points de restauration
          <span class="lvm-table-count">{{ snapshots.length }}</span>
        </div>
        <button class="lvm-btn-icon" @click="loadAll" :class="{ spinning: loading }" title="Actualiser">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.08-8.36"/></svg>
        </button>
      </div>

      <!-- Empty state with use-case suggestions -->
      <div class="lvm-empty" v-if="!loading && snapshots.length === 0">
        <div class="lvm-empty-illu">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.3">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <line x1="9" y1="11" x2="15" y2="11" stroke-dasharray="2 2"/>
          </svg>
          <div class="lvm-empty-glow"></div>
        </div>
        <p>Aucun point de restauration créé</p>
        <span>Créez votre premier checkpoint pour pouvoir revenir en arrière en cas de problème</span>

        <div class="lvm-usecase-grid">
          <div class="lvm-usecase">
            <div class="lvm-usecase-emoji">🛡️</div>
            <strong>Avant une mise à jour</strong>
            <span>Si la nouvelle version pose problème, revenez instantanément</span>
          </div>
          <div class="lvm-usecase">
            <div class="lvm-usecase-emoji">⚙️</div>
            <strong>Avant un changement</strong>
            <span>Modifier un firewall, une route, un VPN — sans risque</span>
          </div>
          <div class="lvm-usecase">
            <div class="lvm-usecase-emoji">🧪</div>
            <strong>Pour tester</strong>
            <span>Essayez une nouvelle config, restaurez si ça ne fonctionne pas</span>
          </div>
        </div>

        <button class="lvm-empty-cta" @click="openCreateDialog" :disabled="!lvmOk">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Créer mon premier point
        </button>
      </div>

      <!-- Timeline list -->
      <div class="lvm-timeline" v-else>
        <div v-for="(snap, idx) in snapshots" :key="snap.snap_id" class="lvm-tl-item">
          <div class="lvm-tl-axis">
            <div class="lvm-tl-dot" :class="usageClass(snap.data_percent)"></div>
            <div class="lvm-tl-line" v-if="idx < snapshots.length - 1"></div>
          </div>

          <div class="lvm-tl-card">
            <div class="lvm-tl-top">
              <div class="lvm-tl-meta">
                <div class="lvm-tl-name">
                  <span class="lvm-tl-icon">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
                  </span>
                  <code>{{ snap.snap_id }}</code>
                  <span class="lvm-tl-badge-fresh" v-if="isRecent(snap)">Récent</span>
                </div>
                <div class="lvm-tl-desc">{{ snap.description || 'Aucune description' }}</div>
              </div>

              <div class="lvm-tl-actions">
                <button class="lvm-action-btn restore" @click="confirmRestore(snap)"
                        :disabled="restoring || creating" title="Revenir à ce point">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/></svg>
                  Restaurer
                </button>
                <button class="lvm-action-btn delete" @click="confirmDelete(snap)"
                        :disabled="restoring || creating" title="Supprimer ce point">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                </button>
              </div>
            </div>

            <div class="lvm-tl-foot">
              <div class="lvm-tl-info">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span class="lvm-tl-age">{{ relativeAge(snap.created_at) }}</span>
                <span class="lvm-tl-sep">·</span>
                <span>{{ formatDate(snap.created_at) }}</span>
              </div>
              <div class="lvm-tl-usage">
                <span class="lvm-tl-size">{{ snap.size }}</span>
                <div class="lvm-usage-bar" title="Espace consommé par les modifications depuis ce point">
                  <div class="lvm-usage-fill" :style="{ width: (parseFloat(snap.data_percent) || 0) + '%' }"
                       :class="usageClass(snap.data_percent)"></div>
                </div>
                <span class="lvm-usage-pct" :class="usageClass(snap.data_percent)">{{ snap.data_percent || '0' }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════ HOW IT WORKS (friendly) ════════ -->
    <div class="lvm-info-box">
      <div class="lvm-info-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Comment ça marche, en 30 secondes
      </div>
      <div class="lvm-info-grid">
        <div class="lvm-info-step">
          <div class="lvm-step-num">1</div>
          <div>
            <strong>📸 Photo instantanée</strong>
            <span>On prend une "photo" de votre système en ~8 secondes. Aucun service ne s'arrête, vos clients ne voient rien.</span>
          </div>
        </div>
        <div class="lvm-info-step">
          <div class="lvm-step-num">2</div>
          <div>
            <strong>🔒 Vos données sont gelées</strong>
            <span>Tout changement après ce point est tracé séparément. La version originale reste intacte, prête à revenir.</span>
          </div>
        </div>
        <div class="lvm-info-step">
          <div class="lvm-step-num">3</div>
          <div>
            <strong>↩️ Retour en arrière</strong>
            <span>Un clic sur "Restaurer" et votre Asguard revient exactement à l'état du point choisi. Comme une machine à remonter le temps.</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════ CREATE DIALOG ════════ -->
    <Transition name="lvm-modal">
      <div class="lvm-modal-overlay" v-if="showCreateDialog" @click.self="showCreateDialog = false">
        <div class="lvm-modal">
          <div class="lvm-modal-header">
            <div class="lvm-modal-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            </div>
            <div>
              <div class="lvm-modal-title">Créer un point de restauration</div>
              <div class="lvm-modal-sub">Photo instantanée de votre système</div>
            </div>
          </div>
          <div class="lvm-modal-body">
            <div class="lvm-form-field">
              <label>Nom du point <span class="lvm-optional">(facultatif)</span></label>
              <input v-model="newSnapName" placeholder="ex: avant-mise-a-jour" class="lvm-input" maxlength="32"/>
              <span class="lvm-hint">💡 Donnez-lui un nom évocateur. Auto-généré si laissé vide.</span>
            </div>
            <div class="lvm-form-field">
              <label>Pourquoi créez-vous ce point ?</label>
              <textarea v-model="newSnapDesc" placeholder="ex: Configuration stable avant ajout des règles VPN..." class="lvm-textarea" rows="3"></textarea>
              <span class="lvm-hint">Cette note vous aidera à savoir quel point restaurer plus tard.</span>
            </div>
            <div class="lvm-modal-info">
              <div class="lvm-modal-info-row">
                <span>⏱️ Durée estimée</span>
                <strong>~{{ vmInfo.snapshot_estimated_seconds || 8 }} secondes</strong>
              </div>
              <div class="lvm-modal-info-row">
                <span>💾 Espace réservé</span>
                <strong>{{ config.snap_size_gb || 4 }} Go</strong>
              </div>
              <div class="lvm-modal-info-row">
                <span>✅ Espace disponible</span>
                <strong>{{ vmInfo.vg?.vg_free || '—' }}</strong>
              </div>
            </div>
          </div>
          <div class="lvm-modal-footer">
            <button class="lvm-btn-ghost" @click="showCreateDialog = false">Annuler</button>
            <button class="lvm-btn-primary" @click="createSnapshot" :disabled="creating">
              <span v-if="creating" class="lvm-spinner-sm"></span>
              {{ creating ? 'Création en cours…' : 'Créer maintenant' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ════════ RESTORE CONFIRM ════════ -->
    <Transition name="lvm-modal">
      <div class="lvm-modal-overlay" v-if="snapToRestore" @click.self="snapToRestore = null">
        <div class="lvm-modal lvm-modal-restore">
          <div class="lvm-modal-header">
            <div class="lvm-modal-icon warning">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/></svg>
            </div>
            <div>
              <div class="lvm-modal-title">Revenir à ce point ?</div>
              <div class="lvm-modal-sub">Action irréversible — confirmation requise</div>
            </div>
          </div>
          <div class="lvm-modal-body">
            <div class="lvm-restore-info">
              <div class="lvm-restore-snap-name">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#7c3aed"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
                {{ snapToRestore?.snap_id }}
              </div>
              <div class="lvm-restore-desc">{{ snapToRestore?.description || 'Aucune description' }}</div>
              <div class="lvm-restore-date">📅 Créé {{ relativeAge(snapToRestore?.created_at) }} · {{ formatDate(snapToRestore?.created_at) }}</div>
            </div>

            <div class="lvm-restore-explain">
              <strong>Que va-t-il se passer ?</strong>
              <ol>
                <li>Le système va revenir à l'état exact de ce point</li>
                <li>Toutes les modifications faites <strong>après</strong> seront perdues</li>
                <li>Asguard reste accessible pendant l'opération (~30s)</li>
              </ol>
            </div>

            <div class="lvm-restore-warning">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <span>Conseil : créez d'abord un nouveau point pour sauvegarder l'état actuel, au cas où.</span>
            </div>
          </div>
          <div class="lvm-modal-footer">
            <button class="lvm-btn-ghost" @click="snapToRestore = null">Annuler</button>
            <button class="lvm-btn-danger" @click="doRestore" :disabled="restoring">
              <span v-if="restoring" class="lvm-spinner-sm"></span>
              {{ restoring ? 'Restauration…' : 'Oui, restaurer ce point' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ════════ DELETE CONFIRM ════════ -->
    <Transition name="lvm-modal">
      <div class="lvm-modal-overlay" v-if="snapToDelete" @click.self="snapToDelete = null">
        <div class="lvm-modal">
          <div class="lvm-modal-header">
            <div class="lvm-modal-icon danger">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </div>
            <div>
              <div class="lvm-modal-title">Supprimer ce point ?</div>
              <div class="lvm-modal-sub"><code>{{ snapToDelete?.snap_id }}</code></div>
            </div>
          </div>
          <div class="lvm-modal-body">
            <p style="color:#475569;font-size:14px;line-height:1.55;margin:0;">
              Ce point de restauration sera définitivement supprimé et son espace de stockage sera libéré.
              <br><br>
              <strong style="color:#dc2626;">Vous ne pourrez plus revenir à cet état.</strong>
            </p>
          </div>
          <div class="lvm-modal-footer">
            <button class="lvm-btn-ghost" @click="snapToDelete = null">Annuler</button>
            <button class="lvm-btn-danger" @click="doDelete">Supprimer définitivement</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script>
import axios from 'axios'

const API = '/backup'

export default {
  name: 'VmSnapshot',
  data() {
    return {
      vmInfo:            {},
      config:            {},
      snapshots:         [],
      loading:           false,
      creating:          false,
      restoring:         false,
      showCreateDialog:  false,
      showConfig:        false,
      showAdvanced:      false,
      newSnapName:       '',
      newSnapDesc:       '',
      snapToRestore:     null,
      snapToDelete:      null,
      activeJob:         null,
      // Structured error payload from the backend when create fails for a
      // recoverable reason (insufficient_space). Drives the actionable
      // dialog that lists existing snapshots the user can delete to free
      // the space and retry with one click.
      spaceError:        null,
      deletingSnapId:    null,
      jobPollTimer:      null,
      jobStartTime:      null,
      lastRestoreBanner: null,
      pollErrorCount:    0,
      restorePollErrors: 0,   // surfaced in the full-screen restore overlay
      editConfig:        {},
      now:               Date.now(),
      nowTimer:          null,
      coverage:          { level: 'unknown', coverage_pct: 0, migrated: 0, applicable: 0, items: [] },
      showCoverageDetails: false,
      showPlanModal:     false,
      migrationPlan:     null,
    }
  },

  computed: {
    lvmOk() {
      return this.vmInfo?.lvm_available === true
    },
    diskBarClass() {
      const pct = parseFloat(this.vmInfo?.disk_usage?.use_percent) || 0
      if (pct > 85) return 'danger'
      if (pct > 60) return 'warn'
      return 'ok'
    },
    jobProgressPct() {
      if (!this.activeJob || !this.jobStartTime) return 5
      const est = this.activeJob.estimated_seconds || 10
      const elapsed = (Date.now() - this.jobStartTime) / 1000
      return Math.min(95, Math.round((elapsed / est) * 100))
    },
    // Restore overlay: prefer real progress reported by the backend job
    // (activeJob.progress_pct), fall back to a time-based estimate so the
    // bar still moves even when the poll endpoint is temporarily unreachable.
    // We cap the time fallback at 85 % so the bar never lies about being
    // "almost done" — the last 15 % must come from a real backend signal.
    restoreOverlayPct() {
      if (this.activeJob?.status === 'done') return 100
      if (Number.isFinite(this.activeJob?.progress_pct)) {
        return Math.max(5, Math.min(99, Math.round(this.activeJob.progress_pct)))
      }
      if (!this.jobStartTime) return 8
      const elapsed = (Date.now() - this.jobStartTime) / 1000
      const est = this.activeJob?.estimated_seconds || 120
      // Cap at 85 % until we hear "done" from the backend.
      return Math.max(8, Math.min(85, Math.round((elapsed / est) * 100)))
    },
    // Phase checklist shown inside the overlay. ONLY the backend's reported
    // phases mark a step "done" — the time-based "active" indicator is just
    // a visual hint of where we likely are, never a "done" promise. This
    // prevents the UX bug where the bar shows 95 % + all-green-checkmarks
    // while the job is actually still running in the background.
    restoreOverlayPhases() {
      const standard = [
        { key: 'quiesce',    label: 'Arrêt des services + container PostgreSQL' },
        { key: 'umount',     label: 'Démontage des binds et du volume' },
        { key: 'merge',      label: 'Fusion LVM (snapshot → origine)' },
        { key: 'reactivate', label: 'Réactivation du volume' },
        { key: 'remount',    label: 'Remontage et rebinds' },
        { key: 'restart',    label: 'Redémarrage services + PostgreSQL' },
        { key: 'resync',     label: 'Resync DB → kernel (rules, NAT, routing)' },
        { key: 'recreate',   label: 'Recréation du snapshot (préservation)' },
      ]
      const reportedKeys = new Set((this.activeJob?.phases || [])
        .filter(p => p.status === 'done').map(p => p.key))
      const allDone = this.activeJob?.status === 'done'

      // Time-based "best guess" of where we likely are now, used only to
      // highlight an "active" pulse when the backend has nothing to say.
      const elapsed = this.jobStartTime ? (Date.now() - this.jobStartTime) / 1000 : 0
      const est     = this.activeJob?.estimated_seconds || 120
      const guessedActiveIdx = Math.min(
        standard.length - 1,
        Math.floor((elapsed / est) * standard.length)
      )

      return standard.map((s, i) => {
        const done = allDone || reportedKeys.has(s.key)
        const active = !done && i === guessedActiveIdx
        return { ...s, done, active }
      })
    },
    lastSnapshot() {
      if (!this.snapshots.length) return null
      const sorted = [...this.snapshots].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      return sorted[0]
    },
    lastSnapshotAge() {
      if (!this.lastSnapshot) return 'Jamais'
      return this.relativeAge(this.lastSnapshot.created_at)
    },
    protectionLevel() {
      if (!this.lvmOk) return 'unprotected'
      if (!this.lastSnapshot) return 'unprotected'
      const ageMs = this.now - new Date(this.lastSnapshot.created_at).getTime()
      const days = ageMs / (1000 * 60 * 60 * 24)
      if (days > 7) return 'warning'
      return 'protected'
    },
    protectionStatusLabel() {
      if (!this.lvmOk) return 'Système non disponible'
      if (this.protectionLevel === 'protected') return 'Système protégé'
      if (this.protectionLevel === 'warning') return 'Protection ancienne'
      return 'Système non protégé'
    },
    protectionHeadline() {
      if (!this.lvmOk) return 'Le système de sauvegarde est inactif'
      if (this.protectionLevel === 'protected') return 'Vous pouvez modifier en toute sérénité'
      if (this.protectionLevel === 'warning') return 'Pensez à créer un nouveau point'
      return 'Créez votre premier point de restauration'
    },
    protectionSubtitle() {
      if (!this.lvmOk) return "Vérifiez que LVM est correctement configuré sur ce serveur."
      if (this.protectionLevel === 'protected') {
        return `Dernière sauvegarde ${this.lastSnapshotAge}. En cas de problème, vous reviendrez en moins d'une minute.`
      }
      if (this.protectionLevel === 'warning') {
        return `Votre dernier point date de plus de 7 jours. Une sauvegarde fraîche est recommandée avant tout changement.`
      }
      return "Une seconde suffit pour créer une 'machine à remonter le temps' avant vos changements."
    },
    coverageLevel() {
      return this.coverage?.level || 'unknown'
    },
    coverageHeadline() {
      const lvl = this.coverageLevel
      if (lvl === 'full')    return "Tous les modules critiques sont inclus dans vos points de restauration."
      if (lvl === 'partial') return "Couverture partielle — certains modules ne seront pas restaurés en cas de rollback."
      if (lvl === 'none')    return "Seul le volume de données est protégé. Les configurations système ne sont pas couvertes."
      return "Détection en cours…"
    },
  },

  mounted() {
    this.loadAll()
    this.checkLastRestore()
    this.checkRunningJobs()
    this.nowTimer = setInterval(() => { this.now = Date.now() }, 30000)
  },

  beforeUnmount() {
    clearInterval(this.jobPollTimer)
    clearInterval(this.nowTimer)
  },

  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [infoRes, listRes, covRes] = await Promise.all([
          axios.get(`${API}/vm-snapshot/info`),
          axios.get(`${API}/vm-snapshot/list`),
          axios.get(`${API}/lvm-migration/status`).catch(() => ({ data: null })),
        ])
        this.vmInfo    = infoRes.data.vm_info || {}
        this.config    = infoRes.data.config  || {}
        this.editConfig = { ...this.config }
        this.snapshots = listRes.data.snapshots || []
        if (covRes && covRes.data) {
          this.coverage = {
            level:        covRes.data.summary?.level || 'unknown',
            coverage_pct: covRes.data.summary?.coverage_pct || 0,
            migrated:     covRes.data.summary?.migrated || 0,
            applicable:   covRes.data.summary?.applicable || 0,
            inconsistent: covRes.data.summary?.inconsistent || 0,
            items:        covRes.data.items || [],
          }
        }
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    toggleCoverageDetails() {
      this.showCoverageDetails = !this.showCoverageDetails
    },

    async openPlanModal() {
      this.showPlanModal = true
      this.migrationPlan = null
      try {
        const res = await axios.get(`${API}/lvm-migration/plan`)
        this.migrationPlan = res.data
      } catch (e) {
        console.error('Plan load failed', e)
        this.migrationPlan = { actions: [], summary: {}, warnings: ['Erreur de chargement du plan.'] }
      }
    },

    coverageItemLabel(id) {
      const map = {
        nftables:     'Pare-feu (nftables)',
        asguard_etc:  'Configuration Asguard',
        backups:      'Archives de sauvegarde',
        openvpn:      'OpenVPN',
        strongswan:   'IPsec (StrongSwan)',
        suricata:     'IDS/IPS (Suricata)',
        squid:        'Proxy (Squid)',
        modsecurity:  'WAF (ModSecurity)',
      }
      return map[id] || id
    },

    coverageStateLabel(state) {
      return {
        migrated:        'Inclus',
        not_migrated:    'Non inclus',
        not_applicable:  'N/A',
        inconsistent:    'Incohérent',
      }[state] || state
    },

    planDecisionLabel(d) {
      return {
        migrate:        'Migrer',
        skip:           'Ignorer',
        manual_review:  'Revue manuelle',
      }[d] || d
    },

    humanBytes(n) {
      if (!n) return '—'
      if (n < 1024) return `${n} B`
      const units = ['KB', 'MB', 'GB', 'TB']
      let v = n
      for (const u of units) {
        v /= 1024
        if (v < 1024) return `${v.toFixed(1)} ${u}`
      }
      return `${v.toFixed(1)} PB`
    },

    async testConnection() {
      try {
        const res = await axios.post(`${API}/vm-snapshot/test-connection`)
        if (res.data.connected && res.data.lv_ok) {
          this.$message?.success('Système opérationnel — vous pouvez créer des points')
        } else {
          this.$message?.warning(res.data.error || 'Système indisponible')
        }
        await this.loadAll()
      } catch (e) {
        this.$message?.error('Erreur lors du diagnostic')
      }
    },

    openCreateDialog() {
      this.newSnapName = ''
      this.newSnapDesc = ''
      this.showCreateDialog = true
    },

    async createSnapshot() {
      this.creating = true
      this.showCreateDialog = false
      this.spaceError = null
      // Remember the inputs so the "delete + retry" path can replay the
      // exact same request without forcing the user to re-fill the form.
      this.pendingCreate = { name: this.newSnapName, description: this.newSnapDesc }
      try {
        const res = await axios.post(`${API}/vm-snapshot/create`, this.pendingCreate)
        const jobId = res.data.job_id
        this.activeJob     = { ...res.data, phase_label: 'Création du point de restauration', estimated_seconds: res.data.estimated_seconds || 10 }
        this.jobStartTime  = Date.now()
        this.pollJob(jobId, 'create')
      } catch (e) {
        this.$message?.error('Erreur lors de la création')
        this.creating = false
      }
    },

    pollJob(jobId, type) {
      clearInterval(this.jobPollTimer)
      // Transient-error tolerance: during a restore, PostgreSQL is briefly
      // down which makes any DB-backed endpoint 500. The progress endpoint
      // itself is auth-free and file-based — it should keep responding even
      // when the DB is down. The longer timeout below covers the worst case
      // where the daemon takes time to come back.
      const MAX_CONSECUTIVE_ERRORS = type === 'restore' ? 180 : 20  // ≈ 270s for restore
      this.pollErrorCount = 0
      this.restorePollErrors = 0
      this.jobPollTimer = setInterval(async () => {
        try {
          const res = await axios.get(`${API}/vm-snapshot/progress/${jobId}`, {
            timeout: 5000,
            // Ignore session cookies for this poll — the endpoint is anonymous
            // and we don't want middleware to 500 us on a DB-down window.
            withCredentials: false,
          })
          this.pollErrorCount = 0
          this.restorePollErrors = 0
          this.activeJob = res.data
          if (res.data.status !== 'running') {
            clearInterval(this.jobPollTimer)
            if (res.data.status === 'done') {
              if (type === 'restore') {
                // Restore is done. PostgreSQL is back, all daemons reloaded.
                // We do a hard reload of the SPA so every component refetches
                // its data from the rolled-back DB (no stale Vuex/Pinia state).
                this.lastRestoreBanner = { snap_id: res.data.snap_id }
                this.activeJob = res.data
                // Tiny delay so the user sees "100% — done" before reload.
                setTimeout(() => { window.location.reload() }, 1200)
                return
              }
              this.activeJob = null
              this.creating = false
              this.$message?.success(res.data.message || 'Opération réussie')
            } else if (res.data.status === 'error') {
              this.activeJob = null
              this.creating = false
              this.restoring = false
              if (type === 'create' && res.data.error_type === 'insufficient_space') {
                this.spaceError = res.data
              } else {
                this.$message?.error(res.data.error || "Erreur lors de l'opération")
              }
            }
            await this.loadAll()
          }
        } catch (e) {
          this.pollErrorCount += 1
          if (type === 'restore') this.restorePollErrors = this.pollErrorCount
          if (this.pollErrorCount >= MAX_CONSECUTIVE_ERRORS) {
            clearInterval(this.jobPollTimer)
            if (type === 'restore') {
              // Couldn't reach the progress endpoint long enough — reload
              // anyway. Either the restore finished (and we missed it) or
              // it's genuinely broken; either way the SPA's "loadAll" on
              // fresh boot is the right next move.
              window.location.reload()
              return
            }
            this.activeJob = null
            this.creating = false
            this.restoring = false
            this.$message?.error("Suivi de l'opération interrompu — actualisez la page pour voir l'état final.")
            await this.loadAll()
          }
          // else: silently retry next tick
        }
      }, 1500)
    },

    async deleteAndRetry(snapId) {
      this.deletingSnapId = snapId
      try {
        await axios.delete(`${API}/vm-snapshot/${snapId}/delete`)
        this.$message?.success(`Snapshot « ${snapId} » supprimé.`)
        await this.loadAll()
        // Re-run the original create request now that space is freed.
        const retry = this.pendingCreate || { name: this.newSnapName, description: this.newSnapDesc }
        this.spaceError = null
        this.newSnapName = retry.name
        this.newSnapDesc = retry.description
        await this.createSnapshot()
      } catch (e) {
        this.$message?.error('Erreur lors de la suppression du snapshot')
      } finally {
        this.deletingSnapId = null
      }
    },

    dismissSpaceError() {
      this.spaceError = null
      this.pendingCreate = null
    },

    formatSnapSize(sizeGb) {
      const n = parseFloat(sizeGb)
      if (!isFinite(n) || n <= 0) return '—'
      return n < 1 ? `${(n * 1024).toFixed(0)} Mo` : `${n.toFixed(2)} Go`
    },

    confirmRestore(snap) {
      this.snapToRestore = snap
    },

    async doRestore() {
      const snap = this.snapToRestore
      this.snapToRestore = null
      this.restoring = true
      try {
        const res = await axios.post(`${API}/vm-snapshot/${snap.snap_id}/restore`)
        // Realistic estimate: merge (~10s) + 5 service restarts (~80s) +
        // resync pipeline (~15s) + snapshot recreation (~10s) ≈ 120s.
        this.activeJob    = { snap_id: snap.snap_id, phase_label: 'Restauration en cours…', estimated_seconds: 120 }
        this.jobStartTime = Date.now()
        this.pollJob(res.data.job_id, 'restore')
      } catch (e) {
        this.$message?.error('Erreur lors de la restauration')
        this.restoring = false
      }
    },

    confirmDelete(snap) {
      this.snapToDelete = snap
    },

    async doDelete() {
      const snap = this.snapToDelete
      this.snapToDelete = null
      try {
        await axios.delete(`${API}/vm-snapshot/${snap.snap_id}/delete`)
        this.$message?.success('Point supprimé')
        await this.loadAll()
      } catch (e) {
        this.$message?.error('Erreur lors de la suppression')
      }
    },

    async saveConfig() {
      try {
        await axios.put(`${API}/vm-snapshot/config`, this.editConfig)
        this.config = { ...this.editConfig }
        this.showConfig = false
        this.$message?.success('Réglages enregistrés')
      } catch (e) {
        this.$message?.error('Erreur lors de la sauvegarde')
      }
    },

    async checkRunningJobs() {
      try {
        const res = await axios.get(`${API}/vm-snapshot/running-jobs`)
        const jobs = res.data.jobs || []
        if (jobs.length > 0) {
          const job = jobs[0]
          this.activeJob    = job
          this.jobStartTime = Date.now()
          if (job.job_id.startsWith('snap_restore')) {
            this.restoring = true
            this.pollJob(job.job_id, 'restore')
          } else {
            this.creating = true
            this.pollJob(job.job_id, 'create')
          }
        }
      } catch (e) { /* silent */ }
    },

    async checkLastRestore() {
      try {
        const res = await axios.get(`${API}/vm-snapshot/last-restore`)
        if (res.data.restore?.status === 'done') {
          this.lastRestoreBanner = res.data.restore
        }
      } catch (e) { /* silent */ }
    },

    formatDate(iso) {
      if (!iso) return '—'
      try {
        return new Date(iso).toLocaleString('fr-FR', {
          day: '2-digit', month: '2-digit', year: 'numeric',
          hour: '2-digit', minute: '2-digit',
        })
      } catch { return iso }
    },

    relativeAge(iso) {
      if (!iso) return '—'
      const t = new Date(iso).getTime()
      if (isNaN(t)) return '—'
      const diff = Math.max(0, this.now - t)
      const s = Math.floor(diff / 1000)
      if (s < 60) return "à l'instant"
      const m = Math.floor(s / 60)
      if (m < 60) return `il y a ${m} min`
      const h = Math.floor(m / 60)
      if (h < 24) return `il y a ${h}h`
      const d = Math.floor(h / 24)
      if (d < 7) return `il y a ${d}j`
      const w = Math.floor(d / 7)
      if (w < 5) return `il y a ${w} sem.`
      const mo = Math.floor(d / 30)
      return `il y a ${mo} mois`
    },

    isRecent(snap) {
      if (!snap?.created_at) return false
      const t = new Date(snap.created_at).getTime()
      return (this.now - t) < 60 * 60 * 1000
    },

    usageClass(pct) {
      const v = parseFloat(pct) || 0
      if (v > 80) return 'danger'
      if (v > 50) return 'warn'
      return 'ok'
    },
  },
}
</script>

<style scoped>
.lvm-wrap { display: flex; flex-direction: column; gap: 18px; padding: 4px 0; }

/* ══════ HERO ══════ */
.lvm-hero {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #faf5ff 60%, #f3e8ff 100%);
  border: 1px solid #ede9fe;
  box-shadow: 0 4px 24px rgba(124, 58, 237, 0.08);
}
.lvm-hero-bg {
  position: absolute; inset: 0; pointer-events: none;
  background:
    radial-gradient(800px 200px at 100% 0%, rgba(124,58,237,0.10), transparent 60%),
    radial-gradient(500px 300px at 0% 100%, rgba(59,130,246,0.08), transparent 60%);
}
.lvm-hero-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  padding: 28px 32px;
}
.lvm-hero-left { display: flex; align-items: center; gap: 22px; flex: 1; min-width: 0; }
.lvm-hero-right { display: flex; flex-direction: column; gap: 10px; align-items: flex-end; }

/* Shield */
.lvm-shield {
  position: relative;
  width: 84px; height: 84px;
  border-radius: 22px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
}
.lvm-shield.protected { background: linear-gradient(135deg, #16a34a, #22c55e); }
.lvm-shield.warning   { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.lvm-shield.unprotected { background: linear-gradient(135deg, #94a3b8, #cbd5e1); }
.lvm-shield-pulse {
  position: absolute; inset: -4px; border-radius: 24px; opacity: 0.5;
  animation: shieldPulse 2.4s ease-in-out infinite;
}
.lvm-shield.protected .lvm-shield-pulse { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
.lvm-shield.warning   .lvm-shield-pulse { box-shadow: 0 0 0 0 rgba(245,158,11,0.4); }
.lvm-shield.unprotected .lvm-shield-pulse { display: none; }
@keyframes shieldPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }
  50%     { box-shadow: 0 0 0 14px rgba(34,197,94,0); }
}

.lvm-hero-text { min-width: 0; }
.lvm-hero-status {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase;
  color: #475569; background: rgba(255,255,255,0.7); padding: 4px 10px; border-radius: 12px;
  margin-bottom: 8px;
}
.lvm-hero-dot { width: 7px; height: 7px; border-radius: 50%; }
.lvm-hero-dot.protected { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.6); }
.lvm-hero-dot.warning { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.6); }
.lvm-hero-dot.unprotected { background: #94a3b8; }
.lvm-hero-title {
  font-size: 22px; font-weight: 800; color: #1e1b4b; margin: 0 0 6px 0;
  line-height: 1.25;
}
.lvm-hero-sub {
  font-size: 13.5px; color: #64748b; margin: 0; max-width: 540px; line-height: 1.55;
}

/* Hero CTA */
.lvm-hero-cta {
  display: flex; align-items: center; gap: 14px;
  background: linear-gradient(135deg, #6d28d9, #7c3aed);
  color: #fff; border: none;
  padding: 14px 18px 14px 16px;
  border-radius: 14px; cursor: pointer;
  box-shadow: 0 8px 22px rgba(124,58,237,0.32);
  transition: all 0.2s ease;
  min-width: 360px;
}
.lvm-hero-cta:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(124,58,237,0.42);
}
.lvm-hero-cta:disabled { opacity: 0.55; cursor: not-allowed; }
.lvm-hero-cta-icon {
  width: 42px; height: 42px;
  background: rgba(255,255,255,0.18); border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.lvm-hero-cta-text { display: flex; flex-direction: column; gap: 2px; align-items: flex-start; flex: 1; }
.lvm-hero-cta-text strong { font-size: 14px; font-weight: 700; }
.lvm-hero-cta-text span { font-size: 11.5px; opacity: 0.88; font-weight: 500; }
.lvm-hero-cta-arrow { opacity: 0.85; transition: transform 0.2s; }
.lvm-hero-cta:hover:not(:disabled) .lvm-hero-cta-arrow { transform: translateX(3px); }

.lvm-hero-mini-actions { display: flex; gap: 6px; }
.lvm-mini-btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.7); color: #6d28d9;
  border: 1px solid #e9d5ff; border-radius: 8px;
  padding: 6px 11px; font-size: 12px; font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.lvm-mini-btn:hover { background: #fff; border-color: #c4b5fd; }
.lvm-mini-btn.active { background: #7c3aed; color: #fff; border-color: #7c3aed; }

/* ══════ INSIGHT ROW ══════ */
.lvm-insight-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.lvm-insight-card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  padding: 16px 18px;
  display: flex; align-items: center; gap: 14px;
  transition: all 0.18s;
}
.lvm-insight-card:hover { border-color: #ddd6fe; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,0,0,0.04); }
.lvm-insight-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
}
.lvm-insight-icon.teal   { background: linear-gradient(135deg, #0d9488, #14b8a6); }
.lvm-insight-icon.purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
.lvm-insight-icon.green  { background: linear-gradient(135deg, #16a34a, #4ade80); }
.lvm-insight-icon.blue   { background: linear-gradient(135deg, #2563eb, #60a5fa); }
.lvm-insight-val { font-size: 19px; font-weight: 800; color: #0f172a; line-height: 1.1; }
.lvm-insight-max { font-size: 13px; color: #94a3b8; font-weight: 600; }
.lvm-insight-lbl { font-size: 11.5px; color: #64748b; margin-top: 3px; font-weight: 500; }

/* ══════ TECH PANEL ══════ */
.lvm-tech-panel {
  background: #fff;
  border: 1px dashed #c4b5fd;
  border-radius: 14px;
  padding: 18px 20px;
}
.lvm-tech-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.lvm-tech-title { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: #5b21b6; }
.lvm-tech-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.lvm-tech-pill.online { background: #dcfce7; color: #166534; }
.lvm-tech-pill.offline { background: #fee2e2; color: #991b1b; }
.lvm-dot { width: 7px; height: 7px; border-radius: 50%; }
.lvm-dot.green { background: #22c55e; }
.lvm-dot.red { background: #ef4444; }

.lvm-vol-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.lvm-vol-item { background: #f8fafc; border-radius: 8px; padding: 10px 12px; }
.lvm-vol-lbl { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 3px; }
.lvm-vol-val { font-size: 13px; font-weight: 600; color: #1e293b; }
.lvm-vol-val.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #6d28d9; }

.lvm-disk-bar-wrap { margin-top: 4px; }
.lvm-disk-bar-header { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 6px; }
.lvm-disk-pct { font-weight: 600; color: #374151; }
.lvm-disk-bar { height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.lvm-disk-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.lvm-disk-fill.ok { background: linear-gradient(90deg, #22c55e, #16a34a); }
.lvm-disk-fill.warn { background: linear-gradient(90deg, #f59e0b, #d97706); }
.lvm-disk-fill.danger { background: linear-gradient(90deg, #ef4444, #dc2626); }

/* ══════ CONFIG PANEL ══════ */
.lvm-config-panel { background: linear-gradient(135deg, #faf5ff, #ede9fe); border: 1px solid #ddd6fe; border-radius: 14px; padding: 20px; }
.lvm-config-title { font-size: 14px; font-weight: 700; color: #6d28d9; margin-bottom: 16px; display: flex; align-items: center; gap: 6px; }
.lvm-config-grid { display: grid; grid-template-columns: 1fr 1fr 1.3fr; gap: 16px; margin-bottom: 14px; }
.lvm-config-field { display: flex; flex-direction: column; gap: 6px; }
.lvm-config-field label { font-size: 12.5px; font-weight: 600; color: #374151; }
.lvm-config-hint { font-size: 11px; color: #7c6f9c; }
.lvm-config-toggle { flex-direction: row; align-items: center; justify-content: space-between; gap: 12px; background: #fff; padding: 10px 14px; border-radius: 10px; border: 1px solid #e9d5ff; }
.lvm-config-toggle > div { display: flex; flex-direction: column; gap: 3px; }
.lvm-config-actions { display: flex; gap: 8px; }

.lvm-toggle-cb { display: none; }
.lvm-toggle-label { display: inline-block; width: 42px; height: 24px; background: #d1d5db; border-radius: 12px; cursor: pointer; position: relative; transition: background 0.2s; flex-shrink: 0; }
.lvm-toggle-label::after { content: ''; position: absolute; width: 18px; height: 18px; border-radius: 50%; background: #fff; top: 3px; left: 3px; transition: left 0.2s; }
.lvm-toggle-cb:checked + .lvm-toggle-label { background: #7c3aed; }
.lvm-toggle-cb:checked + .lvm-toggle-label::after { left: 21px; }

/* ══════ PROGRESS BANNER ══════ */
.lvm-progress-banner {
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
  border: 1px solid #c4b5fd;
  border-radius: 12px;
  padding: 14px 18px;
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 4px 14px rgba(124,58,237,0.1);
}
.lvm-progress-left { display: flex; align-items: center; gap: 12px; min-width: 240px; }
.lvm-progress-title { font-size: 13.5px; font-weight: 700; color: #5b21b6; }
.lvm-progress-sub { font-size: 11.5px; color: #7c3aed; margin-top: 2px; }
.lvm-progress-bar-wrap { flex: 1; height: 8px; background: #e9d5ff; border-radius: 4px; overflow: hidden; position: relative; }
.lvm-progress-bar-fill {
  height: 100%; background: linear-gradient(90deg, #7c3aed, #a855f7); border-radius: 4px;
  transition: width 0.5s ease; position: relative;
}
.lvm-progress-bar-fill::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
.lvm-progress-pct { font-size: 13px; font-weight: 800; color: #6d28d9; min-width: 38px; text-align: right; }

/* ══════ SPACE ERROR MODAL ══════ */
.lvm-space-modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999;
  padding: 20px;
  backdrop-filter: blur(2px);
}
.lvm-space-modal {
  background: #fff;
  width: 100%;
  max-width: 620px;
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  animation: lvm-space-pop 0.22s ease-out;
}
@keyframes lvm-space-pop {
  from { transform: scale(0.94); opacity: 0; }
  to   { transform: scale(1);    opacity: 1; }
}
.lvm-space-modal-head {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 22px 24px 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-bottom: 1px solid #fed7aa;
}
.lvm-space-icon {
  flex-shrink: 0;
  width: 44px; height: 44px;
  border-radius: 12px;
  background: #f97316;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 18px rgba(249, 115, 22, 0.35);
}
.lvm-space-head-body { flex: 1; min-width: 0; }
.lvm-space-title {
  font-size: 16px; font-weight: 800; color: #7c2d12;
  margin-bottom: 4px;
}
.lvm-space-sub {
  font-size: 12.5px; color: #9a3412; line-height: 1.5;
}
.lvm-space-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}
.lvm-space-stat {
  background: #fff;
  padding: 14px 16px;
  display: flex; flex-direction: column; gap: 4px;
}
.lvm-space-stat-lbl {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
  color: #94a3b8;
}
.lvm-space-stat-val {
  font-size: 18px; font-weight: 800; color: #1e293b;
}
.lvm-space-stat-val.warn   { color: #d97706; }
.lvm-space-stat-val.danger { color: #dc2626; }

.lvm-space-action-title {
  padding: 18px 24px 10px;
  display: flex; align-items: center; gap: 8px;
  font-size: 12.5px; font-weight: 700;
  color: #1e293b;
}
.lvm-space-list {
  padding: 0 18px 18px;
  display: flex; flex-direction: column; gap: 8px;
  max-height: 280px;
  overflow-y: auto;
}
.lvm-space-snap {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: border-color 0.15s, background 0.15s;
}
.lvm-space-snap:hover { background: #f1f5f9; }
.lvm-space-snap--suggested {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-color: #fcd34d;
}
.lvm-space-snap--suggested:hover { background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%); }
.lvm-space-snap-left { flex: 1; min-width: 0; }
.lvm-space-snap-name {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin-bottom: 4px;
}
.lvm-space-snap-id {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 12px; font-weight: 700; color: #1e293b;
  background: #fff;
  padding: 2px 7px;
  border-radius: 5px;
  border: 1px solid #e2e8f0;
}
.lvm-space-snap-tag {
  font-size: 10px; font-weight: 700;
  padding: 2px 7px;
  background: #f97316; color: #fff;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.lvm-space-snap-meta {
  font-size: 11px; color: #64748b;
  display: flex; gap: 4px; flex-wrap: wrap;
}
.lvm-space-snap-right {
  display: flex; align-items: center; gap: 10px;
  flex-shrink: 0;
}
.lvm-space-snap-size {
  font-size: 13px; font-weight: 800; color: #0f172a;
  background: #fff;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.lvm-space-snap-del {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 12px; font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}
.lvm-space-snap-del:hover:not(:disabled) { background: #b91c1c; transform: translateY(-1px); }
.lvm-space-snap-del:disabled { background: #94a3b8; cursor: wait; }
.lvm-mini-spin { animation: lvm-spin 0.9s linear infinite; }
@keyframes lvm-spin { to { transform: rotate(360deg); } }

.lvm-space-empty {
  padding: 16px 24px 24px;
  font-size: 12.5px; color: #475569;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.lvm-space-modal-foot {
  padding: 14px 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex; justify-content: flex-end;
}

/* ══════ TIMELINE CARD ══════ */
.lvm-timeline-card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  overflow: hidden;
}
.lvm-timeline-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #f1f5f9;
}
.lvm-timeline-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: #1e293b; }
.lvm-table-count { background: #ede9fe; color: #6d28d9; font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 10px; }

.lvm-timeline { padding: 20px 24px 24px 24px; }
.lvm-tl-item { display: flex; gap: 14px; }
.lvm-tl-axis { display: flex; flex-direction: column; align-items: center; padding-top: 6px; }
.lvm-tl-dot {
  width: 14px; height: 14px; border-radius: 50%;
  background: #7c3aed; border: 3px solid #ede9fe; flex-shrink: 0;
  box-shadow: 0 0 0 4px rgba(124,58,237,0.08);
}
.lvm-tl-dot.warn { background: #f59e0b; border-color: #fef3c7; box-shadow: 0 0 0 4px rgba(245,158,11,0.08); }
.lvm-tl-dot.danger { background: #ef4444; border-color: #fee2e2; box-shadow: 0 0 0 4px rgba(239,68,68,0.08); }
.lvm-tl-line { width: 2px; flex: 1; background: linear-gradient(180deg, #ede9fe, #f1f5f9); margin: 6px 0; min-height: 18px; }

.lvm-tl-card {
  flex: 1;
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 14px;
  transition: all 0.18s;
}
.lvm-tl-card:hover { border-color: #ddd6fe; box-shadow: 0 4px 14px rgba(0,0,0,0.04); }
.lvm-tl-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.lvm-tl-meta { min-width: 0; flex: 1; }
.lvm-tl-name { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 5px; }
.lvm-tl-icon { width: 22px; height: 22px; background: #ede9fe; color: #7c3aed; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.lvm-tl-name code { font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: #5b21b6; background: #f5f3ff; padding: 2px 8px; border-radius: 5px; font-weight: 600; }
.lvm-tl-badge-fresh { background: linear-gradient(135deg, #16a34a, #22c55e); color: #fff; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px; letter-spacing: 0.3px; }
.lvm-tl-desc { font-size: 13px; color: #475569; line-height: 1.45; }

.lvm-tl-actions { display: flex; gap: 6px; flex-shrink: 0; }
.lvm-action-btn { display: flex; align-items: center; gap: 5px; padding: 6px 11px; border-radius: 7px; font-size: 12px; font-weight: 600; border: none; cursor: pointer; transition: all 0.15s; }
.lvm-action-btn.restore { background: #ede9fe; color: #6d28d9; }
.lvm-action-btn.restore:hover:not(:disabled) { background: #7c3aed; color: #fff; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(124,58,237,0.3); }
.lvm-action-btn.delete { background: #fee2e2; color: #dc2626; padding: 6px 9px; }
.lvm-action-btn.delete:hover:not(:disabled) { background: #dc2626; color: #fff; }
.lvm-action-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.lvm-tl-foot {
  display: flex; justify-content: space-between; align-items: center; gap: 14px;
  padding-top: 10px; border-top: 1px dashed #e2e8f0;
}
.lvm-tl-info { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: #94a3b8; }
.lvm-tl-age { color: #6d28d9; font-weight: 600; }
.lvm-tl-sep { opacity: 0.6; }
.lvm-tl-usage { display: flex; align-items: center; gap: 8px; }
.lvm-tl-size { background: #dbeafe; color: #1d4ed8; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.lvm-usage-bar { width: 80px; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }
.lvm-usage-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
.lvm-usage-fill.ok { background: #22c55e; }
.lvm-usage-fill.warn { background: #f59e0b; }
.lvm-usage-fill.danger { background: #ef4444; }
.lvm-usage-pct { font-size: 11px; font-weight: 700; min-width: 36px; text-align: right; }
.lvm-usage-pct.ok { color: #16a34a; }
.lvm-usage-pct.warn { color: #d97706; }
.lvm-usage-pct.danger { color: #dc2626; }

/* ══════ EMPTY STATE ══════ */
.lvm-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 36px 24px 32px 24px; gap: 8px; color: #94a3b8;
}
.lvm-empty-illu { position: relative; margin-bottom: 4px; }
.lvm-empty-glow {
  position: absolute; inset: -10px; border-radius: 50%;
  background: radial-gradient(circle, rgba(167,139,250,0.18), transparent 70%);
  z-index: -1;
}
.lvm-empty p { font-size: 15px; font-weight: 700; color: #1e293b; margin: 8px 0 2px 0; }
.lvm-empty > span { font-size: 12.5px; text-align: center; color: #64748b; max-width: 460px; }

.lvm-usecase-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  margin: 22px 0 18px 0; width: 100%; max-width: 760px;
}
.lvm-usecase {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  background: linear-gradient(135deg, #faf5ff, #fff);
  border: 1px solid #ede9fe; border-radius: 12px;
  padding: 16px 14px;
}
.lvm-usecase-emoji { font-size: 28px; margin-bottom: 6px; }
.lvm-usecase strong { font-size: 13px; color: #1e1b4b; margin-bottom: 4px; }
.lvm-usecase span { font-size: 11.5px; color: #64748b; line-height: 1.45; }

.lvm-empty-cta {
  display: inline-flex; align-items: center; gap: 6px;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: #fff; border: none; padding: 10px 18px;
  border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer;
  box-shadow: 0 6px 16px rgba(124,58,237,0.3);
  transition: all 0.18s;
}
.lvm-empty-cta:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(124,58,237,0.4); }
.lvm-empty-cta:disabled { opacity: 0.5; cursor: not-allowed; }

/* ══════ RESTORE / SUCCESS BANNERS ══════ */
.lvm-restore-banner {
  display: flex; align-items: center; gap: 14px;
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  border: 1px solid #86efac; border-radius: 12px;
  padding: 12px 16px;
}
.lvm-banner-icon-wrap {
  width: 36px; height: 36px; background: #16a34a; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.lvm-banner-text { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.lvm-banner-text strong { font-size: 13px; color: #166534; }
.lvm-banner-text span { font-size: 12px; color: #15803d; }
.lvm-banner-text code { background: rgba(22,101,52,0.1); padding: 1px 6px; border-radius: 4px; font-family: monospace; }
.lvm-banner-close { background: none; border: none; cursor: pointer; color: #166534; padding: 4px; display: flex; }

/* ══════ INFO BOX ══════ */
.lvm-info-box {
  background: linear-gradient(135deg, #f5f3ff, #ede9fe);
  border: 1px solid #ddd6fe;
  border-radius: 14px; padding: 22px;
}
.lvm-info-title { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: #5b21b6; margin-bottom: 16px; }
.lvm-info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.lvm-info-step { display: flex; align-items: flex-start; gap: 12px; font-size: 12.5px; color: #4b5563; line-height: 1.55; }
.lvm-info-step strong { display: block; color: #1e1b4b; font-size: 13px; margin-bottom: 3px; }
.lvm-step-num {
  width: 28px; height: 28px; background: linear-gradient(135deg, #7c3aed, #a78bfa);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 800; flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(124,58,237,0.3);
}

/* ══════ MODALS ══════ */
.lvm-modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.55); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; z-index: 999; }
.lvm-modal { background: #fff; border-radius: 16px; width: 480px; max-width: 96vw; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,0.18); }
.lvm-modal-restore { width: 520px; }
.lvm-modal-header { display: flex; align-items: center; gap: 14px; padding: 20px 24px; border-bottom: 1px solid #f1f5f9; }
.lvm-modal-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: #ede9fe; color: #7c3aed; flex-shrink: 0; }
.lvm-modal-icon.warning { background: #fef3c7; color: #d97706; }
.lvm-modal-icon.danger  { background: #fee2e2; color: #dc2626; }
.lvm-modal-title { font-size: 16px; font-weight: 700; color: #0f172a; }
.lvm-modal-sub { font-size: 12.5px; color: #94a3b8; margin-top: 3px; }
.lvm-modal-body { padding: 22px 24px; }
.lvm-modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 16px 24px; border-top: 1px solid #f1f5f9; background: #f8fafc; }

.lvm-form-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.lvm-form-field label { font-size: 13px; font-weight: 600; color: #1e293b; }
.lvm-optional { font-size: 11px; color: #94a3b8; font-weight: 400; }
.lvm-hint { font-size: 11.5px; color: #7c6f9c; }

.lvm-modal-info {
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
  border: 1px solid #e9d5ff;
  border-radius: 10px; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 6px;
}
.lvm-modal-info-row { display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; color: #5b21b6; }
.lvm-modal-info-row strong { color: #1e1b4b; }

.lvm-restore-info { background: linear-gradient(135deg, #faf5ff, #ede9fe); border: 1px solid #e9d5ff; border-radius: 10px; padding: 14px; margin-bottom: 14px; }
.lvm-restore-snap-name { display: flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 700; color: #5b21b6; margin-bottom: 6px; }
.lvm-restore-desc { font-size: 13px; color: #475569; margin-bottom: 6px; }
.lvm-restore-date { font-size: 12px; color: #94a3b8; }

.lvm-restore-explain { background: #f8fafc; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; }
.lvm-restore-explain strong { display: block; font-size: 12.5px; color: #1e293b; margin-bottom: 6px; }
.lvm-restore-explain ol { margin: 0; padding-left: 20px; font-size: 12.5px; color: #475569; line-height: 1.7; }
.lvm-restore-explain ol li strong { display: inline; color: #dc2626; }

.lvm-restore-warning {
  display: flex; align-items: center; gap: 8px;
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px;
  padding: 10px 12px; font-size: 12.5px; color: #92400e; line-height: 1.5;
}
.lvm-restore-warning svg { flex-shrink: 0; color: #d97706; }

/* ══════ INPUTS ══════ */
.lvm-input { width: 100%; padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; outline: none; box-sizing: border-box; transition: all 0.15s; }
.lvm-input:focus { border-color: #7c3aed; box-shadow: 0 0 0 3px rgba(124,58,237,0.12); }
.lvm-textarea { width: 100%; padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; outline: none; resize: vertical; box-sizing: border-box; font-family: inherit; transition: all 0.15s; }
.lvm-textarea:focus { border-color: #7c3aed; box-shadow: 0 0 0 3px rgba(124,58,237,0.12); }

/* ══════ BUTTONS ══════ */
.lvm-btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 9px 18px; background: linear-gradient(135deg, #7c3aed, #6d28d9); color: #fff; border: none; border-radius: 9px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.lvm-btn-primary:hover:not(:disabled) { box-shadow: 0 6px 14px rgba(124,58,237,0.32); transform: translateY(-1px); }
.lvm-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.lvm-btn-ghost { padding: 9px 18px; background: transparent; color: #64748b; border: 1px solid #e2e8f0; border-radius: 9px; font-size: 13px; cursor: pointer; transition: all 0.15s; }
.lvm-btn-ghost:hover { background: #f8fafc; }
.lvm-btn-danger { padding: 9px 18px; background: #dc2626; color: #fff; border: none; border-radius: 9px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s; }
.lvm-btn-danger:hover:not(:disabled) { background: #b91c1c; box-shadow: 0 6px 14px rgba(220,38,38,0.3); }
.lvm-btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
.lvm-btn-icon { width: 32px; height: 32px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #64748b; transition: all 0.2s; }
.lvm-btn-icon:hover { background: #ede9fe; color: #7c3aed; }
.lvm-btn-icon.spinning svg { animation: spin 1s linear infinite; }

/* ══════ SPINNERS ══════ */
.lvm-spinner { width: 22px; height: 22px; border: 3px solid #e9d5ff; border-top-color: #7c3aed; border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0; }
.lvm-spinner-sm { width: 13px; height: 13px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ══════ TRANSITIONS ══════ */
.lvm-fade-enter-active, .lvm-fade-leave-active { transition: opacity 0.3s; }
.lvm-fade-enter-from, .lvm-fade-leave-to { opacity: 0; }
.lvm-slide-enter-active, .lvm-slide-leave-active { transition: all 0.3s ease; }
.lvm-slide-enter-from, .lvm-slide-leave-to { opacity: 0; transform: translateY(-8px); }
.lvm-modal-enter-active, .lvm-modal-leave-active { transition: all 0.25s; }
.lvm-modal-enter-from, .lvm-modal-leave-to { opacity: 0; }
.lvm-modal-enter-from .lvm-modal, .lvm-modal-leave-to .lvm-modal { transform: scale(0.95) translateY(-10px); }

/* ══════ FULL-SCREEN RESTORE OVERLAY ══════ */
.lvm-restore-overlay {
  position: fixed; inset: 0; z-index: 99999;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.lvm-restore-overlay-card {
  background: linear-gradient(135deg, #ffffff 0%, #faf5ff 100%);
  border: 1px solid #c4b5fd;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(124, 58, 237, 0.4);
  padding: 32px 36px;
  max-width: 560px; width: 100%;
  text-align: center;
}
.lvm-restore-overlay-icon {
  width: 72px; height: 72px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  animation: spin 2.4s linear infinite;
}
.lvm-restore-overlay-title {
  font-size: 20px; font-weight: 700; color: #1f2937;
  margin-bottom: 8px;
}
.lvm-restore-overlay-sub {
  font-size: 13px; color: #4b5563; line-height: 1.55;
  margin-bottom: 20px;
}
.lvm-restore-overlay-sub code {
  background: rgba(124, 58, 237, 0.12); color: #6d28d9;
  padding: 1px 6px; border-radius: 4px; font-size: 12px;
}
.lvm-restore-overlay-bar {
  height: 8px; background: #ede9fe; border-radius: 999px;
  overflow: hidden; margin-bottom: 6px;
}
.lvm-restore-overlay-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #a78bfa);
  border-radius: 999px;
  transition: width 0.5s ease;
}
.lvm-restore-overlay-pct {
  font-size: 12px; font-weight: 700; color: #6d28d9;
  margin-bottom: 18px;
  font-variant-numeric: tabular-nums;
}
.lvm-restore-overlay-phases {
  text-align: left;
  background: #fff;
  border: 1px solid #ede9fe;
  border-radius: 10px;
  padding: 10px 12px;
  display: flex; flex-direction: column; gap: 6px;
  margin-bottom: 14px;
}
.lvm-restore-overlay-phase {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #9ca3af;
  transition: color 0.3s;
}
.lvm-restore-overlay-phase-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #e5e7eb;
  flex-shrink: 0;
  transition: background 0.3s, box-shadow 0.3s;
}
.lvm-restore-overlay-phase.active { color: #6d28d9; font-weight: 600; }
.lvm-restore-overlay-phase.active .lvm-restore-overlay-phase-dot {
  background: #7c3aed;
  box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.2);
  animation: pulse 1.4s ease-in-out infinite;
}
.lvm-restore-overlay-phase.done { color: #047857; }
.lvm-restore-overlay-phase.done .lvm-restore-overlay-phase-dot {
  background: #10b981;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.2); }
  50%      { box-shadow: 0 0 0 7px rgba(124, 58, 237, 0.0); }
}
.lvm-restore-overlay-footer {
  font-size: 11.5px; color: #6b7280;
  padding-top: 8px;
  border-top: 1px dashed #e5e7eb;
}

/* ══════ COVERAGE CARD ══════ */
.lvm-coverage-card {
  background: #fff; border-radius: 14px; padding: 18px 20px;
  border: 1px solid #e2e8f0; margin-bottom: 18px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.lvm-coverage-card.cov-full    { border-left: 4px solid #10b981; }
.lvm-coverage-card.cov-partial { border-left: 4px solid #f59e0b; }
.lvm-coverage-card.cov-none    { border-left: 4px solid #ef4444; }

.lvm-cov-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 12px; flex-wrap: wrap; }
.lvm-cov-title-wrap { display: flex; align-items: center; gap: 12px; }
.lvm-cov-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.lvm-cov-icon.cov-full    { background: #d1fae5; color: #065f46; }
.lvm-cov-icon.cov-partial { background: #fef3c7; color: #92400e; }
.lvm-cov-icon.cov-none    { background: #fee2e2; color: #991b1b; }
.lvm-cov-title { font-size: 14px; font-weight: 700; color: #0f172a; }
.lvm-cov-sub   { font-size: 12.5px; color: #64748b; margin-top: 2px; max-width: 560px; }

.lvm-cov-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.lvm-cov-pill {
  font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 999px;
  background: #f1f5f9; color: #475569;
}
.lvm-cov-pill.cov-full    { background: #d1fae5; color: #065f46; }
.lvm-cov-pill.cov-partial { background: #fef3c7; color: #92400e; }
.lvm-cov-pill.cov-none    { background: #fee2e2; color: #991b1b; }

.lvm-cov-bar { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.lvm-cov-bar-fill { height: 100%; transition: width 0.5s; border-radius: 3px; }
.lvm-cov-bar-fill.cov-full    { background: linear-gradient(90deg, #10b981, #34d399); }
.lvm-cov-bar-fill.cov-partial { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.lvm-cov-bar-fill.cov-none    { background: linear-gradient(90deg, #ef4444, #f87171); }

.lvm-cov-items { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 14px; }
.lvm-cov-item {
  display: flex; gap: 10px; align-items: center;
  padding: 10px 12px; border-radius: 8px;
  background: #f8fafc; border: 1px solid #f1f5f9;
}
.lvm-cov-item.state-migrated       { background: #ecfdf5; border-color: #a7f3d0; }
.lvm-cov-item.state-not_migrated   { background: #fef2f2; border-color: #fecaca; }
.lvm-cov-item.state-not_applicable { background: #f8fafc; opacity: 0.6; }
.lvm-cov-item.state-inconsistent   { background: #fef3c7; border-color: #fde68a; }
.lvm-cov-item-icon { width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.lvm-cov-item.state-migrated      .lvm-cov-item-icon { color: #059669; }
.lvm-cov-item.state-not_migrated  .lvm-cov-item-icon { color: #dc2626; }
.lvm-cov-item.state-not_applicable .lvm-cov-item-icon { color: #94a3b8; }
.lvm-cov-item.state-inconsistent  .lvm-cov-item-icon { color: #d97706; }
.lvm-cov-item-body { flex: 1; min-width: 0; }
.lvm-cov-item-id  { font-size: 12.5px; font-weight: 700; color: #0f172a; }
.lvm-cov-item-src { font-size: 11px; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lvm-cov-item-state { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.lvm-cov-state-pill { font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.lvm-cov-state-pill.state-migrated      { background: #d1fae5; color: #065f46; }
.lvm-cov-state-pill.state-not_migrated  { background: #fee2e2; color: #991b1b; }
.lvm-cov-state-pill.state-not_applicable { background: #e2e8f0; color: #475569; }
.lvm-cov-state-pill.state-inconsistent  { background: #fef3c7; color: #92400e; }
.lvm-cov-size { font-size: 10.5px; color: #94a3b8; font-weight: 600; }

/* ══════ PLAN MODAL ══════ */
.lvm-modal-overlay {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 24px;
}
.lvm-modal {
  background: #fff; border-radius: 16px; max-width: 520px; width: 100%;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.3);
  max-height: 90vh; display: flex; flex-direction: column;
}
.lvm-modal-wide { max-width: 880px; }
.lvm-modal-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 18px 22px; border-bottom: 1px solid #f1f5f9; gap: 16px;
}
.lvm-modal-title { font-size: 15px; font-weight: 700; color: #0f172a; }
.lvm-modal-sub   { font-size: 12px; color: #64748b; margin-top: 4px; max-width: 600px; line-height: 1.5; }
.lvm-modal-close {
  background: none; border: none; font-size: 24px; line-height: 1;
  color: #64748b; cursor: pointer; padding: 4px 10px; border-radius: 6px;
}
.lvm-modal-close:hover { background: #f1f5f9; }
.lvm-modal-foot {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 22px; border-top: 1px solid #f1f5f9; gap: 12px; flex-wrap: wrap;
}
.lvm-plan-note { font-size: 11.5px; color: #94a3b8; font-style: italic; }

.lvm-plan-body { padding: 18px 22px; overflow-y: auto; }
.lvm-plan-loading { padding: 40px; text-align: center; color: #64748b; }

.lvm-plan-summary {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;
  margin-bottom: 14px;
}
.lvm-plan-stat {
  background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 10px;
  padding: 10px 12px; text-align: center;
}
.lvm-plan-stat-val { display: block; font-size: 16px; font-weight: 800; color: #0f172a; }
.lvm-plan-stat-lbl { display: block; font-size: 10.5px; color: #64748b; margin-top: 3px; }

.lvm-plan-warnings {
  background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 8px;
  padding: 10px 14px; margin-bottom: 14px; font-size: 12.5px; color: #78350f;
}
.lvm-plan-warn-title { font-weight: 700; margin-bottom: 4px; }
.lvm-plan-warnings ul { margin: 0; padding-left: 18px; }

.lvm-plan-safety {
  display: flex; align-items: center; gap: 8px;
  background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46;
  padding: 10px 14px; border-radius: 8px; margin-bottom: 14px;
  font-size: 12.5px;
}

.lvm-plan-actions-list { display: flex; flex-direction: column; gap: 8px; }
.lvm-plan-action {
  border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px;
  background: #fff;
}
.lvm-plan-action.decision-migrate       { border-left: 3px solid #3b82f6; }
.lvm-plan-action.decision-skip          { border-left: 3px solid #94a3b8; opacity: 0.85; }
.lvm-plan-action.decision-manual_review { border-left: 3px solid #f59e0b; }

.lvm-plan-action-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.lvm-plan-action-id { font-size: 13px; color: #0f172a; display: flex; align-items: center; gap: 8px; }
.lvm-plan-decision {
  font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 10px;
  background: #f1f5f9; color: #475569;
}
.lvm-plan-decision.decision-migrate       { background: #dbeafe; color: #1d4ed8; }
.lvm-plan-decision.decision-skip          { background: #e2e8f0; color: #475569; }
.lvm-plan-decision.decision-manual_review { background: #fef3c7; color: #92400e; }
.lvm-plan-action-src { font-size: 11px; color: #64748b; margin-top: 4px; word-break: break-all; }
.lvm-plan-reason   { font-size: 11.5px; color: #64748b; font-style: italic; margin-top: 4px; }

.lvm-plan-steps { margin-top: 6px; font-size: 11.5px; }
.lvm-plan-steps summary { cursor: pointer; color: #6366f1; font-weight: 600; }
.lvm-plan-steps ol { margin: 6px 0 0 0; padding-left: 22px; color: #475569; }
.lvm-plan-steps li { padding: 2px 0; word-break: break-all; }

.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

/* ══════ RESPONSIVE ══════ */
@media (max-width: 1100px) {
  .lvm-hero-content { flex-direction: column; align-items: flex-start; gap: 22px; }
  .lvm-hero-right { width: 100%; align-items: stretch; }
  .lvm-hero-cta { min-width: 0; width: 100%; }
  .lvm-insight-row { grid-template-columns: repeat(2, 1fr); }
  .lvm-vol-grid, .lvm-info-grid, .lvm-usecase-grid { grid-template-columns: 1fr; }
  .lvm-config-grid { grid-template-columns: 1fr; }
}
</style>
