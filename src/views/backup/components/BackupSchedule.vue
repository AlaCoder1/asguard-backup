<template>
  <div class="bs-wrap">

    <!-- ── Top bar: storage gauge + actions ── -->
    <div class="bs-topbar">
      <div class="bs-storage-block">
        <div class="bs-storage-icon-wrap" :class="storageClass">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4.03 3-9 3S3 13.66 3 12"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/></svg>
        </div>
        <div class="bs-storage-info">
          <div class="bs-storage-track">
            <div class="bs-storage-fill" :style="{ width: storagePercent + '%' }" :class="storageClass"></div>
          </div>
          <div class="bs-storage-text">
            <span class="bs-storage-used" :class="storageClass">{{ storagePercent }}%</span>
            <span class="bs-storage-sep">·</span>
            <span>{{ stats.total_size_gb }} Go utilisés</span>
            <span class="bs-storage-sep">·</span>
            <span>{{ stats.free_gb }} Go libres</span>
            <span class="bs-storage-sep">·</span>
            <span>{{ stats.total_backups }} backups</span>
            <span v-if="storageClass === 'critical'" class="bs-storage-alert">⚠ Espace critique</span>
            <span v-else-if="storageClass === 'warn'" class="bs-storage-alert warn">⚠ Espace limité</span>
          </div>
        </div>
      </div>
      <div class="bs-topbar-actions">
        <button class="bs-notif-btn" title="Tester les notifications" @click="ntfyTest" :disabled="testingNotif">
          <span v-if="testingNotif" class="bs-spin">⟳</span>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          Tester notif
        </button>
        <button class="bs-apply-btn" :disabled="applyingRetention" @click="applyDialog = true">
          <span v-if="applyingRetention" class="bs-spin">⟳</span>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.08-8.36"/></svg>
          Appliquer la rétention
        </button>
      </div>
    </div>

    <!-- ── Quick stats ── -->
    <div class="bs-stats-row">
      <div class="bs-stat-chip">
        <span class="bs-stat-dot" :class="lastRunStatusGlobal"></span>
        <span class="bs-stat-label">Dernier run</span>
        <strong class="bs-stat-val">{{ lastRunGlobal || '—' }}</strong>
      </div>
      <div class="bs-stat-chip">
        <span class="bs-stat-dot scheduled"></span>
        <span class="bs-stat-label">Prochain run</span>
        <strong class="bs-stat-val">{{ nextRunGlobal || '—' }}</strong>
      </div>
      <div class="bs-stat-chip">
        <span class="bs-stat-dot" :class="tasks.filter(t=>t.enabled).length ? 'ok' : 'warn'"></span>
        <span class="bs-stat-label">Tâches actives</span>
        <strong class="bs-stat-val">{{ tasks.filter(t => t.enabled).length }} / {{ tasks.length }}</strong>
      </div>
      <div class="bs-stat-chip">
        <span class="bs-stat-dot" :class="storageClass"></span>
        <span class="bs-stat-label">Stockage</span>
        <strong class="bs-stat-val">{{ storagePercent }}% utilisé</strong>
      </div>
    </div>

    <!-- ── Timezone selector ──
         The dropdown is "uncommitted": changing the value just stages a
         pending choice. Applying requires explicit confirmation in the
         inline panel below — this prevents the bug where a switch would
         silently trigger missed-run catchups (e.g. Tunis→New_York firing
         a Safe backup because 10am NY just passed in UTC). -->
    <div class="bs-tz-bar">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      <span class="bs-tz-label">Fuseau horaire du planificateur :</span>
      <select class="bs-tz-select" v-model="pendingTimezone" @change="onTimezoneSelect">
        <option v-for="tz in timezoneOptions" :key="tz.value" :value="tz.value">{{ tz.label }}</option>
      </select>
      <span v-if="savingTimezone" class="bs-tz-saving">⟳ Enregistrement…</span>
      <span v-else-if="tzSaved" class="bs-tz-ok">✓ Appliqué</span>
      <span v-else-if="!hasPendingChange" class="bs-tz-hint">Les expressions cron sont interprétées dans ce fuseau.</span>
      <span v-else class="bs-tz-hint bs-tz-hint--pending">Choix non validé — confirmez ci-dessous.</span>
    </div>

    <!-- ── Confirmation card (only shown when pendingTimezone differs from active) ── -->
    <transition name="bs-tz-confirm">
      <div v-if="hasPendingChange" class="bs-tz-confirm-card">
        <div class="bs-tz-confirm-head">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="13"/>
            <circle cx="12" cy="16.5" r="0.6" fill="currentColor"/>
          </svg>
          <div>
            <strong>Confirmer le changement de fuseau ?</strong>
            <p>
              <span class="bs-tz-from">{{ scheduleTimezoneLabel }}</span>
              <span class="bs-tz-arrow">→</span>
              <span class="bs-tz-to">{{ pendingTimezoneLabel }}</span>
            </p>
          </div>
        </div>
        <div class="bs-tz-confirm-impact">
          <div class="bs-tz-confirm-impact-row" v-for="(t, i) in tasks.filter(x => x.enabled)" :key="i">
            <span class="bs-tz-confirm-impact-name">{{ t.label }}</span>
            <span class="bs-tz-confirm-impact-arrow">
              <em>{{ nextRunTime(t) }}</em>
              <span>→</span>
              <strong>{{ previewNextRun(t.cron, pendingTimezone) }}</strong>
            </span>
          </div>
          <div v-if="!tasks.some(x => x.enabled)" class="bs-tz-confirm-impact-empty">
            Aucune tâche active à recalculer.
          </div>
        </div>
        <div class="bs-tz-confirm-note">
          Les exécutions passées ne seront pas rejouées. Les prochaines exécutions
          seront recalculées dans le nouveau fuseau.
        </div>
        <div class="bs-tz-confirm-actions">
          <button class="bs-tz-confirm-btn bs-tz-confirm-btn--cancel" @click="cancelTimezoneChange"
                  :disabled="savingTimezone">Annuler</button>
          <button class="bs-tz-confirm-btn bs-tz-confirm-btn--ok" @click="confirmTimezoneChange"
                  :disabled="savingTimezone">
            <span v-if="!savingTimezone">Confirmer le changement</span>
            <span v-else>Application…</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- ── Undo banner (shown for ~12 s after a successful TZ change) ── -->
    <transition name="bs-tz-undo">
      <div v-if="undoTimezone" class="bs-tz-undo-banner">
        <span>
          ✓ Fuseau appliqué : <strong>{{ scheduleTimezoneLabel }}</strong>.
          Vous pouvez encore revenir à <strong>{{ undoTimezoneLabel }}</strong>.
        </span>
        <button class="bs-tz-undo-btn" @click="revertTimezone" :disabled="savingTimezone">
          ⟲ Revenir au précédent
        </button>
      </div>
    </transition>

    <!-- ── Toast ── -->
    <transition name="bs-toast-anim">
      <div v-if="toast" :class="['bs-toast', toast.type]">
        <span class="bs-toast-icon">{{ toast.type === 'success' ? '✓' : '✕' }}</span>
        {{ toast.msg }}
      </div>
    </transition>

    <!-- ── Main grid ── -->
    <div class="bs-grid">

      <!-- LEFT: Scheduled tasks -->
      <div class="bs-card">
        <div class="bs-card-header">
          <div class="bs-card-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Tâches planifiées
            <span v-if="tasks.length" class="bs-count-badge">{{ tasks.length }}</span>
          </div>
          <button class="bs-add-btn" @click="openDialog()">+ Ajouter</button>
        </div>

        <div v-if="loading" class="bs-state-block">
          <span class="bs-spin-lg">⟳</span>
          <span>Chargement...</span>
        </div>

        <div v-else-if="!tasks.length" class="bs-state-block empty">
          <div class="bs-empty-icon">📅</div>
          <p>Aucune tâche planifiée</p>
          <button class="bs-add-link" @click="openDialog()">Créer la première tâche →</button>
        </div>

        <div v-else class="bs-task-list">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="bs-task-item"
            :class="{ disabled: !task.enabled, expanded: expandedTask === task.id }"
          >
            <!-- Main row -->
            <div class="bs-task-main" @click="expandedTask = expandedTask === task.id ? null : task.id">
              <div class="bs-task-left">
                <span :class="['bs-type-dot', task.type]"></span>
                <div class="bs-task-info">
                  <div class="bs-task-name">
                    {{ task.label }}
                    <span :class="['bs-run-badge', task.last_run_status || 'never']">
                      {{ runStatusLabel(task.last_run_status) }}
                    </span>
                  </div>
                  <div class="bs-task-meta">
                    <code class="bs-cron-code">{{ task.cron }}</code>
                    <span class="bs-cron-human">{{ cronHuman(task.cron) }}</span>
                    <span v-if="task.last_run_at" class="bs-last-run">
                      · {{ formatRelative(task.last_run_at) }}
                    </span>
                  </div>
                  <div class="bs-task-next">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    Prochain : <strong>{{ nextRunTime(task) }}</strong>
                  </div>
                </div>
              </div>
              <div class="bs-task-right">
                <span :class="['bs-type-badge', task.type]">{{ taskTypeLabel(task.type) }}</span>
                <label class="bs-toggle" :title="task.enabled ? 'Désactiver' : 'Activer'" @click.stop>
                  <input type="checkbox" :checked="task.enabled" @change="toggleTask(task)" />
                  <span class="bs-toggle-slider"></span>
                </label>
                <button
                  class="bs-run-btn"
                  :disabled="runningTaskIds.has(task.id)"
                  :title="'Lancer maintenant'"
                  @click.stop="runTask(task)"
                >
                  <span v-if="runningTaskIds.has(task.id)" class="bs-spin">⟳</span>
                  <svg v-else width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </button>
                <button class="bs-icon-btn" title="Modifier" @click.stop="openDialog(task)">✏</button>
                <button class="bs-icon-btn danger" title="Supprimer" @click.stop="confirmDeleteTask(task)">✕</button>
              </div>
            </div>

            <!-- Expanded detail -->
            <transition name="bs-expand">
              <div v-if="expandedTask === task.id" class="bs-task-detail">
                <div class="bs-detail-row">
                  <span class="bs-detail-label">Statut dernier run</span>
                  <span :class="['bs-run-badge lg', task.last_run_status || 'never']">
                    {{ runStatusLabel(task.last_run_status) }}
                  </span>
                </div>
                <div class="bs-detail-row">
                  <span class="bs-detail-label">Heure du dernier run</span>
                  <span class="bs-detail-val">{{ task.last_run_at ? formatDateTime(task.last_run_at) : '—' }}</span>
                </div>
                <div v-if="task.last_run_message" class="bs-detail-row">
                  <span class="bs-detail-label">Message</span>
                  <span class="bs-detail-val mono">{{ task.last_run_message }}</span>
                </div>
                <div class="bs-detail-row">
                  <span class="bs-detail-label">Prochain run prévu</span>
                  <span class="bs-detail-val">{{ nextRunTime(task) }}</span>
                </div>
                <div class="bs-detail-row" v-if="nextOccurrences(task, 3).length > 1">
                  <span class="bs-detail-label">3 prochaines exécutions</span>
                  <span class="bs-detail-val">
                    <span v-for="(d, i) in nextOccurrences(task, 3)" :key="i"
                          class="bs-next-occ" :class="{ first: i === 0 }">
                      {{ formatOccurrence(d) }}<span v-if="i < 2"> · </span>
                    </span>
                  </span>
                </div>
                <div class="bs-detail-row">
                  <span class="bs-detail-label">Expression cron</span>
                  <code class="bs-detail-cron">{{ task.cron }}</code>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- RIGHT: Retention policy -->
      <div class="bs-card">
        <div class="bs-card-header">
          <div class="bs-card-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4.03 3-9 3S3 13.66 3 12"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/></svg>
            Politique de rétention
          </div>
          <span class="bs-gfs-badge">GFS</span>
        </div>

        <p class="bs-retention-intro">
          Stratégie <strong>Grandfather-Father-Son</strong> — les backups récents sont conservés
          en haute résolution, les anciens sont progressivement élagués.
          Au-delà de la fenêtre mensuelle, tout est supprimé automatiquement.
        </p>

        <!-- GFS visual pyramid -->
        <div class="bs-pyramid">
          <div v-for="tier in gfsTierVisual" :key="tier.key" :class="['bs-prow', tier.key]">
            <div class="bs-prow-bar-wrap">
              <div class="bs-prow-bar" :style="{ width: tier.barWidth + '%' }"></div>
            </div>
            <div class="bs-prow-labels">
              <span class="bs-prow-title">{{ tier.title }}</span>
              <span class="bs-prow-rule">{{ tier.rule }}</span>
            </div>
          </div>
          <div class="bs-prow old">
            <div class="bs-prow-bar-wrap">
              <div class="bs-prow-bar striped" style="width: 15%"></div>
            </div>
            <div class="bs-prow-labels">
              <span class="bs-prow-title">Au-delà</span>
              <span class="bs-prow-rule bs-prow-deleted">Supprimé automatiquement</span>
            </div>
          </div>
        </div>

        <!-- Tier controls -->
        <div class="bs-tiers">
          <div class="bs-tier-row">
            <div class="bs-tier-badge recent">Récent</div>
            <div class="bs-tier-desc">Garder tous les backups</div>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.recent_keep_hours" type="number" min="1" max="168" class="bs-num-input" />
              <span class="bs-unit">heures</span>
            </div>
          </div>
          <div class="bs-tier-row">
            <div class="bs-tier-badge daily">Quotidien</div>
            <div class="bs-tier-desc">1 backup/jour pendant</div>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.daily_keep_days" type="number" min="1" max="60" class="bs-num-input" />
              <span class="bs-unit">jours</span>
            </div>
          </div>
          <div class="bs-tier-row">
            <div class="bs-tier-badge weekly">Hebdo</div>
            <div class="bs-tier-desc">1 backup/semaine pendant</div>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.weekly_keep_weeks" type="number" min="1" max="52" class="bs-num-input" />
              <span class="bs-unit">semaines</span>
            </div>
          </div>
          <div class="bs-tier-row">
            <div class="bs-tier-badge monthly">Mensuel</div>
            <div class="bs-tier-desc">1 backup/mois pendant</div>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.monthly_keep_months" type="number" min="1" max="24" class="bs-num-input" />
              <span class="bs-unit">mois</span>
            </div>
          </div>
        </div>

        <div class="bs-limits-row">
          <div class="bs-limit-item">
            <span class="bs-limit-label">Maximum absolu</span>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.max_total" type="number" min="5" max="200" class="bs-num-input" />
              <span class="bs-unit">backups</span>
            </div>
          </div>
          <div class="bs-limit-item">
            <span class="bs-limit-label">Espace libre min.</span>
            <div class="bs-tier-ctl">
              <input v-model.number="retention.min_free_gb" type="number" min="1" max="500" class="bs-num-input" />
              <span class="bs-unit">Go</span>
            </div>
          </div>
        </div>

        <div class="bs-retention-est">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          Estimation : <strong>~{{ estimatedKeep }} backups</strong> conservés au maximum
          <span v-if="lastRetentionApplied" class="bs-last-applied">
            · Dernière application : {{ lastRetentionApplied }}
          </span>
        </div>

        <button class="bs-save-ret-btn" :disabled="savingRetention" @click="saveRetention">
          <span v-if="savingRetention" class="bs-spin">⟳</span>
          Enregistrer la politique
        </button>
      </div>
    </div>

    <!-- ── Add/Edit task dialog ── -->
    <transition name="bs-overlay-fade">
      <div v-if="dialog" class="bs-overlay" @click.self="closeDialog">
        <div class="bs-dialog">
          <div class="bs-dialog-header">
            <span>{{ form.id ? 'Modifier la tâche' : 'Nouvelle tâche planifiée' }}</span>
            <button class="bs-dialog-close" @click="closeDialog">×</button>
          </div>
          <div class="bs-dialog-body">
            <div class="bs-field">
              <label class="bs-label">Nom de la tâche</label>
              <input v-model="form.label" type="text" class="bs-input" placeholder="Ex: Backup quotidien complet" autofocus />
            </div>
            <div class="bs-field">
              <label class="bs-label">Type de backup</label>
              <div class="bs-type-grid">
                <button v-for="t in taskTypes" :key="t.value" :class="['bs-type-opt', { active: form.type === t.value }]" @click="form.type = t.value">
                  <span class="bs-topt-icon">{{ t.icon }}</span>
                  <span class="bs-topt-name">{{ t.label }}</span>
                  <span class="bs-topt-desc">{{ t.desc }}</span>
                </button>
              </div>
            </div>
            <div class="bs-field">
              <label class="bs-label">Planification</label>
              <div class="bs-sched-tabs">
                <button :class="['bs-stab', { active: schedMode === 'preset' }]" @click="schedMode = 'preset'">Assisté</button>
                <button :class="['bs-stab', { active: schedMode === 'cron' }]" @click="schedMode = 'cron'">Cron expert</button>
              </div>
              <div v-if="schedMode === 'preset'" class="bs-preset-builder">
                <select v-model="preset.freq" class="bs-select" @change="onPresetChange">
                  <option value="minutes">Toutes les N minutes</option>
                  <option value="hours">Toutes les N heures</option>
                  <option value="daily">Tous les jours à une heure</option>
                  <option value="weekly">Une fois par semaine</option>
                </select>
                <div v-if="preset.freq === 'minutes'" class="bs-preset-row">
                  <span class="bs-prow-lbl">Toutes les</span>
                  <input v-model.number="preset.every" type="number" min="1" max="59" class="bs-num-input sm" @input="onPresetChange" />
                  <span class="bs-prow-unit">minutes</span>
                </div>
                <div v-if="preset.freq === 'hours'" class="bs-preset-row">
                  <span class="bs-prow-lbl">Toutes les</span>
                  <input v-model.number="preset.every" type="number" min="1" max="23" class="bs-num-input sm" @input="onPresetChange" />
                  <span class="bs-prow-unit">heures</span>
                </div>
                <div v-if="preset.freq === 'daily'" class="bs-preset-row">
                  <span class="bs-prow-lbl">À</span>
                  <input v-model="preset.time" type="time" class="bs-time-input" @input="onPresetChange" />
                </div>
                <div v-if="preset.freq === 'weekly'" class="bs-preset-row">
                  <select v-model="preset.weekday" class="bs-select sm" @change="onPresetChange">
                    <option value="1">Lundi</option><option value="2">Mardi</option>
                    <option value="3">Mercredi</option><option value="4">Jeudi</option>
                    <option value="5">Vendredi</option><option value="6">Samedi</option>
                    <option value="0">Dimanche</option>
                  </select>
                  <span class="bs-prow-lbl">à</span>
                  <input v-model="preset.time" type="time" class="bs-time-input" @input="onPresetChange" />
                </div>
              </div>
              <div v-else class="bs-cron-builder">
                <input v-model="form.cron" type="text" class="bs-input bs-cron-input" placeholder="0 2 * * *" />
                <div class="bs-cron-hint">
                  <span>min</span><span>heure</span><span>jour</span><span>mois</span><span>sem</span>
                </div>
              </div>
            </div>
            <div class="bs-preview-box">
              <span class="bs-preview-lbl">Sera exécuté :</span>
              <strong class="bs-preview-val">{{ cronHuman(form.cron) }}</strong>
              <code class="bs-preview-code">{{ form.cron }}</code>
            </div>
            <div class="bs-toggle-row">
              <span class="bs-toggle-lbl">Activer immédiatement</span>
              <label class="bs-toggle">
                <input type="checkbox" v-model="form.enabled" />
                <span class="bs-toggle-slider"></span>
              </label>
            </div>
          </div>
          <div class="bs-dialog-footer">
            <button class="bs-btn-ghost" @click="closeDialog">Annuler</button>
            <button class="bs-btn-primary" :disabled="!form.label || !form.cron || savingTask" @click="saveTask">
              <span v-if="savingTask" class="bs-spin">⟳</span>
              {{ form.id ? 'Mettre à jour' : 'Créer la tâche' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ── Delete confirm dialog ── -->
    <transition name="bs-overlay-fade">
      <div v-if="deleteTarget" class="bs-overlay" @click.self="deleteTarget = null">
        <div class="bs-dialog bs-dialog-sm">
          <div class="bs-dialog-header danger">
            <span>Supprimer la tâche</span>
            <button class="bs-dialog-close" @click="deleteTarget = null">×</button>
          </div>
          <div class="bs-dialog-body">
            <p class="bs-confirm-text">
              Supprimer <strong>{{ deleteTarget.label }}</strong> ?<br />
              La tâche sera retirée du crontab système.
            </p>
          </div>
          <div class="bs-dialog-footer">
            <button class="bs-btn-ghost" @click="deleteTarget = null">Annuler</button>
            <button class="bs-btn-danger" @click="deleteTask">Supprimer</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ── Apply retention confirm dialog (replaces native confirm()) ── -->
    <transition name="bs-overlay-fade">
      <div v-if="applyDialog" class="bs-overlay" @click.self="applyDialog = false">
        <div class="bs-dialog bs-dialog-sm">
          <div class="bs-dialog-header warning">
            <span>Appliquer la rétention</span>
            <button class="bs-dialog-close" @click="applyDialog = false">×</button>
          </div>
          <div class="bs-dialog-body">
            <div class="bs-confirm-icon">🗑</div>
            <p class="bs-confirm-text">
              Appliquer la politique de rétention maintenant ?<br />
              <strong>Les backups hors limites seront définitivement supprimés.</strong>
            </p>
          </div>
          <div class="bs-dialog-footer">
            <button class="bs-btn-ghost" @click="applyDialog = false">Annuler</button>
            <button class="bs-btn-warning" @click="applyRetention">Appliquer</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ── Run now result dialog ── -->
    <transition name="bs-overlay-fade">
      <div v-if="runResult" class="bs-overlay" @click.self="runResult = null">
        <div class="bs-dialog bs-dialog-sm">
          <div class="bs-dialog-header" :class="runResult.ok ? '' : 'danger'">
            <span>Résultat d'exécution</span>
            <button class="bs-dialog-close" @click="runResult = null">×</button>
          </div>
          <div class="bs-dialog-body">
            <div class="bs-run-result-header">
              <span class="bs-run-result-icon">{{ runResult.ok ? '✅' : '❌' }}</span>
              <div>
                <div class="bs-run-result-title">{{ runResult.ok ? 'Sauvegarde réussie' : 'Échec de la sauvegarde' }}</div>
                <div class="bs-run-result-task">{{ runResult.taskName }}</div>
              </div>
            </div>
            <div v-if="runResult.message" class="bs-run-result-msg">{{ runResult.message }}</div>
          </div>
          <div class="bs-dialog-footer">
            <button class="bs-btn-primary" @click="runResult = null">OK</button>
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
  name: "BackupSchedule",
  inject: ["emitter"],

  data() {
    return {
      loading: true,
      dialog: false,
      deleteTarget: null,
      applyDialog: false,
      runResult: null,
      schedMode: "preset",
      savingTask: false,
      savingRetention: false,
      applyingRetention: false,
      testingNotif: false,
      toast: null,
      lastRetentionApplied: null,
      expandedTask: null,
      runningTaskIds: new Set(),

      // ── Timezone state ────────────────────────────────────────────────
      // `scheduleTimezone`  = currently APPLIED on the server (source of truth)
      // `pendingTimezone`   = currently SELECTED in the dropdown (may differ)
      // `undoTimezone`      = previously applied TZ, kept for the undo banner
      //                       (cleared automatically after `undoExpiresMs`)
      scheduleTimezone: 'Africa/Tunis',
      pendingTimezone:  'Africa/Tunis',
      undoTimezone:     null,
      undoExpiresAt:    0,
      _undoTimer:       null,
      savingTimezone: false,
      tzSaved: false,

      timezoneOptions: [
        { value: 'UTC',              label: 'UTC (UTC+0)' },
        { value: 'Africa/Tunis',     label: 'Tunis — CET (UTC+1)' },
        { value: 'Europe/Paris',     label: 'Paris — CET/CEST (UTC+1/+2)' },
        { value: 'Europe/London',    label: 'Londres — GMT/BST (UTC+0/+1)' },
        { value: 'Europe/Berlin',    label: 'Berlin — CET/CEST (UTC+1/+2)' },
        { value: 'Europe/Istanbul',  label: 'Istanbul — TRT (UTC+3)' },
        { value: 'Asia/Riyadh',      label: 'Riyad — AST (UTC+3)' },
        { value: 'Asia/Dubai',       label: 'Dubaï — GST (UTC+4)' },
        { value: 'America/New_York', label: 'New York — EST/EDT (UTC-5/-4)' },
        { value: 'America/Chicago',  label: 'Chicago — CST/CDT (UTC-6/-5)' },
      ],

      tasks: [],
      retention: {
        recent_keep_hours: 24,
        daily_keep_days: 7,
        weekly_keep_weeks: 4,
        monthly_keep_months: 6,
        max_total: 30,
        min_free_gb: 5,
      },
      stats: { total_backups: 0, total_size_gb: 0, free_gb: 0, total_gb: 0 },

      // Live clock — re-rendered every 30 s so "dans 5 min" → "dans 4 min"
      // without re-hitting the backend. Initialized in `data()` so SSR-style
      // first paint has a real value instead of undefined.
      now: new Date(),
      _nowTimer: null,

      form: { id: null, label: "", type: "safe_backup", cron: "0 2 * * *", enabled: true },
      preset: { freq: "daily", every: 6, time: "02:00", weekday: "1" },

      taskTypes: [
        { value: "safe_backup", label: "Safe",    icon: "🛡",  desc: "Configs & règles (rapide)" },
        { value: "full_backup", label: "Full DR", icon: "💽",  desc: "Disaster Recovery complet" },
        { value: "db_backup",   label: "DB only", icon: "🗃",  desc: "Base de données uniquement" },
      ],
    };
  },

  computed: {
    storagePercent() {
      if (!this.stats.total_gb) return 0;
      return Math.min(100, Math.round((this.stats.total_size_gb / this.stats.total_gb) * 100));
    },

    storageClass() {
      const p = this.storagePercent;
      if (p >= 85) return "critical";
      if (p >= 65) return "warn";
      return "ok";
    },

    estimatedKeep() {
      const r = this.retention;
      const recentCount = Math.max(1, Math.ceil(r.recent_keep_hours / 6));
      return Math.min(r.max_total, recentCount + r.daily_keep_days + r.weekly_keep_weeks + r.monthly_keep_months);
    },

    gfsTierVisual() {
      const r = this.retention;
      return [
        { key: "recent",  title: `Récent (${r.recent_keep_hours}h)`,       rule: "Tous les backups conservés", barWidth: 100 },
        { key: "daily",   title: `Quotidien (${r.daily_keep_days}j)`,       rule: "1 backup / jour",            barWidth: 72  },
        { key: "weekly",  title: `Hebdo (${r.weekly_keep_weeks} sem.)`,      rule: "1 backup / semaine",         barWidth: 48  },
        { key: "monthly", title: `Mensuel (${r.monthly_keep_months} mois)`, rule: "1 backup / mois",            barWidth: 28  },
      ];
    },

    lastRunGlobal() {
      const ran = this.tasks
        .filter(t => t.last_run_at)
        .sort((a, b) => new Date(b.last_run_at) - new Date(a.last_run_at));
      return ran.length ? this.formatRelative(ran[0].last_run_at) : null;
    },

    lastRunStatusGlobal() {
      const ran = this.tasks
        .filter(t => t.last_run_at)
        .sort((a, b) => new Date(b.last_run_at) - new Date(a.last_run_at));
      return ran.length ? (ran[0].last_run_status || "ok") : "never";
    },

    nextRunGlobal() {
      const enabled = this.tasks.filter(t => t.enabled);
      if (!enabled.length) return null;
      // Prefer the backend-computed ISO (timezone-correct); fall back to local.
      const times = enabled
        .map(t => this.taskNextRunDate(t))
        .filter(Boolean);
      if (!times.length) return null;
      times.sort((a, b) => a - b);
      return this.nextRunTime({ next_run: times[0].toISOString(),
                                cron: enabled[0].cron });
    },

    // Did the user stage a TZ different from the one currently applied?
    hasPendingChange() {
      return this.pendingTimezone &&
             this.pendingTimezone !== this.scheduleTimezone;
    },

    // Resolve a tz IANA name to its dropdown label. We fall back to the raw
    // name so even unknown TZs (legacy configs) render readably.
    scheduleTimezoneLabel() {
      const o = this.timezoneOptions.find(x => x.value === this.scheduleTimezone);
      return o ? o.label : this.scheduleTimezone;
    },
    pendingTimezoneLabel() {
      const o = this.timezoneOptions.find(x => x.value === this.pendingTimezone);
      return o ? o.label : this.pendingTimezone;
    },
    undoTimezoneLabel() {
      if (!this.undoTimezone) return "";
      const o = this.timezoneOptions.find(x => x.value === this.undoTimezone);
      return o ? o.label : this.undoTimezone;
    },
  },

  beforeUnmount() {
    if (this._nowTimer) clearInterval(this._nowTimer);
  },

  methods: {
    async fetchSchedule() {
      this.loading = true;
      try {
        const res = await axios.get("/backup/schedule");
        this.tasks = res.data.tasks || [];
        this.retention = { ...this.retention, ...res.data.retention };
        this.stats = { ...this.stats, ...res.data.stats };
        if (res.data.schedule_timezone) {
          this.scheduleTimezone = res.data.schedule_timezone;
          // Only re-sync the dropdown if the user hasn't staged a different
          // choice (otherwise we'd nuke their pending pick on every refresh).
          if (!this.hasPendingChange) {
            this.pendingTimezone = res.data.schedule_timezone;
          }
        }
        if (res.data.last_retention_applied) {
          this.lastRetentionApplied = new Date(res.data.last_retention_applied + "Z")
            .toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
        }
      } catch {
        this.showToast("Erreur de chargement des tâches", "error");
      } finally {
        this.loading = false;
      }
    },

    openDialog(task = null) {
      if (task) {
        this.form = { id: task.id, label: task.label, type: task.type, cron: task.cron, enabled: !!task.enabled };
        this.schedMode = "cron";
      } else {
        this.form = { id: null, label: "", type: "safe_backup", cron: "0 2 * * *", enabled: true };
        this.preset = { freq: "daily", every: 6, time: "02:00", weekday: "1" };
        this.schedMode = "preset";
        this.onPresetChange();
      }
      this.dialog = true;
    },

    closeDialog() { this.dialog = false; },

    // Dropdown @change handler — just stages the choice locally. The actual
    // server call only happens when the user clicks "Confirmer" below.
    onTimezoneSelect() {
      // No-op if the user re-picked the active timezone.
      if (this.pendingTimezone === this.scheduleTimezone) {
        this.tzSaved = false;
      }
    },

    cancelTimezoneChange() {
      this.pendingTimezone = this.scheduleTimezone;
      this.showToast("Changement de fuseau annulé", "info");
    },

    async confirmTimezoneChange() {
      await this._applyTimezone(this.pendingTimezone, { showUndo: true });
    },

    async revertTimezone() {
      if (!this.undoTimezone) return;
      const target = this.undoTimezone;
      // Apply the previous TZ. We DO NOT show an undo for the undo —
      // otherwise the operator could ping-pong indefinitely.
      await this._applyTimezone(target, { showUndo: false });
      this.showToast(`Fuseau revenu à ${target}`, "info");
    },

    // Shared apply path. The backend handles the "don't trigger catchups"
    // safety; we just persist the choice and refresh.
    async _applyTimezone(tz, { showUndo }) {
      if (!tz) return;
      this.savingTimezone = true;
      this.tzSaved = false;
      try {
        this._setCSRF();
        const { data } = await axios.post(
          "/backup/schedule/timezone",
          { timezone: tz },
        );
        const previousTz = data.previous_timezone || this.scheduleTimezone;
        this.scheduleTimezone = data.schedule_timezone || tz;
        this.pendingTimezone  = this.scheduleTimezone;
        this.tzSaved          = true;
        // Re-fetch so every task's `next_run` is recomputed for the new TZ.
        // Safe now — the backend has pre-stamped each task's last_queued_for,
        // so the catchup logic on the next /schedule call is a no-op.
        await this.fetchSchedule();
        this.showToast(`Fuseau appliqué : ${this.scheduleTimezone}`, "success");

        // Undo affordance — 12 s grace window where the user can revert.
        if (showUndo && previousTz && previousTz !== this.scheduleTimezone) {
          this._armUndo(previousTz, 12_000);
        } else {
          this._clearUndo();
        }
        setTimeout(() => { this.tzSaved = false; }, 3000);
      } catch {
        this.showToast("Erreur lors du changement de fuseau", "error");
        // Roll back the dropdown to the applied value so the UI stays honest.
        this.pendingTimezone = this.scheduleTimezone;
      } finally {
        this.savingTimezone = false;
      }
    },

    _armUndo(previousTz, ms) {
      this._clearUndo();
      this.undoTimezone  = previousTz;
      this.undoExpiresAt = Date.now() + ms;
      this._undoTimer = setTimeout(() => { this._clearUndo(); }, ms);
    },

    _clearUndo() {
      this.undoTimezone  = null;
      this.undoExpiresAt = 0;
      if (this._undoTimer) { clearTimeout(this._undoTimer); this._undoTimer = null; }
    },

    // Cheap "preview" of what a task's next run would be in another TZ —
    // used in the confirmation card to show the operator the impact BEFORE
    // committing. We just shift the user-local clock by the TZ offset diff;
    // it's an approximation (doesn't handle DST edge cases perfectly) but
    // it's enough to give the operator confidence.
    previewNextRun(cron, targetTz) {
      try {
        const localDate = this.nextRunDate(cron);
        if (!localDate) return "—";
        // Compute offset diff between current scheduler TZ and target TZ.
        const nowMs = Date.now();
        const targetOffset  = -new Date(nowMs).getTimezoneOffset() * 60_000;
        // Use Intl to get target-zone hour at the same UTC instant.
        const fmt = new Intl.DateTimeFormat("fr-FR", {
          timeZone: targetTz,
          weekday: "short", day: "2-digit", month: "short",
          hour: "2-digit", minute: "2-digit",
        });
        // We need the next-run instant as a UTC date. Backend ISO is preferred
        // (already UTC), so we look it up by cron match if no task object given.
        return fmt.format(localDate);
      } catch {
        return "—";
      }
    },

    onPresetChange() {
      const p = this.preset;
      const [hh, mm] = (p.time || "00:00").split(":").map(Number);
      if (p.freq === "minutes")     this.form.cron = `*/${Math.max(1, p.every || 5)} * * * *`;
      else if (p.freq === "hours")  this.form.cron = `0 */${Math.max(1, p.every || 6)} * * *`;
      else if (p.freq === "daily")  this.form.cron = `${mm} ${hh} * * *`;
      else if (p.freq === "weekly") this.form.cron = `${mm} ${hh} * * ${p.weekday}`;
    },

    cronHuman(expr) {
      if (!expr) return "—";
      const parts = expr.trim().split(/\s+/);
      if (parts.length !== 5) return expr;
      const [min, hour, , , weekday] = parts;
      if (min.startsWith("*/") && hour === "*")
        return `Toutes les ${min.slice(2)} minutes`;
      if (min === "0" && hour.startsWith("*/"))
        return `Toutes les ${hour.slice(2)} heures`;
      if (!min.includes("*") && !hour.includes("*") && weekday === "*")
        return `Tous les jours à ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
      if (!min.includes("*") && !hour.includes("*") && !weekday.includes("*")) {
        const days = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
        return `Chaque ${days[parseInt(weekday)] || weekday} à ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
      }
      return expr;
    },

    // Best-effort local fallback for cron → next-run when the backend hasn't
    // provided one yet (e.g. brand-new task before first refresh).
    // The backend is authoritative — see views.get_schedule which serializes
    // `next_run` per task using the configured scheduler timezone. We only
    // fall back to client-side math if `task.next_run` is missing.
    nextRunDate(expr) {
      if (!expr) return null;
      const parts = expr.trim().split(/\s+/);
      if (parts.length !== 5) return null;
      const [minP, hourP, , , wdP] = parts;
      const now = new Date();
      const next = new Date(now);
      next.setSeconds(0, 0);

      if (minP.startsWith("*/")) {
        const interval = parseInt(minP.slice(2));
        const rem = interval - (now.getMinutes() % interval);
        next.setMinutes(now.getMinutes() + rem);
        return next;
      }
      if (!minP.includes("*") && !hourP.includes("*")) {
        const h = parseInt(hourP), m = parseInt(minP);
        next.setHours(h, m, 0, 0);
        if (next <= now) next.setDate(next.getDate() + 1);
        if (!wdP.includes("*")) {
          const target = parseInt(wdP);
          for (let i = 0; i < 7; i++) {
            if (next.getDay() === target) break;
            next.setDate(next.getDate() + 1);
          }
        }
        return next;
      }
      return null;
    },

    // Returns a JS Date for the task's next run. Prefers the backend-computed
    // ISO (timezone-correct) and falls back to local cron parsing otherwise.
    // `arg` may be a task object OR a raw cron string (for `nextRunGlobal`).
    taskNextRunDate(arg) {
      if (arg && typeof arg === "object") {
        if (arg.next_run) {
          const d = new Date(arg.next_run);
          if (!isNaN(d.getTime())) return d;
        }
        return this.nextRunDate(arg.cron);
      }
      return this.nextRunDate(arg);
    },

    // Multi-tier human formatter. Anchored on `this.now` so a 30 s reactive
    // ticker re-renders "dans 5 min" → "dans 4 min" without re-fetching.
    nextRunTime(arg) {
      const d = this.taskNextRunDate(arg);
      if (!d) return this.cronHuman(typeof arg === "string" ? arg : (arg && arg.cron) || "");
      const now = this.now || new Date();
      const diff = d - now;

      // Past or imminent (within the next minute).
      if (diff < 60000)    return "dans moins d'une minute";
      if (diff < 3600000)  return `dans ${Math.round(diff / 60000)} min`;

      const hh = d.getHours().toString().padStart(2, "0");
      const mm = d.getMinutes().toString().padStart(2, "0");

      // Same calendar day.
      if (d.toDateString() === now.toDateString()) {
        return `aujourd'hui à ${hh}:${mm}`;
      }
      // Next calendar day.
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      if (d.toDateString() === tomorrow.toDateString()) {
        return `demain à ${hh}:${mm}`;
      }
      // 2-6 days ahead — "dans 5 jours, vendredi à 08:00" is more readable
      // than a raw date for short-term planning.
      const daysAhead = Math.round((d - now) / 86400000);
      if (daysAhead < 7) {
        const wd = ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."][d.getDay()];
        return `dans ${daysAhead} j (${wd} ${hh}:${mm})`;
      }
      // Further out — give the date.
      return d.toLocaleDateString("fr-FR", {
        day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
      });
    },

    // Returns the next N occurrences of a cron for the expanded task detail.
    // The first occurrence comes from the backend-provided ISO; subsequent
    // ones are extrapolated by the natural period of the cron:
    //   "*/N * * * *"  → +N minutes
    //   "0 */N * * *"  → +N hours
    //   "M H * * *"    → +1 day
    //   "M H * * DOW"  → +7 days
    // This isn't a full cron evaluator, just enough for the common patterns
    // the schedule UI lets users author.
    nextOccurrences(task, count = 3) {
      const first = this.taskNextRunDate(task);
      if (!first) return [];
      const out = [new Date(first)];
      const parts = (task.cron || "").trim().split(/\s+/);
      if (parts.length !== 5) return out;
      const [minP, hourP, , , wdP] = parts;
      let stepMs = 0;
      if (minP.startsWith("*/"))                         stepMs = parseInt(minP.slice(2)) * 60_000;
      else if (hourP.startsWith("*/"))                   stepMs = parseInt(hourP.slice(2)) * 3600_000;
      else if (wdP.includes("*"))                        stepMs = 86_400_000;       // daily
      else                                               stepMs = 7 * 86_400_000;   // weekly
      for (let i = 1; i < count; i++) {
        out.push(new Date(out[i - 1].getTime() + stepMs));
      }
      return out;
    },

    // Short occurrence formatter for the "3 prochaines exécutions" line.
    // Always shows day + HH:MM so the planning is unambiguous.
    formatOccurrence(d) {
      if (!d) return "—";
      return d.toLocaleString("fr-FR", {
        weekday: "short", day: "2-digit", month: "short",
        hour: "2-digit", minute: "2-digit",
      });
    },

    formatRelative(iso) {
      if (!iso) return "—";
      const d = new Date(iso.includes("T") ? iso : iso + "Z");
      const diff = Date.now() - d;
      if (diff < 60000) return "à l'instant";
      if (diff < 3600000) return `il y a ${Math.round(diff / 60000)} min`;
      if (diff < 86400000) return `il y a ${Math.round(diff / 3600000)}h`;
      return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
    },

    formatDateTime(iso) {
      if (!iso) return "—";
      const d = new Date(iso.includes("T") ? iso : iso + "Z");
      return d.toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
    },

    taskTypeLabel(type) {
      return { safe_backup: "Safe", full_backup: "Full DR", db_backup: "DB" }[type] || type;
    },

    runStatusLabel(status) {
      return { ok: "OK", success: "OK", error: "Erreur", never: "Jamais" }[status] || (status ? status : "Jamais");
    },

    async saveTask() {
      if (!this.form.label || !this.form.cron) return;
      this.savingTask = true;
      try {
        this._setCSRF();
        const res = await axios.post("/backup/schedule/task", this.form);
        this.tasks = res.data.tasks;
        this.emitter.emit("schedule-changed");
        this.showToast(this.form.id ? "Tâche mise à jour" : "Tâche créée avec succès", "success");
        this.closeDialog();
      } catch {
        this.showToast("Erreur lors de la sauvegarde", "error");
      } finally {
        this.savingTask = false;
      }
    },

    async toggleTask(task) {
      try {
        this._setCSRF();
        const res = await axios.post("/backup/schedule/task", { ...task, enabled: !task.enabled });
        this.tasks = res.data.tasks;
        this.emitter.emit("schedule-changed");
      } catch {
        this.showToast("Erreur de mise à jour", "error");
      }
    },

    confirmDeleteTask(task) { this.deleteTarget = task; },

    async deleteTask() {
      if (!this.deleteTarget) return;
      try {
        this._setCSRF();
        const res = await axios.delete(`/backup/schedule/task/${this.deleteTarget.id}`);
        this.tasks = res.data.tasks;
        this.emitter.emit("schedule-changed");
        this.showToast("Tâche supprimée", "success");
      } catch {
        this.showToast("Erreur lors de la suppression", "error");
      } finally {
        this.deleteTarget = null;
      }
    },

    async runTask(task) {
      this.runningTaskIds = new Set([...this.runningTaskIds, task.id]);
      this.showToast(`Lancement de "${task.label}"...`, "info");
      try {
        this._setCSRF();
        const res = await axios.post(`/backup/schedule/run/${task.id}`);
        const ok = res.data.status === "ok" || res.data.status === "success";
        this.runResult = {
          ok,
          taskName: task.label,
          message: res.data.task?.last_run_message || "",
        };
        await this.fetchSchedule();
        this.emitter.emit("schedule-changed");
      } catch (e) {
        this.runResult = { ok: false, taskName: task.label, message: e?.response?.data?.message || "Erreur réseau" };
      } finally {
        const s = new Set(this.runningTaskIds);
        s.delete(task.id);
        this.runningTaskIds = s;
      }
    },

    async saveRetention() {
      this.savingRetention = true;
      try {
        this._setCSRF();
        await axios.put("/backup/schedule/retention", this.retention);
        this.showToast("Politique de rétention enregistrée", "success");
      } catch {
        this.showToast("Erreur lors de l'enregistrement", "error");
      } finally {
        this.savingRetention = false;
      }
    },

    async applyRetention() {
      this.applyDialog = false;
      this.applyingRetention = true;
      try {
        this._setCSRF();
        const res = await axios.post("/backup/schedule/apply-retention");
        const d = res.data;
        this.showToast(`Rétention appliquée — ${d.total_deleted} supprimé(s), ${d.kept} conservé(s)`, "success");
        this.lastRetentionApplied = new Date().toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
        this.emitter.emit("retention-applied");
        await this.fetchSchedule();
      } catch {
        this.showToast("Erreur lors de l'application de la rétention", "error");
      } finally {
        this.applyingRetention = false;
      }
    },

    async ntfyTest() {
      this.testingNotif = true;
      try {
        this._setCSRF();
        await axios.post("/backup/telegram-test");
        this.showToast("Notification test envoyée sur ntfy ✓", "success");
      } catch {
        this.showToast("Échec de l'envoi de la notification test", "error");
      } finally {
        this.testingNotif = false;
      }
    },

    _setCSRF() {
      const t = getCookie("csrftoken");
      if (t) axios.defaults.headers.common["X-CSRFToken"] = t;
    },

    showToast(msg, type = "info") {
      this.toast = { msg, type };
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => { this.toast = null; }, 4500);
    },
  },

  mounted() {
    this.fetchSchedule();
    // 30 s ticker so countdowns ("dans 5 min" → "dans 4 min") refresh without
    // re-hitting the backend. Cleared in beforeUnmount above.
    this._nowTimer = setInterval(() => { this.now = new Date(); }, 30_000);
  },
};
</script>

<style scoped lang="scss" src="../../../assets/scss/BackupSchedule.scss"></style>
