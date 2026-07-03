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
            <span class="mode-card-ico">🛡</span>
            <strong>Safe</strong>
            <small>Config interface · sans risque</small>
          </button>
          <button :class="['mode-card', 'mode-card-full', restoreMode === 'complete' ? 'active' : '']" type="button" title="Restore full" @click="restoreMode = 'complete'">
            <span class="mode-card-ico">💽</span>
            <strong>Full</strong>
            <small>Toute la VM · clone DR</small>
          </button>
          <button :class="['mode-card', 'mode-card-custom', restoreMode === 'custom' ? 'active' : '']" type="button" title="Restaure seulement certains composants" @click="enableCustomRestoreMode">
            <span class="mode-card-ico">🎯</span>
            <strong>Custom</strong>
            <small>À la carte</small>
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
            <span v-if="restoreMode !== 'custom'" class="coverage-count">
              {{ coveredComponentsCount }}/{{ restoreComponents.length }} couverts par ce mode
            </span>
            <button
              class="link-btn"
              type="button"
              :disabled="restoreMode !== 'custom'"
              @click="selectedRestoreComponents = restoreComponents.slice()"
            >
              Tout sélectionner
            </button>
          </div>
          <!-- Coverage legend — makes each mode's scope obvious at a glance -->
          <div v-if="restoreMode !== 'custom'" class="coverage-legend">
            <span class="cov-key cov-key--covered"><i></i>Restauré par ce mode</span>
            <span class="cov-key cov-key--protected"><i></i>Protégé — jamais touché (critique)</span>
          </div>
          <div class="component-grid">
          <label
            v-for="component in restoreComponents"
            :key="component"
            :class="['check-row', restoreMode !== 'custom' ? 'cov-' + componentCoverage(component) : 'cov-selectable']"
          >
            <input v-if="restoreMode === 'custom'" v-model="selectedRestoreComponents" :value="component" type="checkbox" />
            <span v-else class="cov-badge">{{ componentCoverage(component) === 'covered' ? '✓' : '🛡' }}</span>
            <span class="cov-name">{{ component }}</span>
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

          <!-- Vraie différence de CONTENU entre l'état actuel et le backup -->
          <div class="restore-preview-diffbox" v-if="restorePreview.changes_total">
            <template v-if="restorePreview.changes_total.total > 0">
              <div class="rpd-head">
                <strong>Différences avec l'état actuel</strong>
                <span class="rpd-tot rpd-add" v-if="restorePreview.changes_total.added">+{{ restorePreview.changes_total.added }} restaurés</span>
                <span class="rpd-tot rpd-rem" v-if="restorePreview.changes_total.removed">−{{ restorePreview.changes_total.removed }} supprimés</span>
                <span class="rpd-tot rpd-mod" v-if="restorePreview.changes_total.modified">~{{ restorePreview.changes_total.modified }} modifiés</span>
              </div>
              <div class="rpd-list">
                <span v-for="c in changedComponents" :key="c.name" class="rpd-chip">
                  {{ c.name }} : {{ changeLabel(c.changes) }}
                </span>
              </div>
              <div class="rpd-note">Ces éléments seront ramenés à l'état du backup.</div>
            </template>
            <div v-else class="rpd-none">✓ Aucune différence détectée — l'état actuel est déjà identique à ce backup.</div>
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

        <div v-if="previewLoading" class="preview-loading">Chargement de l'aperçu…</div>

        <!-- Corps scrollable unique : hero + système + filtre + cartes défilent
             ENSEMBLE, donc la section "Sécurité & système" n'est jamais coupée
             (le bug du tab "Tout"). Le header et le footer restent figés. -->
        <div v-else class="preview-body">
        <!-- HERO : une phrase claire = "ce que cette restauration va faire". -->
        <div class="preview-hero" :class="previewHasChanges ? 'preview-hero--change' : 'preview-hero--same'">
          <div class="preview-hero-icon">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v4h4"/>
            </svg>
          </div>
          <div class="preview-hero-copy">
            <strong>Restaurer remet le système dans l'état du {{ previewHeroDate }}.</strong>
            <p v-if="previewHasChanges">Voici précisément ce qui changera par rapport à maintenant :</p>
            <p v-else>Aucune différence détectée avec l'état actuel — la restauration est sans risque.</p>
            <div v-if="previewImpactItems.length" class="preview-hero-impact">
              <span
                v-for="it in previewImpactItems"
                :key="it.key"
                class="preview-impact-chip"
                :class="`impact-${it.tone}`"
                :title="it.hint"
              >
                <b>{{ it.icon }}</b> {{ it.label }}
              </span>
            </div>
          </div>
        </div>

        <!-- SÉCURITÉ & SYSTÈME : ce qu'un clone complet réapplique au niveau OS.
             Chaque élément = une mini-carte avec sa pastille colorée. -->
        <div v-if="previewSystem && previewSystemRows.length" class="preview-system">
          <div class="preview-system-head">
            <span class="preview-system-badge">
              <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 1l5 2v4c0 3.5-2.2 6-5 7-2.8-1-5-3.5-5-7V3z"/></svg>
              Clone complet
            </span>
            <strong>Ce qui sera modifié au niveau système</strong>
          </div>
          <div class="preview-system-grid">
            <div v-for="row in previewSystemRows" :key="row.key" class="preview-system-card"
                 :class="[`sys-${row.key}`, row.changed === true ? 'sys-changed' : (row.changed === false ? 'sys-same' : '')]">
              <span class="preview-system-tile">{{ row.icon }}</span>
              <div class="preview-system-text">
                <strong>
                  {{ row.title }}
                  <span v-if="row.status" class="sys-badge"
                        :class="row.status === 'changera' ? 'sys-badge-change' : 'sys-badge-same'">{{ row.status }}</span>
                </strong>
                <span>{{ row.desc }}</span>
                <em v-if="row.detail" class="sys-detail">{{ row.detail }}</em>
              </div>
            </div>
          </div>
        </div>

        <!-- Filtre intelligent : "Tout" / "Différents de l'actuel" / "Identiques".
             Collant en haut du corps scrollable. -->
        <div class="preview-filter-row preview-filter-sticky">
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

        <div v-if="previewCards.length === 0" class="preview-empty">
          <strong>Aucune donnée comparable</strong>
          <span>Ce backup ne contient que des fichiers de configuration — pas de données en base à comparer.</span>
        </div>

        <!-- Grille de cartes : une carte = un composant.
             Couleur immédiate, gros chiffre, verdict en clair. -->
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
              <span v-else-if="card.changed > 0" class="preview-card-delta warn" title="Contenu modifié à comptage égal">≠</span>
              <span v-else class="preview-card-delta neutral" title="Identique à l'état actuel">=</span>
            </header>

            <div class="preview-card-figure">
              <span class="preview-card-big">{{ card.inBackup }}</span>
              <span class="preview-card-unit">{{ card.unitLabel }}</span>
            </div>

            <!-- Verdict en clair : ce que la restauration ferait à ce composant. -->
            <div class="preview-card-verdict" :class="card.changed > 0 ? 'has-change' : 'no-change'">
              <svg v-if="card.changed > 0" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 1v14M1 8h14"/></svg>
              <svg v-else viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5l3.2 3.2L13 5"/></svg>
              <span>{{ card.verdict }}</span>
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

    <!-- ════════ FULL-SCREEN RESTORE OVERLAY ════════
         Replaces the old floating banner. A COMPLETE restore swaps the app code
         and restarts uvicorn, so the UI briefly disappears; this overlay takes
         over the screen, follows the restore through stabilization, and resolves
         to a clear "system is operational" / "needs attention" verdict — the
         single signal the operator needs to know the restore worked. Mirrors the
         LVM-snapshot restore overlay UX. -->
    <Teleport to="body">
      <Transition name="rfs-fade">
        <div v-if="restoreMonitor.visible" class="rfs-overlay" :class="`rfs-${restoreOverlayState}`">
          <div class="rfs-card">

            <div class="rfs-head">
              <div class="rfs-icon" :class="`rfs-icon-${restoreOverlayState}`">
                <svg v-if="restoreOverlayState === 'success'" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                <svg v-else-if="restoreOverlayState === 'error'" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                <svg v-else-if="restoreOverlayState === 'partial'" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 22h20L12 2z"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="12" y1="17.5" x2="12" y2="18"/></svg>
                <svg v-else class="rfs-spin" width="40" height="40" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M8 12 A 16 16 0 1 1 8 36"/><path d="M8 12 L 8 4 L 16 4"/></svg>
              </div>
              <div class="rfs-head-text">
                <div class="rfs-title">{{ restoreOverlayTitle }}</div>
                <div class="rfs-sub">{{ restoreOverlaySub }}</div>
              </div>
              <button v-if="restoreOverlayTerminal" class="rfs-close" type="button" @click="dismissRestoreOverlay">×</button>
            </div>

            <div class="rfs-pills">
              <span class="rfs-pill">{{ restoreMonitor.modeLabel }}</span>
              <span class="rfs-pill">{{ restoreMonitor.backupId }}</span>
              <span class="rfs-pill rfs-pill-status">{{ restoreMonitor.statusLabel }}</span>
            </div>

            <!-- ── In progress / stabilizing / reconnecting ── -->
            <template v-if="!restoreOverlayTerminal">
              <div class="rfs-bar">
                <div class="rfs-bar-fill"
                     :class="{ 'rfs-indeterminate': restoreMonitor.total === 0 && restoreOverlayState !== 'stabilizing' }"
                     :style="(restoreMonitor.total > 0 || restoreOverlayState === 'stabilizing') ? { width: restoreOverlayPct + '%' } : {}"></div>
              </div>
              <div class="rfs-bar-label">
                <span>{{ restoreMonitor.total > 0 ? `${restoreMonitor.done}/${restoreMonitor.total} composants` : "Initialisation…" }}</span>
                <span class="rfs-pct">{{ restoreOverlayPct }}%</span>
              </div>

              <!-- Time row: elapsed + estimated remaining / stabilization window. -->
              <div class="rfs-time">
                <span class="rfs-time-chip">⏱ Écoulé : <strong>{{ fmtClock(restoreElapsed) }}</strong></span>
                <span v-if="restoreOverlayState === 'stabilizing'" class="rfs-time-chip rfs-time-chip-accent">
                  🩺 Stabilisation : <strong>~{{ fmtClock(restoreStabilizeRemaining) }}</strong> restant
                </span>
                <span v-else-if="restoreEtaRemaining > 0" class="rfs-time-chip">
                  ⏳ Restant estimé : <strong>~{{ fmtClock(restoreEtaRemaining) }}</strong>
                </span>
                <span v-else-if="restoreMonitor.etaSeconds" class="rfs-time-chip">⏳ Finalisation…</span>
              </div>

              <div v-if="restoreMonitor.liveComponents && Object.keys(restoreMonitor.liveComponents).length > 0" class="rfs-comp-grid">
                <div
                  v-for="(status, name) in restoreMonitor.liveComponents"
                  :key="name"
                  class="rfs-comp"
                  :class="status === 'success' ? 'rfs-ok' : status === 'failed' ? 'rfs-fail' : status === 'skipped' ? 'rfs-skip' : status === 'running' ? 'rfs-running' : 'rfs-pending'"
                >
                  <span class="rfs-comp-dot"></span>
                  <span class="rfs-comp-name">{{ name }}</span>
                </div>
              </div>

              <div class="rfs-note" :class="{ 'rfs-note-reco': restoreMonitor.statusLabel === 'Reconnexion…' }">
                <span v-if="restoreOverlayState === 'stabilizing'">🩺 Tous les composants sont restaurés. Vérification des services (uvicorn, nginx, base de données)…</span>
                <span v-else-if="restoreMonitor.statusLabel === 'Reconnexion…'">⏳ L'interface redémarre pendant la restauration complète. Reconnexion automatique en cours — <strong>ne fermez pas l'onglet</strong>.</span>
                <span v-else>⚠️ Restauration en cours. L'interface peut être indisponible 1–2 min pendant le remplacement du code et le redémarrage des services. <strong>Ne fermez pas l'onglet.</strong></span>
              </div>
            </template>

            <!-- ── Terminal: success / partial / error ── -->
            <template v-else>
              <div class="rfs-verdict" :class="`rfs-verdict-${restoreOverlayState}`">
                {{ restoreVerdictText }}
              </div>

              <!-- Exactly which components did NOT restore, and why. Makes a
                   "partiel" result self-explanatory instead of a vague failure. -->
              <div v-if="restoreFailedDetails.length" class="rfs-failed">
                <strong>⚠️ Composant(s) non restauré(s) — le reste a réussi :</strong>
                <div v-for="c in restoreFailedDetails" :key="c.name" class="rfs-failed-item">
                  <span class="rfs-failed-name">{{ c.name }}</span>
                  <span class="rfs-failed-msg">{{ c.message || 'échec' }}</span>
                </div>
              </div>

              <div v-if="restoreMonitor.selfHealed" class="rfs-selfheal">
                ℹ️ Le suivi a été interrompu pendant la stabilisation ; l'état final a été reconstitué automatiquement à partir de la progression enregistrée.
              </div>

              <!-- Clone network: this restore reproduced the source VM's IP. Tell
                   the operator where to reconnect if the address changed. -->
              <div v-if="restoreOverlayState !== 'error' && restoreMonitor.cloneNetwork && restoreTargetIp" class="rfs-netclone" :class="{ 'rfs-netclone-changed': restoreIpChanged }">
                <strong>🌐 Identité réseau clonée</strong>
                <span v-if="restoreIpChanged">
                  La VM a repris l'adresse de la source : <code>{{ restoreTargetIp }}</code>.
                  Cet onglet est sur une autre adresse — rouvrez l'interface ici après le redémarrage :
                  <a :href="restoreTargetUrl" class="rfs-netclone-link">{{ restoreTargetUrl }}</a>
                </span>
                <span v-else>
                  IP cible restaurée : <code>{{ restoreTargetIp }}</code> (identique à votre accès actuel — aucune reconnexion nécessaire).
                </span>
              </div>

              <!-- Final connectivity check before the auto-reload. -->
              <div v-if="restoreFinalizing" class="rfs-finalizing">
                <span class="rfs-finalizing-dot"></span>
                Vérification finale de la connexion… l'interface se rechargera dès qu'elle répond (jamais sur une page cassée).
              </div>

              <div v-if="restoreMonitor.verification" class="rfs-summary">
                <div class="rfs-stat rfs-stat-ok"><span>Réussis</span><strong>{{ restoreMonitor.verification.summary.success }}</strong></div>
                <div class="rfs-stat rfs-stat-fail"><span>Échecs</span><strong>{{ restoreMonitor.verification.summary.failed }}</strong></div>
                <div class="rfs-stat rfs-stat-skip"><span>Ignorés</span><strong>{{ restoreMonitor.verification.summary.skipped }}</strong></div>
                <div class="rfs-stat"><span>Durée</span><strong>{{ formatDuration(restoreMonitor.verification.duration_seconds) }}</strong></div>
              </div>

              <div v-if="restoreMonitor.verification" class="rfs-checks">
                <div
                  v-for="check in restoreMonitor.verification.checks || []"
                  :key="check.key"
                  class="rfs-check"
                  :class="restoreCheckClass(check.status)"
                >
                  <strong>{{ check.label }}</strong>
                  <span>{{ check.detail }}</span>
                </div>
              </div>

              <div v-if="restoreMonitor.restoredComponentsLabel" class="rfs-evidence">
                <strong>Indice de vérification</strong>
                <span>{{ restoreMonitor.restoredComponentsLabel }}</span>
              </div>

              <!-- System-level changes (root password, system users, hostname). -->
              <div v-if="restoreSystemChanges && restoreSystemChanges.checked && restoreSystemChanges.any" class="rfs-syschanges">
                <strong>Changements système restaurés</strong>
                <div v-if="restoreSystemChanges.root_password_changed" class="rfs-syschange">🔑 Mot de passe root restauré</div>
                <div v-for="u in restoreSystemChanges.users_removed" :key="'u-'+u" class="rfs-syschange">👤 Utilisateur système supprimé : <code>{{ u }}</code></div>
                <div v-for="u in restoreSystemChanges.users_added" :key="'ua-'+u" class="rfs-syschange">👤 Utilisateur système ajouté : <code>{{ u }}</code></div>
                <div v-if="restoreSystemChanges.hostname_changed" class="rfs-syschange">🏷️ Hostname : {{ restoreSystemChanges.hostname_from }} → {{ restoreSystemChanges.hostname_to }}</div>
              </div>

              <!-- Diff couldn't be computed (DB busy during restore) — never claim "identical". -->
              <div v-if="restoreMonitor.diff && restoreMonitor.diff.available === false" class="rfs-diff-unavail">
                ⚠️ Rapport de changements base de données indisponible (système occupé pendant la restauration). Les changements système ci-dessus restent fiables.
              </div>

              <!-- Row-level diff: exactly which DB rows were added/removed/modified. -->
              <details v-if="restoreMonitor.diff && diffComponents.length > 0" class="rfs-diff">
                <summary>
                  <strong>Rapport de changements</strong>
                  <span class="restore-diff-totals">
                    <span class="restore-diff-tot pos">+{{ restoreMonitor.diff.totals.added }}</span>
                    <span class="restore-diff-tot neg">−{{ restoreMonitor.diff.totals.removed }}</span>
                    <span class="restore-diff-tot mod">~{{ restoreMonitor.diff.totals.modified }}</span>
                  </span>
                </summary>

                <div class="restore-diff-list">
                  <details
                    v-for="comp in diffComponents"
                    :key="`diff-${comp.name}`"
                    class="restore-diff-comp"
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
              </details>

              <!-- Recommandation de redémarrage TEMPORISÉE : un restore COMPLET
                   réécrit l'état noyau (réseau, systemd, /etc) et déclenche une
                   rafale de redémarrages de services. On laisse la VM se stabiliser
                   pendant ~5 min (compte à rebours), puis l'alerte passe en mode
                   "redémarrer maintenant". Le reboot reste possible à tout moment. -->
              <div v-if="restoreRebootRecommended" class="rfs-reboot-reco" :class="{ 'rfs-reboot-alert': rebootAlertActive }">

                <!-- CAS 1 — succès vérifié + fenêtre de stabilisation en cours :
                     redémarrage AUTOMATIQUE programmé (annulable). -->
                <template v-if="rebootAlertCountdown > 0 && !rebootAlertCancelled">
                  <div class="rfs-reboot-reco-head">
                    <span class="rfs-reboot-reco-icon">🔄</span>
                    <strong>Redémarrage automatique programmé</strong>
                  </div>
                  <p>
                    Restauration <b>complète vérifiée</b>. La VM se stabilise, puis
                    redémarrera <b>automatiquement dans {{ fmtClock(rebootAlertCountdown) }}</b>
                    pour repartir propre (réseau, services, système).
                  </p>
                  <div class="rfs-reboot-wait">
                    <div class="rfs-reboot-wait-bar"><div class="rfs-reboot-wait-fill" :style="{ width: rebootAlertProgress + '%' }"></div></div>
                  </div>
                  <div class="rfs-reboot-reco-actions">
                    <button class="rfs-btn rfs-btn-warn" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                      <span v-if="rebootArmed">Confirmer maintenant</span>
                      <span v-else>Redémarrer maintenant</span>
                    </button>
                    <button class="rfs-btn rfs-btn-ghost" type="button" @click="cancelRebootAuto">Annuler le redémarrage auto</button>
                  </div>
                </template>

                <!-- CAS 2 — fenêtre écoulée : auto-reboot en cours (succès) ou
                     alerte manuelle (restauration partielle / annulé). -->
                <template v-else-if="rebootAlertActive">
                  <div class="rfs-reboot-reco-head">
                    <span class="rfs-reboot-reco-icon">⚠️</span>
                    <strong>{{ restoreOverlayState === 'success' && !rebootAlertCancelled ? 'Redémarrage de la VM en cours…' : 'Redémarrez la VM maintenant' }}</strong>
                  </div>
                  <p>
                    La période de stabilisation est terminée. Pour finir de remonter
                    proprement le système restauré et éviter tout ralentissement
                    résiduel ou perte de connexion, <b>la VM doit redémarrer</b>.
                  </p>
                  <div class="rfs-reboot-reco-actions">
                    <button class="rfs-btn rfs-btn-warn" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                      <span v-if="rebootArmed">Confirmer le redémarrage</span>
                      <span v-else>Redémarrer la VM maintenant</span>
                    </button>
                    <button class="rfs-btn rfs-btn-ghost" type="button" @click="reloadAfterRestore">Recharger l'interface</button>
                  </div>
                </template>

                <!-- CAS 3 — auto-reboot annulé, ou restauration partielle sans
                     minuterie : recommandation manuelle simple. -->
                <template v-else>
                  <div class="rfs-reboot-reco-head">
                    <span class="rfs-reboot-reco-icon">🔄</span>
                    <strong>Redémarrage recommandé</strong>
                  </div>
                  <p>
                    La restauration <b>complète</b> est appliquée. Pour que la VM reparte
                    proprement (réseau, services, système) et éviter tout ralentissement
                    résiduel, redémarrez-la.
                  </p>
                  <div class="rfs-reboot-reco-actions">
                    <button class="rfs-btn rfs-btn-warn" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                      <span v-if="rebootArmed">Confirmer le redémarrage</span>
                      <span v-else>Redémarrer la VM maintenant</span>
                    </button>
                    <button class="rfs-btn rfs-btn-ghost" type="button" @click="reloadAfterRestore">Plus tard — recharger l'interface</button>
                  </div>
                </template>
              </div>

              <div class="rfs-actions">
                <template v-if="restoreOverlayState === 'success'">
                  <!-- Clone moved us to a new IP: the only safe action is to open
                       the new address (a reload here would hit a dead host). -->
                  <template v-if="restoreIpChanged">
                    <a class="rfs-btn rfs-btn-primary" :href="restoreTargetUrl">Ouvrir à la nouvelle adresse →</a>
                    <button class="rfs-btn rfs-btn-warn" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                      {{ rebootArmed ? "Confirmer le redémarrage" : "Redémarrer la VM" }}
                    </button>
                    <button class="rfs-btn rfs-btn-ghost" type="button" @click="dismissRestoreOverlay">Fermer</button>
                  </template>
                  <!-- Reboot already offered prominently above for a complete
                       restore — here we only keep the lightweight "continue". -->
                  <template v-else-if="restoreRebootRecommended">
                    <button class="rfs-btn rfs-btn-ghost" type="button" @click="dismissRestoreOverlay">Fermer</button>
                  </template>
                  <template v-else>
                    <button class="rfs-btn rfs-btn-primary" type="button" :disabled="restoreFinalizing" @click="reloadAfterRestore">
                      <span v-if="restoreFinalizing">Vérification…</span>
                      <span v-else>Continuer<span v-if="restoreReloadCountdown > 0"> ({{ restoreReloadCountdown }}s)</span></span>
                    </button>
                    <button v-if="restoreReloadCountdown > 0 || restoreFinalizing" class="rfs-btn rfs-btn-ghost" type="button" @click="cancelAutoReload">Rester sur la page</button>
                  </template>
                </template>
                <template v-else-if="restoreOverlayState === 'partial'">
                  <button class="rfs-btn rfs-btn-primary" type="button" @click="reloadAfterRestore">Recharger l'interface</button>
                  <button class="rfs-btn rfs-btn-warn" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                    {{ rebootArmed ? "Confirmer le redémarrage" : "Redémarrer la VM" }}
                  </button>
                  <button class="rfs-btn rfs-btn-ghost" type="button" @click="dismissRestoreOverlay">Fermer</button>
                </template>
                <template v-else>
                  <button class="rfs-btn rfs-btn-primary" type="button" @click="reloadAfterRestore">Recharger l'interface</button>
                  <button class="rfs-btn rfs-btn-danger" type="button" :class="{ 'rfs-armed': rebootArmed }" @click="rebootArmed ? rebootVm() : (rebootArmed = true)">
                    {{ rebootArmed ? "Confirmer le redémarrage" : "Redémarrer la VM" }}
                  </button>
                  <button class="rfs-btn rfs-btn-ghost" type="button" @click="dismissRestoreOverlay">Fermer</button>
                </template>
              </div>

              <div v-if="restoreOverlayState !== 'success'" class="rfs-advice">
                <span v-if="restoreOverlayState === 'error'">💡 Si l'interface reste instable : <strong>Redémarrer la VM</strong> finit proprement de remonter le système restauré. Les logs détaillés sont dans l'onglet <em>Logs</em>.</span>
                <span v-else>💡 La restauration est appliquée mais un ou plusieurs services n'ont pas confirmé leur état. Rechargez l'interface ; si un service reste indisponible, un redémarrage de la VM le rétablit.</span>
              </div>
            </template>

          </div>
        </div>
      </Transition>
    </Teleport>

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
        selfHealed: false,
        phase: "",
        etaSeconds: 0,           // estimated total restore duration (from backend)
        stabilizeEtaSeconds: 0,  // estimated stabilization window
        cloneNetwork: null,      // { restored_ips:[], applied } when a clone restored the IP
        mode: "",
      },
      restorePoller: null,
      restoreReloadCountdown: 0,   // auto-reload countdown shown on success
      reloadTimer: null,
      rebootArmed: false,          // two-click guard on the "Reboot VM" action
      restoreStartedAt: 0,         // ms epoch when the current restore began
      restoreElapsed: 0,           // seconds elapsed, ticked every 1s
      elapsedTimer: null,
      // Timed reboot alert after a COMPLETE restore: count down the stabilization
      // window, then escalate the banner into an actionable "reboot now" alert.
      rebootAlertDelay: 300,       // 5 min stabilization window before escalation
      rebootAlertCountdown: 0,     // seconds remaining before the alert fires
      rebootAlertActive: false,    // true once the window elapsed → escalate
      rebootAlertTimer: null,
      rebootAlertStarted: false,   // guard so we arm the countdown only once
      rebootAlertCancelled: false, // operator opted out of the auto-reboot
      restoreFinalizing: false,    // "final health check before reload" state
      healthProbeTimer: null,      // setTimeout handle for the pre-reload probe
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
          // Real content diff for THIS component (added/removed/modified rows).
          // A rule edited in place keeps the count identical, so without this a
          // modified firewall rule would look "= identique" — exactly the gap
          // the operator complained about.
          const ch = c.changes || {};
          const changed = (ch.added || 0) + (ch.removed || 0) + (ch.modified || 0);
          let tone = "tone-same";
          if (changed > 0 && (ch.modified || 0) > 0 && delta === 0) tone = "tone-warn";
          else if (delta > 0) tone = "tone-pos";
          else if (delta < 0) tone = "tone-neg";
          else if (changed > 0) tone = "tone-warn";
          // One-line, jargon-free verdict shown on every card.
          let verdict = "Identique à l'état actuel";
          if (changed > 0) {
            const bits = [];
            if (ch.added)    bits.push(`${ch.added} rétabli(s)`);
            if (ch.removed)  bits.push(`${ch.removed} supprimé(s)`);
            if (ch.modified) bits.push(`${ch.modified} modifié(s)`);
            verdict = bits.join(" · ");
          }
          return {
            name: c.name,
            title: meta.title,
            subtitle: meta.subtitle,
            icon: meta.icon,
            unitLabel: meta.unit,
            inBackup,
            current,
            delta,
            changed,
            changes: { added: ch.added || 0, removed: ch.removed || 0, modified: ch.modified || 0 },
            verdict,
            deltaTitle: delta > 0
              ? `${delta} élément(s) en plus dans ce backup`
              : `${Math.abs(delta)} élément(s) en moins dans ce backup`,
            tone,
            lines,
          };
        })
        // Show the most "interesting" cards first: anything with a real content
        // change on top, then biggest count delta, so the operator sees what
        // would actually change before the identical rows.
        .sort((a, b) => (b.changed - a.changed) || (Math.abs(b.delta) - Math.abs(a.delta)) || b.inBackup - a.inBackup);
    },
    // A card "changes" the system if its content diff is non-empty OR its row
    // count moves — so a modified-in-place rule (delta 0) still counts.
    previewCards() {
      const all = this.previewCardsAll;
      const isChanged = c => c.changed > 0 || c.delta !== 0;
      if (this.previewFilter === "changed") return all.filter(isChanged);
      if (this.previewFilter === "same")    return all.filter(c => !isChanged(c));
      return all;
    },
    previewFilters() {
      const all = this.previewCardsAll;
      const changed = all.filter(c => c.changed > 0 || c.delta !== 0).length;
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
    // ── Aperçu : résumé "humain" en haut de la modale ───────────────────────
    // changes_total = vrai diff de CONTENU (ajoutés/supprimés/modifiés), pas un
    // simple écart de comptes — détecte une règle modifiée en place.
    previewChanges() {
      return this.previewPayload?.changes_total || null;
    },
    previewHeroDate() {
      const raw = this.previewPayload?.created_at || this.previewBackup?.modified_at;
      return raw ? this.formatDate(raw) : "";
    },
    // Plain-language list of what restoring would do, ready to render as chips.
    previewImpactItems() {
      const c = this.previewChanges;
      if (!c) return [];
      const out = [];
      if (c.added)    out.push({ key: "added",    icon: "↩", tone: "pos",  label: `${c.added} élément(s) rétabli(s)`,  hint: "présents dans le backup, absents aujourd'hui" });
      if (c.removed)  out.push({ key: "removed",  icon: "✕", tone: "neg",  label: `${c.removed} ajout(s) supprimé(s)`,  hint: "créés après ce backup — seront retirés" });
      if (c.modified) out.push({ key: "modified", icon: "↻", tone: "warn", label: `${c.modified} modification(s) annulée(s)`, hint: "valeurs changées depuis — reviennent à l'état du backup" });
      return out;
    },
    previewHasChanges() {
      const c = this.previewChanges;
      return !!(c && c.total > 0);
    },
    // ── Aperçu : section Sécurité & système (clone complet) ──────────────────
    previewSystem() {
      const s = this.previewPayload?.system;
      return s && s.applicable ? s : null;
    },
    previewSystemRows() {
      const s = this.previewSystem;
      if (!s) return [];
      const d = s.diff || {};
      // status: true = will change, false = identical, null = unknown/not comparable
      const badge = (changed) => (changed === null || changed === undefined ? null : (changed ? "changera" : "identique"));
      const rows = [];

      if (s.root_password) {
        const ch = d.root_password ? d.root_password.changes : null;
        rows.push({
          key: "pw", icon: "🔑", title: "Mot de passe root",
          desc: ch === false ? "Identique au mot de passe actuel — aucun changement"
              : ch === true ? "Différent de l'actuel — sera remplacé (login + SSH)"
              : "Remis au mot de passe de ce backup (login + SSH)",
          changed: ch, status: badge(ch),
        });
      }
      if (s.login_users && s.login_users.length) {
        const du = d.users || {};
        const added = du.added || [], removed = du.removed || [];
        const changed = added.length + removed.length > 0;
        const bits = [];
        if (added.length) bits.push(`+ ${added.join(", ")} (ajouté${added.length > 1 ? "s" : ""})`);
        if (removed.length) bits.push(`− ${removed.join(", ")} (retiré${removed.length > 1 ? "s" : ""})`);
        rows.push({
          key: "users", icon: "👥", title: "Comptes de connexion",
          desc: `Backup : ${s.login_users.join(", ")}`,
          detail: changed ? bits.join(" · ") : "Identiques à l'actuel",
          changed, status: badge(changed),
        });
      }
      if (s.hostname) {
        const dh = d.hostname || {};
        const changed = !!dh.changes;
        rows.push({
          key: "host", icon: "🏷️", title: "Nom d'hôte",
          desc: changed ? `${dh.current || "?"}  →  « ${s.hostname} »` : `« ${s.hostname} » — inchangé`,
          changed, status: badge(changed),
        });
      }
      if (s.packages_count) {
        const dp = d.packages || {};
        const miss = dp.missing_count;
        rows.push({
          key: "pkg", icon: "📦", title: "Paquets système",
          desc: miss === 0 ? `${s.packages_count} paquets — tous déjà installés`
              : miss > 0 ? `${miss} paquet(s) manquant(s) à réinstaller sur ${s.packages_count}`
              : `${s.packages_count} paquets réinstallés si manquants`,
          detail: dp.missing && dp.missing.length ? dp.missing.join(", ") : null,
          changed: miss === null || miss === undefined ? null : miss > 0,
          status: badge(miss === null || miss === undefined ? null : miss > 0),
        });
      }
      if (s.has_application)
        rows.push({ key: "app", icon: "💽", title: "Code de l'application", desc: "Réécrit — clone complet de la VM", changed: null, status: null });
      return rows;
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
    // ── Restore overlay state machine ──────────────────────────────────────
    // Collapses the raw job status into the 5 visual states the overlay renders.
    restoreOverlayState() {
      const s = this.restoreMonitor.status;
      if (s === "success") return "success";
      if (s === "error") return "error";
      if (s === "partial_success") return "partial";
      if (s === "stabilizing" || this.restoreMonitor.phase === "stabilizing") return "stabilizing";
      return "progress";   // running / queued / reconnecting
    },
    restoreOverlayTerminal() {
      return ["success", "partial", "error"].includes(this.restoreOverlayState);
    },
    restoreOverlayPct() {
      if (this.restoreOverlayState === "stabilizing") return 100;
      const pct = Number(this.restoreMonitor.progressPct) || 0;
      return Math.max(0, Math.min(100, Math.round(pct)));
    },
    restoreOverlayTitle() {
      switch (this.restoreOverlayState) {
        case "success":     return "Restauration réussie";
        case "partial":     return "Restauration terminée avec réserves";
        case "error":       return "Restauration échouée";
        case "stabilizing": return "Stabilisation du système…";
        default:
          return this.restoreMonitor.statusLabel === "Reconnexion…"
            ? "Restauration en cours — reconnexion…"
            : "Restauration en cours…";
      }
    },
    restoreFailedDetails() {
      const s = this.restoreMonitor.verification && this.restoreMonitor.verification.summary;
      return (s && s.failed_details) || [];
    },
    // A COMPLETE (whole-VM) restore re-applies kernel-level state — network
    // profiles, systemd units, /etc — and triggers a service-restart storm that
    // can keep the box sluggish for a couple of minutes. A clean reboot is the
    // reliable way to finish bringing the restored system up, so we recommend it
    // explicitly on a successful complete restore (and never for a same-IP UI
    // restore, which only reloads the page).
    restoreRebootRecommended() {
      return (
        this.restoreMonitor.mode === "complete" &&
        ["success", "partial"].includes(this.restoreOverlayState) &&
        !this.restoreIpChanged
      );
    },
    // Fill % of the stabilization-wait bar (0 → 100 as the countdown drains).
    rebootAlertProgress() {
      if (!this.rebootAlertDelay) return 100;
      const done = this.rebootAlertDelay - this.rebootAlertCountdown;
      return Math.max(0, Math.min(100, Math.round((done / this.rebootAlertDelay) * 100)));
    },
    restoreOverlaySub() {
      switch (this.restoreOverlayState) {
        case "success":     return "Le système restauré est opérationnel.";
        case "partial":     return "La restauration est appliquée mais la vérification est incomplète.";
        case "error":       return "La restauration ne s'est pas terminée correctement.";
        case "stabilizing": return "Composants restaurés — vérification des services en cours.";
        default:            return `Backup ${this.restoreMonitor.backupId || ""}`;
      }
    },
    restoreVerdictText() {
      switch (this.restoreOverlayState) {
        case "success":
          return "✅ Restauration vérifiée — tous les composants sont restaurés et les services (uvicorn, nginx) sont actifs. Le système est 100% opérationnel.";
        case "partial":
          return "⚠️ La restauration a été appliquée, mais la stabilisation des services est incomplète. Vérifiez les contrôles ci-dessous puis rechargez ; un redémarrage de la VM peut finir de rétablir le système.";
        case "error":
          return "❌ La restauration a échoué ou s'est interrompue. Consultez les contrôles ci-dessous, rechargez l'interface, ou redémarrez la VM pour repartir d'un état propre.";
        default:
          return "";
      }
    },
    // ── ETA / time helpers shown in the overlay ────────────────────────────
    restoreEtaRemaining() {
      const eta = Number(this.restoreMonitor.etaSeconds) || 0;
      if (!eta) return 0;
      return Math.max(0, eta - this.restoreElapsed);
    },
    restoreStabilizeRemaining() {
      const eta = Number(this.restoreMonitor.stabilizeEtaSeconds) || 0;
      if (!eta) return 0;
      // Stabilization is the tail of the restore; estimate from elapsed-vs-total.
      const total = Number(this.restoreMonitor.etaSeconds) || eta;
      const intoStabilize = Math.max(0, this.restoreElapsed - (total - eta));
      return Math.max(0, Math.round(eta - intoStabilize));
    },
    // First static IP the clone restored — where to reconnect if the IP changed.
    restoreTargetIp() {
      const ips = this.restoreMonitor.cloneNetwork && this.restoreMonitor.cloneNetwork.restored_ips;
      return Array.isArray(ips) && ips.length ? ips[0] : "";
    },
    // True when a clone restore moved the appliance to an IP this tab isn't on,
    // so a plain reload would land on a dead host — we must point the user to the
    // new address instead of auto-reloading.
    restoreIpChanged() {
      const ip = this.restoreTargetIp;
      if (!ip) return false;
      try { return !String(window.location.host).includes(ip); }
      catch (e) { return false; }
    },
    restoreTargetUrl() {
      const ip = this.restoreTargetIp;
      if (!ip) return "";
      const proto = (typeof window !== "undefined" && window.location.protocol) || "https:";
      return `${proto}//${ip}/asguard/`;
    },
    restoreSystemChanges() {
      return this.restoreMonitor.systemChanges || null;
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
          title: "Restauration de la config de l'interface",
          description: "Restaure tout ce qui se gère dans l'interface (firewall, VPN, IDS, proxy, NAT, VLAN/VXLAN, certificats…) sans toucher au code de l'application, au socle OS, aux users Linux ni à l'IP physique de la machine. L'interface ne tombe jamais.",
          highlights: ["Interface jamais coupée", "Réseau UI (VLAN/VXLAN) restauré", "Code, OS & IP préservés"],
          noteLabel: "UI-safe",
          note: "Rétablit la configuration métier — VLAN/VXLAN inclus — sans risque de couper la session web/SSH.",
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
    // Components UI-safe deliberately does NOT restore — mirrors the backend
    // UI_FULL_EXCLUDED_COMPONENTS (code, OS socle, host identity, users…). The
    // network config (incl. VLAN/VXLAN) IS covered by UI-safe; only the
    // physical NIC IP identity is protected inside the network component.
    safeProtectedComponents() {
      return [
        "application",
        "system_config",
        "systemd_services",
        "logs",
        "users_groups",
        "packages",
        "docker_state",
        "vm_snapshot",
      ];
    },
    coveredComponentsCount() {
      return this.restoreComponents.filter(
        (c) => this.componentCoverage(c) === "covered"
      ).length;
    },
    changedComponents() {
      const inc = (this.restorePreview && this.restorePreview.included) || [];
      return inc.filter(c => c.changes && c.changes.total > 0);
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
    this.showPostRestoreMessage();
    this.resumeActiveRestore();
  },
  beforeUnmount() {
    this.stopRestorePolling();
    this.stopBackupPolling();
    this.cancelAutoReload();
    this.stopElapsedTimer();
    this.stopRebootAlertCountdown();
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
    startElapsedTimer() {
      this.stopElapsedTimer();
      if (!this.restoreStartedAt) this.restoreStartedAt = Date.now();
      this.restoreElapsed = Math.round((Date.now() - this.restoreStartedAt) / 1000);
      this.elapsedTimer = window.setInterval(() => {
        this.restoreElapsed = Math.round((Date.now() - this.restoreStartedAt) / 1000);
      }, 1000);
    },
    stopElapsedTimer() {
      if (this.elapsedTimer) {
        window.clearInterval(this.elapsedTimer);
        this.elapsedTimer = null;
      }
    },
    // ── Timed reboot alert (COMPLETE restore only) ─────────────────────────
    // Let the VM stabilize for `rebootAlertDelay` seconds, then escalate the
    // reboot banner into an active alert (+ a toast) so the operator is told
    // to reboot once the service-restart storm has settled.
    startRebootAlertCountdown() {
      if (this.rebootAlertStarted) return;     // arm only once per restore
      this.rebootAlertStarted = true;
      this.rebootAlertActive = false;
      this.rebootAlertCancelled = false;
      this.rebootAlertCountdown = this.rebootAlertDelay;
      this.stopRebootAlertCountdown(false);
      this.rebootAlertTimer = window.setInterval(() => {
        this.rebootAlertCountdown -= 1;
        if (this.rebootAlertCountdown <= 0) {
          this.rebootAlertCountdown = 0;
          this.stopRebootAlertCountdown(false);
          this.onRebootWindowElapsed();
        }
      }, 1000);
    },
    // Window elapsed: only AUTO-reboot when the restore is a verified full
    // success (everything restored). On a partial/degraded restore we never
    // reboot on our own — we just escalate the banner to a manual alert.
    onRebootWindowElapsed() {
      this.rebootAlertActive = true;
      const verifiedSuccess = this.restoreOverlayState === "success";
      try {
        if (typeof Notification !== "undefined" && Notification.permission === "granted") {
          new Notification("Asguard — Redémarrage de la VM", {
            body: verifiedSuccess
              ? "Restauration complète stabilisée — redémarrage automatique en cours."
              : "Restauration stabilisée — redémarrez la VM pour finaliser.",
          });
        }
      } catch (e) { /* ignore */ }
      if (verifiedSuccess && !this.rebootAlertCancelled) {
        this.notify("VM stabilisée et restauration vérifiée — redémarrage automatique…", "warning");
        this.rebootVm();
      } else {
        this.notify(
          "VM stabilisée — redémarrez-la manuellement pour finaliser la restauration.",
          "warning"
        );
      }
    },
    // Operator opted out of the auto-reboot — keep the overlay, manual only.
    cancelRebootAuto() {
      this.rebootAlertCancelled = true;
      this.stopRebootAlertCountdown(false);
      this.rebootAlertActive = false;
      this.notify("Redémarrage automatique annulé. Vous pouvez redémarrer manuellement.", "info");
    },
    stopRebootAlertCountdown(reset = true) {
      if (this.rebootAlertTimer) {
        window.clearInterval(this.rebootAlertTimer);
        this.rebootAlertTimer = null;
      }
      if (reset) {
        this.rebootAlertStarted = false;
        this.rebootAlertActive = false;
        this.rebootAlertCancelled = false;
        this.rebootAlertCountdown = 0;
      }
    },
    // mm:ss for the overlay clock/ETA chips.
    fmtClock(seconds) {
      const s = Math.max(0, Math.round(Number(seconds) || 0));
      const m = Math.floor(s / 60);
      const r = s % 60;
      return m > 0 ? `${m}min ${r.toString().padStart(2, "0")}s` : `${r}s`;
    },
    // After the success auto-reload, surface a confirmation toast so the
    // operator returns to a normal interface WITH a clear "it worked" signal.
    showPostRestoreMessage() {
      let done = null;
      try { done = JSON.parse(localStorage.getItem("asguard_restore_done") || "null"); }
      catch (e) { done = null; }
      if (done && done.status === "success") {
        this.notify(`✅ Restauration réussie — système opérationnel (${done.backupId || "backup"}).`, "success");
      }
      try { localStorage.removeItem("asguard_restore_done"); } catch (e) { /* ignore */ }
    },
    // Re-attach the restore banner on page load / browser reopen. Source of
    // truth = server (GET /backup/restore/active); localStorage is a hint.
    resumeActiveRestore() {
      let saved = null;
      try { saved = JSON.parse(localStorage.getItem("asguard_active_restore") || "null"); }
      catch (e) { saved = null; }
      axios.get("/backup/restore/active")
        .then(({ data }) => {
          if (data && data.active && data.job_id) {
            this.startRestorePolling(
              data.job_id,
              data.backup_id || (saved && saved.backupId) || "",
              (saved && saved.modeLabel) || (data.mode === "complete" ? "Restauration complète (VM entière)" : "Restauration UI-safe"),
            );
          } else if (saved && saved.jobId) {
            this.startRestorePolling(saved.jobId, saved.backupId, saved.modeLabel);
          } else {
            try { localStorage.removeItem("asguard_active_restore"); } catch (e) { /* ignore */ }
          }
        })
        .catch(() => {
          // Server unreachable (uvicorn restarting mid-restore) → resume from the
          // saved hint; the poller reconnects automatically when the API returns.
          if (saved && saved.jobId) {
            this.startRestorePolling(saved.jobId, saved.backupId, saved.modeLabel);
          }
        });
    },
    closeRestoreMonitor() {
      if (this.restoreMonitor.progressActive) return;
      this.restoreMonitor.visible = false;
    },
    openRestoreMonitor({ backupId, modeLabel, title, subtitle, status = "running", statusLabel = "Running", progressActive = true, verification = null, progressPct = 0, done = 0, total = 0, liveComponents = null, diff = null, selfHealed = false, phase = "", etaSeconds = null, stabilizeEtaSeconds = null, cloneNetwork = undefined, mode = undefined, systemChanges = undefined }) {
      const prev = this.restoreMonitor || {};
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
        selfHealed,
        phase,
        // Sticky fields: keep last known value when a poll tick doesn't carry it.
        etaSeconds: etaSeconds != null ? etaSeconds : (prev.etaSeconds || 0),
        stabilizeEtaSeconds: stabilizeEtaSeconds != null ? stabilizeEtaSeconds : (prev.stabilizeEtaSeconds || 0),
        cloneNetwork: cloneNetwork !== undefined ? cloneNetwork : (prev.cloneNetwork || null),
        mode: mode !== undefined ? mode : (prev.mode || ""),
        systemChanges: systemChanges !== undefined ? systemChanges : (prev.systemChanges || null),
      };
    },
    // ── Restore overlay actions ────────────────────────────────────────────
    dismissRestoreOverlay() {
      if (!this.restoreOverlayTerminal) return;   // can't dismiss while live
      this.cancelAutoReload();
      this.stopRestorePolling();
      this.stopRebootAlertCountdown();
      this.rebootArmed = false;
      this.restoreMonitor.visible = false;
      try { localStorage.removeItem("asguard_active_restore"); } catch (e) { /* ignore */ }
    },
    reloadAfterRestore() {
      this.cancelAutoReload();
      try { localStorage.removeItem("asguard_active_restore"); } catch (e) { /* ignore */ }
      window.location.reload();
    },
    // Only reload once the backend is confirmed reachable, so the operator never
    // lands on a half-up interface (their explicit concern). The success status
    // already came from a live API call, so this is usually instant; if the box
    // is still settling we keep probing (showing "vérification finale") and only
    // then start the short visible countdown.
    beginHealthGatedReload() {
      this.cancelAutoReload();
      this.restoreFinalizing = true;
      let tries = 0;
      const probe = async () => {
        tries += 1;
        try {
          await axios.get("/backup/restore/active", { timeout: 4000 });
          this.restoreFinalizing = false;
          this.startRestoreReloadCountdown(4);
        } catch (e) {
          if (tries >= 40) {            // ~60s of settling → reload anyway
            this.restoreFinalizing = false;
            this.startRestoreReloadCountdown(3);
            return;
          }
          this.healthProbeTimer = window.setTimeout(probe, 1500);
        }
      };
      probe();
    },
    startRestoreReloadCountdown(seconds = 6) {
      this.cancelAutoReload();
      this.restoreReloadCountdown = seconds;
      this.reloadTimer = window.setInterval(() => {
        this.restoreReloadCountdown -= 1;
        if (this.restoreReloadCountdown <= 0) {
          this.reloadAfterRestore();
        }
      }, 1000);
    },
    cancelAutoReload() {
      if (this.reloadTimer) {
        window.clearInterval(this.reloadTimer);
        this.reloadTimer = null;
      }
      if (this.healthProbeTimer) {
        window.clearTimeout(this.healthProbeTimer);
        this.healthProbeTimer = null;
      }
      this.restoreFinalizing = false;
      this.restoreReloadCountdown = 0;
    },
    async rebootVm() {
      try {
        this.stopRebootAlertCountdown(false);   // we're rebooting — stop the timer
        this.setCsrfHeader();
        await axios.post("/backup/system/reboot");
        this.notify("Redémarrage de la VM lancé. La page se reconnectera au retour.", "warning");
        this.restoreMonitor = {
          ...this.restoreMonitor,
          statusLabel: "Redémarrage…",
        };
      } catch (e) {
        this.notify(e.response?.data?.message || "Impossible de redémarrer la VM (action non autorisée).", "error");
        this.rebootArmed = false;
      }
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
      this._restoreReconnectTries = 0;
      this.rebootArmed = false;
      // Anchor the elapsed clock. Re-attach (after a reload) restarts the clock
      // from "now"; the backend ETA still drives the remaining-time estimate.
      this.restoreStartedAt = Date.now();
      this.restoreElapsed = 0;
      this.startElapsedTimer();
      // Persist so the banner re-attaches after a page reload / browser reopen
      // (the server endpoint /backup/restore/active is the real source of truth;
      // this is a hint for which job to poll).
      try {
        localStorage.setItem("asguard_active_restore",
          JSON.stringify({ jobId, backupId, modeLabel, ts: Date.now() }));
      } catch (e) { /* ignore */ }
      this.openRestoreMonitor({
        backupId,
        modeLabel,
        title: "Restore en cours",
        subtitle: "Lancement accepte. Verification et suivi en temps reel...",
      });

      const poll = async () => {
        try {
          const response = await axios.get(`/backup/restore-full-status/${jobId}`);
          this._restoreReconnectTries = 0;   // API answered → reset reconnect state
          const payload = response.data || {};
          const verification = payload.verification || null;
          const status = payload.status || "running";
          const isFinished = ["success", "partial_success", "error"].includes(status);
          // "stabilizing" = component loop done, services being verified. Still
          // non-terminal, but the overlay shows a distinct "verifying" phase.
          const isStabilizing = status === "stabilizing";
          const liveComponents = (!isFinished && payload.components_progress)
            ? payload.components_progress
            : null;

          const diff = (isFinished || isStabilizing)
            ? (payload.result && payload.result.diff) || null
            : null;

          const cloneNetwork = (payload.result && payload.result.clone_network) || undefined;
          const systemChanges = (payload.result && payload.result.system_changes) || undefined;

          this.openRestoreMonitor({
            backupId: payload.backup_id || backupId,
            modeLabel,
            title: isFinished ? "Restore termine" : "Restore en cours",
            subtitle: isFinished
              ? "Verification finale du restore disponible ci-dessous."
              : `Composant actuel: ${payload.current_component || "initialisation..."}`,
            status,
            statusLabel: isStabilizing ? "Stabilisation…" : this.restoreStatusLabel(status),
            progressActive: !isFinished,
            verification: isFinished ? verification : null,
            progressPct: isStabilizing ? 100 : (payload.progress_pct || 0),
            done: payload.done || 0,
            total: payload.total || 0,
            liveComponents,
            diff,
            selfHealed: !!payload.self_healed,
            phase: payload.phase || (isStabilizing ? "stabilizing" : ""),
            etaSeconds: payload.estimated_seconds != null ? payload.estimated_seconds : null,
            stabilizeEtaSeconds: payload.stabilize_estimate_seconds != null ? payload.stabilize_estimate_seconds : null,
            cloneNetwork,
            systemChanges,
            mode: payload.mode,
          });

          if (isFinished) {
            this.stopRestorePolling();
            this.stopElapsedTimer();
            this.rebootArmed = false;
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
            // On a verified success: if a clone restore moved us to a NEW IP this
            // tab can't reach, do NOT reload (we'd land on a dead host) — the
            // overlay shows the reconnect link instead. Otherwise, only reload
            // AFTER a final health probe confirms the backend is truly reachable,
            // so the operator never lands on a half-up interface.
            if (status === "success") {
              try {
                localStorage.setItem("asguard_restore_done",
                  JSON.stringify({ status, backupId: payload.backup_id || backupId, ts: Date.now() }));
              } catch (e) { /* ignore */ }
              // For a COMPLETE restore we DON'T auto-reload (bouncing the page
              // would drop the operator onto a still-stabilizing system). Instead
              // we arm a timed reboot: let the VM stabilize for ~5 min, then
              // AUTO-reboot it (only because this is a verified success) to bring
              // the restored system up clean. The operator can reboot early or
              // cancel the auto-reboot from the overlay.
              if (this.restoreMonitor.mode === "complete" && !this.restoreIpChanged) {
                this.startRebootAlertCountdown();
              } else if (!this.restoreIpChanged) {
                this.beginHealthGatedReload();
              }
              // else: keep overlay up; user clicks the new-IP link or reboots.
            } else {
              try { localStorage.removeItem("asguard_active_restore"); } catch (e) { /* ignore */ }
            }
            await this.fetchBackups();
          }
        } catch (error) {
          // The API is briefly unreachable — NORMAL during a COMPLETE restore:
          // uvicorn restarts to load the restored code (502/no response). Do
          // NOT give up — keep polling so we reconnect automatically when it
          // comes back. Show a calm "reconnecting / please wait" state, with
          // actionable advice if it drags on. The restore runs in a detached
          // systemd unit, independent of the web UI.
          this._restoreReconnectTries = (this._restoreReconnectTries || 0) + 1;
          const longWait = this._restoreReconnectTries >= 24; // ~1 min @ 2.5s
          this.openRestoreMonitor({
            backupId,
            modeLabel,
            title: "Restauration en cours — reconnexion…",
            subtitle: longWait
              ? "L'interface redémarre (restore complet). Patientez 1–2 min : la restauration se termine en arrière-plan (processus détaché). Si rien ne revient après plusieurs minutes, redémarrez la VM — la restauration sera déjà terminée au retour."
              : "L'API redémarre pendant la restauration complète. Reconnexion automatique… patientez, ne fermez pas la page.",
            status: "running",
            statusLabel: "Reconnexion…",
            progressActive: true,
            verification: null,
            liveComponents: null,
          });
          // keep this.restorePoller running → reconnect on the next tick
        }
      };

      poll();
      this.restorePoller = window.setInterval(poll, 2500);
    },
    changeLabel(ch) {
      if (!ch) return "";
      const parts = [];
      if (ch.modified) parts.push(`${ch.modified} modifié${ch.modified > 1 ? "s" : ""}`);
      if (ch.added) parts.push(`${ch.added} à restaurer`);
      if (ch.removed) parts.push(`${ch.removed} à supprimer`);
      return parts.join(", ") || "—";
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
    // Per-mode coverage state of one component (for the visual picker):
    //  - "covered"   : this mode WILL restore it (green ✓)
    //  - "protected" : this mode never touches it — critical/host item (grey 🛡)
    // Full restores everything; Safe protects the socle/OS/identity list.
    componentCoverage(component) {
      if (this.restoreMode === "complete") return "covered";
      if (this.restoreMode === "safe") {
        return this.safeProtectedComponents.includes(component)
          ? "protected"
          : "covered";
      }
      return "covered";
    },
    async submitRestoreBackup() {
      if (!this.restoreTarget) return;
      this.loading = true;
      this.setCsrfHeader();
      try {
        let response;
        const modeLabel = this.restoreMode === "complete"
          ? "Restauration complète (VM entière)"
          : this.restoreMode === "custom"
            ? "Restauration personnalisée"
            : "Restauration UI-safe";
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
