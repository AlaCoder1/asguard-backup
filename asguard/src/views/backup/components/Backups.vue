<template>
  <div class="backup-panel">
    <div class="backup-toolbar">
      <div class="backup-toolbar-left">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="loading"
          @click="openCreateDialog"
        >
          + Nouveau backup
        </button>
        <button
          class="btn btn-light"
          type="button"
          :disabled="loading"
          @click="triggerImport"
        >
          ↓ Importer
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".tar.gz,.tgz"
          class="backup-file-input"
          @change="importBackup"
        />
      </div>

      <div class="backup-filters">
        <label class="date-filter">
          <span class="filter-label">Période</span>
          <span class="select-wrap">
            <select v-model="selectedDateRange" class="backup-select">
              <option value="all">Toutes les dates</option>
              <option value="today">Aujourd'hui</option>
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>

              <option value="month">Ce mois</option>
              <option value="custom">Personnalisée</option>
            </select>
          </span>
        </label>

        <div v-if="selectedDateRange === 'custom'" class="custom-dates">
          <input v-model="dateFrom" class="date-input" type="date" />
          <span class="date-separator">à</span>
          <input v-model="dateTo" class="date-input" type="date" />
        </div>

        <span class="select-wrap type-select">
          <select v-model="selectedType" class="backup-select">
            <option value="all">Tous les types</option>
            <option value="full">Full</option>
            <option value="safe">Safe</option>
            <option value="custom">Custom</option>
            <option value="database_only">DB only</option>
          </select>
        </span>
      </div>
    </div>

              <div class="date-insight">
                <div class="date-insight-header">
                  <div class="date-insight-copy">
                    <strong>{{ dateInsightTitle }}</strong>
                    <span>{{ dateInsightText }}</span>
                  </div>
                  <button class="clear-filter-btn" type="button" @click="resetFilters">
                    Réinitialiser
                  </button>
                </div>
                <div class="insight-cards">
                  <div v-for="card in metricCards" :key="card.label" class="insight-card">
                    <span>{{ card.label }}</span>
                    <strong>{{ card.value }}</strong>
                    <small>{{ card.hint }}</small>
                  </div>
                </div>
              </div>

              <section class="backup-card">
                <div class="backup-card-header">
                  <span>Liste des backups</span>
                  <span class="backup-summary">
                    {{ filteredBackups.length }} backups -- {{ totalSizeLabel }}
                  </span>
                </div>

                <div class="table-scroll">
                  <table class="backup-table">
                    <thead>
                      <tr>
                        <th>BACKUP ID</th>
                        <th>DATE</th>
                        <th>TYPE</th>
                        <th>HEALTH</th>
                        <th>STATUT</th>
                        <th>TAILLE</th>
                        <th>COMPOSANTS</th>
                        <th>ACTIONS</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="loading">
                        <td colspan="8" class="backup-empty">Chargement...</td>
                      </tr>
                      <tr v-else-if="filteredBackups.length === 0">
                        <td colspan="8" class="backup-empty">Aucun backup trouvé.</td>
                      </tr>
                      <tr v-for="backup in paginatedBackups" v-else :key="backup.id">
                        <td class="backup-id">{{ backup.id }}</td>
                        <td>{{ formatDate(backup.modified_at) }}</td>
                        <td>
                          <span :class="['tag', typeClass(backup.type)]">
                            {{ typeLabel(backup.type) }}
                          </span>
                        </td>
                        <td>
                          <span :class="healthClass(backup.health)">
                            {{ backup.health }}
                          </span><span class="muted">/100</span>
                        </td>
                        <td>
                          <span :class="['status', statusClass(backup)]">
                            {{ statusLabel(backup) }}
                          </span>
                        </td>
                        <td>{{ formatSize(backup.sizeBytes) }}</td>
                        <td>{{ backup.componentsOk }}/{{ backup.componentsTotal }}</td>
                        <td>
                          <div class="backup-actions">
                            <button
                              :class="['btn', restoreButtonClass(backup)]"
                              type="button"
                              :disabled="loading || backup.type === 'database_only'"
                              @click="openRestoreDialog(backup)"
                            >
                              Restore
                            </button>
                            <button
                              class="btn btn-light"
                              type="button"
                              :disabled="loading || backup.type === 'database_only'"
                              @click="openDetails(backup)"
                            >
                              Details
                            </button>
                            <button
                              class="btn btn-light"
                              type="button"
                              :disabled="loading || backup.type === 'database_only' || exportLoading === backup.id"
                              @click="exportBackup(backup)"
                            >
                              {{ exportLoading === backup.id ? '...' : '↑ Export' }}
                            </button>
                            <button
                              class="btn btn-danger"
                              type="button"
                              :disabled="loading"
                              @click="deleteBackup(backup)"
                            >
                              Supprimer
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="filteredBackups.length > 0" class="pagination-bar">
                  <div class="pagination-info">
                    {{ paginationStart }}-{{ paginationEnd }} sur {{ filteredBackups.length }}
                  </div>
                  <div class="pagination-controls">
                    <button class="page-btn" :disabled="currentPage === 1" @click="currentPage -= 1">
                      Précédent
                    </button>
                    <button
                      v-for="page in visiblePages"
                      :key="page"
                      :class="['page-number', page === currentPage ? 'active' : '']"
                      @click="currentPage = page"
                    >
                      {{ page }}
                    </button>
                    <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage += 1">
                      Suivant
                    </button>
                    <span class="select-wrap page-size-select">
                      <select v-model.number="pageSize" class="backup-select">
                        <option :value="8">8 / page</option>
                        <option :value="12">12 / page</option>
                        <option :value="20">20 / page</option>
                      </select>
                    </span>
                  </div>
                </div>
              </section>

              <section class="backup-card import-card">
                <div class="backup-card-header">
                  <span>Importer un backup externe</span>
                </div>
                <div
                  :class="['drop-zone', { 'is-dragging': dragging }]"
                  @dragenter.prevent="dragging = true"
                  @dragover.prevent="dragging = true"
                  @dragleave.prevent="dragging = false"
                  @drop.prevent="dropImport"
                  @click="triggerImport"
                >
                  <div class="upload-icon">↓</div>
                  <div>Glisser-deposer un fichier backup</div>
                  <div class="muted">Formats .tar.gz, .tgz -- max 2 GB</div>
                  <button class="btn btn-primary mt-10" type="button">
                    Parcourir les fichiers
                  </button>
                </div>
              </section>

    <div v-if="createDialog" class="modal-backdrop" @click.self="closeCreateDialog">
      <div class="action-modal action-modal-create">
        <div class="action-modal-header">
          <div class="action-modal-copy">
            <span class="action-modal-kicker">Backup Studio</span>
            <strong>Créer un backup</strong>
            <span>Choisis le mode de sauvegarde avant de lancer l'opération.</span>
          </div>
          <button class="drawer-close" type="button" @click="closeCreateDialog">×</button>
        </div>

        <div class="mode-grid">
          <button :class="['mode-card', 'mode-card-full', createMode === 'full' ? 'active' : '']" type="button" title="Backup complet" @click="createMode = 'full'">
            <strong>Full</strong>
          </button>
          <button :class="['mode-card', 'mode-card-safe', createMode === 'safe' ? 'active' : '']" type="button" title="Backup admin sans partie applicative" @click="createMode = 'safe'">
            <strong>Safe</strong>
          </button>
          <button :class="['mode-card', 'mode-card-custom', createMode === 'custom' ? 'active' : '']" type="button" title="Selection de composants" @click="enableCustomCreateMode">
            <strong>Custom</strong>
          </button>
        </div>

        <div class="mode-spotlight">
          <div class="mode-spotlight-main">
            <span class="mode-spotlight-label">{{ createModeMeta.eyebrow }}</span>
            <strong>{{ createModeMeta.title }}</strong>
            <p>{{ createModeMeta.description }}</p>
          </div>
          <div class="mode-spotlight-side">
            <div class="mode-chip-list">
              <span
                v-for="highlight in createModeMeta.highlights"
                :key="highlight"
                class="mode-chip"
              >
                {{ highlight }}
              </span>
            </div>
            <div class="mode-side-note">
              <span>{{ createModeMeta.noteLabel }}</span>
              <strong>{{ createModeMeta.note }}</strong>
            </div>
          </div>
        </div>

        <div class="component-picker">
          <div class="component-picker-head">
            <strong>Composants</strong>
            <button
              class="link-btn"
              type="button"
              :disabled="createMode !== 'custom'"
              @click="selectedCreateComponents = backupComponents.slice()"
            >
              Tout sélectionner
            </button>
          </div>
          <div class="component-grid">
          <label v-for="component in backupComponents" :key="component" class="check-row">
            <input v-model="selectedCreateComponents" :value="component" type="checkbox" :disabled="createMode !== 'custom'" />
            <span>{{ component }}</span>
          </label>
          </div>
        </div>

        <div class="action-modal-footer">
          <button class="btn btn-light" type="button" :disabled="loading" @click="closeCreateDialog">
            Annuler
          </button>
          <button
            class="btn btn-primary"
            type="button"
            :disabled="loading || (createMode === 'custom' && selectedCreateComponents.length === 0)"
            @click="submitCreateBackup"
          >
            Lancer le backup
          </button>
        </div>
      </div>
    </div>

    <div v-if="restoreDialog" class="modal-backdrop" @click.self="closeRestoreDialog">
      <div class="action-modal action-modal-restore">
        <div class="action-modal-header">
          <div class="action-modal-copy">
            <span class="action-modal-kicker">Restore Control</span>
            <strong>Restore {{ restoreTarget?.id }}</strong>
            <span>Choisis le mode de restauration adapté à ce backup.</span>
          </div>
          <button class="drawer-close" type="button" @click="closeRestoreDialog">×</button>
        </div>

        <div class="mode-grid">
          <button
            v-if="showSafeRestoreMode"
            :class="['mode-card', 'mode-card-safe', restoreMode === 'safe' ? 'active' : '']"
            type="button"
            title="Restore sans application"
            @click="restoreMode = 'safe'"
          >
            <strong>Safe</strong>
          </button>
          <button :class="['mode-card', 'mode-card-full', restoreMode === 'complete' ? 'active' : '']" type="button" title="Restore full" @click="restoreMode = 'complete'">
            <strong>Full</strong>
          </button>
          <button :class="['mode-card', 'mode-card-custom', restoreMode === 'custom' ? 'active' : '']" type="button" title="Restaure seulement certains composants" @click="enableCustomRestoreMode">
            <strong>Custom</strong>
          </button>
        </div>

        <div class="mode-spotlight restore-spotlight">
          <div class="mode-spotlight-main">
            <span class="mode-spotlight-label">{{ restoreModeMeta.eyebrow }}</span>
            <strong>{{ restoreModeMeta.title }}</strong>
            <p>{{ restoreModeMeta.description }}</p>
          </div>
          <div class="mode-spotlight-side">
            <div class="mode-chip-list">
              <span
                v-for="highlight in restoreModeMeta.highlights"
                :key="highlight"
                class="mode-chip"
              >
                {{ highlight }}
              </span>
            </div>
            <div class="mode-side-note">
              <span>{{ restoreModeMeta.noteLabel }}</span>
              <strong>{{ restoreModeMeta.note }}</strong>
            </div>
          </div>
        </div>

        <div class="component-picker">
          <div class="component-picker-head">
            <strong>Composants restaurables</strong>
            <button
              class="link-btn"
              type="button"
              :disabled="restoreMode !== 'custom'"
              @click="selectedRestoreComponents = restoreComponents.slice()"
            >
              Tout sélectionner
            </button>
          </div>
          <div class="component-grid">
          <label v-for="component in restoreComponents" :key="component" class="check-row">
            <input v-model="selectedRestoreComponents" :value="component" type="checkbox" :disabled="restoreMode !== 'custom'" />
            <span>{{ component }}</span>
          </label>
          </div>
        </div>

        <div class="action-modal-footer">
          <button class="btn btn-light" type="button" :disabled="loading" @click="closeRestoreDialog">
            Annuler
          </button>
          <button
            class="btn btn-primary"
            type="button"
            :disabled="loading || (restoreMode === 'custom' && selectedRestoreComponents.length === 0)"
            @click="submitRestoreBackup"
          >
            Lancer le restore
          </button>
        </div>
      </div>
    </div>

    <div v-if="detailsDialog" class="drawer-backdrop" @click.self="detailsDialog = false">
      <aside class="details-drawer">
        <button class="drawer-close" type="button" @click="detailsDialog = false">×</button>
        <div v-if="selectedDetails">
          <header class="drawer-header">
            <span>Détails</span>
            <strong>{{ selectedDetails.backup_id }}</strong>
          </header>

          <div class="drawer-metrics">
            <div v-for="item in detailsSummary" :key="item.label" class="drawer-metric">
              <span>{{ item.label }}</span>
              <strong v-html="item.value"></strong>
            </div>
          </div>

          <section class="drawer-section">
            <div class="drawer-section-title">
              <h4>Composants</h4>
              <span>{{ detailsComponentSummary }}</span>
            </div>

            <div class="component-list">
              <div
                v-for="component in detailComponents"
                :key="component.name"
                class="component-row"
              >
                <div class="component-main">
                  <strong>{{ component.name }}</strong>
                  <small>sha256: {{ shortSha(component.sha256) }}</small>
                  <small
                    v-if="component.message"
                    :class="['component-message', component.status]"
                  >
                    {{ component.message }}
                  </small>
                </div>
                <div class="component-side">
                  <span :class="['component-status', component.status]">
                    {{ componentStatusLabel(component.status) }}
                  </span>
                  <small>{{ formatSizeFromMb(component.size_mb) }} · {{ formatDuration(component.duration_seconds) }}</small>
                </div>
              </div>
            </div>
          </section>

          <section class="drawer-section">
            <div class="drawer-section-title">
              <h4>Fichiers</h4>
              <span>{{ selectedDetails.files?.length || 0 }} fichiers</span>
            </div>
            <div class="file-list">
              <div v-for="file in selectedDetails.files" :key="file.path" class="file-row">
                <span>{{ file.path }}</span>
                <strong>{{ formatSize(file.size_bytes) }}</strong>
              </div>
            </div>
          </section>
        </div>
      </aside>
    </div>

    <div v-if="deleteConfirmDialog" class="modal-backdrop" @click.self="deleteConfirmDialog = false">
      <div class="action-modal action-modal-delete">
        <div class="action-modal-header">
          <div class="action-modal-copy">
            <span class="action-modal-kicker">Suppression définitive</span>
            <strong>Supprimer ce backup ?</strong>
            <span>Cette opération est irréversible. L'archive sera définitivement effacée du disque.</span>
          </div>
          <button class="drawer-close" type="button" @click="deleteConfirmDialog = false">×</button>
        </div>
        <div class="delete-target-info" v-if="deleteTarget">
          <div><span>ID</span><strong>{{ deleteTarget.id }}</strong></div>
          <div><span>Type</span><strong>{{ typeLabel(deleteTarget.type) }}</strong></div>
          <div><span>Date</span><strong>{{ formatDate(deleteTarget.modified_at) }}</strong></div>
          <div><span>Taille</span><strong>{{ formatSize(deleteTarget.sizeBytes) }}</strong></div>
        </div>
        <div class="action-modal-footer">
          <button class="btn btn-light" type="button" :disabled="loading" @click="deleteConfirmDialog = false">
            Annuler
          </button>
          <button class="btn btn-danger" type="button" :disabled="loading" @click="confirmDelete">
            Supprimer définitivement
          </button>
        </div>
      </div>
    </div>

    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="3200"
      location="bottom right"
    >
      {{ snackbarText }}
    </v-snackbar>

    <transition name="restore-monitor-fade">
      <div v-if="backupMonitor.visible" class="restore-monitor progress-monitor" :class="backupMonitor.status">
        <div class="restore-monitor-head">
          <div>
            <strong>{{ backupMonitor.title }}</strong>
            <span>{{ backupMonitor.subtitle }}</span>
          </div>
          <button class="restore-monitor-close" type="button" @click="closeBackupMonitor">×</button>
        </div>
        <div class="restore-monitor-pill-row">
          <span class="restore-pill">{{ backupMonitor.backupType === "safe" ? "Safe Backup" : "Full Backup" }}</span>
          <span class="restore-pill">{{ backupMonitor.jobId }}</span>
          <span class="restore-pill">{{ backupMonitor.statusLabel }}</span>
        </div>
        <div v-if="backupMonitor.progressActive || backupMonitor.progressPct > 0" class="pm-progress-wrap">
          <div class="pm-progress-track">
            <div class="pm-progress-fill" :class="{ 'pm-indeterminate': backupMonitor.total === 0 }" :style="backupMonitor.total > 0 ? { width: backupMonitor.progressPct + '%' } : {}"></div>
          </div>
          <span class="pm-progress-label">{{ backupMonitor.total > 0 ? `${backupMonitor.done}/${backupMonitor.total} composants` : "Initialisation..." }}</span>
        </div>
        <div v-if="backupMonitor.components && Object.keys(backupMonitor.components).length > 0" class="pm-component-grid">
          <div
            v-for="(status, name) in backupMonitor.components"
            :key="name"
            class="pm-component-chip"
            :class="status === 'success' ? 'pm-ok' : status === 'failed' ? 'pm-fail' : status === 'skipped' ? 'pm-skip' : name === backupMonitor.currentComponent ? 'pm-running' : 'pm-pending'"
          >
            <span class="pm-chip-dot"></span>
            <span class="pm-chip-name">{{ name }}</span>
          </div>
        </div>
        <div v-if="!backupMonitor.progressActive && backupMonitor.status === 'success' && backupMonitor.components" class="restore-summary">
          <div class="restore-summary-card">
            <span>Succes</span>
            <strong>{{ Object.values(backupMonitor.components).filter(s => s === 'success').length }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Echec</span>
            <strong>{{ Object.values(backupMonitor.components).filter(s => s === 'failed').length }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Ignores</span>
            <strong>{{ Object.values(backupMonitor.components).filter(s => s === 'skipped').length }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Total</span>
            <strong>{{ Object.keys(backupMonitor.components).length }}</strong>
          </div>
        </div>
      </div>
    </transition>

    <transition name="restore-monitor-fade">
      <div v-if="restoreMonitor.visible" class="restore-monitor" :class="restoreMonitor.status">
        <div class="restore-monitor-head">
          <div>
            <strong>{{ restoreMonitor.title }}</strong>
            <span>{{ restoreMonitor.subtitle }}</span>
          </div>
          <button class="restore-monitor-close" type="button" @click="closeRestoreMonitor">×</button>
        </div>

        <div class="restore-monitor-pill-row">
          <span class="restore-pill">{{ restoreMonitor.modeLabel }}</span>
          <span class="restore-pill">{{ restoreMonitor.backupId }}</span>
          <span class="restore-pill">{{ restoreMonitor.statusLabel }}</span>
        </div>

        <div v-if="restoreMonitor.progressActive || restoreMonitor.progressPct > 0" class="pm-progress-wrap">
          <div class="pm-progress-track">
            <div class="pm-progress-fill" :class="{ 'pm-indeterminate': restoreMonitor.total === 0 }" :style="restoreMonitor.total > 0 ? { width: restoreMonitor.progressPct + '%' } : {}"></div>
          </div>
          <span class="pm-progress-label">{{ restoreMonitor.total > 0 ? `${restoreMonitor.done}/${restoreMonitor.total} composants` : "Initialisation..." }}</span>
        </div>

        <div v-if="restoreMonitor.liveComponents && Object.keys(restoreMonitor.liveComponents).length > 0" class="pm-component-grid">
          <div
            v-for="(status, name) in restoreMonitor.liveComponents"
            :key="name"
            class="pm-component-chip"
            :class="status === 'success' ? 'pm-ok' : status === 'failed' ? 'pm-fail' : status === 'skipped' ? 'pm-skip' : status === 'running' ? 'pm-running' : 'pm-pending'"
          >
            <span class="pm-chip-dot"></span>
            <span class="pm-chip-name">{{ name }}</span>
          </div>
        </div>

        <div v-if="restoreMonitor.verification" class="restore-check-grid">
          <div
            v-for="check in restoreMonitor.verification.checks || []"
            :key="check.key"
            class="restore-check"
            :class="restoreCheckClass(check.status)"
          >
            <strong>{{ check.label }}</strong>
            <span>{{ check.detail }}</span>
          </div>
        </div>

        <div v-if="restoreMonitor.verification" class="restore-summary">
          <div class="restore-summary-card">
            <span>Succes</span>
            <strong>{{ restoreMonitor.verification.summary.success }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Failed</span>
            <strong>{{ restoreMonitor.verification.summary.failed }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Skipped</span>
            <strong>{{ restoreMonitor.verification.summary.skipped }}</strong>
          </div>
          <div class="restore-summary-card">
            <span>Duree</span>
            <strong>{{ formatDuration(restoreMonitor.verification.duration_seconds) }}</strong>
          </div>
        </div>

        <div v-if="restoreMonitor.restoredComponentsLabel" class="restore-evidence">
          <strong>Indice de verification</strong>
          <span>{{ restoreMonitor.restoredComponentsLabel }}</span>
        </div>
      </div>
    </transition>

    <transition name="restore-monitor-fade">
      <div v-if="importMonitor.visible" class="restore-monitor im-monitor" :class="importMonitor.status">
        <div class="restore-monitor-head">
          <div class="im-head-copy">
            <span class="im-kicker">{{ importMonitor.stage === 'done' ? 'Import réussi' : importMonitor.stage === 'error' ? 'Import échoué' : 'Import en cours' }}</span>
            <strong>{{ importMonitor.title }}</strong>
            <span v-if="importMonitor.stage !== 'error'">{{ importMonitor.subtitle }}</span>
          </div>
          <button class="restore-monitor-close" type="button" :disabled="importMonitor.progressActive" @click="importMonitor.visible = false">×</button>
        </div>

        <div class="im-stage-row">
          <div class="im-step" :class="{ 'im-step-active': importMonitor.stage === 'uploading', 'im-step-done': ['processing','done'].includes(importMonitor.stage), 'im-step-error': importMonitor.stage === 'error' }">
            <span class="im-step-dot"></span><span>Upload</span>
          </div>
          <div class="im-step-line"></div>
          <div class="im-step" :class="{ 'im-step-active': importMonitor.stage === 'processing', 'im-step-done': importMonitor.stage === 'done', 'im-step-error': importMonitor.stage === 'error' }">
            <span class="im-step-dot"></span><span>Validation</span>
          </div>
          <div class="im-step-line"></div>
          <div class="im-step" :class="{ 'im-step-done': importMonitor.stage === 'done', 'im-step-error': importMonitor.stage === 'error' }">
            <span class="im-step-dot"></span><span>Terminé</span>
          </div>
        </div>

        <div v-if="importMonitor.stage !== 'error'" class="pm-progress-wrap">
          <div class="pm-progress-track">
            <div
              class="pm-progress-fill"
              :class="{ 'pm-indeterminate': importMonitor.stage === 'processing' }"
              :style="importMonitor.stage === 'uploading' ? { width: importMonitor.uploadPct + '%' } : importMonitor.stage === 'done' ? { width: '100%' } : {}"
            ></div>
          </div>
          <span class="pm-progress-label">
            {{ importMonitor.stage === 'uploading' ? `Upload ${importMonitor.uploadPct}%` : importMonitor.stage === 'processing' ? 'Validation & extraction...' : '100% — Importé' }}
          </span>
        </div>

        <div v-if="importMonitor.stage === 'done' && importMonitor.result" class="im-success-block">
          <div class="im-success-row">
            <span class="im-label">Backup ID</span>
            <strong class="im-value">{{ importMonitor.result.backup_id || '-' }}</strong>
          </div>
          <div class="im-success-row">
            <span class="im-label">Message</span>
            <span class="im-value">{{ importMonitor.result.message || 'Importé avec succès.' }}</span>
          </div>
        </div>

        <div v-if="importMonitor.stage === 'error'" class="im-error-block">
          <div class="im-error-icon">✕</div>
          <div class="im-error-copy">
            <strong>{{ importMonitor.errorTitle }}</strong>
            <span>{{ importMonitor.errorMsg }}</span>
            <small v-if="importMonitor.errorHint">{{ importMonitor.errorHint }}</small>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  name: "Backups",
  inject: ["emitter"],
  data() {
    return {
      selectedType: "all",
      selectedDateRange: "all",
      dateFrom: "",
      dateTo: "",
      backups: [],
      loading: false,
      dragging: false,
      currentPage: 1,
      pageSize: 12,
      detailsDialog: false,
      selectedDetails: null,
      createDialog: false,
      createMode: "full",
      backupComponents: [],
      selectedCreateComponents: [],
      restoreDialog: false,
      restoreTarget: null,
      restoreMode: "complete",
      restoreComponents: [],
      selectedRestoreComponents: [],
      restoreMonitor: {
        visible: false,
        title: "",
        subtitle: "",
        backupId: "",
        modeLabel: "",
        status: "idle",
        statusLabel: "Idle",
        progressActive: false,
        progressPct: 0,
        done: 0,
        total: 0,
        verification: null,
        restoredComponentsLabel: "",
        liveComponents: null,
      },
      restorePoller: null,
      importMonitor: {
        visible: false,
        title: "",
        subtitle: "",
        status: "idle",
        statusLabel: "Idle",
        progressActive: false,
        uploadPct: 0,
        stage: "",
        result: null,
        errorTitle: "",
        errorMsg: "",
        errorHint: "",
      },
      exportLoading: null,
      backupMonitor: {
        visible: false,
        title: "",
        subtitle: "",
        jobId: "",
        backupType: "",
        status: "idle",
        statusLabel: "Idle",
        progressActive: false,
        progressPct: 0,
        done: 0,
        total: 0,
        components: null,
        currentComponent: null,
        result: null,
      },
      backupPoller: null,
      snackbar: false,
      snackbarColor: "success",
      snackbarText: "",
      deleteConfirmDialog: false,
      deleteTarget: null,
    };
  },
  computed: {
    filteredBackups() {
      return this.backups.filter((backup) => {
        const typeMatches = this.selectedType === "all" || backup.type === this.selectedType;
        return typeMatches && this.isInsideSelectedDateRange(backup.modified_at);
      });
    },
    paginatedBackups() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.filteredBackups.slice(start, start + this.pageSize);
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredBackups.length / this.pageSize));
    },
    showSafeRestoreMode() {
      return this.restoreTargetHasApplication;
    },
    restoreTargetHasApplication() {
      return this.backupHasApplication(this.restoreTarget);
    },
    createModeMeta() {
      const meta = {
        full: {
          eyebrow: "Mode integral",
          title: "Image complete du systeme",
          description: "Capture toute la plateforme, y compris la couche applicative, pour un vrai scenario de reprise totale.",
          highlights: ["Application incluse", "Reprise complete", "Scenario disaster recovery"],
          noteLabel: "Usage ideal",
          note: "A utiliser quand tu veux pouvoir remettre toute la machine telle quelle.",
        },
        safe: {
          eyebrow: "Mode cadence",
          title: "Snapshot leger pret pour l'automatisation",
          description: "Capture le coeur reseau et securite sans embarquer l'application. Plus rapide, plus propre, meilleur pour les sauvegardes regulieres.",
          highlights: ["Sans overwrite du code", "Parfait pour cron", "Restore rapide config/securite"],
          noteLabel: "Signature",
          note: "Le mode safe devient ton backup recurrent et discret, pas juste une version mini du full.",
        },
        custom: {
          eyebrow: "Mode precision",
          title: "Selection libre composant par composant",
          description: "Tu choisis exactement ce que tu emportes. Rien n'est coche par defaut pour te laisser un vrai controle.",
          highlights: [
            "Choix composant par composant",
            "Ideal avant gros changements",
            this.selectedCreateComponents.length
              ? `${this.selectedCreateComponents.length} composant(s) selectionne(s)`
              : "Aucune selection par defaut",
          ],
          noteLabel: "Pilotage",
          note: "Parfait pour preparer un backup cible avant une operation sensible.",
        },
      };
      return meta[this.createMode] || meta.full;
    },
    restoreModeMeta() {
      const meta = {
        safe: {
          eyebrow: "Restore prudent",
          title: "Restauration sans toucher a l'application",
          description: "Remet les couches de config et de securite tout en gardant le code actuellement en place.",
          highlights: ["Application preservee", "Moins intrusif", "Bon pour un retour rapide"],
          noteLabel: "Disponible",
          note: "Ce mode apparait seulement quand le backup contient aussi la couche application.",
        },
        complete: {
          eyebrow: "Restore integral",
          title: this.restoreTargetHasApplication
            ? "Restauration full du backup"
            : "Restauration de tout le contenu disponible",
          description: this.restoreTargetHasApplication
            ? "Remet tout le backup, application comprise, avec verification et suivi du job de restauration."
            : "Applique tout ce que ce backup contient. Si l'application n'est pas dedans, elle n'est pas touchee.",
          highlights: this.restoreTargetHasApplication
            ? ["Application restauree", "Tous les composants disponibles", "Reprise complete"]
            : ["Tous les composants du backup", "Sans couche application", "Restore global du contenu disponible"],
          noteLabel: "Lecture du backup",
          note: this.restoreTargetHasApplication
            ? "Ce backup embarque l'application, donc tu peux choisir safe, full ou custom."
            : "Ce backup ne contient pas l'application, donc seuls full et custom sont proposes.",
        },
        custom: {
          eyebrow: "Restore cible",
          title: "Restauration au composant",
          description: "Pratique pour corriger une zone precise sans relancer tout le scope du backup.",
          highlights: [
            "Selection libre",
            "Impact limite",
            this.selectedRestoreComponents.length
              ? `${this.selectedRestoreComponents.length} composant(s) choisis`
              : "Choisis les composants a restaurer",
          ],
          noteLabel: "Selection",
          note: "Utilise ce mode pour corriger un service ou une zone sans restaurer tout le reste.",
        },
      };
      return meta[this.restoreMode] || meta.complete;
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, start + 4);
      for (let page = start; page <= end; page += 1) {
        pages.push(page);
      }
      return pages;
    },
    paginationStart() {
      if (this.filteredBackups.length === 0) return 0;
      return (this.currentPage - 1) * this.pageSize + 1;
    },
    paginationEnd() {
      return Math.min(this.currentPage * this.pageSize, this.filteredBackups.length);
    },
    totalSizeLabel() {
      const total = this.filteredBackups.reduce(
        (sum, backup) => sum + (backup.sizeBytes || 0),
        0
      );
      return this.formatSize(total);
    },
    dateInsightTitle() {
      const labels = {
        all: "Vue complète",
        today: "Focus aujourd'hui",
        "7d": "Fenêtre courte",
        "30d": "Tendance mensuelle",
        month: "Mois courant",
        custom: "Fenêtre personnalisée",
      };
      return labels[this.selectedDateRange];
    },
    dateInsightText() {
      if (this.filteredBackups.length === 0) {
        return "Aucun backup ne correspond aux critères.";
      }
      const newest = this.filteredBackups[0]?.modified_at;
      return `${this.filteredBackups.length} résultat(s), dernier backup ${this.formatDate(newest)}.`;
    },
    metricCards() {
      const partial = this.filteredBackups.filter((backup) => this.statusLabel(backup) === "Incomplet").length;
      const failed = this.filteredBackups.filter((backup) => this.statusLabel(backup) === "Echec").length;
      let healthHint = "tout est OK";
      if (failed > 0) {
        healthHint = `${failed} en echec`;
      } else if (partial > 0) {
        healthHint = `${partial} incomplet(s)`;
      }
      return [
        {
          label: "Résultats",
          value: String(this.filteredBackups.length),
          hint: "après filtres",
        },
        {
          label: "Taille",
          value: this.totalSizeLabel,
          hint: "volume cumulé",
        },
        {
          label: "Health moyen",
          value: `${this.averageHealth}/100`,
          hint: healthHint,
        },
        {
          label: "Dernier",
          value: this.formatDate(this.filteredBackups[0]?.modified_at),
          hint: "backup le plus récent",
        },
      ];
    },
    averageHealth() {
      if (this.filteredBackups.length === 0) return 0;
      const total = this.filteredBackups.reduce((sum, backup) => sum + Number(backup.health || 0), 0);
      return Math.round(total / this.filteredBackups.length);
    },
    detailsSummary() {
      const metadata = this.selectedDetails?.metadata || {};
      const totals = metadata.totals || {};
      const componentsOk = totals.components_success ?? 0;
      const componentsFailed = totals.components_failed ?? 0;
      const componentsSkipped = totals.components_skipped ?? 0;
      const totalComponents = componentsOk + componentsFailed + componentsSkipped;
      const overallStatus =
        metadata.overall_status ??
        (componentsFailed > 0 ? "error" : componentsSkipped > 0 ? "partial" : "ok");

      return [
        {
          label: "Statut",
          value: `<span class="metric-${this.statusClassFromValue(overallStatus)}">${this.statusLabelFromValue(overallStatus)}</span>`,
        },
        {
          label: "Health score",
          value: `<span class="metric-${this.healthMetricClass(metadata.health_score)}">${metadata.health_score ?? "-"}</span>/100`,
        },
        {
          label: "Durée totale",
          value: this.formatDuration(totals.duration_seconds),
        },
        {
          label: "Taille totale",
          value: this.formatSize(this.selectedDetails?.total_size_bytes),
        },
        {
          label: "Composants",
          value: `${componentsOk}/${totalComponents} <span class="metric-good">OK</span>`,
        },
      ];
    },
    detailComponents() {
      const components = this.selectedDetails?.metadata?.components || {};
      return Object.entries(components).map(([name, data]) => ({
        name,
        status: data.status || "unknown",
        sha256: data.sha256 || "",
        size_mb: data.size_mb || 0,
        duration_seconds: data.duration_seconds || 0,
        message: data.message || "",
      }));
    },
    detailsComponentSummary() {
      const totals = this.selectedDetails?.metadata?.totals || {};
      const ok = totals.components_success ?? 0;
      const failed = totals.components_failed ?? 0;
      const skipped = totals.components_skipped ?? 0;
      const total = ok + failed + skipped || this.detailComponents.length;
      return `${ok}/${total} OK · ${failed} failed · ${skipped} skipped`;
    },
  },
  watch: {
    selectedType() {
      this.currentPage = 1;
    },
    selectedDateRange() {
      this.currentPage = 1;
    },
    dateFrom() {
      this.currentPage = 1;
    },
    dateTo() {
      this.currentPage = 1;
    },
    pageSize() {
      this.currentPage = 1;
    },
    totalPages(value) {
      if (this.currentPage > value) {
        this.currentPage = value;
      }
    },
  },
  mounted() {
    this.fetchBackups();
    this.emitter.on("retention-applied", () => this.fetchBackups());
  },
  beforeUnmount() {
    this.stopRestorePolling();
    this.stopBackupPolling();
  },
  methods: {
    setCsrfHeader() {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    },
    async fetchComponentCatalog(backupId = null) {
      const response = await axios.get("/backup/components", {
        params: backupId ? { backup_id: backupId } : {},
      });
      this.backupComponents = response.data?.backup_components || [];
      this.restoreComponents = response.data?.restore_components || [];
    },
    stopRestorePolling() {
      if (this.restorePoller) {
        window.clearInterval(this.restorePoller);
        this.restorePoller = null;
      }
    },
    closeRestoreMonitor() {
      if (this.restoreMonitor.progressActive) return;
      this.restoreMonitor.visible = false;
    },
    openRestoreMonitor({ backupId, modeLabel, title, subtitle, status = "running", statusLabel = "Running", progressActive = true, verification = null, progressPct = 0, done = 0, total = 0, liveComponents = null }) {
      this.restoreMonitor = {
        visible: true,
        title,
        subtitle,
        backupId,
        modeLabel,
        status,
        statusLabel,
        progressActive,
        verification,
        progressPct,
        done,
        total,
        liveComponents,
        restoredComponentsLabel: verification ? this.buildRestoredComponentsLabel(verification.summary) : "",
      };
    },
    restoreCheckClass(status) {
      if (status === "passed") return "passed";
      if (status === "warning") return "warning";
      if (status === "failed") return "failed";
      return "unknown";
    },
    buildRestoredComponentsLabel(summary = {}) {
      const restored = summary.restored_components || [];
      const failed = summary.failed_components || [];
      if (restored.length && failed.length === 0) {
        return `Restore confirme sur ${restored.length} composant(s): ${restored.slice(0, 4).join(", ")}${restored.length > 4 ? "..." : ""}.`;
      }
      if (restored.length || failed.length) {
        return `Succes: ${restored.join(", ") || "aucun"} | Failed: ${failed.join(", ") || "aucun"}.`;
      }
      return "Le restore est termine mais aucun composant valide n'a ete confirme.";
    },
    startBackupPolling(jobId, backupType) {
      this.stopBackupPolling();
      const typeLabel = backupType === "safe" ? "Safe Backup" : "Full Backup";
      this.backupMonitor = {
        visible: true,
        title: "Backup en cours",
        subtitle: "Démarré en arrière-plan. Suivi en temps réel...",
        jobId,
        backupType,
        status: "running",
        statusLabel: "Running",
        progressActive: true,
        progressPct: 0,
        done: 0,
        total: 0,
        components: null,
        currentComponent: null,
        result: null,
      };

      const poll = async () => {
        try {
          const response = await axios.get(`/backup/progress/${jobId}`);
          const payload = response.data || {};
          const status = payload.status || "running";
          const isFinished = ["success", "error"].includes(status);

          this.backupMonitor = {
            ...this.backupMonitor,
            status,
            statusLabel: isFinished ? (status === "success" ? "Terminé" : "Erreur") : "Running",
            title: isFinished ? (status === "success" ? "Backup terminé" : "Backup échoué") : `Backup en cours — ${typeLabel}`,
            subtitle: isFinished
              ? (status === "success" ? "Tous les composants sauvegardés." : "Une erreur est survenue.")
              : `Composant actuel: ${payload.current_component || "initialisation..."}`,
            progressActive: !isFinished,
            progressPct: payload.progress_pct || 0,
            done: payload.done || 0,
            total: payload.total || 0,
            components: payload.components_progress || null,
            currentComponent: payload.current_component || null,
            result: payload.result || null,
          };

          if (isFinished) {
            this.stopBackupPolling();
            this.notify(
              status === "success" ? `Backup ${typeLabel} terminé avec succès.` : `Backup ${typeLabel} échoué.`,
              status === "success" ? "success" : "error"
            );
            await this.fetchBackups();
          }
        } catch (error) {
          this.stopBackupPolling();
          this.backupMonitor = {
            ...this.backupMonitor,
            status: "error",
            statusLabel: "Erreur",
            title: "Suivi backup interrompu",
            subtitle: "Impossible de lire le statut du backup.",
            progressActive: false,
          };
        }
      };

      poll();
      this.backupPoller = window.setInterval(poll, 2000);
    },
    stopBackupPolling() {
      if (this.backupPoller) {
        clearInterval(this.backupPoller);
        this.backupPoller = null;
      }
    },
    closeBackupMonitor() {
      if (this.backupMonitor.progressActive) return;
      this.backupMonitor.visible = false;
    },
    startRestorePolling(jobId, backupId, modeLabel) {
      this.stopRestorePolling();
      this.openRestoreMonitor({
        backupId,
        modeLabel,
        title: "Restore en cours",
        subtitle: "Lancement accepte. Verification et suivi en temps reel...",
      });

      const poll = async () => {
        try {
          const response = await axios.get(`/backup/restore-full-status/${jobId}`);
          const payload = response.data || {};
          const verification = payload.verification || null;
          const status = payload.status || "running";
          const isFinished = ["success", "partial_success", "error"].includes(status);
          const liveComponents = (!isFinished && payload.components_progress)
            ? payload.components_progress
            : null;

          this.openRestoreMonitor({
            backupId: payload.backup_id || backupId,
            modeLabel,
            title: isFinished ? "Restore termine" : "Restore en cours",
            subtitle: isFinished
              ? "Verification finale du restore disponible ci-dessous."
              : `Composant actuel: ${payload.current_component || "initialisation..."}`,
            status,
            statusLabel: this.restoreStatusLabel(status),
            progressActive: !isFinished,
            verification: isFinished ? verification : null,
            progressPct: payload.progress_pct || 0,
            done: payload.done || 0,
            total: payload.total || 0,
            liveComponents,
          });

          if (isFinished) {
            this.stopRestorePolling();
            this.notify(
              status === "success"
                ? "Restore termine et verifie."
                : status === "partial_success"
                  ? "Restore termine avec verification partielle."
                  : "Restore termine avec erreur.",
              status === "success" ? "success" : "error"
            );
            await this.fetchBackups();
          }
        } catch (error) {
          this.stopRestorePolling();
          this.openRestoreMonitor({
            backupId,
            modeLabel,
            title: "Suivi restore interrompu",
            subtitle: "Impossible de lire le statut du job de restore.",
            status: "error",
            statusLabel: "Error",
            progressActive: false,
            verification: null,
            liveComponents: null,
          });
        }
      };

      poll();
      this.restorePoller = window.setInterval(poll, 2500);
    },
    restoreStatusLabel(status) {
      const labels = {
        queued: "Queued",
        running: "Running",
        success: "Verified",
        partial_success: "Partial",
        error: "Error",
      };
      return labels[status] || status;
    },
    normalizeImmediateRestoreVerification(backupId, mode, result) {
      const summary = result?.summary || {};
      const results = result?.results || {};
      const checks = [
        {
          key: "restore_result",
          label: "Execution restore",
          status: result?.status === "success" ? "passed" : (result?.status === "partial_success" ? "warning" : "failed"),
          detail: `${summary.success || 0} composant(s) restaures avec succes.`,
        },
      ];
      if (results.firewall) {
        checks.push({
          key: "firewall",
          label: "Firewall applique",
          status: results.firewall.status === "success" ? "passed" : (results.firewall.status === "skipped" ? "warning" : "failed"),
          detail: results.firewall.message || "Verification firewall terminee.",
        });
      }
      return {
        backup_id: backupId,
        mode,
        status: result?.status || "error",
        duration_seconds: 0,
        summary: {
          success: summary.success || 0,
          failed: summary.failed || 0,
          skipped: summary.skipped || 0,
          restored_components: Object.entries(results).filter(([, item]) => item.status === "success").map(([name]) => name),
          failed_components: Object.entries(results).filter(([, item]) => item.status === "failed").map(([name]) => name),
          skipped_components: Object.entries(results).filter(([, item]) => item.status === "skipped").map(([name]) => name),
        },
        checks,
      };
    },
    async fetchBackups() {
      this.loading = true;
      try {
        const response = await axios.get("/backup/getAllBackups");
        this.backups = (response.data.results || []).map(this.normalizeBackup);
      } catch (error) {
        this.notify("Erreur lors du chargement des backups.", "error");
      } finally {
        this.loading = false;
      }
    },
    normalizeBackup(backup) {
      const metadata = backup.metadata || {};
      const totals = metadata.totals || {};
      const components = metadata.components || {};
      const componentsList = Object.values(components);
      const componentsOk =
        backup.components_success ??
        totals.components_success ??
        componentsList.filter((item) => item.status === "success").length;
      const componentsFailed =
        backup.components_failed ??
        totals.components_failed ??
        componentsList.filter((item) => item.status === "failed").length;
      const componentsSkipped =
        backup.components_skipped ??
        totals.components_skipped ??
        componentsList.filter((item) => item.status === "skipped").length;
      const componentsTotal =
        componentsOk +
        componentsFailed +
        componentsSkipped ||
        (backup.type === "database_only" ? 1 : componentsList.length);
      const sizeBytes =
        backup.size_bytes ??
        Math.round((totals.size_mb || 0) * 1024 * 1024);

      const NON_CRITICAL = new Set(["vm_snapshot", "vm_snapshot_pre", "vm_snapshot_post"]);
      const allSkippedComponents = Object.entries(metadata.components || {})
        .filter(([, data]) => data?.status === "skipped")
        .map(([name]) => name);
      const hasCriticalSkipped = allSkippedComponents.some((name) => !NON_CRITICAL.has(name));
      return {
        ...backup,
        overallStatus:
          backup.overall_status ??
          metadata.overall_status ??
          (componentsFailed > 0 ? "error" : hasCriticalSkipped ? "partial" : "ok"),
        health: backup.health_score ?? metadata.health_score ?? (componentsFailed > 0 ? 0 : 100),
        sizeBytes,
        componentsOk,
        componentsFailed,
        componentsSkipped,
        componentsTotal,
      };
    },
    backupHasApplication(backup) {
      return backup?.metadata?.components?.application?.status === "success";
    },
    async openCreateDialog() {
      this.createMode = "full";
      this.selectedCreateComponents = [];
      this.createDialog = true;
      try {
        await this.fetchComponentCatalog();
      } catch (error) {
        this.notify("Impossible de charger les composants backup.", "error");
      }
    },
    closeCreateDialog() {
      if (this.loading) return;
      this.createDialog = false;
    },
    enableCustomCreateMode() {
      this.createMode = "custom";
      this.selectedCreateComponents = [];
    },
    async submitCreateBackup() {
      this.loading = true;
      this.setCsrfHeader();
      try {
        let response;
        if (this.createMode === "safe") {
          response = await axios.post("/backup/create-safe-backup");
        } else if (this.createMode === "custom") {
          response = await axios.post("/backup/create-custom-backup", {
            components: this.selectedCreateComponents,
          });
        } else {
          response = await axios.post("/backup/create-full-backup");
        }
        this.createDialog = false;
        if (response.data?.job_id && this.createMode !== "custom") {
          this.startBackupPolling(response.data.job_id, this.createMode);
          this.notify(response.data.message || "Backup démarré en arrière-plan.");
        } else {
          this.notify(response.data?.message || "Backup créé avec succès.");
          await this.fetchBackups();
        }
      } catch (error) {
        this.notify(
          error.response?.data?.message || "Erreur lors de la création du backup.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    async openRestoreDialog(backup) {
      if (backup.type === "database_only") {
        this.notify("Restore non disponible pour les anciens dumps DB.", "error");
        return;
      }
      this.restoreTarget = backup;
      this.restoreMode = "complete";
      this.restoreComponents = [];
      this.selectedRestoreComponents = [];
      this.restoreDialog = true;
      try {
        await this.fetchComponentCatalog(backup.id);
      } catch (error) {
        this.notify("Impossible de charger les composants restaurables.", "error");
      }
    },
    closeRestoreDialog() {
      if (this.loading) return;
      this.restoreDialog = false;
    },
    enableCustomRestoreMode() {
      this.restoreMode = "custom";
      this.selectedRestoreComponents = [];
    },
    async submitRestoreBackup() {
      if (!this.restoreTarget) return;
      this.loading = true;
      this.setCsrfHeader();
      try {
        let response;
        const modeLabel = this.restoreMode === "complete"
          ? "Full restore"
          : this.restoreMode === "custom"
            ? "Custom restore"
            : "Safe restore";
        if (this.restoreMode === "custom") {
          response = await axios.post(
            `/backup/${this.restoreTarget.id}/restore-components`,
            { components: this.selectedRestoreComponents }
          );
          const verification = this.normalizeImmediateRestoreVerification(
            this.restoreTarget.id,
            this.restoreMode,
            response.data
          );
          this.openRestoreMonitor({
            backupId: this.restoreTarget.id,
            modeLabel,
            title: "Restore termine",
            subtitle: "Le restore custom a fini. Verification disponible.",
            status: response.data?.status || "success",
            statusLabel: this.restoreStatusLabel(response.data?.status || "success"),
            progressActive: false,
            verification,
          });
          await this.fetchBackups();
        } else {
          const endpoint = this.restoreMode === "complete" ? "restore-full" : "restore";
          response = await axios.post(`/backup/${this.restoreTarget.id}/${endpoint}`);
          if (response.data?.job_id) {
            this.startRestorePolling(response.data.job_id, this.restoreTarget.id, modeLabel);
          }
        }
        this.notify(response.data.message || "Restore lancé.");
        this.restoreDialog = false;
      } catch (error) {
        this.notify(
          error.response?.data?.message || "Erreur lors du lancement du restore.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    deleteBackup(backup) {
      this.deleteTarget = backup;
      this.deleteConfirmDialog = true;
    },
    async confirmDelete() {
      if (!this.deleteTarget) return;
      this.loading = true;
      this.setCsrfHeader();
      try {
        const response = await axios.delete(`/backup/${this.deleteTarget.id}/delete`);
        this.notify(response.data.message || "Backup supprimé avec succès.");
        this.deleteConfirmDialog = false;
        this.deleteTarget = null;
        await this.fetchBackups();
      } catch (error) {
        this.notify(
          error.response?.data?.message || "Erreur lors de la suppression du backup.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    async openDetails(backup) {
      this.loading = true;
      try {
        const response = await axios.get(`/backup/${backup.id}/details`);
        this.selectedDetails = response.data;
        this.detailsDialog = true;
      } catch (error) {
        this.notify("Impossible de charger les détails du backup.", "error");
      } finally {
        this.loading = false;
      }
    },
    async exportBackup(backup) {
      if (backup.type === "database_only") {
        this.notify("Export non disponible pour les anciens dumps DB.", "error");
        return;
      }
      this.exportLoading = backup.id;
      this.notify(`Export en préparation — ${backup.id}...`);
      try {
        const link = document.createElement("a");
        link.href = `/backup/${backup.id}/export`;
        link.setAttribute("download", `asguard_export_${backup.id}.tar.gz`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setTimeout(() => {
          this.notify(`Export lancé — ${backup.id}.`, "success");
          this.exportLoading = null;
        }, 3000);
      } catch (e) {
        this.notify(`Erreur lors de l'export: ${e.message}`, "error");
        this.exportLoading = null;
      }
    },
    triggerImport() {
      const fileInput = Array.isArray(this.$refs.fileInput)
        ? this.$refs.fileInput[0]
        : this.$refs.fileInput;
      if (fileInput) {
        fileInput.click();
      } else {
        this.notify("Input import introuvable. Recharge la page puis réessaie.", "error");
      }
    },
    dropImport(event) {
      this.dragging = false;
      const file = event.dataTransfer.files?.[0];
      if (file) this.uploadImport(file);
    },
    importBackup(event) {
      const file = event.target.files?.[0];
      if (file) this.uploadImport(file);
      event.target.value = "";
    },
    _parseImportError(error) {
      const status = error.response?.status;
      const serverMsg = error.response?.data?.message || "";

      if (status === 413) {
        return {
          errorTitle: "Fichier trop volumineux (413)",
          errorMsg: "Le serveur a rejeté le fichier car il dépasse la taille maximale autorisée.",
          errorHint: "Limite : 2 GB. Vérifiez que le fichier est bien une archive backup Asguard valide.",
        };
      }
      if (status === 400 && serverMsg.toLowerCase().includes("already exists")) {
        const match = serverMsg.match(/Backup (.+) already exists/i);
        const bid = match ? match[1] : "";
        return {
          errorTitle: "Backup déjà présent",
          errorMsg: bid ? `Le backup « ${bid} » existe déjà sur cette machine.` : "Ce backup existe déjà sur cette machine.",
          errorHint: "Supprimez le backup existant avant de réimporter, ou utilisez une archive d'un autre backup.",
        };
      }
      if (status === 400 && serverMsg) {
        return {
          errorTitle: "Validation échouée",
          errorMsg: serverMsg,
          errorHint: "Vérifiez que l'archive est bien un export Asguard (.tar.gz) valide et non corrompu.",
        };
      }
      if (!error.response) {
        return {
          errorTitle: "Connexion interrompue",
          errorMsg: "La requête n'a pas pu atteindre le serveur.",
          errorHint: "Vérifiez votre connexion réseau et réessayez.",
        };
      }
      return {
        errorTitle: `Erreur serveur (${status || "?"})`,
        errorMsg: serverMsg || "Une erreur inattendue s'est produite côté serveur.",
        errorHint: "Consultez les logs Django pour plus de détails.",
      };
    },
    async uploadImport(file) {
      if (file.size > 2 * 1024 * 1024 * 1024) {
        this.importMonitor = {
          visible: true,
          title: file.name,
          subtitle: "",
          status: "error",
          statusLabel: "Erreur",
          progressActive: false,
          uploadPct: 0,
          stage: "error",
          result: null,
          errorTitle: "Fichier trop volumineux",
          errorMsg: `Le fichier fait ${(file.size / 1024 / 1024 / 1024).toFixed(2)} GB, la limite est 2 GB.`,
          errorHint: "Utilisez un backup plus léger ou fragmentez l'archive.",
        };
        return;
      }

      this.importMonitor = {
        visible: true,
        title: file.name,
        subtitle: `Taille : ${(file.size / 1024 / 1024).toFixed(1)} MB`,
        status: "running",
        statusLabel: "Upload",
        progressActive: true,
        uploadPct: 0,
        stage: "uploading",
        result: null,
        errorTitle: "",
        errorMsg: "",
        errorHint: "",
      };

      this.setCsrfHeader();
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post("/backup/import", formData, {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (evt) => {
            if (evt.total) {
              const pct = Math.min(99, Math.round((evt.loaded / evt.total) * 100));
              this.importMonitor = { ...this.importMonitor, uploadPct: pct };
              if (pct >= 99) {
                this.importMonitor = {
                  ...this.importMonitor,
                  stage: "processing",
                  statusLabel: "Traitement",
                  subtitle: "Validation et extraction en cours...",
                };
              }
            }
          },
        });
        this.importMonitor = {
          visible: true,
          title: response.data?.backup_id || file.name,
          subtitle: "",
          status: "success",
          statusLabel: "Terminé",
          progressActive: false,
          uploadPct: 100,
          stage: "done",
          result: response.data,
          errorTitle: "",
          errorMsg: "",
          errorHint: "",
        };
        this.notify(response.data.message || "Backup importé avec succès.");
        await this.fetchBackups();
      } catch (error) {
        const parsed = this._parseImportError(error);
        this.importMonitor = {
          ...this.importMonitor,
          status: "error",
          statusLabel: "Erreur",
          progressActive: false,
          stage: "error",
          ...parsed,
        };
        this.notify(parsed.errorMsg, "error");
      }
    },
    isInsideSelectedDateRange(value) {
      if (this.selectedDateRange === "all") return true;
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return false;

      const now = new Date();
      const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      let from = null;
      let to = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);

      if (this.selectedDateRange === "today") {
        from = startOfToday;
      } else if (this.selectedDateRange === "7d") {
        from = new Date(now);
        from.setDate(now.getDate() - 7);
      } else if (this.selectedDateRange === "30d") {
        from = new Date(now);
        from.setDate(now.getDate() - 30);
      } else if (this.selectedDateRange === "month") {
        from = new Date(now.getFullYear(), now.getMonth(), 1);
      } else if (this.selectedDateRange === "custom") {
        from = this.dateFrom ? new Date(`${this.dateFrom}T00:00:00`) : null;
        to = this.dateTo ? new Date(`${this.dateTo}T23:59:59`) : null;
      }

      if (from && date < from) return false;
      if (to && date > to) return false;
      return true;
    },
    resetFilters() {
      this.selectedDateRange = "all";
      this.selectedType = "all";
      this.dateFrom = "";
      this.dateTo = "";
      this.currentPage = 1;
    },
    statusLabel(backup) {
      return this.statusLabelFromValue(backup.overallStatus);
    },
    statusClass(backup) {
      return this.statusClassFromValue(backup.overallStatus);
    },
    statusLabelFromValue(status) {
      if (status === "error" || status === "failed") return "Echec";
      if (status === "partial") return "Incomplet";
      return "OK";
    },
    statusClassFromValue(status) {
      if (status === "error" || status === "failed") return "failed";
      if (status === "partial") return "partial";
      return "ok";
    },
    restoreButtonClass(backup) {
      const status = this.statusClass(backup);
      if (status === "failed") return "btn-danger-solid";
      if (status === "partial") return "btn-warning";
      return "btn-success";
    },
    typeLabel(type) {
      const labels = {
        full: "Full",
        safe: "Safe",
        custom: "Custom",
        database_only: "DB only",
      };
      return labels[type] || type;
    },
    typeClass(type) {
      return type === "database_only" ? "db" : type;
    },
    scopeLabel(scope) {
      const labels = {
        bare_metal_disaster_recovery: "Full disaster recovery",
        full_clone: "Full clone",
        safe_restore_ui: "Safe restore UI",
        selected_components: "Custom components",
        legacy_database_only: "DB only",
      };
      return labels[scope] || scope || "-";
    },
    healthClass(health) {
      if (health >= 100) return "health-ok";
      if (health >= 80) return "health-warning";
      return "health-error";
    },
    healthMetricClass(health) {
      if (Number(health) >= 100) return "good";
      if (Number(health) >= 80) return "warning";
      return "error";
    },
    formatDate(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString("fr-FR", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    formatSize(bytes) {
      if (!bytes) return "0 B";
      const units = ["B", "KB", "MB", "GB", "TB"];
      let size = bytes;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex += 1;
      }
      const precision = size >= 10 || unitIndex === 0 ? 0 : 1;
      return `${size.toFixed(precision)} ${units[unitIndex]}`;
    },
    formatSizeFromMb(sizeMb) {
      return this.formatSize(Number(sizeMb || 0) * 1024 * 1024);
    },
    formatDuration(seconds) {
      const value = Number(seconds || 0);
      if (value < 1) return "0s";
      if (value < 60) return `${Math.round(value)}s`;
      const minutes = Math.floor(value / 60);
      const rest = Math.round(value % 60);
      return `${minutes}m ${rest}s`;
    },
    shortSha(value) {
      if (!value) return "non disponible";
      return `${value.slice(0, 12)}...`;
    },
    componentStatusLabel(status) {
      const labels = {
        success: "OK",
        failed: "FAILED",
        skipped: "SKIP",
      };
      return labels[status] || status;
    },
    importStageName(stage) {
      const labels = { uploading: "Upload", processing: "Traitement", done: "Terminé", error: "Erreur" };
      return labels[stage] || stage;
    },
    notify(message, color = "success") {
      this.snackbarText = message;
      this.snackbarColor = color;
      this.snackbar = true;
    },
  },
};
</script>
