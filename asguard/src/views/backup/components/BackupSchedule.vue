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

    <!-- ── Timezone selector ── -->
    <div class="bs-tz-bar">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      <span class="bs-tz-label">Fuseau horaire du planificateur :</span>
      <select class="bs-tz-select" v-model="scheduleTimezone" @change="saveTimezone">
        <option v-for="tz in timezoneOptions" :key="tz.value" :value="tz.value">{{ tz.label }}</option>
      </select>
      <span v-if="savingTimezone" class="bs-tz-saving">⟳ Enregistrement...</span>
      <span v-else-if="tzSaved" class="bs-tz-ok">✓ Appliqué</span>
      <span class="bs-tz-hint">Les expressions cron sont interprétées dans ce fuseau.</span>
    </div>

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
                    Prochain : <strong>{{ nextRunTime(task.cron) }}</strong>
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
                  <span class="bs-detail-val">{{ nextRunTime(task.cron) }}</span>
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

      scheduleTimezone: 'Africa/Tunis',
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
      const times = enabled.map(t => this.nextRunDate(t.cron)).filter(Boolean);
      if (!times.length) return null;
      times.sort((a, b) => a - b);
      return this.formatRelative(times[0].toISOString());
    },
  },

  methods: {
    async fetchSchedule() {
      this.loading = true;
      try {
        const res = await axios.get("/backup/schedule");
        this.tasks = res.data.tasks || [];
        this.retention = { ...this.retention, ...res.data.retention };
        this.stats = { ...this.stats, ...res.data.stats };
        if (res.data.schedule_timezone) this.scheduleTimezone = res.data.schedule_timezone;
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

    async saveTimezone() {
      this.savingTimezone = true;
      this.tzSaved = false;
      try {
        this._setCSRF();
        await axios.post("/backup/schedule/timezone", { timezone: this.scheduleTimezone });
        this.tzSaved = true;
        this.showToast(`Fuseau horaire réglé sur ${this.scheduleTimezone}`, "success");
        setTimeout(() => { this.tzSaved = false; }, 3000);
      } catch {
        this.showToast("Erreur lors du changement de fuseau", "error");
      } finally {
        this.savingTimezone = false;
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

    nextRunTime(expr) {
      const d = this.nextRunDate(expr);
      if (!d) return this.cronHuman(expr);
      const now = new Date();
      const diff = d - now;
      if (diff < 60000) return "dans moins d'une minute";
      if (diff < 3600000) return `dans ${Math.round(diff / 60000)} min`;
      if (diff < 86400000) return `aujourd'hui à ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
      return `demain à ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
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

  mounted() { this.fetchSchedule(); },
};
</script>

<style scoped>
/* ── Root ───────────────────────────────────────────────────────────── */
.bs-wrap { padding: 20px 24px; min-height: 400px; font-family: inherit; }

/* ── Top bar ────────────────────────────────────────────────────────── */
.bs-topbar {
  display: flex; align-items: center; gap: 16px;
  background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 12px; padding: 12px 16px; margin-bottom: 12px;
}
.bs-storage-block { display: flex; align-items: center; gap: 10px; flex: 1; }
.bs-storage-icon-wrap {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.bs-storage-icon-wrap.ok       { background: #dcfce7; color: #16a34a; }
.bs-storage-icon-wrap.warn     { background: #fef3c7; color: #d97706; }
.bs-storage-icon-wrap.critical { background: #fee2e2; color: #dc2626; }
.bs-storage-info { flex: 1; }
.bs-storage-track { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-bottom: 5px; }
.bs-storage-fill  { height: 100%; border-radius: 3px; transition: width 0.6s ease; }
.bs-storage-fill.ok       { background: #22c55e; }
.bs-storage-fill.warn     { background: #f59e0b; }
.bs-storage-fill.critical { background: #ef4444; }
.bs-storage-text  { font-size: 12px; color: #64748b; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.bs-storage-sep   { color: #cbd5e1; }
.bs-storage-used  { font-weight: 700; }
.bs-storage-used.ok       { color: #16a34a; }
.bs-storage-used.warn     { color: #d97706; }
.bs-storage-used.critical { color: #dc2626; }
.bs-storage-alert { font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 10px; background: #fee2e2; color: #dc2626; }
.bs-storage-alert.warn    { background: #fef3c7; color: #92400e; }
.bs-topbar-actions { display: flex; gap: 8px; flex-shrink: 0; }

.bs-notif-btn {
  display: flex; align-items: center; gap: 5px;
  background: #f0fdf4; color: #16a34a;
  border: 1px solid #bbf7d0; border-radius: 8px;
  padding: 7px 13px; font-size: 12.5px; font-weight: 500; cursor: pointer;
  transition: all 0.15s; white-space: nowrap;
}
.bs-notif-btn:hover:not(:disabled) { background: #dcfce7; }
.bs-notif-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.bs-apply-btn {
  display: flex; align-items: center; gap: 6px;
  background: #0f172a; color: #fff; border: none;
  border-radius: 8px; padding: 7px 14px; font-size: 12.5px; font-weight: 500;
  cursor: pointer; white-space: nowrap; transition: background 0.2s;
}
.bs-apply-btn:hover:not(:disabled) { background: #1e293b; }
.bs-apply-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Quick stats ───────────────────────────────────────────────────── */
.bs-stats-row {
  display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;
}
.bs-stat-chip {
  display: flex; align-items: center; gap: 7px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 9px;
  padding: 7px 13px; font-size: 12.5px; flex: 1; min-width: 160px;
}
.bs-stat-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.bs-stat-dot.ok        { background: #22c55e; }
.bs-stat-dot.warn      { background: #f59e0b; }
.bs-stat-dot.critical  { background: #ef4444; }
.bs-stat-dot.error     { background: #ef4444; }
.bs-stat-dot.never     { background: #cbd5e1; }
.bs-stat-dot.scheduled { background: #6366f1; }
.bs-stat-label { color: #94a3b8; }
.bs-stat-val   { color: #0f172a; margin-left: auto; }

/* ── Toast ────────────────────────────────────────────────────────── */
.bs-toast {
  position: fixed; bottom: 28px; right: 28px; z-index: 9999;
  display: flex; align-items: center; gap: 10px; padding: 12px 18px;
  border-radius: 10px; font-size: 14px; font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15); max-width: 420px;
}
.bs-toast.success { background: #166534; color: #dcfce7; }
.bs-toast.error   { background: #7f1d1d; color: #fee2e2; }
.bs-toast.info    { background: #1e3a5f; color: #dbeafe; }
.bs-toast-icon    { font-size: 16px; }
.bs-toast-anim-enter-active, .bs-toast-anim-leave-active { transition: all 0.3s ease; }
.bs-toast-anim-enter-from, .bs-toast-anim-leave-to { opacity: 0; transform: translateY(12px); }

/* ── Grid ─────────────────────────────────────────────────────────── */
.bs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 900px) { .bs-grid { grid-template-columns: 1fr; } }

/* ── Card ─────────────────────────────────────────────────────────── */
.bs-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.bs-card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid #f1f5f9; background: #f8fafc;
}
.bs-card-title { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: #0f172a; }
.bs-count-badge { background: #e0e7ff; color: #3730a3; font-size: 11px; font-weight: 700; padding: 1px 7px; border-radius: 10px; }
.bs-gfs-badge   { background: #0f172a; color: #94a3b8; font-size: 10px; font-weight: 700; letter-spacing: 1px; padding: 3px 8px; border-radius: 5px; }
.bs-add-btn     { background: #6366f1; color: #fff; border: none; border-radius: 7px; padding: 6px 14px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.bs-add-btn:hover { background: #4f46e5; }

/* ── State blocks ─────────────────────────────────────────────────── */
.bs-state-block { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 48px 20px; color: #94a3b8; font-size: 14px; }
.bs-state-block.empty .bs-empty-icon { font-size: 36px; }
.bs-add-link { background: none; border: none; color: #6366f1; font-size: 13px; cursor: pointer; text-decoration: underline; padding: 0; margin-top: 4px; }
.bs-spin-lg { font-size: 28px; animation: bs-spin 1s linear infinite; display: inline-block; }
@keyframes bs-spin { to { transform: rotate(360deg); } }
.bs-spin { display: inline-block; animation: bs-spin 1s linear infinite; }

/* ── Task list ────────────────────────────────────────────────────── */
.bs-task-list { padding: 0; }
.bs-task-item {
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.15s;
}
.bs-task-item:last-child { border-bottom: none; }
.bs-task-item:hover { background: #f8fafc; }
.bs-task-item.disabled { opacity: 0.5; }

.bs-task-main {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 12px 18px; cursor: pointer;
}
.bs-task-left  { display: flex; align-items: flex-start; gap: 12px; min-width: 0; flex: 1; }
.bs-type-dot   { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.bs-type-dot.safe_backup { background: #22c55e; }
.bs-type-dot.full_backup { background: #3b82f6; }
.bs-type-dot.db_backup   { background: #a855f7; }
.bs-task-info  { min-width: 0; flex: 1; }
.bs-task-name  { font-size: 13px; font-weight: 600; color: #1e293b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
.bs-task-meta  { display: flex; align-items: center; gap: 8px; margin-top: 4px; flex-wrap: wrap; }
.bs-cron-code  { font-size: 11px; background: #f1f5f9; color: #475569; padding: 1px 5px; border-radius: 4px; font-family: monospace; }
.bs-cron-human { font-size: 11px; color: #94a3b8; }
.bs-last-run   { font-size: 11px; color: #94a3b8; }
.bs-task-next  { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #6366f1; margin-top: 3px; }
.bs-task-next strong { font-weight: 600; }

/* Run status badges */
.bs-run-badge {
  font-size: 10px; font-weight: 700; padding: 1px 7px; border-radius: 10px;
  text-transform: uppercase; letter-spacing: 0.3px;
}
.bs-run-badge.ok, .bs-run-badge.success { background: #dcfce7; color: #166534; }
.bs-run-badge.error   { background: #fee2e2; color: #dc2626; }
.bs-run-badge.never   { background: #f1f5f9; color: #94a3b8; }
.bs-run-badge.lg      { font-size: 12px; padding: 3px 10px; }

.bs-task-right  { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.bs-type-badge  { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 5px; text-transform: uppercase; letter-spacing: 0.5px; }
.bs-type-badge.safe_backup { background: #dcfce7; color: #166534; }
.bs-type-badge.full_backup { background: #dbeafe; color: #1e40af; }
.bs-type-badge.db_backup   { background: #f3e8ff; color: #7e22ce; }

.bs-run-btn {
  background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe;
  border-radius: 6px; width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; cursor: pointer; transition: all 0.15s;
}
.bs-run-btn:hover:not(:disabled) { background: #6366f1; color: #fff; border-color: #6366f1; }
.bs-run-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.bs-icon-btn {
  background: none; border: 1px solid #e2e8f0; border-radius: 6px;
  width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
  font-size: 13px; cursor: pointer; color: #64748b; transition: all 0.15s;
}
.bs-icon-btn:hover          { background: #f1f5f9; color: #0f172a; }
.bs-icon-btn.danger:hover   { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }

/* ── Task expanded detail ──────────────────────────────────────────── */
.bs-task-detail {
  padding: 12px 18px 14px 39px;
  background: #f8fafc; border-top: 1px solid #f1f5f9;
  display: flex; flex-direction: column; gap: 8px;
}
.bs-detail-row   { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.bs-detail-label { color: #94a3b8; min-width: 130px; font-weight: 500; }
.bs-detail-val   { color: #334155; }
.bs-detail-val.mono { font-family: monospace; font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
.bs-detail-cron  { font-family: monospace; font-size: 12px; background: #f1f5f9; color: #475569; padding: 2px 7px; border-radius: 5px; }
.bs-expand-enter-active, .bs-expand-leave-active { transition: all 0.2s ease; overflow: hidden; }
.bs-expand-enter-from, .bs-expand-leave-to { opacity: 0; max-height: 0; padding-top: 0; padding-bottom: 0; }
.bs-expand-enter-to, .bs-expand-leave-from { max-height: 200px; }

/* ── Toggle ────────────────────────────────────────────────────────── */
.bs-toggle { position: relative; display: inline-block; width: 34px; height: 18px; cursor: pointer; }
.bs-toggle input { opacity: 0; width: 0; height: 0; }
.bs-toggle-slider { position: absolute; inset: 0; background: #cbd5e1; border-radius: 9px; transition: background 0.2s; }
.bs-toggle-slider::before { content: ""; position: absolute; width: 12px; height: 12px; border-radius: 50%; background: #fff; top: 3px; left: 3px; transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }
.bs-toggle input:checked + .bs-toggle-slider { background: #22c55e; }
.bs-toggle input:checked + .bs-toggle-slider::before { transform: translateX(16px); }

/* ── Retention ─────────────────────────────────────────────────────── */
.bs-retention-intro { font-size: 12.5px; color: #64748b; line-height: 1.6; margin: 12px 18px 14px; }
.bs-retention-intro strong { color: #0f172a; }
.bs-pyramid { padding: 4px 18px 12px; }
.bs-prow { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
.bs-prow-bar-wrap { width: 140px; height: 16px; background: #f1f5f9; border-radius: 4px; overflow: hidden; flex-shrink: 0; }
.bs-prow-bar { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
.bs-prow.recent  .bs-prow-bar { background: #22c55e; }
.bs-prow.daily   .bs-prow-bar { background: #3b82f6; }
.bs-prow.weekly  .bs-prow-bar { background: #f59e0b; }
.bs-prow.monthly .bs-prow-bar { background: #a855f7; }
.bs-prow.old     .bs-prow-bar { background: #e2e8f0; }
.bs-prow-bar.striped { background: repeating-linear-gradient(45deg, #e2e8f0, #e2e8f0 4px, #f1f5f9 4px, #f1f5f9 8px); }
.bs-prow-labels  { display: flex; flex-direction: column; gap: 1px; }
.bs-prow-title   { font-size: 11.5px; font-weight: 600; color: #334155; }
.bs-prow-rule    { font-size: 10.5px; color: #94a3b8; }
.bs-prow-deleted { color: #ef4444; }
.bs-tiers        { padding: 0 18px; }
.bs-tier-row     { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f8fafc; }
.bs-tier-row:last-child { border-bottom: none; }
.bs-tier-badge   { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 2px 8px; border-radius: 4px; width: 68px; text-align: center; flex-shrink: 0; }
.bs-tier-badge.recent  { background: #dcfce7; color: #166534; }
.bs-tier-badge.daily   { background: #dbeafe; color: #1e40af; }
.bs-tier-badge.weekly  { background: #fef3c7; color: #92400e; }
.bs-tier-badge.monthly { background: #f3e8ff; color: #7e22ce; }
.bs-tier-desc  { flex: 1; font-size: 12.5px; color: #475569; }
.bs-tier-ctl   { display: flex; align-items: center; gap: 5px; }
.bs-num-input  { width: 56px; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 6px; font-size: 13px; text-align: center; outline: none; transition: border-color 0.15s; }
.bs-num-input:focus { border-color: #6366f1; }
.bs-num-input.sm { width: 44px; }
.bs-unit       { font-size: 12px; color: #94a3b8; white-space: nowrap; }
.bs-limits-row { display: flex; gap: 16px; padding: 12px 18px; background: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; margin-top: 8px; }
.bs-limit-item { display: flex; align-items: center; gap: 8px; }
.bs-limit-label { font-size: 12px; color: #64748b; font-weight: 500; white-space: nowrap; }
.bs-retention-est { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: #475569; padding: 10px 18px; flex-wrap: wrap; }
.bs-retention-est strong { color: #0f172a; }
.bs-last-applied { font-size: 11px; color: #94a3b8; }
.bs-save-ret-btn { display: flex; align-items: center; justify-content: center; gap: 6px; width: calc(100% - 36px); margin: 0 18px 18px; background: #0f172a; color: #fff; border: none; border-radius: 8px; padding: 10px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.bs-save-ret-btn:hover:not(:disabled) { background: #1e293b; }
.bs-save-ret-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Overlay / Dialog ──────────────────────────────────────────────── */
.bs-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.55); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 16px; }
.bs-overlay-fade-enter-active, .bs-overlay-fade-leave-active { transition: opacity 0.2s; }
.bs-overlay-fade-enter-from, .bs-overlay-fade-leave-to { opacity: 0; }
.bs-dialog    { background: #fff; border-radius: 14px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden; }
.bs-dialog-sm { max-width: 380px; }
.bs-dialog-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; font-weight: 700; font-size: 15px; color: #0f172a; }
.bs-dialog-header.danger  { background: #fef2f2; color: #dc2626; }
.bs-dialog-header.warning { background: #fffbeb; color: #d97706; }
.bs-dialog-close  { background: none; border: none; font-size: 20px; color: #94a3b8; cursor: pointer; line-height: 1; padding: 0; }
.bs-dialog-close:hover { color: #475569; }
.bs-dialog-body   { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.bs-dialog-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px; border-top: 1px solid #f1f5f9; background: #fafafa; }

.bs-confirm-icon  { font-size: 32px; text-align: center; }
.bs-confirm-text  { font-size: 14px; color: #374151; line-height: 1.6; margin: 0; }

/* Run result dialog */
.bs-run-result-header { display: flex; align-items: center; gap: 12px; }
.bs-run-result-icon   { font-size: 28px; }
.bs-run-result-title  { font-size: 15px; font-weight: 700; color: #0f172a; }
.bs-run-result-task   { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.bs-run-result-msg    { font-size: 12.5px; color: #475569; background: #f8fafc; border-radius: 8px; padding: 10px 12px; font-family: monospace; }

/* Form elements */
.bs-field  { display: flex; flex-direction: column; gap: 6px; }
.bs-label  { font-size: 12.5px; font-weight: 600; color: #374151; }
.bs-input  { border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; font-size: 14px; outline: none; transition: border-color 0.15s; background: #fff; }
.bs-input:focus { border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,0.1); }
.bs-type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.bs-type-opt  { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 10px 6px; border: 2px solid #e2e8f0; border-radius: 10px; background: #fff; cursor: pointer; transition: all 0.15s; text-align: center; }
.bs-type-opt:hover  { border-color: #a5b4fc; background: #f5f3ff; }
.bs-type-opt.active { border-color: #6366f1; background: #eef2ff; }
.bs-topt-icon { font-size: 22px; }
.bs-topt-name { font-size: 12px; font-weight: 700; color: #0f172a; }
.bs-topt-desc { font-size: 10.5px; color: #94a3b8; }
.bs-sched-tabs { display: flex; gap: 4px; margin-bottom: 10px; }
.bs-stab       { padding: 5px 14px; border: 1px solid #e2e8f0; border-radius: 6px; background: #fff; font-size: 12.5px; color: #64748b; cursor: pointer; transition: all 0.15s; }
.bs-stab.active { background: #0f172a; color: #fff; border-color: #0f172a; }
.bs-preset-builder { display: flex; flex-direction: column; gap: 10px; }
.bs-select    { border: 1px solid #e2e8f0; border-radius: 7px; padding: 7px 10px; font-size: 13px; outline: none; background: #fff; color: #1e293b; cursor: pointer; }
.bs-select.sm { width: auto; }
.bs-preset-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.bs-prow-lbl   { font-size: 13px; color: #475569; }
.bs-prow-unit  { font-size: 13px; color: #94a3b8; }
.bs-time-input { border: 1px solid #e2e8f0; border-radius: 7px; padding: 6px 10px; font-size: 13px; outline: none; background: #fff; }
.bs-cron-builder { display: flex; flex-direction: column; gap: 6px; }
.bs-cron-input   { font-family: monospace; font-size: 14px; }
.bs-cron-hint    { display: flex; gap: 8px; }
.bs-cron-hint span { font-size: 10.5px; color: #94a3b8; background: #f1f5f9; padding: 1px 6px; border-radius: 3px; font-family: monospace; }
.bs-preview-box  { display: flex; align-items: center; gap: 8px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px; flex-wrap: wrap; }
.bs-preview-lbl  { font-size: 12px; color: #166534; }
.bs-preview-val  { font-size: 13px; color: #14532d; }
.bs-preview-code { font-size: 11px; background: #dcfce7; color: #166534; padding: 1px 6px; border-radius: 4px; font-family: monospace; }
.bs-toggle-row   { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; }
.bs-toggle-lbl   { font-size: 13px; color: #374151; font-weight: 500; }
.bs-btn-ghost   { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 18px; font-size: 13px; color: #475569; cursor: pointer; transition: all 0.15s; }
.bs-btn-ghost:hover { background: #f1f5f9; }
.bs-btn-primary { background: #6366f1; color: #fff; border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; display: flex; align-items: center; gap: 6px; }
.bs-btn-primary:hover:not(:disabled) { background: #4f46e5; }
.bs-btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
.bs-btn-danger  { background: #dc2626; color: #fff; border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.bs-btn-danger:hover { background: #b91c1c; }
.bs-btn-warning { background: #d97706; color: #fff; border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.bs-btn-warning:hover { background: #b45309; }

/* ── Timezone bar ── */
.bs-tz-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f0f4ff;
  border: 1px solid #c7d2fe;
  border-radius: 8px;
  padding: 7px 14px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  color: #3730a3;
  font-size: 12px;
}
.bs-tz-label {
  font-weight: 600;
  white-space: nowrap;
}
.bs-tz-select {
  border: 1px solid #a5b4fc;
  border-radius: 6px;
  background: #fff;
  color: #1e1b4b;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  cursor: pointer;
  outline: none;
}
.bs-tz-select:focus { border-color: #6366f1; }
.bs-tz-saving { color: #6366f1; font-style: italic; }
.bs-tz-ok { color: #16a34a; font-weight: 700; }
.bs-tz-hint { color: #6b7280; font-size: 11px; margin-left: auto; }
</style>
