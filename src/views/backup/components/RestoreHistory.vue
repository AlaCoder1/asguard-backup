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

                  <!-- Rapport diff ligne par ligne — quand le restore a été
                       fait avec le nouveau code (restore_diff.py), on a un
                       diff exact des lignes ajoutées / supprimées / modifiées
                       par composant. Le placeholder s'affiche pour les
                       anciens restores qui n'ont pas généré de diff. -->
                  <div v-if="entry.diff && rhDiffComponents(entry).length > 0" class="rh-rowdiff-section">
                    <div class="rh-detail-title">
                      Rapport de changements ligne par ligne
                      <span class="rh-rowdiff-totals">
                        <span v-if="entry.diff.totals.added"   class="rh-rowdiff-tot pos">+{{ entry.diff.totals.added }} ajouté{{ entry.diff.totals.added>1?'s':'' }}</span>
                        <span v-if="entry.diff.totals.removed" class="rh-rowdiff-tot neg">−{{ entry.diff.totals.removed }} supprimé{{ entry.diff.totals.removed>1?'s':'' }}</span>
                        <span v-if="entry.diff.totals.modified" class="rh-rowdiff-tot mod">~{{ entry.diff.totals.modified }} modifié{{ entry.diff.totals.modified>1?'s':'' }}</span>
                      </span>
                    </div>

                    <div class="rh-rowdiff-list">
                      <details
                        v-for="comp in rhDiffComponents(entry)"
                        :key="`rdiff-${entry.job_id}-${comp.name}`"
                        class="rh-rowdiff-comp"
                      >
                        <summary>
                          <span class="rh-rowdiff-comp-name">{{ comp.name }}</span>
                          <span class="rh-rowdiff-comp-summary">
                            <span v-if="comp.summary.added"    class="rh-rowdiff-tot pos">+{{ comp.summary.added }}</span>
                            <span v-if="comp.summary.removed"  class="rh-rowdiff-tot neg">−{{ comp.summary.removed }}</span>
                            <span v-if="comp.summary.modified" class="rh-rowdiff-tot mod">~{{ comp.summary.modified }}</span>
                          </span>
                        </summary>

                        <div v-for="m in comp.models" :key="m.path" class="rh-rowdiff-model">
                          <div class="rh-rowdiff-model-head">
                            <strong>{{ m.label }}</strong>
                            <span class="rh-rowdiff-model-counts">{{ m.pre_count }} → {{ m.post_count }}</span>
                          </div>

                          <ul v-if="m.removed.length" class="rh-rowdiff-rows neg">
                            <li v-for="r in m.removed" :key="`r-${m.path}-${r.pk}`">
                              <span class="rh-rowdiff-op">−</span>
                              <span class="rh-rowdiff-pk">#{{ r.pk }}</span>
                              <span class="rh-rowdiff-summary">{{ r.summary }}</span>
                            </li>
                          </ul>

                          <ul v-if="m.added.length" class="rh-rowdiff-rows pos">
                            <li v-for="r in m.added" :key="`a-${m.path}-${r.pk}`">
                              <span class="rh-rowdiff-op">+</span>
                              <span class="rh-rowdiff-pk">#{{ r.pk }}</span>
                              <span class="rh-rowdiff-summary">{{ r.summary }}</span>
                            </li>
                          </ul>

                          <ul v-if="m.modified.length" class="rh-rowdiff-rows mod">
                            <li v-for="r in m.modified" :key="`m-${m.path}-${r.pk}`">
                              <span class="rh-rowdiff-op">~</span>
                              <span class="rh-rowdiff-pk">#{{ r.pk }}</span>
                              <span class="rh-rowdiff-summary">{{ r.summary }}</span>
                              <details v-if="r.changes" class="rh-rowdiff-changes">
                                <summary>{{ Object.keys(r.changes).length }} champ(s)</summary>
                                <table>
                                  <tbody>
                                    <tr v-for="(ch, field) in r.changes" :key="field">
                                      <td class="field">{{ field }}</td>
                                      <td class="before">{{ ch.before == null ? "∅" : ch.before }}</td>
                                      <td class="arrow">→</td>
                                      <td class="after">{{ ch.after == null ? "∅" : ch.after }}</td>
                                    </tr>
                                  </tbody>
                                </table>
                              </details>
                            </li>
                          </ul>
                        </div>
                      </details>
                    </div>
                  </div>
                  <!-- Diff could NOT be computed (timed out / DB busy during the
                       restore I/O window) — do NOT claim "identical". -->
                  <div
                    v-else-if="entry.diff && entry.diff.available === false"
                    class="rh-rowdiff-section rh-rowdiff-empty rh-rowdiff-unavail"
                  >
                    <div class="rh-detail-title">Rapport de changements ligne par ligne</div>
                    <span>⚠️ Rapport indisponible — le calcul du diff base de données n'a pas pu aboutir (système occupé pendant la restauration). Les changements système ci-dessous restent fiables.</span>
                  </div>
                  <!-- Only claim "identical" when the diff ACTUALLY ran (available
                       === true). Old restores (no availability flag) or ones whose
                       diff didn't run show nothing here, never a false "identical". -->
                  <div
                    v-else-if="entry.diff && entry.diff.available === true && rhDiffComponents(entry).length === 0"
                    class="rh-rowdiff-section rh-rowdiff-empty"
                  >
                    <div class="rh-detail-title">Rapport de changements ligne par ligne</div>
                    <span>Aucun changement détecté en base — le contenu restauré était identique à l'état précédent.</span>
                  </div>

                  <!-- System-level changes (root password, system users, hostname)
                       — what the DB row-diff can't show. -->
                  <div
                    v-if="entry.system_changes && entry.system_changes.checked"
                    class="rh-syschanges-section"
                  >
                    <div class="rh-detail-title">Changements système (hors base)</div>
                    <div v-if="entry.system_changes.any" class="rh-syschanges-list">
                      <div v-if="entry.system_changes.root_password_changed" class="rh-syschange rh-syschange-pwd">
                        🔑 <strong>Mot de passe root</strong> — restauré (différent de l'état avant restauration)
                      </div>
                      <div v-for="u in entry.system_changes.users_removed" :key="'ur-'+u" class="rh-syschange rh-syschange-userdel">
                        👤 Utilisateur système <code>{{ u }}</code> — supprimé par la restauration
                      </div>
                      <div v-for="u in entry.system_changes.users_added" :key="'ua-'+u" class="rh-syschange rh-syschange-useradd">
                        👤 Utilisateur système <code>{{ u }}</code> — ajouté par la restauration
                      </div>
                      <div v-if="entry.system_changes.hostname_changed" class="rh-syschange">
                        🏷️ Hostname — <code>{{ entry.system_changes.hostname_from }}</code> → <code>{{ entry.system_changes.hostname_to }}</code>
                      </div>
                    </div>
                    <div v-else class="rh-syschanges-none">
                      Aucun changement système détecté (mot de passe root, utilisateurs et hostname inchangés).
                    </div>
                  </div>

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
    // Flatten the diff payload from get_restore_history into a list of
    // components, each with its models[] ready to render. Identical shape
    // to Backups.vue's diffComponents — keeps the two views consistent.
    rhDiffComponents(entry) {
      const diff = entry && entry.diff;
      if (!diff || !diff.components) return [];
      return Object.entries(diff.components).map(([name, payload]) => ({
        name,
        summary: payload.summary || { added: 0, removed: 0, modified: 0 },
        models: Object.entries(payload.models || {}).map(([path, m]) => ({ path, ...m })),
      }));
    },
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
      const map = { manual: "Manuel", auto_pre_backup: "Auto · avant backup", auto_post_backup: "Auto · après backup" };
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

<style scoped lang="scss" src="../../../assets/scss/RestoreHistory.scss"></style>
