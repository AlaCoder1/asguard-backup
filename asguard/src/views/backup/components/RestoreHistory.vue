<template>
  <div class="restore-history-page">

    <!-- Loading overlay -->
    <transition name="fade">
      <div v-if="loading" class="rh-loading-overlay">
        <div class="rh-loading-card">
          <div class="rh-spinner"></div>
          <span>Chargement de l'historique…</span>
        </div>
      </div>
    </transition>

    <!-- Stats bar -->
    <div class="rh-stats-bar">
      <div class="rh-stat-card">
        <span class="rh-stat-value">{{ stats.total }}</span>
        <span class="rh-stat-label">Total</span>
      </div>
      <div class="rh-stat-card">
        <span class="rh-stat-value rh-val-blue">{{ vmSnapshotCount }}</span>
        <span class="rh-stat-label">LVM Snapshots</span>
      </div>
      <div class="rh-stat-card success">
        <span class="rh-stat-value">{{ stats.success }}</span>
        <span class="rh-stat-label">Succès</span>
      </div>
      <div class="rh-stat-card" :class="stats.failed > 0 ? 'danger' : ''">
        <span class="rh-stat-value">{{ stats.failed }}</span>
        <span class="rh-stat-label">Échecs</span>
      </div>
      <div class="rh-stat-card">
        <span class="rh-stat-value">{{ stats.success_rate }}%</span>
        <span class="rh-stat-label">Taux de succès</span>
      </div>
      <div class="rh-stat-card">
        <span class="rh-stat-value">{{ formatDuration(stats.avg_duration_seconds) }}</span>
        <span class="rh-stat-label">Durée moyenne</span>
      </div>
      <button class="rh-refresh-btn" :disabled="loading" @click="fetchHistory">
        <span>↻</span> Actualiser
      </button>
    </div>

    <!-- Filters -->
    <div class="rh-filters">
      <input
        v-model="search"
        class="rh-search"
        placeholder="Rechercher par backup ID, snapshot, mode, job…"
      />
      <div class="rh-filter-chips">
        <button
          v-for="f in statusFilters"
          :key="f.value"
          class="rh-chip"
          :class="{ active: activeFilter === f.value }"
          @click="activeFilter = f.value"
        >
          {{ f.label }}
        </button>
        <!-- Type filter -->
        <div class="rh-filter-sep"></div>
        <button
          v-for="t in typeFilters"
          :key="t.value"
          class="rh-chip rh-chip-type"
          :class="{ active: activeTypeFilter === t.value, 'vm-chip': t.value === 'vm_snapshot' }"
          @click="activeTypeFilter = t.value"
        >
          <span v-if="t.value === 'vm_snapshot'" class="rh-chip-vm-icon">⬡</span>
          {{ t.label }}
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && filteredEntries.length === 0" class="rh-empty">
      <div class="rh-empty-icon">📋</div>
      <p>Aucun restore trouvé.</p>
    </div>

    <!-- Table -->
    <div v-else class="rh-table-wrap">
      <table class="rh-table">
        <thead>
          <tr>
            <th></th>
            <th>Type</th>
            <th>Date</th>
            <th>Source</th>
            <th>Mode</th>
            <th>Statut</th>
            <th>Composants</th>
            <th>Durée</th>
            <th>Stabilisation</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="entry in filteredEntries" :key="entry.job_id">

            <!-- ── VM Snapshot restore row ── -->
            <tr
              v-if="entry.type === 'vm_snapshot'"
              class="rh-row rh-row-vm"
              :class="{ expanded: expandedJob === entry.job_id }"
              @click="toggleExpand(entry.job_id)"
            >
              <td class="rh-expand-cell">
                <span class="rh-expand-icon">{{ expandedJob === entry.job_id ? '▾' : '▸' }}</span>
              </td>
              <td>
                <span class="rh-type-badge vm">
                  <svg viewBox="0 0 14 14" fill="none" width="10" height="10" style="flex-shrink:0">
                    <rect x="1" y="3" width="12" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
                    <path d="M4 3V2M7 3V1M10 3V2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                    <path d="M4 7l2 2 4-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  LVM Snapshot
                </span>
              </td>
              <td>
                <div class="rh-date-primary">{{ formatDate(entry.started_at) }}</div>
                <div class="rh-date-secondary">{{ formatTime(entry.started_at) }}</div>
              </td>
              <td>
                <span class="rh-snap-id-badge" :title="entry.snap_id">
                  <svg viewBox="0 0 12 12" fill="none" width="9" height="9" style="flex-shrink:0;opacity:.7">
                    <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M6 4v3M6 8.5v.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                  </svg>
                  {{ shortSnapId(entry.snap_id) }}
                </span>
              </td>
              <td>
                <span class="rh-mode-badge vm_snapshot">LVM Snapshot</span>
              </td>
              <td>
                <span class="rh-status-badge" :class="entry.status">{{ statusLabel(entry.status) }}</span>
              </td>
              <td>
                <span class="rh-vm-full-pill">
                  <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                    <rect x="1" y="2" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M3 6l2 2 4-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  VM entière
                </span>
              </td>
              <td>
                <span class="rh-duration">{{ formatDuration(entry.duration_seconds) }}</span>
              </td>
              <td>
                <span class="rh-stab-badge unknown">—</span>
              </td>
            </tr>

            <!-- ── VM Snapshot expanded detail ── -->
            <tr v-if="entry.type === 'vm_snapshot' && expandedJob === entry.job_id" class="rh-detail-row rh-detail-row-vm">
              <td colspan="9">
                <div class="rh-detail-panel rh-detail-panel-vm">

                  <!-- VM restore header card -->
                  <div class="rh-vm-header-card">
                    <div class="rh-vm-header-icon">
                      <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
                        <rect x="2" y="6" width="28" height="18" rx="3" stroke="currentColor" stroke-width="1.8"/>
                        <path d="M10 17l4 4 8-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M9 6V4M16 6V2M23 6V4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                        <path d="M7 27h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                      </svg>
                    </div>
                    <div class="rh-vm-header-body">
                      <div class="rh-vm-header-title">Restauration LVM complète</div>
                      <div class="rh-vm-header-sub">
                        Volume LVM fusionné et remonté à l'état du point de restauration
                      </div>
                    </div>
                    <div class="rh-vm-header-status">
                      <span :class="['rh-vm-status-big', entry.status]">{{ statusLabel(entry.status) }}</span>
                      <span class="rh-vm-duration-big">{{ formatDuration(entry.duration_seconds) }}</span>
                    </div>
                  </div>

                  <!-- Snapshot info + timeline grid -->
                  <div class="rh-vm-detail-grid">

                    <!-- Snapshot identity -->
                    <div class="rh-vm-info-card">
                      <div class="rh-vm-card-title">
                        <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                          <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.3"/>
                          <path d="M7 4.5V7l2 1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                        </svg>
                        Snapshot restauré
                      </div>
                      <div class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Nom</span>
                        <code class="rh-vm-snap-code">{{ entry.snap_id || '—' }}</code>
                      </div>
                      <div v-if="entry.description && entry.description !== '—'" class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Description</span>
                        <span class="rh-vm-desc">{{ entry.description }}</span>
                      </div>
                      <div v-if="entry.created_by" class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Créé par</span>
                        <span class="rh-vm-creator-pill" :class="entry.created_by">
                          {{ creatorLabel(entry.created_by) }}
                        </span>
                      </div>
                      <div v-if="entry.created_at" class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Capturé le</span>
                        <span>{{ formatDateTime(entry.created_at) }}</span>
                      </div>
                      <div class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Job ID</span>
                        <code class="rh-vm-snap-code small">{{ entry.job_id || '—' }}</code>
                      </div>
                    </div>

                    <!-- Timeline -->
                    <div class="rh-vm-info-card">
                      <div class="rh-vm-card-title">
                        <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                          <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.3"/>
                          <path d="M7 4v3.5L9 9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                        </svg>
                        Chronologie
                      </div>
                      <div class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Lancé</span>
                        <span>{{ formatDateTime(entry.started_at) }}</span>
                      </div>
                      <div class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Terminé</span>
                        <span>{{ formatDateTime(entry.finished_at) || '—' }}</span>
                      </div>
                      <div class="rh-vm-info-row">
                        <span class="rh-vm-info-label">Durée</span>
                        <strong>{{ formatDuration(entry.duration_seconds) }}</strong>
                      </div>
                    </div>

                    <!-- Restored coverage — actual scope from the backend -->
                    <div class="rh-vm-info-card rh-vm-info-card--scope">
                      <div class="rh-vm-card-title">
                        <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                          <path d="M2 7l3 3 7-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Périmètre restauré
                        <span class="rh-vm-scope-count" v-if="restoredModules(entry).length">
                          {{ restoredModules(entry).length }} module<span v-if="restoredModules(entry).length>1">s</span>
                        </span>
                      </div>
                      <div class="rh-vm-scope-list" v-if="restoredModules(entry).length">
                        <div v-for="m in restoredModules(entry)" :key="m.id" class="rh-vm-scope-mod">
                          <span class="rh-vm-scope-mod-icon" :class="m.kind">
                            <span v-if="m.kind==='container'">🐳</span>
                            <span v-else-if="m.kind==='service'">⚙</span>
                            <span v-else>📁</span>
                          </span>
                          <div class="rh-vm-scope-mod-body">
                            <div class="rh-vm-scope-mod-label">{{ m.label }}</div>
                            <div class="rh-vm-scope-mod-path"><code>{{ m.path }}</code></div>
                          </div>
                          <span class="rh-vm-scope-mod-tick">✓</span>
                        </div>
                      </div>
                      <div class="rh-vm-scope-empty" v-else>
                        Aucune information de périmètre dans ce job.
                      </div>
                    </div>

                  </div>

                  <!-- Content-level proof: what the database actually rolled back -->
                  <div v-if="entry.db_changes && entry.db_changes.length" class="rh-vm-dbdiff-card">
                    <div class="rh-vm-card-title">
                      <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                        <ellipse cx="7" cy="3.5" rx="5" ry="1.8" stroke="currentColor" stroke-width="1.3"/>
                        <path d="M2 3.5v7c0 1 2.2 1.8 5 1.8s5-.8 5-1.8v-7" stroke="currentColor" stroke-width="1.3"/>
                        <path d="M2 7c0 1 2.2 1.8 5 1.8s5-.8 5-1.8" stroke="currentColor" stroke-width="1.3"/>
                      </svg>
                      Contenu effectivement restauré (base PostgreSQL)
                      <span class="rh-vm-dbdiff-count">
                        {{ dbChangesSummary(entry).tables }}
                        table<span v-if="dbChangesSummary(entry).tables>1">s</span>
                        modifiée<span v-if="dbChangesSummary(entry).tables>1">s</span>
                        / {{ dbChangesSummary(entry).scanned }} surveillée<span v-if="dbChangesSummary(entry).scanned>1">s</span>
                      </span>
                    </div>

                    <!-- Empty state when nothing changed: prove that we DID
                         check, not just hide the section. -->
                    <div v-if="!dbChangesGrouped(entry).length" class="rh-vm-dbdiff-empty">
                      <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                        <path d="M2 7l3 3 7-7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Aucune ligne supprimée ou ajoutée — la base était déjà à l'état du snapshot.
                    </div>

                    <!-- Headline summary: removed vs added rows -->
                    <div v-else class="rh-vm-dbdiff-summary">
                      <div class="rh-vm-dbdiff-stat rh-vm-dbdiff-stat--removed" v-if="dbChangesSummary(entry).removed > 0">
                        <span class="rh-vm-dbdiff-stat-num">−{{ dbChangesSummary(entry).removed }}</span>
                        <span class="rh-vm-dbdiff-stat-lbl">ligne<span v-if="dbChangesSummary(entry).removed>1">s</span> retirée<span v-if="dbChangesSummary(entry).removed>1">s</span></span>
                        <span class="rh-vm-dbdiff-stat-sub">supprimées depuis le snapshot</span>
                      </div>
                      <div class="rh-vm-dbdiff-stat rh-vm-dbdiff-stat--added" v-if="dbChangesSummary(entry).added > 0">
                        <span class="rh-vm-dbdiff-stat-num">+{{ dbChangesSummary(entry).added }}</span>
                        <span class="rh-vm-dbdiff-stat-lbl">ligne<span v-if="dbChangesSummary(entry).added>1">s</span> remise<span v-if="dbChangesSummary(entry).added>1">s</span></span>
                        <span class="rh-vm-dbdiff-stat-sub">présentes dans le snapshot</span>
                      </div>
                    </div>

                    <!-- Per-group breakdown -->
                    <div v-if="dbChangesGrouped(entry).length" class="rh-vm-dbdiff-groups">
                      <div v-for="g in dbChangesGrouped(entry)" :key="g.group" class="rh-vm-dbdiff-group">
                        <div class="rh-vm-dbdiff-group-head">
                          <span class="rh-vm-dbdiff-group-name">{{ g.group }}</span>
                          <span class="rh-vm-dbdiff-group-total">{{ g.total }} changement<span v-if="g.total>1">s</span></span>
                        </div>
                        <div class="rh-vm-dbdiff-rows">
                          <div v-for="r in g.rows" :key="r.table" class="rh-vm-dbdiff-row">
                            <span class="rh-vm-dbdiff-row-label">{{ r.label }}</span>
                            <span class="rh-vm-dbdiff-row-counts">
                              <span class="rh-vm-dbdiff-before">{{ r.before }}</span>
                              <svg viewBox="0 0 12 12" fill="none" width="10" height="10" class="rh-vm-dbdiff-arrow">
                                <path d="M2 6h7M6 3l3 3-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                              </svg>
                              <span class="rh-vm-dbdiff-after">{{ r.after }}</span>
                            </span>
                            <span class="rh-vm-dbdiff-row-delta"
                                  :class="r.delta > 0 ? 'rh-vm-dbdiff-row-delta--removed' : 'rh-vm-dbdiff-row-delta--added'">
                              {{ r.delta > 0 ? "−" + r.delta : "+" + (-r.delta) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Services & containers restarted -->
                  <div v-if="(entry.services_restarted && entry.services_restarted.length) || (entry.containers_restarted && entry.containers_restarted.length)"
                       class="rh-vm-quiesce-card">
                    <div class="rh-vm-card-title">
                      <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                        <path d="M7 1v3M7 10v3M1 7h3M10 7h3M3 3l2 2M9 9l2 2M3 11l2-2M9 5l2-2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                      </svg>
                      Services redémarrés autour du merge
                    </div>
                    <div class="rh-vm-quiesce-row">
                      <span v-for="svc in entry.services_restarted" :key="'s-'+svc" class="rh-vm-quiesce-pill service">
                        <span class="rh-vm-quiesce-dot"></span> {{ svc }}
                      </span>
                      <span v-for="ctr in entry.containers_restarted" :key="'c-'+ctr" class="rh-vm-quiesce-pill container">
                        <span class="rh-vm-quiesce-dot"></span> 🐳 {{ ctr }}
                      </span>
                    </div>
                  </div>

                  <!-- Snapshot persistence note (post-restore behaviour) -->
                  <div v-if="entry.status === 'success' && entry.snapshot_preserved"
                       class="rh-vm-merge-note rh-vm-merge-note--ok">
                    <svg viewBox="0 0 16 16" fill="none" width="13" height="13" style="flex-shrink:0">
                      <path d="M3 8l3 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <div>
                      <strong>Point de restauration préservé.</strong>
                      Après la fusion LVM, un snapshot identique a été recréé sous le même
                      nom <code>{{ entry.recreated_snap_id || entry.snap_id }}</code>.
                      Vous pouvez restaurer ce point de nouveau à tout moment.
                    </div>
                  </div>
                  <div v-else-if="entry.status === 'success'" class="rh-vm-merge-note">
                    <svg viewBox="0 0 16 16" fill="none" width="13" height="13" style="flex-shrink:0">
                      <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/>
                      <path d="M8 7v5M8 5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                    </svg>
                    <div>
                      <strong>Snapshot consommé par le merge.</strong>
                      La recréation post-restore a échoué (probablement espace VG insuffisant).
                      Libérez de l'espace puis créez un nouveau point depuis <em>VM Snapshot</em>.
                    </div>
                  </div>

                  <!-- Phases timeline — the actual restore steps -->
                  <div v-if="entry.phases && entry.phases.length" class="rh-vm-phases-card">
                    <div class="rh-vm-card-title">
                      <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                        <path d="M2 7h10M2 7l3-3M12 7l-3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Étapes de restauration
                    </div>
                    <div class="rh-vm-phases-track">
                      <div
                        v-for="(phase, idx) in entry.phases"
                        :key="phase.key"
                        class="rh-vm-phase"
                        :class="`rh-vm-phase--${phase.status}`"
                      >
                        <div class="rh-vm-phase-marker">
                          <span class="rh-vm-phase-dot"></span>
                          <span v-if="idx < entry.phases.length - 1" class="rh-vm-phase-line"></span>
                        </div>
                        <div class="rh-vm-phase-body">
                          <div class="rh-vm-phase-label">{{ phase.label }}</div>
                          <div class="rh-vm-phase-meta">
                            <span class="rh-vm-phase-status">{{ phaseStatusLabel(phase.status) }}</span>
                            <span v-if="phase.at" class="rh-vm-phase-time">· {{ formatTime(phase.at) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Message / Error -->
                  <div v-if="entry.message || entry.error" class="rh-vm-message-row">
                    <div v-if="entry.error" class="rh-vm-message rh-vm-message--error">
                      <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                        <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/>
                        <path d="M8 5v4M8 10.5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                      </svg>
                      {{ entry.error }}
                    </div>
                    <div v-else-if="entry.message" class="rh-vm-message rh-vm-message--info">
                      <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                        <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/>
                        <path d="M8 7v5M8 5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                      </svg>
                      {{ entry.message }}
                    </div>
                  </div>

                </div>
              </td>
            </tr>

            <!-- ── Standard backup restore row ── -->
            <tr
              v-else-if="entry.type !== 'vm_snapshot'"
              class="rh-row"
              :class="{ expanded: expandedJob === entry.job_id }"
              @click="toggleExpand(entry.job_id)"
            >
              <td class="rh-expand-cell">
                <span class="rh-expand-icon">{{ expandedJob === entry.job_id ? '▾' : '▸' }}</span>
              </td>
              <td>
                <span class="rh-type-badge backup">
                  <svg viewBox="0 0 14 14" fill="none" width="10" height="10" style="flex-shrink:0">
                    <path d="M2 4h10M2 4v7a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4M5 4V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                  </svg>
                  Backup
                </span>
              </td>
              <td>
                <div class="rh-date-primary">{{ formatDate(entry.started_at) }}</div>
                <div class="rh-date-secondary">{{ formatTime(entry.started_at) }}</div>
              </td>
              <td>
                <span class="rh-backup-id" :title="entry.backup_id">{{ shortBackupId(entry.backup_id) }}</span>
              </td>
              <td>
                <span class="rh-mode-badge" :class="entry.mode">{{ modeLabel(entry.mode) }}</span>
              </td>
              <td>
                <span class="rh-status-badge" :class="entry.status">{{ statusLabel(entry.status) }}</span>
              </td>
              <td>
                <div class="rh-comp-pills">
                  <span class="rh-pill ok" title="Succès">✓ {{ entry.summary.success }}</span>
                  <span v-if="entry.summary.failed > 0" class="rh-pill fail" title="Échecs">✗ {{ entry.summary.failed }}</span>
                  <span class="rh-pill skip" title="Ignorés">⊘ {{ entry.summary.skipped }}</span>
                </div>
              </td>
              <td>
                <span class="rh-duration">{{ formatDuration(entry.duration_seconds) }}</span>
              </td>
              <td>
                <span class="rh-stab-badge" :class="entry.stabilization_status || 'unknown'">
                  {{ stabLabel(entry.stabilization_status) }}
                </span>
              </td>
            </tr>

            <!-- ── Standard backup expanded detail ── -->
            <tr v-if="entry.type !== 'vm_snapshot' && expandedJob === entry.job_id" class="rh-detail-row">
              <td colspan="9">
                <div class="rh-detail-panel">

                  <div class="rh-detail-jobid">
                    <span class="rh-detail-label">Job ID</span>
                    <code>{{ entry.job_id }}</code>
                  </div>

                  <div v-if="entry.components_detail && entry.components_detail.length > 0" class="rh-impact-banner">
                    <div class="rh-impact-header">
                      <span class="rh-impact-title">Zones système modifiées</span>
                      <span class="rh-impact-subtitle">{{ impactSentence(entry) }}</span>
                    </div>
                    <div class="rh-impact-chips">
                      <div
                        v-for="chip in impactChips(entry)"
                        :key="chip.key"
                        class="rh-impact-chip"
                        :class="chip.status"
                        :title="chip.desc"
                      >
                        <span class="rh-impact-icon">{{ chip.icon }}</span>
                        <span class="rh-impact-label">{{ chip.label }}</span>
                        <span class="rh-impact-dot" :class="chip.status"></span>
                      </div>
                    </div>
                  </div>

                  <div v-if="entry.components_detail && entry.components_detail.length > 0" class="rh-comp-detail-section">
                    <div class="rh-detail-title">Détail des composants restaurés</div>
                    <table class="rh-comp-detail-table">
                      <thead>
                        <tr>
                          <th>Statut</th>
                          <th>Composant</th>
                          <th>Système</th>
                          <th>Action effectuée</th>
                          <th>Fichier</th>
                          <th>Taille</th>
                          <th>Durée</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="c in entry.components_detail"
                          :key="c.name"
                          :class="'rh-cd-row-' + c.status"
                        >
                          <td>
                            <span class="rh-cd-status" :class="c.status">
                              {{ c.status === 'success' ? '✓' : '✗' }}
                            </span>
                          </td>
                          <td><span class="rh-cd-name">{{ c.name }}</span></td>
                          <td><span class="rh-cd-area">{{ componentDescription(c.name) }}</span></td>
                          <td><span class="rh-cd-msg" :title="c.message">{{ c.message || '—' }}</span></td>
                          <td>
                            <span v-if="c.file" class="rh-cd-file" :title="c.file">{{ shortFile(c.file) }}</span>
                            <span v-else class="rh-cd-empty">—</span>
                          </td>
                          <td>
                            <span v-if="c.size_mb" class="rh-cd-size">{{ c.size_mb }} Mo</span>
                            <span v-else class="rh-cd-empty">—</span>
                          </td>
                          <td><span class="rh-cd-dur">{{ formatDuration(c.duration_seconds) }}</span></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="rh-detail-empty" style="margin: 8px 0 16px">Aucun détail disponible (restore en cours ou ancien job).</div>

                  <div class="rh-detail-grid">
                    <div class="rh-detail-section">
                      <div class="rh-detail-title">🕐 Chronologie</div>
                      <div class="rh-timing-list">
                        <div class="rh-timing-item"><span>Début</span><span>{{ formatDateTime(entry.started_at) }}</span></div>
                        <div class="rh-timing-item"><span>Fin</span><span>{{ formatDateTime(entry.finished_at) }}</span></div>
                        <div class="rh-timing-item"><span>Durée totale</span><strong>{{ formatDuration(entry.duration_seconds) }}</strong></div>
                      </div>
                    </div>
                    <div v-if="entry.slowest_components && entry.slowest_components.length > 0" class="rh-detail-section">
                      <div class="rh-detail-title">⏱ Composants les plus lents</div>
                      <div class="rh-slowest-list">
                        <div v-for="s in entry.slowest_components" :key="s.name" class="rh-slowest-item">
                          <span class="rh-slowest-name">{{ s.name }}</span>
                          <div class="rh-slowest-bar-wrap">
                            <div class="rh-slowest-bar" :style="{ width: slowestBarWidth(s.duration_seconds, entry.slowest_components) + '%' }"></div>
                          </div>
                          <span class="rh-slowest-dur">{{ formatDuration(s.duration_seconds) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </td>
            </tr>

          </template>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RestoreHistory",
  data() {
    return {
      loading: false,
      entries: [],
      stats: { total: 0, success: 0, failed: 0, success_rate: 0, avg_duration_seconds: 0 },
      search: "",
      activeFilter: "all",
      activeTypeFilter: "all",
      expandedJob: null,
      statusFilters: [
        { label: "Tous", value: "all" },
        { label: "Succès", value: "success" },
        { label: "Partiel", value: "partial_success" },
        { label: "Erreur", value: "error" },
        { label: "En cours", value: "running" },
      ],
      typeFilters: [
        { label: "Tous types", value: "all" },
        { label: "Backup", value: "backup" },
        { label: "LVM Snapshot", value: "vm_snapshot" },
      ],
      systemAreas: [
        { key: "firewall",       icon: "🔥", label: "Firewall",     desc: "Règles nftables + DB règles",         components: ["firewall", "firewall_rules", "firewall_rules_db", "nftables"] },
        { key: "nat",            icon: "🔀", label: "NAT",          desc: "NAT / masquerade",                    components: ["nat"] },
        { key: "routing",        icon: "🛣️", label: "Routage",      desc: "Table de routage IP",                 components: ["routing"] },
        { key: "network",        icon: "🌐", label: "Réseau",       desc: "Interfaces et adresses IP",           components: ["network", "vlan", "vxlan", "gateway", "double_mask"] },
        { key: "dhcp",           icon: "📡", label: "DHCP",         desc: "Serveur DHCP",                        components: ["dhcp"] },
        { key: "vpn",            icon: "🔐", label: "VPN",          desc: "OpenVPN / IPsec strongSwan",          components: ["vpn", "ipsec_detailed", "strongswan", "openvpn"] },
        { key: "proxy",          icon: "🛡️", label: "Proxy",        desc: "Proxy Squid HTTP/HTTPS",              components: ["proxy", "squid"] },
        { key: "ids",            icon: "👁️", label: "IDS/IPS",      desc: "Suricata intrusion detection",        components: ["ids", "suricata"] },
        { key: "certificates",   icon: "🔒", label: "Certificats",  desc: "Certificats SSL/TLS",                 components: ["certificates", "ssl"] },
        { key: "dns",            icon: "🔍", label: "DNS",          desc: "Résolveur DNS",                       components: ["dns"] },
        { key: "waf",            icon: "🧱", label: "WAF",          desc: "Web Application Firewall",            components: ["waf"] },
        { key: "sdwan",          icon: "🕸️", label: "SD-WAN",       desc: "Software-Defined WAN",                components: ["sdwan"] },
        { key: "ztna",           icon: "🔑", label: "ZTNA",         desc: "Zero Trust Network Access",           components: ["ztna"] },
        { key: "users",          icon: "👤", label: "Utilisateurs", desc: "Comptes et groupes",                  components: ["users", "users_groups"] },
        { key: "database",       icon: "🗄️", label: "Base de données", desc: "DB Asguard",                      components: ["database", "asguard_db"] },
      ],
      componentDescriptions: {
        firewall_rules:    "Règles nftables + DB règles firewall",
        firewall_rules_db: "Base de données des règles firewall",
        nat:               "NAT / masquerade nftables",
        routing:           "Table de routage IP",
        network:           "Interfaces et adresses IP",
        dhcp:              "Configuration DHCP",
        proxy:             "Proxy Squid (filtrage HTTP/HTTPS)",
        ids:               "IDS/IPS Suricata",
        vpn:               "VPN OpenVPN / IPsec (strongSwan)",
        dns:               "Résolveur DNS",
        ntp:               "Synchronisation NTP",
        ssh:               "Configuration SSH",
        ssl:               "Certificats SSL/TLS",
        users:             "Comptes utilisateurs système",
        asguard_db:        "Base de données Asguard",
        asguard_app:       "Application web Asguard",
        logs:              "Journaux système",
        cron:              "Tâches planifiées (cron)",
        sysctl:            "Paramètres noyau (sysctl)",
        hosts:             "Fichier /etc/hosts",
        nftables:          "Configuration nftables complète",
        squid:             "Proxy Squid",
        suricata:          "IDS Suricata",
        strongswan:        "VPN IPsec strongSwan",
        openvpn:           "VPN OpenVPN",
      },
    };
  },
  computed: {
    vmSnapshotCount() {
      return this.entries.filter(e => e.type === "vm_snapshot").length;
    },
    filteredEntries() {
      let list = this.entries;
      if (this.activeTypeFilter !== "all") {
        list = list.filter(e => e.type === this.activeTypeFilter);
      }
      if (this.activeFilter !== "all") {
        list = list.filter(e => e.status === this.activeFilter);
      }
      if (this.search.trim()) {
        const q = this.search.trim().toLowerCase();
        list = list.filter(
          (e) =>
            (e.backup_id || "").toLowerCase().includes(q) ||
            (e.snap_id || "").toLowerCase().includes(q) ||
            (e.job_id || "").toLowerCase().includes(q) ||
            (e.mode || "").toLowerCase().includes(q)
        );
      }
      return list;
    },
  },
  mounted() {
    this.fetchHistory();
  },
  methods: {
    async fetchHistory() {
      this.loading = true;
      try {
        const res = await axios.get("/backup/restore-history");
        this.entries = res.data.results || [];
        this.stats = res.data.stats || {};
      } catch {
        this.entries = [];
      } finally {
        this.loading = false;
      }
    },
    toggleExpand(jobId) {
      this.expandedJob = this.expandedJob === jobId ? null : jobId;
    },
    shortBackupId(id) {
      if (!id) return "—";
      return id.replace(/^backup_(safe_|full_|custom_)?/, "").slice(0, 19);
    },
    shortSnapId(id) {
      if (!id) return "—";
      return id.length > 22 ? id.slice(0, 22) + "…" : id;
    },
    modeLabel(mode) {
      const map = { safe: "Safe", complete: "Full", ui_full: "Full UI-safe", full: "Full", selected_components: "Custom", vm_snapshot: "LVM Snapshot" };
      return map[mode] || mode || "—";
    },
    statusLabel(status) {
      const map = { success: "Vérifié", partial_success: "Partiel", error: "Erreur", running: "En cours", queued: "En attente", done: "Vérifié" };
      return map[status] || status || "—";
    },
    stabLabel(s) {
      if (s === "success") return "OK";
      if (s === "partial") return "Partiel";
      if (!s) return "—";
      return s;
    },
    phaseStatusLabel(s) {
      const map = { done: "Terminé", pending: "En attente", failed: "Échec", running: "En cours" };
      return map[s] || "—";
    },
    creatorLabel(c) {
      const map = { manual: "Manuel", auto_pre_backup: "Auto · avant backup", auto_post_backup: "Auto · après backup", ai_risk: "IA Risk Center", scheduled: "Planifié" };
      return map[c] || c;
    },
    // Human-friendly label + kind for each restored bind-mount + container.
    // Keeps the UI honest: only shows what the backend confirmed it rebound.
    restoredModules(entry) {
      if (!entry || !entry.binds_restored) return [];
      const pathToLabel = {
        "/etc/nftables.conf":                              { label: "Règles firewall (nftables)",   kind: "file" },
        "/etc/rules":                                      { label: "Règles par interface",          kind: "dir"  },
        "/etc/asguard":                                    { label: "Configuration Asguard",         kind: "dir"  },
        "/var/backups/asguard":                            { label: "Backups & historique",           kind: "dir"  },
        "/etc/openvpn":                                    { label: "OpenVPN",                        kind: "service" },
        "/etc/strongswan.d":                               { label: "IPsec / StrongSwan",             kind: "service" },
        "/etc/squid":                                      { label: "Proxy Web (Squid)",              kind: "service" },
        "/etc/suricata":                                   { label: "IDS/IPS (Suricata)",             kind: "service" },
        "/etc/modsecurity":                                { label: "WAF (ModSecurity)",              kind: "service" },
        "/etc/dhcpd.conf":                                 { label: "DHCP v4",                        kind: "file" },
        "/etc/dhcpd6.conf":                                { label: "DHCP v6",                        kind: "file" },
        "/var/lib/docker/volumes/asguard_pgdb/_data":      { label: "Base de données PostgreSQL",     kind: "container" },
      };
      return (entry.binds_restored || []).map((p, i) => {
        const meta = pathToLabel[p] || { label: p, kind: "dir" };
        return { id: `${i}-${p}`, path: p, label: meta.label, kind: meta.kind };
      });
    },
    // Group the raw db_changes list (one row per table) by the backend-
    // provided "group" so the UI can render it as small section blocks
    // (Pare-feu, NAT, IDS/IPS, …). Only sections that have at least one
    // changed row are returned, sorted by total absolute delta descending.
    dbChangesGrouped(entry) {
      const rows = (entry && entry.db_changes) || [];
      if (!rows.length) return [];
      const byGroup = new Map();
      for (const r of rows) {
        if (!byGroup.has(r.group)) byGroup.set(r.group, []);
        byGroup.get(r.group).push(r);
      }
      const out = [];
      for (const [group, list] of byGroup) {
        const changed = list.filter((r) => r.changed);
        if (!changed.length) continue;
        const total = changed.reduce((s, r) => s + Math.abs(r.delta), 0);
        out.push({ group, rows: changed, total });
      }
      out.sort((a, b) => b.total - a.total);
      return out;
    },
    dbChangesSummary(entry) {
      const rows = (entry && entry.db_changes) || [];
      const changed = rows.filter((r) => r.changed);
      const removed = changed.reduce((s, r) => s + (r.delta > 0 ? r.delta : 0), 0);
      const added   = changed.reduce((s, r) => s + (r.delta < 0 ? -r.delta : 0), 0);
      return { tables: changed.length, removed, added, scanned: rows.length };
    },
    formatDate(iso) {
      if (!iso) return "—";
      return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
    },
    formatTime(iso) {
      if (!iso) return "";
      return new Date(iso).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    },
    formatDateTime(iso) {
      if (!iso) return "—";
      return new Date(iso).toLocaleString("fr-FR");
    },
    formatDuration(s) {
      if (!s) return "0s";
      const sec = Math.round(s);
      if (sec < 60) return `${sec}s`;
      return `${Math.floor(sec / 60)}m ${sec % 60}s`;
    },
    slowestBarWidth(dur, list) {
      const max = Math.max(...list.map((x) => x.duration_seconds));
      return max > 0 ? Math.round((dur / max) * 100) : 0;
    },
    impactChips(entry) {
      const detail = entry.components_detail || [];
      const successNames = new Set(detail.filter((c) => c.status === "success").map((c) => c.name));
      const failedNames  = new Set(detail.filter((c) => c.status === "failed").map((c) => c.name));
      return this.systemAreas
        .map((area) => {
          const hasFail    = area.components.some((c) => failedNames.has(c));
          const hasSuccess = area.components.some((c) => successNames.has(c));
          if (!hasFail && !hasSuccess) return null;
          return { ...area, status: hasFail ? "failed" : "success" };
        })
        .filter(Boolean);
    },
    impactSentence(entry) {
      const chips = this.impactChips(entry);
      if (!chips.length) return "";
      const labels = chips.map((c) => c.label);
      const last = labels.pop();
      const list = labels.length ? labels.join(", ") + " et " + last : last;
      const failed = chips.filter((c) => c.status === "failed").length;
      const suffix = failed ? ` (${failed} zone${failed > 1 ? "s" : ""} en échec)` : "";
      return `${chips.length} zone${chips.length > 1 ? "s" : ""} système modifiée${chips.length > 1 ? "s" : ""} : ${list}${suffix}.`;
    },
    componentDescription(name) {
      return this.componentDescriptions[name] || name.replace(/_/g, " ");
    },
    shortFile(filePath) {
      if (!filePath) return "—";
      const parts = filePath.split("/");
      return parts.length > 3 ? "…/" + parts.slice(-2).join("/") : filePath;
    },
  },
};
</script>

<style scoped>
.restore-history-page {
  padding: 24px;
  min-height: 400px;
  position: relative;
}

/* Loading */
.rh-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}
.rh-loading-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 16px 28px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  font-size: 14px;
  color: #444;
}
.rh-spinner {
  width: 20px; height: 20px;
  border: 3px solid #e0e0e0;
  border-top-color: #1565c0;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Stats bar */
.rh-stats-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #f8f9fc;
  border-radius: 12px;
  border: 1px solid #e8eaf0;
}
.rh-stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  padding: 8px 14px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e4ec;
}
.rh-stat-card.success { border-color: #a5d6a7; background: #f1f8e9; }
.rh-stat-card.danger  { border-color: #ef9a9a; background: #fff3f3; }
.rh-stat-value { font-size: 22px; font-weight: 700; color: #1a237e; line-height: 1.2; }
.rh-val-blue   { color: #6a1b9a; }
.rh-stat-label { font-size: 11px; color: #78909c; margin-top: 2px; text-align: center; }
.rh-refresh-btn {
  margin-left: auto;
  padding: 8px 18px;
  border: 1.5px solid #1565c0;
  border-radius: 8px;
  background: #fff;
  color: #1565c0;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s;
}
.rh-refresh-btn:hover:not(:disabled) { background: #e3f2fd; }
.rh-refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Filters */
.rh-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.rh-search {
  flex: 1;
  min-width: 220px;
  padding: 8px 14px;
  border: 1.5px solid #dde1ea;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: #fff;
}
.rh-search:focus { border-color: #1565c0; }
.rh-filter-chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.rh-filter-sep { width: 1px; height: 20px; background: #dde1ea; margin: 0 4px; }
.rh-chip {
  padding: 5px 12px;
  border: 1.5px solid #dde1ea;
  border-radius: 20px;
  background: #fff;
  font-size: 12px;
  color: #546e7a;
  cursor: pointer;
  transition: all 0.15s;
}
.rh-chip.active { border-color: #1565c0; background: #1565c0; color: #fff; }
.rh-chip:hover:not(.active) { border-color: #90a4ae; }

.rh-chip-type { display: flex; align-items: center; gap: 4px; }
.rh-chip-type.vm-chip { border-color: #ce93d8; color: #6a1b9a; }
.rh-chip-type.vm-chip.active { border-color: #6a1b9a; background: #6a1b9a; color: #fff; }
.rh-chip-vm-icon { font-size: 10px; }

/* Empty */
.rh-empty { text-align: center; padding: 60px 20px; color: #90a4ae; }
.rh-empty-icon { font-size: 40px; margin-bottom: 10px; }

/* Table */
.rh-table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #e8eaf0; }
.rh-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.rh-table thead tr { background: #f3f5fa; border-bottom: 2px solid #e0e4ec; }
.rh-table th {
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #546e7a;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.rh-row { border-bottom: 1px solid #f0f2f7; cursor: pointer; transition: background 0.1s; }
.rh-row:hover { background: #f5f7fc; }
.rh-row.expanded { background: #eef2fb; }

/* VM snapshot row — distinct purple tint */
.rh-row-vm { border-left: 3px solid #9c27b0; }
.rh-row-vm:hover { background: #fdf5ff; }
.rh-row-vm.expanded { background: #f8f0ff; border-left-color: #7b1fa2; }

.rh-table td { padding: 10px 14px; vertical-align: middle; }
.rh-expand-cell { width: 28px; color: #90a4ae; }
.rh-expand-icon { font-size: 14px; }

/* Type badges */
.rh-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
  white-space: nowrap;
}
.rh-type-badge.backup     { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
.rh-type-badge.vm         { background: #f3e5f5; color: #6a1b9a; border: 1px solid #ce93d8; }

/* Snap ID in VM row */
.rh-snap-id-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: monospace;
  font-size: 11px;
  color: #6a1b9a;
  background: #f3e5f5;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #ce93d8;
}

/* VM "entière" pill */
.rh-vm-full-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: #f3e5f5;
  color: #6a1b9a;
  border: 1px solid #ce93d8;
}

/* Date */
.rh-date-primary { font-weight: 600; color: #263238; font-size: 13px; }
.rh-date-secondary { font-size: 11px; color: #90a4ae; }

/* Backup ID */
.rh-backup-id {
  font-family: monospace;
  font-size: 12px;
  color: #37474f;
  background: #f0f2f7;
  padding: 2px 7px;
  border-radius: 4px;
}

/* Mode badge */
.rh-mode-badge {
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: #e8eaf0;
  color: #455a64;
}
.rh-mode-badge.complete, .rh-mode-badge.ui_full, .rh-mode-badge.full { background: #e3f2fd; color: #1565c0; }
.rh-mode-badge.safe { background: #e8f5e9; color: #2e7d32; }
.rh-mode-badge.selected_components { background: #fff3e0; color: #e65100; }
.rh-mode-badge.vm_snapshot { background: #f3e5f5; color: #6a1b9a; }

/* Status badge */
.rh-status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  display: inline-block;
}
.rh-status-badge.success { background: #e8f5e9; color: #2e7d32; }
.rh-status-badge.partial_success { background: #fff8e1; color: #f57f17; }
.rh-status-badge.error { background: #ffebee; color: #c62828; }
.rh-status-badge.running { background: #e3f2fd; color: #1565c0; }
.rh-status-badge.queued { background: #f3e5f5; color: #6a1b9a; }

/* Component pills */
.rh-comp-pills { display: flex; gap: 6px; }
.rh-pill { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.rh-pill.ok   { background: #e8f5e9; color: #2e7d32; }
.rh-pill.fail { background: #ffebee; color: #c62828; }
.rh-pill.skip { background: #f0f2f7; color: #78909c; }

/* Duration */
.rh-duration { font-weight: 600; color: #37474f; font-size: 13px; }

/* Stabilisation */
.rh-stab-badge { padding: 2px 9px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.rh-stab-badge.success { background: #e8f5e9; color: #2e7d32; }
.rh-stab-badge.partial { background: #fff8e1; color: #f57f17; }
.rh-stab-badge.unknown { background: #f0f2f7; color: #90a4ae; }

/* ── VM Snapshot expanded detail ── */
.rh-detail-row td { padding: 0; }
.rh-detail-row-vm td { padding: 0; }

.rh-detail-panel-vm {
  background: linear-gradient(135deg, #faf5ff 0%, #f8f0ff 100%);
  border-top: 2px solid #ce93d8;
  padding: 20px 24px;
}

.rh-vm-header-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border: 1px solid #ce93d8;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 18px;
  box-shadow: 0 2px 8px rgba(106, 27, 154, 0.06);
}

.rh-vm-header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #f3e5f5, #e1bee7);
  border-radius: 14px;
  color: #6a1b9a;
  flex-shrink: 0;
}

.rh-vm-header-body { flex: 1; }
.rh-vm-header-title {
  font-weight: 700;
  font-size: 14px;
  color: #4a148c;
  margin-bottom: 4px;
}
.rh-vm-header-sub { font-size: 12px; color: #7b5fa5; line-height: 1.4; }

.rh-vm-header-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.rh-vm-status-big {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}
.rh-vm-status-big.success { background: #e8f5e9; color: #2e7d32; }
.rh-vm-status-big.error   { background: #ffebee; color: #c62828; }
.rh-vm-status-big.running { background: #e3f2fd; color: #1565c0; }
.rh-vm-duration-big { font-size: 18px; font-weight: 700; color: #6a1b9a; }

/* VM detail grid */
.rh-vm-detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.rh-vm-info-card {
  background: #fff;
  border: 1px solid #e1bee7;
  border-radius: 10px;
  padding: 14px 16px;
}

.rh-vm-info-card--scope { border-color: #ce93d8; }

.rh-vm-card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 11px;
  color: #6a1b9a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.rh-vm-info-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  font-size: 12px;
  color: #546e7a;
  padding: 4px 0;
  border-bottom: 1px solid #f5f0f8;
}
.rh-vm-info-row:last-child { border-bottom: none; }
.rh-vm-info-label { color: #90a4ae; font-size: 11px; flex-shrink: 0; }
.rh-vm-snap-code {
  background: #f3e5f5;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 11px;
  color: #4a148c;
  font-family: monospace;
  word-break: break-all;
}
.rh-vm-snap-code.small { font-size: 10px; }

/* Scope list — restored modules from backend */
.rh-vm-scope-list { display: flex; flex-direction: column; gap: 6px; max-height: 240px; overflow-y: auto; }
.rh-vm-scope-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #546e7a; }
.rh-vm-scope-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.rh-vm-scope-dot.green  { background: #43a047; }
.rh-vm-scope-dot.orange { background: #fb8c00; }
.rh-vm-scope-count {
  margin-left: auto;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  background: #ede7f6; color: #4527a0;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.rh-vm-scope-mod {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 9px;
  background: #f3e5f5;
  border: 1px solid #ce93d8;
  border-radius: 7px;
  font-size: 11.5px;
  transition: transform 0.1s;
}
.rh-vm-scope-mod:hover { transform: translateX(2px); }
.rh-vm-scope-mod-icon {
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  flex-shrink: 0;
}
.rh-vm-scope-mod-icon.container { background: #e3f2fd; }
.rh-vm-scope-mod-icon.service   { background: #fff8e1; }
.rh-vm-scope-mod-body { flex: 1; min-width: 0; }
.rh-vm-scope-mod-label { font-weight: 600; color: #1a237e; line-height: 1.2; }
.rh-vm-scope-mod-path { font-size: 10px; color: #78909c; line-height: 1.3; margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rh-vm-scope-mod-path code { background: transparent; padding: 0; font-size: 10px; }
.rh-vm-scope-mod-tick { color: #2e7d32; font-weight: 800; font-size: 14px; flex-shrink: 0; }
.rh-vm-scope-empty { font-size: 11.5px; color: #90a4ae; font-style: italic; padding: 6px 2px; }

/* Services / containers restarted around the merge */
.rh-vm-quiesce-card {
  margin-top: 14px;
  padding: 12px 16px 14px;
  background: #fff;
  border: 1px solid #e1bee7;
  border-radius: 9px;
}
.rh-vm-quiesce-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.rh-vm-quiesce-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 11.5px; font-weight: 600;
  border: 1px solid;
}
.rh-vm-quiesce-pill.service   { background: #fff8e1; border-color: #ffcc80; color: #b45309; }
.rh-vm-quiesce-pill.container { background: #e3f2fd; border-color: #90caf9; color: #1565c0; }
.rh-vm-quiesce-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.6);
}

/* Merge-consumed informational note */
.rh-vm-merge-note {
  margin-top: 14px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #93c5fd;
  border-radius: 9px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12px;
  color: #1e3a8a;
  line-height: 1.5;
}
.rh-vm-merge-note svg { color: #2563eb; margin-top: 2px; }
.rh-vm-merge-note.rh-vm-merge-note--ok {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-color: #6ee7b7;
  color: #065f46;
}
.rh-vm-merge-note.rh-vm-merge-note--ok svg { color: #10b981; }
.rh-vm-merge-note.rh-vm-merge-note--ok code { background: rgba(16, 185, 129, 0.12); color: #047857; }
.rh-vm-merge-note code { background: rgba(37, 99, 235, 0.1); padding: 1px 5px; border-radius: 3px; font-size: 11px; }
.rh-vm-merge-note em { color: #1e40af; font-style: italic; }

/* Database content diff — proof of what was reverted */
.rh-vm-dbdiff-card {
  margin-top: 12px;
  background: linear-gradient(135deg, #faf5ff 0%, #ede9fe 100%);
  border: 1px solid #c4b5fd;
  border-radius: 10px;
  padding: 12px 14px;
}
.rh-vm-dbdiff-card .rh-vm-card-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 11.5px; font-weight: 700;
  color: #5b21b6; text-transform: uppercase; letter-spacing: 0.4px;
  margin-bottom: 10px;
}
.rh-vm-dbdiff-count {
  margin-left: auto;
  background: rgba(124, 58, 237, 0.12);
  color: #6d28d9;
  font-size: 10.5px; font-weight: 600; text-transform: none; letter-spacing: 0;
  padding: 2px 8px; border-radius: 999px;
}
.rh-vm-dbdiff-empty {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #047857;
  background: rgba(16, 185, 129, 0.08); border: 1px dashed #6ee7b7;
  padding: 8px 10px; border-radius: 8px;
}
.rh-vm-dbdiff-empty svg { color: #10b981; }
.rh-vm-dbdiff-summary {
  display: flex; gap: 10px; margin-bottom: 10px;
}
.rh-vm-dbdiff-stat {
  flex: 1;
  display: flex; flex-direction: column; gap: 2px;
  padding: 8px 10px; border-radius: 8px; background: #fff; border: 1px solid #e9d5ff;
}
.rh-vm-dbdiff-stat--removed { border-left: 3px solid #dc2626; }
.rh-vm-dbdiff-stat--added   { border-left: 3px solid #059669; }
.rh-vm-dbdiff-stat-num { font-size: 18px; font-weight: 700; color: #1f2937; line-height: 1; }
.rh-vm-dbdiff-stat--removed .rh-vm-dbdiff-stat-num { color: #b91c1c; }
.rh-vm-dbdiff-stat--added   .rh-vm-dbdiff-stat-num { color: #047857; }
.rh-vm-dbdiff-stat-lbl { font-size: 11px; font-weight: 600; color: #4b5563; }
.rh-vm-dbdiff-stat-sub { font-size: 10.5px; color: #6b7280; }
.rh-vm-dbdiff-groups { display: flex; flex-direction: column; gap: 8px; }
.rh-vm-dbdiff-group {
  background: #fff; border: 1px solid #ede9fe; border-radius: 8px; padding: 8px 10px;
}
.rh-vm-dbdiff-group-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 6px;
}
.rh-vm-dbdiff-group-name {
  font-size: 11.5px; font-weight: 700; color: #5b21b6;
  text-transform: uppercase; letter-spacing: 0.4px;
}
.rh-vm-dbdiff-group-total { font-size: 10.5px; color: #7c3aed; font-weight: 600; }
.rh-vm-dbdiff-rows { display: flex; flex-direction: column; gap: 4px; }
.rh-vm-dbdiff-row {
  display: grid; grid-template-columns: 1fr auto auto;
  align-items: center; gap: 12px;
  padding: 4px 6px; border-radius: 6px;
}
.rh-vm-dbdiff-row:hover { background: #faf5ff; }
.rh-vm-dbdiff-row-label { font-size: 12px; color: #1f2937; }
.rh-vm-dbdiff-row-counts {
  display: flex; align-items: center; gap: 4px;
  font-variant-numeric: tabular-nums; font-size: 11.5px; color: #6b7280;
}
.rh-vm-dbdiff-before { color: #9ca3af; }
.rh-vm-dbdiff-after  { color: #1f2937; font-weight: 600; }
.rh-vm-dbdiff-arrow  { color: #c4b5fd; }
.rh-vm-dbdiff-row-delta {
  font-size: 11px; font-weight: 700;
  padding: 2px 7px; border-radius: 999px;
  font-variant-numeric: tabular-nums;
}
.rh-vm-dbdiff-row-delta--removed { background: #fee2e2; color: #b91c1c; }
.rh-vm-dbdiff-row-delta--added   { background: #d1fae5; color: #047857; }

/* Description + creator pill */
.rh-vm-desc {
  font-size: 12px;
  color: #1a237e;
  font-style: italic;
  text-align: right;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rh-vm-creator-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 9px;
  border-radius: 11px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: #ede7f6;
  color: #4527a0;
  border: 1px solid #d1c4e9;
}
.rh-vm-creator-pill.ai_risk        { background: #ffebee; color: #c62828; border-color: #ef9a9a; }
.rh-vm-creator-pill.scheduled      { background: #e3f2fd; color: #1565c0; border-color: #90caf9; }
.rh-vm-creator-pill.auto_pre_backup,
.rh-vm-creator-pill.auto_post_backup { background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7; }

/* Phases timeline */
.rh-vm-phases-card {
  margin-top: 16px;
  padding: 14px 18px 18px;
  background: linear-gradient(180deg, #faf5ff 0%, #f3e5f5 100%);
  border: 1px solid #ce93d8;
  border-radius: 10px;
}
.rh-vm-phases-track {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
  position: relative;
}
.rh-vm-phase {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1 1 0;
  min-width: 0;
  text-align: center;
}
.rh-vm-phase-marker {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 22px;
}
.rh-vm-phase-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #e0e0e0;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #bdbdbd;
  position: relative;
  z-index: 2;
  transition: all 0.2s;
}
.rh-vm-phase-line {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100%;
  height: 2px;
  background: #cfd8dc;
  z-index: 1;
}
.rh-vm-phase-body {
  margin-top: 8px;
  padding: 0 4px;
}
.rh-vm-phase-label {
  font-size: 11.5px;
  font-weight: 600;
  color: #37474f;
  line-height: 1.25;
}
.rh-vm-phase-meta {
  font-size: 10px;
  color: #78909c;
  margin-top: 3px;
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: wrap;
}
.rh-vm-phase-status { font-weight: 600; }
.rh-vm-phase-time   { color: #90a4ae; }

/* Phase status colors */
.rh-vm-phase--done .rh-vm-phase-dot {
  background: #43a047;
  box-shadow: 0 0 0 2px #43a047, 0 0 0 5px rgba(67, 160, 71, 0.2);
}
.rh-vm-phase--done .rh-vm-phase-line   { background: #43a047; }
.rh-vm-phase--done .rh-vm-phase-status { color: #2e7d32; }

.rh-vm-phase--running .rh-vm-phase-dot {
  background: #1e88e5;
  box-shadow: 0 0 0 2px #1e88e5, 0 0 0 5px rgba(30, 136, 229, 0.25);
  animation: rh-vm-pulse 1.4s infinite;
}
.rh-vm-phase--running .rh-vm-phase-status { color: #1565c0; }

.rh-vm-phase--failed .rh-vm-phase-dot {
  background: #e53935;
  box-shadow: 0 0 0 2px #e53935, 0 0 0 5px rgba(229, 57, 53, 0.2);
}
.rh-vm-phase--failed .rh-vm-phase-line   { background: #ef9a9a; }
.rh-vm-phase--failed .rh-vm-phase-status { color: #c62828; }

.rh-vm-phase--pending .rh-vm-phase-status { color: #90a4ae; }

@keyframes rh-vm-pulse {
  0%, 100% { box-shadow: 0 0 0 2px #1e88e5, 0 0 0 5px rgba(30, 136, 229, 0.25); }
  50%      { box-shadow: 0 0 0 2px #1e88e5, 0 0 0 9px rgba(30, 136, 229, 0.10); }
}

/* Message row */
.rh-vm-message-row { margin-top: 4px; }
.rh-vm-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.5;
}
.rh-vm-message--error { background: #fff3f3; color: #c62828; border: 1px solid #ef9a9a; }
.rh-vm-message--info  { background: #f0f4ff; color: #1a237e; border: 1px solid #90caf9; }

/* ── Standard backup detail panel ── */
.rh-detail-panel {
  background: #f8faff;
  border-top: 2px solid #c5cae9;
  padding: 20px 24px;
}
.rh-detail-jobid {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-size: 12px;
}
.rh-detail-label { font-weight: 600; color: #78909c; text-transform: uppercase; font-size: 11px; }
code {
  background: #e8eaf0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #37474f;
}
.rh-detail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.rh-detail-section {
  background: #fff;
  border: 1px solid #e0e4ec;
  border-radius: 8px;
  padding: 14px 16px;
}
.rh-detail-title {
  font-weight: 700;
  font-size: 12px;
  color: #455a64;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.rh-detail-empty { font-size: 12px; color: #90a4ae; }

/* Slowest components */
.rh-slowest-list { display: flex; flex-direction: column; gap: 8px; }
.rh-slowest-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.rh-slowest-name { width: 90px; font-weight: 500; color: #37474f; flex-shrink: 0; }
.rh-slowest-bar-wrap { flex: 1; background: #e8eaf0; border-radius: 4px; height: 6px; overflow: hidden; }
.rh-slowest-bar { height: 100%; background: #1565c0; border-radius: 4px; transition: width 0.3s; }
.rh-slowest-dur { width: 36px; text-align: right; color: #546e7a; font-weight: 600; flex-shrink: 0; }

/* Timing */
.rh-timing-list { display: flex; flex-direction: column; gap: 6px; }
.rh-timing-item { display: flex; justify-content: space-between; font-size: 12px; color: #546e7a; }
.rh-timing-item strong { color: #263238; }

/* Impact banner */
.rh-impact-banner {
  background: linear-gradient(135deg, #f0f4ff 0%, #f8faff 100%);
  border: 1px solid #c5cae9;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 18px;
}
.rh-impact-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.rh-impact-title { font-weight: 700; font-size: 12px; color: #1a237e; text-transform: uppercase; letter-spacing: 0.05em; flex-shrink: 0; }
.rh-impact-subtitle { font-size: 12px; color: #546e7a; font-style: italic; }
.rh-impact-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.rh-impact-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 1.5px solid transparent;
  cursor: default;
  transition: transform 0.1s;
}
.rh-impact-chip:hover { transform: translateY(-1px); }
.rh-impact-chip.success { background: #e8f5e9; border-color: #a5d6a7; color: #1b5e20; }
.rh-impact-chip.failed  { background: #ffebee; border-color: #ef9a9a; color: #b71c1c; }
.rh-impact-icon { font-size: 14px; line-height: 1; }
.rh-impact-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.rh-impact-dot.success { background: #43a047; }
.rh-impact-dot.failed  { background: #e53935; }

/* Component detail table */
.rh-comp-detail-section { margin-bottom: 16px; }
.rh-comp-detail-section .rh-detail-title { font-weight: 700; font-size: 12px; color: #455a64; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.03em; }
.rh-comp-detail-table { width: 100%; border-collapse: collapse; font-size: 12px; background: #fff; border-radius: 8px; overflow: hidden; border: 1px solid #e0e4ec; }
.rh-comp-detail-table thead tr { background: #f3f5fa; border-bottom: 1.5px solid #e0e4ec; }
.rh-comp-detail-table th { padding: 7px 12px; text-align: left; font-weight: 600; color: #78909c; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
.rh-comp-detail-table td { padding: 7px 12px; vertical-align: middle; border-bottom: 1px solid #f0f2f7; }
.rh-comp-detail-table tbody tr:last-child td { border-bottom: none; }
.rh-cd-row-failed { background: #fffbfb; }
.rh-cd-row-success { background: #fff; }
.rh-cd-status { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: 700; }
.rh-cd-status.success { background: #e8f5e9; color: #2e7d32; }
.rh-cd-status.failed  { background: #ffebee; color: #c62828; }
.rh-cd-name { font-family: monospace; font-size: 11px; font-weight: 600; color: #37474f; background: #f0f2f7; padding: 2px 6px; border-radius: 4px; white-space: nowrap; }
.rh-cd-area { color: #455a64; font-size: 12px; white-space: nowrap; }
.rh-cd-msg { color: #546e7a; font-size: 12px; max-width: 320px; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rh-cd-file { font-family: monospace; font-size: 11px; color: #546e7a; white-space: nowrap; }
.rh-cd-size { color: #78909c; white-space: nowrap; }
.rh-cd-dur  { font-weight: 600; color: #37474f; white-space: nowrap; }
.rh-cd-empty { color: #bdbdbd; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
