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
                              class="btn btn-preview"
                              type="button"
                              :disabled="loading || backup.type === 'database_only'"
                              @click="openContentPreview(backup)"
                            >
                              <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M1.5 8s2.5-5 6.5-5 6.5 5 6.5 5-2.5 5-6.5 5-6.5-5-6.5-5z"/>
                                <circle cx="8" cy="8" r="2"/>
                              </svg>
                              Aperçu
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

        <!-- Preview panel — shown only for the "complete" UI-safe restore.
             Tells the operator EXACTLY what will be touched and which engine
             components are intentionally protected, with the technical reason.
             Backed by GET /backup/<id>/restore-preview. -->
        <div v-if="restoreMode === 'complete' && restorePreview" class="restore-preview">
          <div class="restore-preview-head">
            <strong>Aperçu — ce qui sera fait</strong>
            <span class="restore-preview-badge restore-preview-badge--ui">restauration complète · toute la VM</span>
          </div>

          <div class="restore-preview-cols">
            <div class="restore-preview-col restore-preview-col--ok">
              <div class="restore-preview-col-head">
                <span class="restore-preview-dot restore-preview-dot--ok"></span>
                <span><strong>{{ restorePreview.counts.included + restorePreview.counts.excluded }}</strong> composants restaurés (code application inclus)</span>
              </div>
              <div class="restore-preview-list">
                <span v-for="c in restorePreview.included" :key="'i-' + c.name" class="restore-preview-chip restore-preview-chip--ok">
                  {{ c.name }}
                </span>
                <span v-for="c in restorePreview.excluded" :key="'e-' + c.name" class="restore-preview-chip restore-preview-chip--ok">
                  {{ c.name }}
                </span>
              </div>
            </div>

            <div class="restore-preview-col restore-preview-col--skip">
              <div class="restore-preview-col-head">
                <span class="restore-preview-dot restore-preview-dot--ok"></span>
                <span>Identité de la machine préservée</span>
              </div>
              <div class="restore-preview-skip-list">
                <p class="restore-preview-skip-reason">• Adresse IP conservée — pas de conflit réseau.</p>
                <p class="restore-preview-skip-reason">• /etc/fstab conservé — montages LVM ignorés si pas de 2e disque (mode natif).</p>
                <p class="restore-preview-skip-reason">• uvicorn redémarre automatiquement à la fin (l'interface se recharge).</p>
              </div>
            </div>
          </div>

          <div class="restore-preview-footer">
            <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="8" cy="8" r="6.5"/>
              <path d="M8 5v4M8 11v.5"/>
            </svg>
            <span>Restauration complète de toute la VM (système + code + données). L'identité réseau et le fstab de cette machine sont préservés.</span>
          </div>
        </div>
        <div v-else-if="restoreMode === 'complete' && restorePreviewLoading" class="restore-preview restore-preview--loading">
          Calcul de l'aperçu en cours…
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

    <!-- ════════════════════════════════════════════════════════════════════
         APERÇU DU CONTENU — modale dédiée pour répondre à "qu'est-ce
         qu'il y a dans ce backup ?". Vue lisible, sans tableaux
         imbriqués : une carte par catégorie, gros chiffre, badge delta
         vs l'état actuel. Permet de choisir la bonne version de backup
         avant même de penser au restore. CTA "Restaurer ce backup" en
         bas si l'opérateur valide son choix.
         ═══════════════════════════════════════════════════════════════════ -->
    <div v-if="previewDialog" class="modal-backdrop" @click.self="closeContentPreview">
      <div class="preview-modal">
        <header class="preview-head">
          <div class="preview-head-copy">
            <span class="preview-kicker">Aperçu du contenu</span>
            <strong>{{ previewBackup ? previewBackup.id : "" }}</strong>
            <div class="preview-meta">
              <span v-if="previewBackup" class="preview-meta-pill">{{ typeLabel(previewBackup.type) }}</span>
              <span v-if="previewBackup">{{ formatDate(previewBackup.modified_at) }}</span>
              <span v-if="previewBackup">·</span>
              <span v-if="previewBackup">{{ formatSize(previewBackup.sizeBytes) }}</span>
            </div>
          </div>
          <button class="drawer-close" type="button" @click="closeContentPreview">×</button>
        </header>

        <!-- Filtre intelligent : "Tout" / "Différents de l'actuel" / "Identiques".
             Aide l'opérateur à voir d'un coup d'œil ce qui changerait. -->
        <div class="preview-filter-row">
          <button
            v-for="f in previewFilters"
            :key="f.id"
            class="preview-filter-chip"
            :class="{ active: previewFilter === f.id }"
            type="button"
            @click="previewFilter = f.id"
          >
            {{ f.label }}
            <span class="preview-filter-count">{{ f.count }}</span>
          </button>
        </div>

        <!-- Bandeau résumé : total éléments + delta global. La phrase est
             naturelle ("12 éléments, 3 de plus qu'actuellement") pour
             ne demander aucune lecture technique. -->
        <div v-if="previewSummaryText" class="preview-summary">
          <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="10" cy="10" r="8"/>
            <path d="M10 6v5l3 2"/>
          </svg>
          <span v-html="previewSummaryText"></span>
        </div>

        <div v-if="previewLoading" class="preview-loading">Chargement de l'aperçu…</div>

        <div v-else-if="previewCards.length === 0" class="preview-empty">
          <strong>Aucune donnée comparable</strong>
          <span>Ce backup ne contient que des fichiers de configuration — pas de données en base à comparer.</span>
        </div>

        <!-- Grille de cartes : une carte = un composant.
             Couleur immédiate, gros chiffre, badge delta. -->
        <div v-else class="preview-grid">
          <article
            v-for="card in previewCards"
            :key="card.name"
            class="preview-card"
            :class="card.tone"
          >
            <header class="preview-card-head">
              <span class="preview-card-icon" v-html="card.icon"></span>
              <div class="preview-card-titles">
                <strong>{{ card.title }}</strong>
                <span>{{ card.subtitle }}</span>
              </div>
              <span
                v-if="card.delta !== 0"
                class="preview-card-delta"
                :class="card.delta > 0 ? 'pos' : 'neg'"
                :title="card.deltaTitle"
              >
                {{ card.delta > 0 ? "+" : "" }}{{ card.delta }}
              </span>
              <span v-else class="preview-card-delta neutral" title="Identique à l'état actuel">=</span>
            </header>

            <div class="preview-card-figure">
              <span class="preview-card-big">{{ card.inBackup }}</span>
              <span class="preview-card-unit">{{ card.unitLabel }}</span>
            </div>

            <footer class="preview-card-foot">
              <span>Actuellement</span>
              <strong>{{ card.current }}</strong>
            </footer>

            <details v-if="card.lines.length > 1" class="preview-card-detail">
              <summary>Voir le détail</summary>
              <ul>
                <li v-for="line in card.lines" :key="line.model">
                  <span>{{ line.label }}</span>
                  <span class="preview-line-counts">
                    <strong>{{ line.in_backup ?? 0 }}</strong>
                    <span class="preview-line-arrow">{{ line.in_backup === line.current ? "=" : "→" }}</span>
                    <strong>{{ line.current ?? 0 }}</strong>
                  </span>
                </li>
              </ul>
            </details>
          </article>
        </div>

        <footer class="preview-foot">
          <button class="btn btn-light" type="button" @click="closeContentPreview">Fermer</button>
          <button
            class="btn btn-primary"
            type="button"
            :disabled="!previewBackup"
            @click="restoreFromPreview"
          >
            Restaurer ce backup
            <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="margin-left:6px">
              <path d="M3 8h10M9 4l4 4-4 4"/>
            </svg>
          </button>
        </footer>
      </div>
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

        <!-- Rapport diff post-restore : montre exactement quelles lignes
             ont été ajoutées, supprimées ou modifiées pendant la
             restauration. Ne s'affiche que si le moteur a calculé un diff
             (composants DB-backed uniquement, restore terminé). -->
        <div v-if="restoreMonitor.diff && diffComponents.length > 0" class="restore-diff">
          <div class="restore-diff-head">
            <strong>Rapport de changements</strong>
            <span class="restore-diff-totals">
              <span class="restore-diff-tot pos">+{{ restoreMonitor.diff.totals.added }} ajoutés</span>
              <span class="restore-diff-tot neg">−{{ restoreMonitor.diff.totals.removed }} supprimés</span>
              <span class="restore-diff-tot mod">~{{ restoreMonitor.diff.totals.modified }} modifiés</span>
            </span>
          </div>

          <div class="restore-diff-list">
            <details
              v-for="comp in diffComponents"
              :key="`diff-${comp.name}`"
              class="restore-diff-comp"
              open
            >
              <summary>
                <span class="restore-diff-comp-name">{{ comp.name }}</span>
                <span class="restore-diff-comp-summary">
                  <span v-if="comp.summary.added" class="restore-diff-tot pos">+{{ comp.summary.added }}</span>
                  <span v-if="comp.summary.removed" class="restore-diff-tot neg">−{{ comp.summary.removed }}</span>
                  <span v-if="comp.summary.modified" class="restore-diff-tot mod">~{{ comp.summary.modified }}</span>
                </span>
              </summary>

              <div v-for="m in comp.models" :key="m.path" class="restore-diff-model">
                <div class="restore-diff-model-head">
                  <strong>{{ m.label }}</strong>
                  <span class="restore-diff-model-counts">{{ m.pre_count }} → {{ m.post_count }}</span>
                </div>

                <ul v-if="m.removed.length" class="restore-diff-rows neg">
                  <li v-for="r in m.removed" :key="`r-${m.path}-${r.pk}`">
                    <span class="restore-diff-op">−</span>
                    <span class="restore-diff-pk">#{{ r.pk }}</span>
                    <span class="restore-diff-summary">{{ r.summary }}</span>
                  </li>
                </ul>

                <ul v-if="m.added.length" class="restore-diff-rows pos">
                  <li v-for="r in m.added" :key="`a-${m.path}-${r.pk}`">
                    <span class="restore-diff-op">+</span>
                    <span class="restore-diff-pk">#{{ r.pk }}</span>
                    <span class="restore-diff-summary">{{ r.summary }}</span>
                  </li>
                </ul>

                <ul v-if="m.modified.length" class="restore-diff-rows mod">
                  <li v-for="r in m.modified" :key="`m-${m.path}-${r.pk}`">
                    <span class="restore-diff-op">~</span>
                    <span class="restore-diff-pk">#{{ r.pk }}</span>
                    <span class="restore-diff-summary">{{ r.summary }}</span>
                    <details class="restore-diff-changes">
                      <summary>{{ Object.keys(r.changes).length }} champ(s) modifié(s)</summary>
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
        <div
          v-else-if="restoreMonitor.diff && diffComponents.length === 0 && !restoreMonitor.progressActive"
          class="restore-diff restore-diff--empty"
        >
          <strong>Rapport de changements</strong>
          <span>Aucun changement détecté en base — le contenu restauré était identique à l'état précédent.</span>
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
      // ── Aperçu du contenu (modale "qu'y a-t-il dans ce backup ?") ─────
      previewDialog: false,
      previewBackup: null,            // backup row currently previewed
      previewPayload: null,           // restore-preview API response
      previewLoading: false,
      previewFilter: "all",           // 'all' | 'changed' | 'same'
      createDialog: false,
      createMode: "full",
      backupComponents: [],
      selectedCreateComponents: [],
      restoreDialog: false,
      restoreTarget: null,
      restoreMode: "complete",
      restorePreview: null,        // { included, excluded, counts, dr_hint, ... }
      restorePreviewLoading: false,
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
        diff: null,    // post-restore row-level diff (added/removed/modified)
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
    // ── Aperçu du contenu : cartes par composant ────────────────────────
    // Each "card" is one DB-backed component (firewall, NAT, ZTNA, …)
    // turned into a glance-able tile: icon, title, big number, delta.
    // Pure presentation — the raw data comes from restore-preview.
    previewCardsAll() {
      const included = this.previewPayload?.included || [];
      return included
        .filter(c => c.has_db_inventory && (c.inventory || []).length > 0)
        .map(c => {
          // Drop rows where both backup and live sides are zero — they
          // contribute nothing to the operator's decision and would
          // bloat the "Voir le détail" expander.
          const lines = (c.inventory || []).filter(
            r => (r.in_backup || 0) > 0 || (r.current || 0) > 0
          );
          const inBackup = c.total_in_backup || 0;
          const current = c.total_current || 0;
          const delta = inBackup - current;
          const meta = this.componentDisplayMeta(c.name);
          // tone drives card color: green = identical, blue = backup
          // has MORE than current (restoring brings rows back),
          // amber = backup has LESS than current (restoring drops rows).
          let tone = "tone-same";
          if (delta > 0) tone = "tone-pos";
          else if (delta < 0) tone = "tone-neg";
          return {
            name: c.name,
            title: meta.title,
            subtitle: meta.subtitle,
            icon: meta.icon,
            unitLabel: meta.unit,
            inBackup,
            current,
            delta,
            deltaTitle: delta > 0
              ? `${delta} élément(s) en plus dans ce backup`
              : `${Math.abs(delta)} élément(s) en moins dans ce backup`,
            tone,
            lines,
          };
        })
        // Show the most "interesting" cards first: biggest absolute
        // delta on top so the operator sees what would change first.
        .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta) || b.inBackup - a.inBackup);
    },
    previewCards() {
      const all = this.previewCardsAll;
      if (this.previewFilter === "changed") return all.filter(c => c.delta !== 0);
      if (this.previewFilter === "same")    return all.filter(c => c.delta === 0);
      return all;
    },
    previewFilters() {
      const all = this.previewCardsAll;
      const changed = all.filter(c => c.delta !== 0).length;
      const same = all.length - changed;
      return [
        { id: "all",     label: "Tout",                count: all.length },
        { id: "changed", label: "Différents de l'actuel", count: changed },
        { id: "same",    label: "Identiques",          count: same },
      ];
    },
    previewSummaryText() {
      const all = this.previewCardsAll;
      if (!all.length) return "";
      let inBackup = 0, current = 0;
      for (const c of all) { inBackup += c.inBackup; current += c.current; }
      const delta = inBackup - current;
      if (delta === 0) {
        return `<strong>${inBackup}</strong> éléments en base — <strong class="pos">identiques à l'état actuel</strong>.`;
      }
      if (delta > 0) {
        return `<strong>${inBackup}</strong> éléments dans le backup, soit <strong class="pos">+${delta}</strong> de plus qu'actuellement (<strong>${current}</strong>).`;
      }
      return `<strong>${inBackup}</strong> éléments dans le backup, soit <strong class="neg">${delta}</strong> de moins qu'actuellement (<strong>${current}</strong>).`;
    },
    diffComponents() {
      const diff = this.restoreMonitor.diff;
      if (!diff || !diff.components) return [];
      return Object.entries(diff.components).map(([name, payload]) => ({
        name,
        summary: payload.summary || { added: 0, removed: 0, modified: 0 },
        models: Object.entries(payload.models || {}).map(([path, m]) => ({ path, ...m })),
      }));
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
          eyebrow: "Restore prudent (UI-safe)",
          title: "Restauration du système Asguard uniquement",
          description: "Restaure uniquement la config Asguard (firewall, VPN, IDS, proxy, réseau, NAT…) sans toucher au code de l'application, au socle /etc OS ni à l'identité de la machine. L'interface ne tombe jamais.",
          highlights: ["Interface jamais coupée", "Code & OS préservés", "Config Asguard restaurée"],
          noteLabel: "UI-safe",
          note: "Idéal pour rétablir la configuration métier sans risque de couper la session web/SSH.",
        },
        complete: {
          eyebrow: "Restore complet",
          title: "Restauration complète de toute la VM",
          description: "Restaure TOUT : système, configurations, données et le code de l'application. L'adresse IP et le /etc/fstab de cette machine sont préservés ; les montages LVM sont ignorés s'il n'y a pas de 2e disque (mode natif).",
          highlights: ["Toute la VM (code inclus)", "IP + fstab préservés", "uvicorn redémarre à la fin"],
          noteLabel: "Identité préservée",
          note: "L'adresse IP et le fstab de cette machine ne sont jamais écrasés par le backup source.",
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
    // Re-attach to any restore that is running / just finished — survives page
    // refresh, browser close+reopen, and the uvicorn restart of a full restore.
    this.resumeActiveRestore();
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
    openRestoreMonitor({ backupId, modeLabel, title, subtitle, status = "running", statusLabel = "Running", progressActive = true, verification = null, progressPct = 0, done = 0, total = 0, liveComponents = null, diff = null }) {
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
        diff,
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
      this.restoreReconnectTries = 0;
      try {
        localStorage.setItem("asguard_active_restore",
          JSON.stringify({ jobId, backupId, modeLabel }));
      } catch (e) {}
      this.openRestoreMonitor({
        backupId,
        modeLabel,
        title: "Restore en cours",
        subtitle: "Lancement accepte. Verification et suivi en temps reel...",
      });

      const poll = async () => {
        try {
          const response = await axios.get(`/backup/restore-full-status/${jobId}`);
          this.restoreReconnectTries = 0;
          const payload = response.data || {};
          const verification = payload.verification || null;
          const status = payload.status || "running";
          const isFinished = ["success", "partial_success", "error"].includes(status);
          const liveComponents = (!isFinished && payload.components_progress)
            ? payload.components_progress
            : null;

          const diff = isFinished ? (payload.result && payload.result.diff) || null : null;

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
            diff,
          });

          if (isFinished) {
            this.stopRestorePolling();
            try {
              localStorage.removeItem("asguard_active_restore");
              localStorage.setItem("asguard_seen_restore", jobId);
            } catch (e) {}
            this.notify(
              status === "success"
                ? "Restore termine et verifie."
                : status === "partial_success"
                  ? "Restore termine avec verification partielle."
                  : "Restore termine avec erreur.",
              status === "success" ? "success" : "error"
            );
            // Restored onto a VM without the LVM 2nd disk: the appliance was
            // reconciled to run natively (LVM/bind lines stripped from fstab).
            // Tell the operator and recommend a reboot for a clean mount state.
            const fr = payload.result && payload.result.fstab_reconcile;
            if (fr && fr.mode === "native" && fr.changed) {
              this.notify(
                "Mode natif activé : aucun 2e disque LVM détecté, les montages LVM ont été retirés du fstab. Un redémarrage est recommandé pour finaliser.",
                "warning"
              );
            }
            await this.fetchBackups();
          }
        } catch (error) {
          // The API is very likely restarting (a COMPLETE restore restarts
          // uvicorn at the end) or briefly unreachable. Do NOT give up — the
          // restore continues in a detached systemd process. Keep polling; show
          // a reassuring "reconnecting" message, then actionable advice if the
          // API stays down for a while.
          this.restoreReconnectTries = (this.restoreReconnectTries || 0) + 1;
          const advise = this.restoreReconnectTries >= 12; // ~30 s of failures
          this.openRestoreMonitor({
            backupId,
            modeLabel,
            title: "Restauration en cours…",
            subtitle: advise
              ? "L'API ne répond pas (elle redémarre sûrement). La restauration CONTINUE en arrière-plan. Patientez 1–2 min : le suivi reprend tout seul. Sinon rechargez la page (Ctrl+Shift+R) ou redémarrez la VM — au retour le suivi reprend et le résultat est dans « Historique Restores »."
              : "Reconnexion à l'interface… (l'API redémarre — c'est normal pour un restore complet)",
            status: "running",
            statusLabel: "Reconnexion",
            progressActive: true,
          });
          // IMPORTANT: keep the poller alive (do not stopRestorePolling) so it
          // reconnects automatically once uvicorn is back.
        }
      };

      poll();
      this.restorePoller = window.setInterval(poll, 2500);
    },

    // Re-attach to an in-flight (or just-finished) restore on page load / browser
    // reopen / after a uvicorn restart. The server is the source of truth, so
    // this survives refreshes and closing the browser.
    async resumeActiveRestore() {
      try {
        const { data } = await axios.get("/backup/restore-active");
        if (!data || !data.job) return;
        const job = data.job;
        const jobId = job.job_id;
        const modeLabel = this.modeLabelFromJob(job);
        if (data.active) {
          this.startRestorePolling(jobId, job.backup_id, modeLabel);
          return;
        }
        if (data.finished && jobId) {
          let seen = null;
          try { seen = localStorage.getItem("asguard_seen_restore"); } catch (e) {}
          if (seen !== jobId && data.age_seconds < 900) {
            const status = job.status || "success";
            this.openRestoreMonitor({
              backupId: job.backup_id,
              modeLabel,
              title: "Restore terminé",
              subtitle: "Résultat de la dernière restauration.",
              status,
              statusLabel: this.restoreStatusLabel(status),
              progressActive: false,
              verification: job.verification || null,
              diff: (job.result && job.result.diff) || null,
            });
            try { localStorage.setItem("asguard_seen_restore", jobId); } catch (e) {}
          }
        }
      } catch (e) { /* no active restore / endpoint unreachable — ignore */ }
    },
    modeLabelFromJob(job) {
      const m = (job && job.mode) || "";
      return m === "complete" ? "Full DR (complete)"
        : m === "ui_full" ? "Full UI-safe"
        : m === "safe" ? "Safe"
        : "Restore";
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
      this.restorePreview = null;
      this.restoreDialog = true;
      try {
        await Promise.all([
          this.fetchComponentCatalog(backup.id),
          this.fetchRestorePreview(backup.id),
        ]);
      } catch (error) {
        this.notify("Impossible de charger les composants restaurables.", "error");
      }
    },

    // Pre-restore preview — fetched once when the dialog opens. Tells the
    // operator EXACTLY what the UI-safe restore will and will not touch.
    async fetchRestorePreview(backupId) {
      this.restorePreviewLoading = true;
      try {
        const { data } = await axios.get(`/backup/${backupId}/restore-preview`);
        this.restorePreview = data;
      } catch (e) {
        this.restorePreview = null;
      } finally {
        this.restorePreviewLoading = false;
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
          ? "Full UI-safe restore"
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
            diff: response.data?.diff || null,
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

    // ── Aperçu du contenu ───────────────────────────────────────────────
    // Opens a focused, visual modal answering "what's inside this backup,
    // and how does it differ from the live system?". The technical
    // Details drawer stays untouched — clear separation of concerns:
    // Aperçu = decision support, Details = technical audit.
    async openContentPreview(backup) {
      this.previewBackup = backup;
      this.previewPayload = null;
      this.previewFilter = "all";
      this.previewLoading = true;
      this.previewDialog = true;
      try {
        const { data } = await axios.get(`/backup/${backup.id}/restore-preview`);
        this.previewPayload = data;
      } catch (e) {
        this.notify("Impossible de charger l'aperçu du contenu.", "error");
        this.previewPayload = null;
      } finally {
        this.previewLoading = false;
      }
    },
    closeContentPreview() {
      this.previewDialog = false;
      this.previewPayload = null;
      this.previewBackup = null;
    },
    restoreFromPreview() {
      const backup = this.previewBackup;
      this.closeContentPreview();
      if (backup) this.openRestoreDialog(backup);
    },
    // Visual identity per backup component. Pure presentation: pretty
    // title, one-line subtitle, inline SVG icon, unit label. Keeps the
    // preview cards readable without forcing the operator to know
    // backend component names (e.g. "ipsec_detailed" → "VPN IPsec").
    componentDisplayMeta(name) {
      const map = {
        firewall:       { title: "Firewall",         subtitle: "Règles nftables", unit: "règle(s)",         icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2L3 5v5c0 4 3 7 7 8 4-1 7-4 7-8V5l-7-3z"/></svg>' },
        nat:            { title: "NAT",              subtitle: "DNAT, SNAT, 1-to-1",unit: "règle(s)",       icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h11M11 4l3 3-3 3M17 13H6M9 16l-3-3 3-3"/></svg>' },
        routing:        { title: "Routage",          subtitle: "Routes statiques",  unit: "route(s)",       icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="4" cy="16" r="2"/><circle cx="16" cy="4" r="2"/><path d="M5 14c4-2 4-8 9-9"/></svg>' },
        gateway:        { title: "Passerelles",      subtitle: "Gateways réseau",   unit: "passerelle(s)",  icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="14" height="10" rx="2"/><path d="M3 10h14M7 6V3M13 6V3"/></svg>' },
        vpn:            { title: "VPN OpenVPN",      subtitle: "Serveurs et clients",unit: "instance(s)",    icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v6m0 0L7 5m3 3l3-3M3 13c0 3 3 5 7 5s7-2 7-5"/></svg>' },
        ipsec_detailed: { title: "VPN IPsec",        subtitle: "Tunnels site-à-site",unit: "tunnel(s)",      icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10h4m8 0h4M6 10a4 4 0 014-4 4 4 0 014 4 4 4 0 01-4 4 4 4 0 01-4-4z"/></svg>' },
        ztna:           { title: "ZTNA",             subtitle: "Identités et services",unit: "élément(s)",   icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="7" r="3"/><path d="M3 17c0-4 3-6 7-6s7 2 7 6"/></svg>' },
        waf:            { title: "WAF",              subtitle: "Pare-feu applicatif", unit: "règle(s)",       icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2L3 5v6c0 4 3 7 7 8 4-1 7-4 7-8V5l-7-3z"/><path d="M7 10l2 2 4-4"/></svg>' },
        ids:            { title: "IDS / IPS",        subtitle: "Suricata",          unit: "interface(s)",   icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="9" r="5"/><path d="M13 13l4 4"/></svg>' },
        proxy:          { title: "Proxy Squid",      subtitle: "Règles & utilisateurs",unit: "élément(s)",     icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h14v8H3z"/><path d="M3 10h14"/></svg>' },
        dhcp:           { title: "DHCP",             subtitle: "Serveur DHCPv4",    unit: "serveur(s)",      icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="14" height="10" rx="2"/><path d="M7 9h6M7 12h4"/></svg>' },
        vlan:           { title: "VLAN",             subtitle: "Réseaux virtuels",  unit: "VLAN(s)",        icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10h14M5 6h10M5 14h10"/></svg>' },
        vxlan:          { title: "VXLAN",            subtitle: "Tunnels L2 overlay", unit: "VXLAN(s)",       icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10h14M5 6l4 4-4 4M15 6l-4 4 4 4"/></svg>' },
        sdwan:          { title: "SD-WAN",           subtitle: "Zones et politiques",unit: "élément(s)",     icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="10" r="7"/><path d="M3 10h14M10 3v14"/></svg>' },
        certificates:   { title: "Certificats",      subtitle: "PKI / CA",          unit: "certificat(s)",   icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="14" height="10" rx="2"/><path d="M7 17l3-2 3 2"/></svg>' },
        double_mask:    { title: "Double Mask",      subtitle: "Anonymisation IP",  unit: "règle(s)",         icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="10" r="4"/><circle cx="13" cy="10" r="4"/></svg>' },
      };
      return map[name] || {
        title: name,
        subtitle: "Composant",
        unit: "élément(s)",
        icon: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="14" height="14" rx="2"/></svg>',
      };
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
