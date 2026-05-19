<template>
  <div class="monitor-page">
    <transition name="analysis-overlay">
      <div v-if="loading" class="analysis-overlay">
        <div class="analysis-overlay-card">
          <span class="analysis-overlay-title">{{ loadingTitle }}</span>
          <strong>{{ loadingMessage }}</strong>
          <v-progress-linear
            indeterminate
            color="white"
            bg-color="rgba(255,255,255,0.18)"
            class="analysis-overlay-progress"
          ></v-progress-linear>
        </div>
      </div>
    </transition>

    <section
      v-if="primaryAlert"
      :class="['hero-alert', `hero-alert-${primaryAlert.severity}`]"
    >
      <div class="hero-alert-main">
        <div class="hero-alert-icon">
          <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
            <path d="M10 2L2 17h16L10 2z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M10 8v4M10 14.5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="hero-alert-copy">
          <strong>{{ alertTitle(primaryAlert) }}</strong>
          <span>{{ primaryAlert.cause }}</span>
        </div>
      </div>

      <div class="hero-alert-actions">
        <span v-if="primaryAlert.severity === 'critical'" class="hero-badge">
          Critique
        </span>
        <button
          v-if="primaryAlert.action === 'restart_service'"
          class="hero-btn hero-btn-primary"
          type="button"
          :disabled="loading"
          @click="triggerAlertAction(primaryAlert)"
        >
          Redémarrer
        </button>
        <button
          v-else-if="primaryAlert.action"
          class="hero-btn hero-btn-primary"
          type="button"
          :disabled="loading"
          @click="triggerAlertAction(primaryAlert)"
        >
          {{ primaryAlert.action_label || "Voir le détail" }}
        </button>
        <button
          class="hero-btn hero-btn-light"
          type="button"
          @click="ignoreAlert(primaryAlert)"
        >
          Ignorer pour l'instant
        </button>
      </div>
    </section>

    <!-- ======= FIREWALL OPERATIONAL STRIP ======= -->
    <div class="fw-ops-strip">
      <div class="fw-ops-strip-label">
        <span class="fw-ops-live-dot"></span>
        Statut opérationnel
      </div>
      <div class="fw-ops-zones">
        <div
          v-for="zone in firewallZones"
          :key="zone.key"
          :class="['fw-ops-zone', zone.running === null ? 'unknown' : zone.running ? 'up' : 'down']"
          :title="zone.running === null ? 'Service non détecté' : zone.running ? `${zone.label} actif` : `${zone.label} arrêté`"
        >
          <span class="fw-ops-zone-icon">{{ zone.icon }}</span>
          <span class="fw-ops-zone-label">{{ zone.label }}</span>
          <span :class="['fw-ops-zone-dot', zone.running === null ? 'unknown' : zone.running ? 'up' : 'down']"></span>
        </div>
      </div>
      <div class="fw-ops-strip-right">
        <span class="fw-ops-cpu">CPU {{ liveMetrics.cpu }}%</span>
        <span class="fw-ops-ram">RAM {{ liveMetrics.memory }}%</span>
        <span v-if="liveMetrics.uptime" class="fw-ops-uptime">↑ {{ uptimeReadableTitle }}</span>
      </div>
    </div>

    <nav class="monitor-tabs" aria-label="Navigation monitoring backup">
      <button
        :class="['monitor-tab', { active: activeMonitoringTab === 'overview' }]"
        type="button"
        @click="setMonitoringTab('overview')"
      >
        <span>Vue d'ensemble</span>
        <small>Etat, risques, actions</small>
      </button>
      <button
        :class="['monitor-tab', { active: activeMonitoringTab === 'analytics' }]"
        type="button"
        @click="setMonitoringTab('analytics')"
      >
        <span>Analytics Lab</span>
        <small>Charts, tendances, signaux</small>
      </button>
    </nav>

    <template v-if="activeMonitoringTab === 'overview'">
    <!-- ======= DRP METRICS STRIP — visible observability layer ======= -->
    <section class="drp-live-strip" :class="`drp-live-strip--${drpGlobalTone}`">
      <div class="drp-live-head">
        <div class="drp-live-title">
          <span class="drp-live-dot"></span>
          <div>
            <strong>DRP Metrics</strong>
            <small>RPO, restores, stockage et services critiques</small>
          </div>
        </div>
        <div class="drp-live-actions">
          <span class="drp-live-updated">{{ drpMetrics ? `MAJ ${formatTime(drpMetrics.generated_at)}` : 'chargement...' }}</span>
          <button class="drp-live-btn" type="button" :disabled="loading" @click="fetchDrpMetrics">
            Rafraîchir
          </button>
        </div>
      </div>
      <div class="drp-metric-grid">
        <article
          v-for="card in drpMetricCards"
          :key="card.key"
          :class="['drp-metric-card', `tone-${card.tone}`]"
        >
          <span class="drp-metric-label">{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <small>{{ card.hint }}</small>
          <div class="drp-metric-bar">
            <span :style="{ width: `${card.bar}%` }"></span>
          </div>
        </article>
      </div>
    </section>

    <!-- ======= PRIORITY COCKPIT ======= -->
    <section class="cockpit">
      <!-- P1 · ÉTAT MACHINE -->
      <article :class="['cockpit-col', 'cockpit-col--machine', `cockpit-col--tone-${cockpitMachineTone}`]">
        <header class="cockpit-head">
          <span class="cockpit-eyebrow">
            <span class="cockpit-rank">P1</span>
            État machine
          </span>
          <span class="cockpit-live"><span class="cockpit-live-dot"></span>live</span>
        </header>
        <strong :class="['cockpit-headline', `tone-${cockpitMachineTone}`]">{{ machineHealthLabel }}</strong>
        <span class="cockpit-sub">{{ vmStatusTitle }}</span>
        <a
          v-if="aiAnalysis.scores && aiAnalysis.scores.smoothed !== undefined"
          href="/backup"
          @click="openAiRiskCenter"
          :class="['ai-verdict-pill', `ai-verdict-${aiAnalysis.scores.level || 'stable'}`]"
          :title="`IA: ${aiAnalysis.explanation || ''} — cliquer pour ouvrir l'AI Risk Center`"
        >
          <span class="ai-verdict-dot"></span>
          <span class="ai-verdict-text">IA · {{ aiVerdictLabel }}</span>
          <strong class="ai-verdict-score">{{ aiAnalysis.scores.smoothed }}/100</strong>
        </a>
        <div class="cockpit-meters">
          <div class="cm-row">
            <span class="cm-lbl">CPU</span>
            <div class="cm-bar"><div :class="['cm-fill', meterTone(liveMetrics.cpu)]" :style="{ width: `${Math.min(100, liveMetrics.cpu)}%` }"></div></div>
            <strong class="cm-val">{{ liveMetrics.cpu }}%</strong>
          </div>
          <div class="cm-row">
            <span class="cm-lbl">RAM</span>
            <div class="cm-bar"><div :class="['cm-fill', meterTone(liveMetrics.memory)]" :style="{ width: `${Math.min(100, liveMetrics.memory)}%` }"></div></div>
            <strong class="cm-val">{{ liveMetrics.memory }}%</strong>
          </div>
          <div class="cm-row">
            <span class="cm-lbl">Disk /</span>
            <div class="cm-bar"><div :class="['cm-fill', meterTone(diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes))]" :style="{ width: `${diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes)}%` }"></div></div>
            <strong class="cm-val">{{ diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes) }}%</strong>
          </div>
        </div>
        <footer class="cockpit-foot">
          <span class="cf-pill"><span class="cf-pill-ico">↑</span>{{ uptimeReadableTitle }}</span>
          <span class="cf-pill">{{ loadAverageReadableTitle }}</span>
        </footer>
      </article>

      <!-- P2 · SAUVEGARDE -->
      <article :class="['cockpit-col', 'cockpit-col--backup', `cockpit-col--tone-${statusMetricClass(latestBackup.status)}`]">
        <header class="cockpit-head">
          <span class="cockpit-eyebrow">
            <span class="cockpit-rank">P2</span>
            Sauvegarde
          </span>
          <span :class="['cockpit-score', statusMetricClass(latestBackup.status)]">
            {{ latestBackup.health_score ?? 0 }}<small>/100</small>
          </span>
        </header>
        <strong :class="['cockpit-headline', `tone-${statusMetricClass(latestBackup.status)}`]">
          {{ statusMetricLabel(latestBackup.status) }}
        </strong>
        <span class="cockpit-sub">{{ formatDate(latestBackup.timestamp) || 'Aucun backup' }}</span>
        <div class="cockpit-mini-grid">
          <div class="cmg-cell">
            <span>Archives</span>
            <strong>{{ storageSummary.count || 0 }}</strong>
          </div>
          <div class="cmg-cell">
            <span>Stockage</span>
            <strong>{{ formatSize(storageSummary.used_bytes) }}</strong>
          </div>
          <div class="cmg-cell">
            <span>RPO</span>
            <strong :class="rpoToneClass">{{ rpoLabel }}</strong>
          </div>
          <div class="cmg-cell">
            <span>Services</span>
            <strong :class="serviceSummary.failing > 0 ? 'tone-warning' : 'tone-ok'">
              {{ serviceSummary.running }}/{{ serviceSummary.total }}
            </strong>
          </div>
        </div>
        <footer class="cockpit-foot">
          <div class="cf-bar">
            <div :class="['cf-bar-fill', statusMetricClass(latestBackup.status)]" :style="{ width: `${latestBackup.health_score ?? 0}%` }"></div>
          </div>
        </footer>
      </article>

      <!-- P3 · DERNIER RESTORE -->
      <article :class="['cockpit-col', 'cockpit-col--restore', lastRestore ? `cockpit-col--tone-${lastRestore.status === 'success' ? 'ok' : 'warning'}` : 'cockpit-col--tone-neutral']">
        <header class="cockpit-head">
          <span class="cockpit-eyebrow">
            <span class="cockpit-rank">P3</span>
            Dernier restore
          </span>
          <span v-if="lastRestore" :class="['cockpit-pill', `mode-${lastRestore.mode}`]">{{ lastRestoreModeLabel }}</span>
          <span v-else class="cockpit-pill muted">aucun</span>
        </header>
        <template v-if="lastRestore">
          <strong class="cockpit-headline tone-neutral">{{ formatDate(lastRestore.started_at) }}</strong>
          <span class="cockpit-sub">{{ lastRestoreAgo }} · durée {{ lastRestoreDurationLabel }}</span>
          <div class="cockpit-mini-grid">
            <div class="cmg-cell">
              <span>Composants</span>
              <strong>{{ lastRestore.summary?.success ?? 0 }}</strong>
            </div>
            <div class="cmg-cell">
              <span>Statut</span>
              <strong :class="lastRestore.status === 'success' ? 'tone-ok' : 'tone-warning'">
                {{ lastRestore.status === 'success' ? 'Vérifié' : lastRestore.status === 'partial_success' ? 'Partiel' : lastRestore.status }}
              </strong>
            </div>
            <div class="cmg-cell">
              <span>Mode</span>
              <strong>{{ lastRestoreModeLabel }}</strong>
            </div>
          </div>
        </template>
        <template v-else>
          <strong class="cockpit-headline muted">—</strong>
          <span class="cockpit-sub">Aucun restore enregistré sur cette plateforme.</span>
          <div class="cockpit-empty-hint">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M13 8A5 5 0 1 1 8 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M13 3v5h-5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Utiliser l'onglet Backups pour lancer un test.
          </div>
        </template>
      </article>

      <!-- P4 · AUTOMATISATION -->
      <article :class="['cockpit-col', 'cockpit-col--auto', scheduledTasks.length ? 'cockpit-col--tone-info' : 'cockpit-col--tone-warning']">
        <header class="cockpit-head">
          <span class="cockpit-eyebrow">
            <span class="cockpit-rank">P4</span>
            Automatisation
          </span>
          <span v-if="scheduledTasks.length" class="cockpit-pill ok">
            {{ enabledTaskCount }} active{{ enabledTaskCount > 1 ? 's' : '' }}
          </span>
          <span v-else class="cockpit-pill warning">off</span>
        </header>

        <template v-if="nextTaskInfo">
          <div class="cockpit-countdown">
            <div class="cc-block">
              <strong>{{ countdown.h.toString().padStart(2,'0') }}</strong>
              <span>h</span>
            </div>
            <span class="cc-sep">:</span>
            <div class="cc-block">
              <strong>{{ countdown.m.toString().padStart(2,'0') }}</strong>
              <span>min</span>
            </div>
            <span class="cc-sep cc-sep-sm">:</span>
            <div class="cc-block cc-block-sec">
              <strong>{{ countdown.s.toString().padStart(2,'0') }}</strong>
              <span>s</span>
            </div>
          </div>
          <span class="cockpit-sub">
            <span :class="['auto-typedot', nextTaskInfo.type]"></span>
            {{ nextTaskInfo.label }} · {{ cronHumanShort(nextTaskInfo.cron) }}
          </span>
          <footer class="cockpit-foot cockpit-foot--split">
            <span class="cf-pill">{{ nextTaskInfo.nextRunFormatted }}</span>
            <button class="cockpit-cfg-btn" type="button" @click="goToScheduleTab">⚙ Configurer</button>
          </footer>
        </template>
        <template v-else-if="scheduledTasks.length">
          <strong class="cockpit-headline tone-warning">En pause</strong>
          <span class="cockpit-sub">Aucune exécution planifiée à venir.</span>
          <footer class="cockpit-foot cockpit-foot--split">
            <span class="cf-pill">{{ enabledTaskCount }} sur {{ scheduledTasks.length }} active{{ enabledTaskCount > 1 ? 's' : '' }}</span>
            <button class="cockpit-cfg-btn primary" type="button" @click="goToScheduleTab">⚙ Configurer</button>
          </footer>
        </template>
        <template v-else>
          <strong class="cockpit-headline tone-warning">Non configurée</strong>
          <span class="cockpit-sub">Les backups ne se déclenchent pas automatiquement.</span>
          <footer class="cockpit-foot cockpit-foot--split">
            <button class="cockpit-cfg-btn primary cockpit-cfg-btn--full" type="button" @click="goToScheduleTab">⚙ Configurer l'automatisation</button>
          </footer>
        </template>
      </article>
    </section>

    <!-- ======= AUTOMATION NOTICE (kept inline, condensed) ======= -->
    <div
      v-if="automationNotice"
      :class="['auto-notice-strip', `auto-notice-strip--${automationNotice.tone}`]"
    >
      <span class="auto-notice-strip-dot"></span>
      <div class="auto-notice-strip-copy">
        <strong>{{ automationNotice.title }}</strong>
        <span>{{ automationNotice.message }}</span>
      </div>
      <span class="auto-notice-strip-time">{{ automationNotice.timeLabel }}</span>
      <button type="button" class="auto-notice-strip-ok" @click="dismissAutomationNotice(automationNotice.key)">OK</button>
    </div>

    <!-- ======= SCHEDULED TASKS — compact strip ======= -->
    <div v-if="scheduledTasks.length" class="task-strip">
      <div class="task-strip-head">
        <span class="task-strip-title">Tâches planifiées</span>
        <span class="task-strip-count">{{ scheduledTasks.length }} défini{{ scheduledTasks.length > 1 ? 's' : '' }} · {{ enabledTaskCount }} actif{{ enabledTaskCount > 1 ? 's' : '' }}</span>
      </div>
      <div class="task-strip-list">
        <div
          v-for="task in allTasksWithNextRun"
          :key="task.id"
          :class="['task-chip', { 'task-chip--off': !task.enabled }]"
        >
          <span :class="['auto-typedot', task.type]"></span>
          <span class="task-chip-name">{{ task.label }}</span>
          <span class="task-chip-freq">{{ cronHumanShort(task.cron) }}</span>
          <span v-if="task.nextRun" class="task-chip-eta">
            <span class="task-chip-eta-lbl">dans</span>
            <strong>{{ timeUntil(task.nextRun) }}</strong>
          </span>
          <span v-else class="task-chip-eta muted">en pause</span>
          <span
            v-if="taskRunBadge(task)"
            :class="['task-chip-badge', `task-chip-badge--${taskRunBadge(task).tone}`]"
          >{{ taskRunBadge(task).label }}</span>
          <span :class="['task-chip-status', task.enabled ? 'on' : 'off']"></span>
        </div>
      </div>
    </div>
    <!-- ======= END PRIORITY COCKPIT ======= -->


    <!-- ======= ALERTS PRIORITY STRIP (visible dès le haut) ======= -->
    <div v-if="visibleAlerts.length > 0" class="alert-priority-strip">
      <div class="alert-priority-strip-head">
        <div class="alert-priority-icon">
          <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 2L2 14h12L8 2z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 7v3M8 11.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
        </div>
        <strong>{{ visibleAlerts.length }} alerte{{ visibleAlerts.length > 1 ? 's' : '' }} active{{ visibleAlerts.length > 1 ? 's' : '' }}</strong>
        <span>— action requise</span>
      </div>
      <div class="alert-priority-list">
        <div
          v-for="alert in visibleAlerts.slice(0, 4)"
          :key="alertKey(alert)"
          :class="['alert-priority-item', alert.severity]"
        >
          <span :class="['alert-priority-dot', alert.severity]"></span>
          <div class="alert-priority-body">
            <strong>{{ alert.service }}</strong>
            <span>{{ alert.message }}</span>
          </div>
          <span :class="['alert-priority-badge', alert.severity]">
            {{ alert.severity === 'critical' ? 'Critique' : 'Attention' }}
          </span>
          <button
            v-if="alert.action"
            class="alert-priority-btn"
            type="button"
            @click="triggerAlertAction(alert)"
          >{{ alert.action_label || 'Voir' }}</button>
          <button class="alert-priority-dismiss" type="button" @click="ignoreAlert(alert)">✕</button>
        </div>
        <div v-if="visibleAlerts.length > 4" class="alert-priority-more">
          + {{ visibleAlerts.length - 4 }} autre{{ visibleAlerts.length - 4 > 1 ? 's' : '' }} — voir le tableau complet ci-dessous
        </div>
      </div>
    </div>

    <section class="insight-grid">
      <article class="insight-hero-card">
        <!-- Score banner -->
        <div :class="['insight-score-banner', protectionScoreClass]">
          <div class="insight-score-banner-left">
            <div class="insight-score-number-wrap">
              <span :class="['insight-score-big', protectionScoreClass]">{{ insights.protection_score ?? 0 }}</span>
              <span class="insight-score-of">/100</span>
            </div>
            <div class="insight-score-copy">
              <strong>{{ protectionScoreText }}</strong>
              <span>Score de protection global</span>
            </div>
          </div>
          <div class="insight-score-gauge">
            <div class="insight-score-gauge-track">
              <div
                :class="['insight-score-gauge-fill', protectionScoreClass]"
                :style="{ width: `${insights.protection_score ?? 0}%` }"
              ></div>
              <div class="insight-score-gauge-marker" style="left:60%"><span>60</span></div>
              <div class="insight-score-gauge-marker" style="left:85%"><span>85</span></div>
            </div>
            <div class="insight-score-gauge-labels">
              <span class="gauge-label-bad">Faible</span>
              <span class="gauge-label-mid">Moyen</span>
              <span class="gauge-label-good">Bon</span>
            </div>
          </div>
        </div>

        <!-- Breakdown list -->
        <div class="insight-breakdown-list">
          <div
            v-for="item in scoreBreakdown"
            :key="item.key"
            class="insight-breakdown-row"
          >
            <div :class="['insight-breakdown-row-icon', scoreItemClass(item.value)]">
              <svg v-if="item.key === 'backup_health' || item.key === 'backup'" viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 1L2 3.5v4.5C2 11.6 4.7 14.8 8 16c3.3-1.2 6-4.4 6-8V3.5L8 1z" stroke="currentColor" stroke-width="1.2"/></svg>
              <svg v-else-if="item.key === 'sync' || item.key === 'synchronisation'" viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M13 8A5 5 0 1 1 8 3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M13 3v5h-5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <svg v-else-if="item.key === 'services'" viewBox="0 0 16 16" fill="none" width="14" height="14"><rect x="1.5" y="2.5" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M5 8h6M8 5.5v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              <svg v-else viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 4.5V8.5l2.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            </div>
            <div class="insight-breakdown-row-body">
              <div class="insight-breakdown-row-top">
                <span class="insight-breakdown-row-label">{{ scoreItemFriendlyLabel(item) }}</span>
                <span :class="['insight-breakdown-row-score', scoreItemClass(item.value)]">
                  {{ item.value }}/100
                </span>
              </div>
              <div class="insight-breakdown-bar">
                <div
                  :class="['insight-breakdown-fill', scoreItemClass(item.value)]"
                  :style="{ width: `${item.value}%` }"
                ></div>
              </div>
              <small class="insight-breakdown-row-hint">{{ scoreItemHint(item) }}</small>
            </div>
            <div class="insight-breakdown-row-weight">
              <span>{{ item.weight_percent }}%</span>
              <small>du score</small>
            </div>
          </div>
        </div>

        <div class="insight-footer-row">
          <div class="insight-footer-note">
            <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="12" height="12" rx="3" stroke="currentColor" stroke-width="1.2"/><path d="M5 8h6M8 5v6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            <span>Périmètre :</span>
            <strong>{{ insights.score_scope_label || syncSummary.scope_label || "-" }}</strong>
          </div>
          <div class="insight-footer-note">
            <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="2.5" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M5 8h6M8 5.5v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            <span>Services :</span>
            <strong>{{ serviceHealthReadable }}</strong>
          </div>
        </div>
      </article>

      <article :class="['metric-card', 'smart-card', 'freshness-card', freshnessToneClass]">
        <div class="smart-card-topline">
          <div class="smart-card-topline-left">
            <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 4.5V8.5l2.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            <span>Fraîcheur des backups</span>
          </div>
          <span :class="['smart-pill', freshnessToneClass]">{{ freshnessPill }}</span>
        </div>
        <strong :class="freshnessClass">{{ freshnessHeadline }}</strong>
        <small>{{ freshnessSubline }}</small>
        <div class="freshness-rail">
          <div
            v-for="stage in freshnessStages"
            :key="stage.key"
            :class="['freshness-stage', {
              active: stage.key === activeFreshnessStage,
              passed: stage.order < activeFreshnessStageOrder,
            }]"
          >
            <strong>{{ stage.label }}</strong>
            <span>{{ stage.range }}</span>
          </div>
        </div>
        <div class="smart-meter">
          <div class="smart-meter-track">
            <div class="smart-meter-fill" :style="{ width: `${freshnessMeterValue}%` }"></div>
          </div>
          <span>{{ insights.freshness_score ?? 0 }}/100</span>
        </div>
        <p class="smart-copy">{{ freshnessNarrative }}</p>
      </article>

      <article :class="['metric-card', 'smart-card', 'restore-card', restoreReadinessClass]">
        <div class="smart-card-topline">
          <div class="smart-card-topline-left">
            <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><path d="M13 8A5 5 0 1 1 8 3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M13 3v5h-5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>Peut-on restaurer ?</span>
          </div>
          <span :class="['smart-pill', restoreReadinessClass]">{{ restoreReadinessPill }}</span>
        </div>
        <strong :class="restoreReadinessClass">{{ restoreReadinessLabel }}</strong>
        <small>{{ restoreReadinessSubline }}</small>
        <p class="smart-copy">{{ insights.restore_reason || `${insights.active_alerts ?? 0} alertes actives` }}</p>
        <div v-if="restoreImpactItems.length" class="smart-detail-list">
          <div
            v-for="item in restoreImpactItems"
            :key="`${item.name}-${item.message}`"
            :class="['smart-detail-item', item.tone]"
          >
            <strong>{{ item.name }}</strong>
            <span>{{ item.message }}</span>
          </div>
        </div>
      </article>

      <article class="metric-card smart-card recommendation-card">
        <div class="recommendation-card-topline">
          <div class="recommendation-card-icon">
            <svg viewBox="0 0 20 20" fill="none" width="20" height="20"><path d="M10 2l2 6h6l-5 3.5 2 6L10 14l-5 3.5 2-6L2 8h6L10 2z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
          </div>
          <span class="recommendation-card-label">Ce qu'on vous conseille</span>
        </div>
        <div class="recommendation-list">
          <div
            v-for="(rec, idx) in allRecommendations"
            :key="idx"
            :class="['recommendation-item', idx === 0 ? 'recommendation-item--primary' : 'recommendation-item--secondary']"
          >
            <span class="recommendation-rank">{{ idx + 1 }}</span>
            <p class="recommendation-text">{{ rec }}</p>
          </div>
        </div>
        <div class="recommendation-footer">
          <span>Basé sur le backup, la cohérence et les services</span>
          <span v-if="lastRefreshedLabel" class="recommendation-refresh-label">· {{ lastRefreshedLabel }}</span>
        </div>
      </article>
    </section>

    <section class="guide-grid">
      <article class="guide-card">
        <div class="guide-step-icon">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M10 2L3 5v5c0 4.1 3 7.9 7 9 4-1.1 7-4.9 7-9V5l-7-3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
          <span class="guide-step">1</span>
        </div>
        <div>
          <strong>Sauvegarde</strong>
          <p>Votre archive est-elle saine et complète ?</p>
        </div>
      </article>
      <article class="guide-card">
        <div class="guide-step-icon">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M3 10h14M10 3l7 7-7 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span class="guide-step">2</span>
        </div>
        <div>
          <strong>Cohérence</strong>
          <p>Le système correspond-il à la base de données ?</p>
        </div>
      </article>
      <article class="guide-card">
        <div class="guide-step-icon">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M3 15l4-6 4 3 4-8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span class="guide-step">3</span>
        </div>
        <div>
          <strong>Tendance</strong>
          <p>CPU, RAM, backups et dérives dans le temps.</p>
        </div>
      </article>
    </section>
    </template>
    <section class="integrity-card">
      <div class="section-head">
        <div class="section-head-title-group">
          <div class="section-icon section-icon--blue">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M10 2L3 5v5c0 4.1 3 7.9 7 9 4-1.1 7-4.9 7-9V5l-7-3z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M7 10l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div>
            <h3>Intégrité de la sauvegarde</h3>
            <p>Votre dernière sauvegarde est-elle complète et récupérable ?</p>
          </div>
        </div>
        <span :class="['state-pill', integrityClass]">
          {{ integrityLabel }}
        </span>
      </div>

      <div class="integrity-explainer">
        <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3.5L10 10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        On vérifie que tous les éléments importants sont présents dans l'archive et peuvent être restaurés si nécessaire.
      </div>

      <div class="integrity-flow">
        <div class="flow-node">
          <span class="flow-dot flow-dot-system"></span>
          <strong>Votre système</strong>
          <small>au moment du backup</small>
        </div>
        <div class="flow-arrow-wrap">
          <div class="flow-arrow-line"></div>
          <span class="flow-arrow-label">vérifié</span>
        </div>
        <div class="flow-node">
          <span class="flow-dot flow-dot-backup"></span>
          <strong>Archive sauvegardée</strong>
          <small>stockée et contrôlée</small>
        </div>
      </div>

      <div class="integrity-metrics">
        <div class="integrity-box">
          <div class="integrity-box-icon">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 4.5V8.5l2.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </div>
          <span>Dernière vérification</span>
          <strong>{{ formatDate(overview.integrity?.last_check_at) }}</strong>
        </div>
        <div class="integrity-box">
          <div class="integrity-box-icon integrity-box-icon--blue">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 2l1.5 3 3.5.5-2.5 2.5.5 3.5L8 10l-3 1.5.5-3.5L3 5.5 6.5 5 8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
          </div>
          <span>Score de santé moyen</span>
          <strong>{{ overview.integrity?.average_health ?? 0 }}/100</strong>
        </div>
        <div class="integrity-box integrity-box-coverage">
          <div class="integrity-box-icon integrity-box-icon--green">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 1L2 3.5v4.5C2 11.6 4.7 14.8 8 16c3.3-1.2 6-4.4 6-8V3.5L8 1z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
          </div>
          <span>Éléments couverts</span>
          <strong>{{ criticalCoverageLabel }}</strong>
          <small>{{ criticalCoverageText }}</small>
        </div>
        <div class="integrity-box" :title="integrityDriftTooltip">
          <div :class="['integrity-box-icon', ((overview.integrity?.components_failed ?? 0) + (overview.integrity?.components_skipped ?? 0)) > 0 ? 'integrity-box-icon--orange' : 'integrity-box-icon--green']">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3M8 10.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          </div>
          <span>Points à vérifier</span>
          <strong>
            {{ (overview.integrity?.components_failed ?? 0) + (overview.integrity?.components_skipped ?? 0) }}
          </strong>
          <small>{{ integrityIssueShortText }}</small>
        </div>
      </div>

      <div v-if="criticalCoverageItems.length" class="coverage-detail-panel">
        <div class="issue-list-title">
          <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><path d="M8 1L2 3.5v4.5C2 11.6 4.7 14.8 8 16c3.3-1.2 6-4.4 6-8V3.5L8 1z" stroke="currentColor" stroke-width="1.2"/></svg>
          Ce qui est inclus dans cette sauvegarde
        </div>
        <div class="coverage-chip-list">
          <div
            v-for="item in criticalCoverageItems"
            :key="item.key"
            :class="['coverage-chip', item.status === 'success' ? 'ok' : item.status === 'skipped' ? 'skipped' : 'failed']"
          >
            <span class="coverage-chip-dot"></span>
            <strong>{{ item.label }}</strong>
            <span>{{ integrityStatusLabel(item.status) }}</span>
          </div>
        </div>
      </div>

      <div v-if="integrityIssues.length > 0" class="issue-list issue-list-detailed">
        <div class="issue-list-title">
          <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><path d="M8 2L2 14h12L8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M8 7v3M8 11.5v.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          Points qui nécessitent votre attention
        </div>
        <div class="issue-card-grid">
          <article
            v-for="issue in integrityIssues"
            :key="`${issue.component}-${issue.status}`"
            :class="['issue-card', issue.status]"
          >
            <div class="issue-card-head">
              <div class="issue-card-head-left">
                <span :class="['issue-status-icon', issue.status === 'failed' ? 'error' : 'warn']">
                  <svg v-if="issue.status === 'failed'" viewBox="0 0 12 12" fill="none" width="12" height="12"><circle cx="6" cy="6" r="5.5" stroke="currentColor" stroke-width="1.1"/><path d="M6 3.5v3M6 8v.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
                  <svg v-else viewBox="0 0 12 12" fill="none" width="12" height="12"><path d="M6 1l-5 9h10L6 1z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><path d="M6 5v2M6 8.5v.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
                </span>
                <strong>{{ issue.label || issue.component }}</strong>
              </div>
              <span :class="['issue-badge', issue.status === 'failed' ? 'error' : 'skipped']">
                {{ issue.status === "failed" ? "Problème détecté" : "Non vérifié" }}
              </span>
            </div>
            <p>{{ issue.message }}</p>
            <small>{{ issue.impact }}</small>
            <div v-if="issue.restore_support === 'manual_only'" class="issue-card-badge">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M6 1v6M6 9v.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              Restauration manuelle requise
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="integrity-card">
      <div class="section-head">
        <div class="section-head-title-group">
          <div class="section-icon section-icon--purple">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M3 10h14M10 3l7 7-7 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div>
            <h3>Cohérence système / base</h3>
            <p>Dernier contrôle entre l'état réel du système et ce qui est enregistré.</p>
          </div>
        </div>
        <div class="section-head-actions">
          <span :class="['state-pill', syncClass]">
            {{ syncLabel }}
          </span>
          <span v-if="lastRefreshedLabel" class="last-refreshed-label">{{ lastRefreshedLabel }}</span>
          <button class="hero-btn hero-btn-light" type="button" :disabled="loading" @click="refreshDashboardAnalysis">
            <svg viewBox="0 0 14 14" fill="none" width="13" height="13" style="margin-right:4px;vertical-align:middle"><path d="M12 7A5 5 0 1 1 7 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M12 2v5h-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Relancer l'analyse
          </button>
        </div>
      </div>

      <!-- Compact scope summary + collapsible expert pilot -->
      <div class="sync-pilot-summary">
        <div class="sps-left">
          <div class="sps-eyebrow">SCOPE COURANT</div>
          <strong class="sps-title">{{ syncSummary.scope_label || "Périmètre par défaut" }}</strong>
          <span class="sps-sub">{{ syncSelectedCount }}/{{ availableSyncComponents.length }} modules · couverture {{ syncCoveragePercent }}%</span>
        </div>
        <div class="sps-presets">
          <button
            v-for="preset in syncPresets"
            :key="preset.key"
            :class="['sps-preset', { active: activeSyncPreset === preset.key }]"
            type="button"
            :title="preset.description"
            @click="applySyncPreset(preset)"
          >{{ preset.label }}</button>
        </div>
        <div class="sps-actions">
          <button
            type="button"
            class="sps-toggle"
            :aria-expanded="syncPilotExpanded ? 'true' : 'false'"
            @click="syncPilotExpanded = !syncPilotExpanded"
          >
            <svg viewBox="0 0 12 12" width="11" height="11" fill="none" :style="{ transform: syncPilotExpanded ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform .2s' }"><path d="M3 4.5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ syncPilotExpanded ? "Réduire" : "Personnaliser" }}
          </button>
          <button class="hero-btn hero-btn-primary sps-analyze" type="button" :disabled="loading" @click="refreshDashboardAnalysis">
            Analyser
          </button>
        </div>
      </div>

      <div v-show="syncPilotExpanded" class="sync-orbit">
          <div class="sync-pilot-card">
            <div class="sync-pilot-head">
              <div>
                <span class="section-kicker">Pilotage intelligent</span>
              <strong>Choisis ce que tu veux contrôler.</strong>
              <p>Le bouton d'analyse compare ensuite le système réel avec la base.</p>
              </div>

            <div class="sync-pilot-stats">
              <div>
                <span>Selection preparee</span>
                <strong>{{ syncSelectedCount }}/{{ availableSyncComponents.length }}</strong>
              </div>
              <div>
                <span>Couverture</span>
                <strong>{{ syncCoveragePercent }}%</strong>
              </div>
            </div>
          </div>

          <div class="sync-preset-row">
            <button
              v-for="preset in syncPresets"
              :key="preset.key"
              :class="['sync-preset-btn', { active: activeSyncPreset === preset.key }]"
              type="button"
              @click="applySyncPreset(preset)"
            >
              <span class="action-hint">Choisir</span>
              <strong>{{ preset.label }}</strong>
              <small>{{ preset.description }}</small>
            </button>
          </div>

          <div class="sync-scope-banner">
            <strong>Scope IT utile</strong>
            <span>Acces, protection, connectivite, tunnels, publication.</span>
          </div>

          <div class="sync-component-grid">
            <button
              v-for="component in availableSyncComponents"
              :key="component.key"
              :class="['sync-component-card', { active: isSyncComponentSelected(component.key) }]"
              type="button"
              @click="handleSyncComponentCardClick(component.key)"
            >
              <span class="sync-component-badge">{{ component.short }}</span>
              <span class="sync-component-copy">
                <strong>{{ component.label }}</strong>
                <small>{{ component.description }}</small>
              </span>
              <span class="sync-component-side">
                <span class="sync-component-state">
                  {{ isSyncComponentSelected(component.key) ? "inclus" : "pause" }}
                </span>
                <span class="action-hint">
                  {{ isSyncComponentSelected(component.key) ? "Retirer" : "Ajouter" }}
                </span>
              </span>
            </button>
          </div>

          <div class="sync-toolbar">
            <div class="sync-toolbar-group">
              <button
                :class="['sync-filter-btn', { active: syncViewMode === 'all' }]"
                type="button"
                @click="setSyncViewMode('all', { scrollToResults: true })"
              >
                Vue
              </button>
              <button
                :class="['sync-filter-btn', { active: syncViewMode === 'drift' }]"
                type="button"
                @click="setSyncViewMode('drift', { scrollToResults: true, focusFirst: true })"
              >
                A corriger
              </button>
              <button
                :class="['sync-filter-btn', { active: syncViewMode === 'ok' }]"
                type="button"
                @click="setSyncViewMode('ok', { scrollToResults: true, focusFirst: true })"
              >
                Alignes
              </button>
            </div>

            <div class="sync-toolbar-actions">
              <button class="hero-btn hero-btn-light" type="button" :disabled="loading" @click="selectAllSyncComponents">
                Tout cocher
              </button>
              <button class="hero-btn hero-btn-primary" type="button" :disabled="loading" @click="refreshDashboardAnalysis">
                Analyser maintenant
              </button>
            </div>
          </div>
        </div>

        <aside v-if="syncSpotlight" :class="['sync-spotlight-card', syncSpotlight.tone]">
          <div class="sync-spotlight-top">
            <span class="section-kicker">{{ syncSpotlight.label }}</span>
            <span :class="['sync-spotlight-pill', syncSpotlight.tone]">{{ syncSpotlight.badge }}</span>
          </div>

          <div class="sync-spotlight-score">
            <div class="sync-spotlight-score-ring">
              <strong>{{ syncSpotlight.score }}</strong>
              <span>/100</span>
            </div>
            <div class="sync-spotlight-score-copy">
              <strong>{{ syncSpotlight.title }}</strong>
              <p>{{ syncSpotlight.copy }}</p>
            </div>
          </div>

          <div class="sync-spotlight-highlight">
            <span>Pourquoi ce module remonte</span>
            <strong>{{ syncSpotlight.highlight }}</strong>
          </div>

          <div v-if="syncSpotlight.topDrifts?.length" class="sync-spotlight-list">
            <div class="sync-spotlight-list-title">Ce qu'il faut verifier en premier</div>
            <div
              v-for="item in syncSpotlight.topDrifts"
              :key="item"
              class="sync-spotlight-item"
            >
              {{ item }}
            </div>
          </div>

          <div class="sync-spotlight-stats">
            <div>
              <span>Scope actif</span>
              <strong>{{ syncSummary.scope_label || "-" }}</strong>
            </div>
            <div>
              <span>Ecarts</span>
              <strong>{{ syncSpotlight.driftCount }}</strong>
            </div>
            <div>
              <span>Etat du scan</span>
              <strong>{{ syncSpotlight.badge }}</strong>
            </div>
          </div>
        </aside>
      </div>

      <div class="sync-explainer">
        <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3M8 9.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
        Périmètre du dernier contrôle : <strong>{{ syncSummary.scope_label || "-" }}</strong> · affichage <strong>{{ syncDisplayModeLabel }}</strong>.
      </div>

      <div :class="['sync-result-banner', syncHasResult ? 'ready' : 'empty']">
        <div class="sync-result-banner-main">
          <span class="sync-result-icon" aria-hidden="true">
            <svg v-if="syncHasResult" viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M3 8l3 3 7-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3M8 10.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          </span>
          <div class="sync-result-copy">
            <strong>{{ syncStatusLead }}</strong>
            <p>{{ syncStatusDetail }}</p>
          </div>
        </div>
        <button class="hero-btn hero-btn-primary sync-result-action" type="button" :disabled="loading" @click="refreshDashboardAnalysis">
          {{ syncHasResult ? "Mettre à jour l'analyse" : "Lancer l'analyse" }}
        </button>
      </div>

      <div ref="syncResultsStart" class="integrity-flow">
        <div class="flow-node">
          <span class="flow-dot flow-dot-system"></span>
          <strong>État réel du système</strong>
          <small>lu en direct</small>
        </div>
        <div class="flow-arrow-wrap">
          <div class="flow-arrow-line"></div>
          <span class="flow-arrow-label">comparé</span>
        </div>
        <div class="flow-node">
          <span class="flow-dot flow-dot-backup"></span>
          <strong>Base de données</strong>
          <small>ce qui est enregistré</small>
        </div>
      </div>

      <div class="integrity-metrics">
        <div class="integrity-box">
          <div class="integrity-box-icon">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 4.5V8.5l2.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </div>
          <span>{{ syncHasResult ? "Dernière analyse conservée" : "Dernière analyse" }}</span>
          <strong>{{ formatDate(syncSummary.last_check_at) }}</strong>
        </div>
        <div class="integrity-box">
          <div class="integrity-box-icon integrity-box-icon--blue">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><circle cx="8" cy="5" r="2.5" stroke="currentColor" stroke-width="1.2"/><path d="M3 14c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </div>
          <span>Points vérifiés</span>
          <strong>{{ syncSummary.verified_entities ?? 0 }}</strong>
        </div>
        <div class="integrity-box">
          <div class="integrity-box-icon integrity-box-icon--green">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M3 8l3.5 3.5L13 5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <span>Modules analysés</span>
          <strong>{{ syncAnalyzedCount }} / {{ availableSyncComponents.length }}</strong>
        </div>
        <div class="integrity-box" :title="syncDriftTooltip">
          <div :class="['integrity-box-icon', (syncSummary.desync_detected ?? 0) > 0 ? 'integrity-box-icon--orange' : 'integrity-box-icon--green']">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 2L2 14h12L8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M8 7v3M8 11.5v.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </div>
          <span>Différences détectées</span>
          <strong>{{ syncSummary.desync_detected ?? "-" }}</strong>
        </div>
      </div>

      <div class="sync-reading-strip">
        <div class="sync-reading-box">
          <span>Alignés</span>
          <strong class="sync-reading-ok">{{ syncHealthyModulesCount }} module{{ syncHealthyModulesCount > 1 ? "s" : "" }}</strong>
        </div>
        <div class="sync-reading-box sync-reading-box--divider">
          <span>À corriger</span>
          <strong :class="syncDriftModulesCount > 0 ? 'sync-reading-warn' : ''">{{ syncDriftModulesCount }} module{{ syncDriftModulesCount > 1 ? "s" : "" }}</strong>
        </div>
        <div class="sync-reading-box">
          <span>Principe</span>
          <strong>Système réel → base</strong>
        </div>
      </div>

      <!-- Drift action banner -->
      <div v-if="syncViewMode === 'drift' && filteredSyncModules.length > 0" class="drift-action-banner">
        <div class="drift-action-banner-icon">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M10 2L2 17h16L10 2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M10 8v4M10 14.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </div>
        <div class="drift-action-banner-body">
          <strong>{{ filteredSyncModules.length }} module{{ filteredSyncModules.length > 1 ? 's' : '' }} avec des différences détectées</strong>
          <span>Voici ce qui ne correspond pas entre votre système réel et ce qui est enregistré. Lisez chaque module ci-dessous pour savoir quoi vérifier.</span>
        </div>
      </div>

      <div v-if="syncViewMode === 'ok' && filteredSyncModules.length > 0" class="drift-ok-banner">
        <div class="drift-ok-banner-icon">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18"><path d="M3 10l5 5L17 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
        <div>
          <strong>{{ filteredSyncModules.length }} module{{ filteredSyncModules.length > 1 ? 's' : '' }} parfaitement alignés</strong>
          <span>Ces modules sont synchronisés entre le système réel et la base de données.</span>
        </div>
      </div>

      <div class="module-grid">
        <article
          v-for="module in filteredSyncModules"
          :key="module.key"
          :id="`sync-module-${module.key}`"
          :class="['module-card', module.status]"
        >
          <div class="module-card-head">
            <div class="module-card-head-left">
              <span :class="['module-status-dot', module.status === 'ok' ? 'ok' : 'error']"></span>
              <strong>{{ module.label }}</strong>
            </div>
            <span :class="['mini-status', module.status === 'ok' ? 'ok' : 'error']">
              {{ module.status === "ok" ? "Synchronisé" : "Différences" }}
            </span>
          </div>
          <div class="module-card-subtitle">
            {{ moduleFriendlyLabel(module.key) }}
          </div>
          <small>{{ module.summary }}</small>
          <div class="module-card-stats">
            <span class="module-stat">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.1"/></svg>
              {{ module.checked_items }} vérifiés
            </span>
            <span class="module-stat module-stat--ok">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
              {{ module.ok_count || 0 }} OK
            </span>
            <span :class="['module-stat', module.drift_count > 0 ? 'module-stat--warn' : '']">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M6 1L1 10h10L6 1z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>
              {{ module.drift_count }} à corriger
            </span>
          </div>
          <div v-if="module.entities?.length" class="module-entities">
            <div
              v-for="entity in module.entities"
              :key="`${module.key}-${entity.label}`"
              :class="['entity-chip', entity.status === 'ok' ? 'ok' : 'drift']"
              :title="`${entity.label}: ${entity.detail}`"
            >
              <span class="entity-dot"></span>
              <strong>{{ entity.label }}</strong>
              <small>{{ entity.detail }}</small>
            </div>
          </div>
          <ul v-if="module.drifts?.length" class="module-drift-list">
            <li v-for="drift in module.drifts.slice(0, 3)" :key="`${module.key}-${drift.kind}-${drift.label}`">
              <svg viewBox="0 0 10 10" fill="none" width="9" height="9" class="drift-item-dot"><circle cx="5" cy="5" r="4" stroke="currentColor" stroke-width="1.2"/><path d="M5 3v2M5 6.5v.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
              {{ drift.detail }}
            </li>
            <li v-if="module.drifts.length > 3" class="drift-more">
              + {{ module.drifts.length - 3 }} autre{{ module.drifts.length - 3 > 1 ? 's' : '' }} différence{{ module.drifts.length - 3 > 1 ? 's' : '' }}
            </li>
          </ul>
          <div v-else class="module-ok-copy">
            <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M2 7l3.5 3.5L12 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Tout est en ordre pour ce module.
          </div>
        </article>

        <article v-if="filteredSyncModules.length === 0" class="module-empty-state">
          <div class="module-empty-icon">
            <svg viewBox="0 0 28 28" fill="none" width="24" height="24"><path d="M5 14h18M14 5l9 9-9 9" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <strong>{{ syncHasResult ? "Aucun module dans ce filtre" : "Analyse système / base non lancée" }}</strong>
          <p>
            {{ syncHasResult
              ? "Changez le filtre pour revoir le dernier contrôle complet."
              : "Cliquez sur Lancer l'analyse pour afficher les vrais résultats. Les modules ne sont pas considérés comme des différences avant le scan." }}
          </p>
          <button v-if="!syncHasResult" class="hero-btn hero-btn-primary" type="button" :disabled="loading" @click="refreshDashboardAnalysis">
            Lancer l'analyse
          </button>
        </article>
      </div>
    </section>


    <template v-if="activeMonitoringTab === 'analytics'">
      <section class="analytics-hero">
        <div class="analytics-hero-main">
          <span class="section-kicker">Lecture intelligente</span>
          <h3>Les graphes sont isolés ici pour lire les tendances sans bruit opérationnel.</h3>
          <p>
            Le compteur services vient du runtime: services critiques actifs sur le total supervisé.
            Le `{{ syncSelectedCount }}/{{ availableSyncComponents.length }}` vient du scan live: modules sélectionnés pour comparer système réel et base.
            La couverture backup, elle, lit la dernière archive sauvegardée.
          </p>
        </div>
        <div class="analytics-compare-grid">
          <div class="analytics-compare-card">
            <span>Services critiques</span>
            <strong>{{ serviceSummary.running }}/{{ serviceSummary.total }}</strong>
            <small>Services/checks actifs maintenant sur le périmètre supervisé.</small>
          </div>
          <div class="analytics-compare-card analytics-compare-card--sync">
            <span>Synchronisation</span>
            <strong>{{ syncSelectedCount }}/{{ availableSyncComponents.length }}</strong>
            <small>Scope live choisi pour l'analyse système/base.</small>
          </div>
          <div class="analytics-compare-card analytics-compare-card--backup">
            <span>Archive backup</span>
            <strong>{{ criticalCoverageLabel }}</strong>
            <small>Composants critiques réussis dans la dernière archive.</small>
          </div>
          <div class="analytics-compare-card analytics-compare-card--score">
            <span>Signal global</span>
            <strong>{{ insights.protection_score ?? 0 }}/100</strong>
            <small>Score croisé: backup, sync, services, fraîcheur.</small>
          </div>
        </div>
      </section>

      <section class="chart-grid chart-grid--isolated">
        <article class="panel-card chart-card chart-card--cockpit">
          <div class="section-head compact">
            <div class="chart-head-left">
              <div class="chart-icon chart-icon--blue">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 1.5a6.5 6.5 0 1 0 6.5 6.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M8 8l4-4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
              </div>
              <div>
                <h3>Cockpit pression live</h3>
                <div class="chart-copy">Jauge instantanée CPU, RAM, disque système et espace backup</div>
              </div>
            </div>
            <span :class="['state-pill', resourcePressureClass]">{{ resourcePressureLabel }}</span>
          </div>
          <apexchart
            height="270"
            type="radialBar"
            :options="resourceCockpitOptions"
            :series="resourceCockpitSeries"
          ></apexchart>
          <div class="chart-micro-grid">
            <div v-for="metric in resourceCockpitMetrics" :key="metric.label" class="chart-micro-card">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}%</strong>
              <small>{{ metric.hint }}</small>
            </div>
          </div>
        </article>

        <article class="panel-card chart-card chart-card--backup-lab">
          <div class="section-head compact">
            <div class="chart-head-left">
              <div class="chart-icon chart-icon--green">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M2 4.5h12M3.5 2.5h9A1.5 1.5 0 0 1 14 4v8a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 12V4a1.5 1.5 0 0 1 1.5-1.5Z" stroke="currentColor" stroke-width="1.2"/><path d="M5 9l2 2 4-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              <div>
                <h3>Constellation backup</h3>
                <div class="chart-copy">Heatmap des dernières archives avec lecture qualité/temps</div>
              </div>
            </div>
            <span class="live-pill">8 derniers</span>
          </div>
          <apexchart
            height="220"
            type="heatmap"
            :options="backupHeatmapOptions"
            :series="backupHeatmapSeries"
          ></apexchart>
          <div class="backup-orbit-strip">
            <div
              v-for="point in backupTimelinePoints"
              :key="`${point.label}-${point.score}`"
              :class="['backup-orbit-node', point.tone]"
              :title="`${point.label}: ${point.score}/100`"
            >
              <span></span>
              <strong>{{ point.score }}</strong>
              <small>{{ point.label }}</small>
            </div>
          </div>
        </article>

        <article class="panel-card chart-card chart-card--radar">
          <div class="section-head compact">
            <div class="chart-head-left">
              <div class="chart-icon chart-icon--orange">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 1.5l6 3.5v6l-6 3.5-6-3.5v-6l6-3.5Z" stroke="currentColor" stroke-width="1.2"/><path d="M8 4v4l3 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
              </div>
              <div>
                <h3>Radar cohérence</h3>
                <div class="chart-copy">Score système/base par module analysé</div>
              </div>
            </div>
            <span :class="['state-pill', syncClass]">{{ syncScoreAverage }}%</span>
          </div>
          <apexchart
            height="270"
            type="radar"
            :options="syncRadarOptions"
            :series="syncRadarSeries"
          ></apexchart>
          <div class="radar-module-strip">
            <div
              v-for="module in syncModules"
              :key="module.key"
              :class="['radar-module-chip', module.status === 'ok' ? 'ok' : 'warning']"
            >
              <span>{{ module.label }}</span>
              <strong>{{ module.score ?? 0 }}%</strong>
            </div>
          </div>
        </article>
      </section>
    </template>

    <section v-if="activeMonitoringTab === 'overview'" class="split-grid">
      <article class="panel-card">
        <div class="section-head compact">
          <div class="chart-head-left">
            <div :class="['chart-icon', serviceSummary.failing > 0 ? 'chart-icon--orange' : 'chart-icon--green']">
              <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><rect x="1.5" y="2.5" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M5 8h6M8 5.5v5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            </div>
            <div>
              <h3>État des services</h3>
            </div>
          </div>
          <span :class="['state-pill', serviceSummary.failing > 0 ? 'warning' : 'ok']">
            {{ servicePulseLabel }}
          </span>
        </div>

        <div class="services-explainer">
          <svg class="kpi-icon" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.2"/><path d="M8 5v3M8 9.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
          Les services critiques de votre système en un coup d'œil.
        </div>

        <div class="pulse-scope-banner">
          <strong>Perimetre</strong>
          <span>{{ serviceScopeReadable }}</span>
          <small>Services critiques + checks VM + stockage.</small>
        </div>

        <div class="pulse-summary-grid">
          <div class="pulse-summary-card">
            <span>Etat global</span>
            <strong>{{ serviceHealthReadable }}</strong>
            <small>{{ servicePulseSummary }}</small>
          </div>
          <div class="pulse-summary-card">
            <span>Priorite immediate</span>
            <strong>{{ primaryServiceActionTitle }}</strong>
            <small>{{ primaryServiceActionText }}</small>
          </div>
        </div>

        <div class="priority-strip">
          <div class="priority-strip-head">
            <strong>Priorites</strong>
            <span>{{ prioritizedServices.length }} element{{ prioritizedServices.length > 1 ? "s" : "" }}</span>
          </div>
          <div
            v-for="service in prioritizedServices"
            :key="service.name"
            class="priority-service-row"
          >
            <div class="service-meta">
              <span :class="['service-dot', service.running ? 'up' : service.kind === 'runtime_check' ? 'warn' : 'down']"></span>
              <div>
                <strong>{{ service.label || service.name }}</strong>
                <small>{{ servicePulseReason(service) }}</small>
                <small class="service-subline">
                  {{ service.status_detail }}
                  <span v-if="service.category">· {{ serviceCategoryLabel(service.category) }}</span>
                </small>
              </div>
            </div>

            <div class="service-actions">
              <span :class="['mini-status', service.running ? 'ok' : service.kind === 'runtime_check' ? 'warning' : 'error']">
                {{ service.running ? "OK" : service.kind === 'runtime_check' ? "check" : "alerte" }}
              </span>
              <button
                v-if="service.manageable"
                class="mini-btn"
                type="button"
                :disabled="loading"
                @click="service.running ? restartService(service.name) : startService(service.name)"
              >
                {{ service.running ? "Restart" : "Start" }}
              </button>
              <span v-else class="mini-status neutral">info</span>
            </div>
          </div>
        </div>
      </article>

      <article class="panel-card machine-card-v2">
        <div class="section-head compact">
          <div class="chart-head-left">
            <div :class="['chart-icon', cockpitMachineTone === 'ok' ? 'chart-icon--green' : cockpitMachineTone === 'warning' ? 'chart-icon--orange' : 'chart-icon--red']">
              <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.2"/><path d="M5 13v2M11 13v2M3 15h10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            </div>
            <h3>Santé de la machine</h3>
          </div>
          <span class="live-pill">
            <span class="live-dot"></span>
            En direct
          </span>
        </div>

        <!-- Hero gauge + identity card -->
        <div :class="['mh-hero', `mh-hero--${cockpitMachineTone}`]">
          <div class="mh-gauge">
            <svg viewBox="0 0 80 80" width="92" height="92" class="mh-gauge-svg">
              <circle cx="40" cy="40" r="34" stroke="#eef2f7" stroke-width="8" fill="none"/>
              <circle
                cx="40" cy="40" r="34"
                :stroke="cockpitMachineTone === 'ok' ? '#16a34a' : cockpitMachineTone === 'warning' ? '#d29031' : '#c23b32'"
                stroke-width="8" fill="none"
                stroke-linecap="round"
                :stroke-dasharray="`${machineHealthScore * 2.136} 213.6`"
                transform="rotate(-90 40 40)"
                style="transition: stroke-dasharray .8s cubic-bezier(.4,0,.2,1)"
              />
              <text x="40" y="44" text-anchor="middle" font-size="20" font-weight="700" :fill="cockpitMachineTone === 'ok' ? '#16a34a' : cockpitMachineTone === 'warning' ? '#d29031' : '#c23b32'">{{ machineHealthScore }}</text>
              <text x="40" y="58" text-anchor="middle" font-size="8" fill="#94a3b8" font-weight="600">/100</text>
            </svg>
          </div>
          <div class="mh-hero-copy">
            <span class="mh-eyebrow">SANTÉ INSTANTANÉE</span>
            <strong :class="['mh-headline', `tone-${cockpitMachineTone}`]">{{ machineHealthLabel }}</strong>
            <p class="mh-sub">{{ machineHealthText }}</p>
            <div class="mh-tags">
              <span class="mh-tag"><span class="mh-tag-dot"></span>{{ vmStatusTitle }}</span>
              <span class="mh-tag"><span class="mh-tag-ico">↑</span>{{ uptimeReadableTitle }}</span>
              <span class="mh-tag">{{ loadAverageReadableTitle }}</span>
            </div>
          </div>
        </div>

        <!-- Resources detail with absolute values -->
        <div class="mh-block">
          <div class="mh-block-head">
            <strong>Ressources en temps réel</strong>
            <span>{{ liveMetrics.currentDate || "" }}</span>
          </div>
          <div class="mh-meters-grid">
            <div class="mh-meter">
              <div class="mh-meter-head">
                <span class="mh-meter-lbl">CPU</span>
                <strong :class="['mh-meter-val', meterTone(liveMetrics.cpu)]">{{ liveMetrics.cpu }}%</strong>
              </div>
              <div class="mh-meter-bar">
                <div :class="['mh-meter-fill', meterTone(liveMetrics.cpu)]" :style="{ width: `${Math.min(100, liveMetrics.cpu)}%` }"></div>
              </div>
              <span class="mh-meter-hint">{{ cpuStateHint }}</span>
            </div>

            <div class="mh-meter">
              <div class="mh-meter-head">
                <span class="mh-meter-lbl">RAM</span>
                <strong :class="['mh-meter-val', meterTone(liveMetrics.memory)]">{{ liveMetrics.memory }}%</strong>
              </div>
              <div class="mh-meter-bar">
                <div :class="['mh-meter-fill', meterTone(liveMetrics.memory)]" :style="{ width: `${Math.min(100, liveMetrics.memory)}%` }"></div>
              </div>
              <span class="mh-meter-hint">{{ ramStateHint }}</span>
            </div>

            <div class="mh-meter">
              <div class="mh-meter-head">
                <span class="mh-meter-lbl">Disk /</span>
                <strong :class="['mh-meter-val', meterTone(diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes))]">
                  {{ diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes) }}%
                </strong>
              </div>
              <div class="mh-meter-bar">
                <div :class="['mh-meter-fill', meterTone(diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes))]" :style="{ width: `${diskUsagePercent(rootDisk.used_bytes, rootDisk.total_bytes)}%` }"></div>
              </div>
              <span class="mh-meter-hint">{{ formatSize(rootDisk.used_bytes) }} / {{ formatSize(rootDisk.total_bytes) }}</span>
            </div>

            <div class="mh-meter">
              <div class="mh-meter-head">
                <span class="mh-meter-lbl">Disk backup</span>
                <strong :class="['mh-meter-val', meterTone(diskUsagePercent(backupDisk.used_bytes, backupDisk.total_bytes))]">
                  {{ diskUsagePercent(backupDisk.used_bytes, backupDisk.total_bytes) }}%
                </strong>
              </div>
              <div class="mh-meter-bar">
                <div :class="['mh-meter-fill', meterTone(diskUsagePercent(backupDisk.used_bytes, backupDisk.total_bytes))]" :style="{ width: `${diskUsagePercent(backupDisk.used_bytes, backupDisk.total_bytes)}%` }"></div>
              </div>
              <span class="mh-meter-hint">{{ formatSize(backupDisk.used_bytes) }} / {{ formatSize(backupDisk.total_bytes) }}</span>
            </div>
          </div>
        </div>

        <!-- Load average breakdown -->
        <div class="mh-block">
          <div class="mh-block-head">
            <strong>Charge système</strong>
            <span>moyenne sur 1 / 5 / 15 min</span>
          </div>
          <div class="mh-load-grid">
            <div class="mh-load-cell">
              <span>1 min</span>
              <strong :class="loadToneClass(loadAverage1)">{{ loadAverage1 !== null ? loadAverage1.toFixed(2) : '—' }}</strong>
              <small>{{ loadAverageShortText(loadAverage1) }}</small>
            </div>
            <div class="mh-load-cell">
              <span>5 min</span>
              <strong :class="loadToneClass(loadAverage5)">{{ loadAverage5 !== null ? loadAverage5.toFixed(2) : '—' }}</strong>
              <small>récent</small>
            </div>
            <div class="mh-load-cell">
              <span>15 min</span>
              <strong :class="loadToneClass(loadAverage15)">{{ loadAverage15 !== null ? loadAverage15.toFixed(2) : '—' }}</strong>
              <small>tendance</small>
            </div>
          </div>
          <p class="mh-load-hint">{{ loadAverageHumanHint }}</p>
        </div>

        <!-- Environment & runtime details -->
        <div class="mh-block">
          <div class="mh-block-head">
            <strong>Environnement</strong>
            <span>contexte d'exécution</span>
          </div>
          <div class="mh-env-grid">
            <div class="mh-env-row">
              <div class="mh-env-ico">⚙</div>
              <div>
                <span>Plateforme</span>
                <strong>{{ vmStatusTitle }}</strong>
                <small>{{ vmStatusText }}</small>
              </div>
            </div>
            <div class="mh-env-row">
              <div class="mh-env-ico">⏱</div>
              <div>
                <span>Uptime · dernier reboot</span>
                <strong>{{ uptimeReadableTitle }}</strong>
                <small>{{ uptimeReadableText }}</small>
              </div>
            </div>
            <div class="mh-env-row">
              <div class="mh-env-ico">💾</div>
              <div>
                <span>Espace backup libre</span>
                <strong>{{ formatSize(backupDisk.free_bytes) }}</strong>
                <small>{{ formatSize(rootDisk.free_bytes) }} libre sur /</small>
              </div>
            </div>
            <div class="mh-env-row">
              <div class="mh-env-ico">🛡</div>
              <div>
                <span>Services critiques</span>
                <strong :class="serviceSummary.failing > 0 ? 'tone-warning' : 'tone-ok'">{{ serviceSummary.running }}/{{ serviceSummary.total }}</strong>
                <small>{{ serviceSummary.failing > 0 ? `${serviceSummary.failing} en alerte` : 'tout opérationnel' }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Pressure points -->
        <div v-if="machinePressurePoints.length" class="mh-pressure">
          <div class="mh-pressure-head">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 2L2 14h12L8 2z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 6v3M8 10.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
            <strong>Points de pression</strong>
          </div>
          <ul>
            <li v-for="p in machinePressurePoints" :key="p.label" :class="`tone-${p.tone}`">
              <strong>{{ p.label }}</strong>
              <span>{{ p.detail }}</span>
            </li>
          </ul>
        </div>
        <div v-else class="mh-pressure mh-pressure--ok">
          <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M3 8l3 3 7-7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <span>Aucun point de pression — toutes les ressources sont dans les seuils.</span>
        </div>
      </article>
    </section>

    <section v-if="activeMonitoringTab === 'overview'" class="alerts-card alerts-card-v2">
      <div class="section-head compact">
        <div class="chart-head-left">
          <div :class="['chart-icon', visibleAlerts.length > 0 ? 'chart-icon--orange' : 'chart-icon--green']">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path d="M8 2L2 14h12L8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M8 7v3M8 11.5v.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          </div>
          <h3>Alertes actives</h3>
        </div>
        <span :class="['state-pill', visibleAlerts.length > 0 ? 'warning' : 'ok']">
          {{ visibleAlerts.length > 0 ? `${visibleAlerts.length} non résolue${visibleAlerts.length > 1 ? 's' : ''}` : 'Tout est calme' }}
        </span>
      </div>

      <!-- Severity counters + filter pills -->
      <div v-if="visibleAlerts.length > 0" class="alerts-controls">
        <div class="alerts-counters">
          <div :class="['alerts-counter', 'critical', { active: alertsFilter === 'critical' }]" @click="setAlertsFilter('critical')">
            <span class="ac-dot"></span>
            <strong>{{ alertsCountBySeverity.critical }}</strong>
            <span class="ac-lbl">Critique{{ alertsCountBySeverity.critical > 1 ? 's' : '' }}</span>
          </div>
          <div :class="['alerts-counter', 'warning', { active: alertsFilter === 'warning' }]" @click="setAlertsFilter('warning')">
            <span class="ac-dot"></span>
            <strong>{{ alertsCountBySeverity.warning }}</strong>
            <span class="ac-lbl">Attention</span>
          </div>
          <div :class="['alerts-counter', 'all', { active: alertsFilter === 'all' }]" @click="setAlertsFilter('all')">
            <span class="ac-dot"></span>
            <strong>{{ visibleAlerts.length }}</strong>
            <span class="ac-lbl">Toutes</span>
          </div>
        </div>
        <div class="alerts-filter-info">
          <span v-if="alertsFilter !== 'all'">Filtré · </span>
          <strong>{{ filteredAlerts.length }}</strong> visible{{ filteredAlerts.length > 1 ? 's' : '' }}
        </div>
      </div>

      <div class="alerts-table-wrap">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>Heure</th>
              <th>Niveau</th>
              <th>Service</th>
              <th>Problème</th>
              <th>Cause</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="empty-row">
                <span class="empty-row-inner">Chargement des alertes...</span>
              </td>
            </tr>
            <tr v-else-if="visibleAlerts.length === 0">
              <td colspan="6" class="empty-row">
                <div class="alerts-empty-state">
                  <svg viewBox="0 0 32 32" fill="none" width="28" height="28"><path d="M16 3l13 23H3L16 3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" opacity=".25"/><path d="M9 8l14 14M23 8L9 22" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" opacity=".25"/></svg>
                  <strong>Aucune alerte active</strong>
                  <span>Tout fonctionne correctement.</span>
                </div>
              </td>
            </tr>
            <tr
              v-for="alert in filteredAlerts"
              :key="alertKey(alert)"
              :class="['alert-row', `alert-row--${alert.severity}`]"
            >
              <td class="alert-td-time">{{ formatTime(alert.time) }}</td>
              <td>
                <span :class="['severity-pill', alert.severity]">
                  {{ alert.severity === 'critical' ? 'Critique' : alert.severity === 'warning' ? 'Attention' : alert.severity }}
                </span>
              </td>
              <td class="alert-td-service">{{ alert.service }}</td>
              <td class="alert-td-msg">{{ alert.message }}</td>
              <td class="alert-td-cause">{{ alert.cause }}</td>
              <td>
                <button
                  v-if="alert.action"
                  class="table-action"
                  type="button"
                  :disabled="loading"
                  @click="triggerAlertAction(alert)"
                >
                  {{ alert.action_label || "Voir le détail" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="2800"
      location="bottom right"
    >
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import { nextTick } from "vue";
import VueApexCharts from "vue3-apexcharts";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  name: "BackupDashboardMonitoring",
  components: {
    apexchart: VueApexCharts,
  },
  inject: ["emitter"],
  data() {
    return {
      loading: false,
      snackbar: false,
      snackbarColor: "success",
      snackbarText: "",
      overview: {
        cards: {},
        integrity: {},
        sync: {},
        insights: {},
        charts: {
          resources_history: [],
          backup_health_history: [],
          sync_modules: [],
        },
        services: [],
        resources: {
          backup_disk: {},
          root_disk: {},
        },
        alerts: [],
      },
      ignoredAlerts: [],
      lastRestore: null,
      liveMetrics: {
        cpu: 0,
        memory: 0,
        uptime: "",
        loadAverage: "",
        currentDate: "",
      },
      socket: null,
      aiAnalysis: { scores: {}, trend: {} },
      _aiPollTimer: null,
      _aiWsDebounce: null,
      syncViewMode: "all",
      syncPilotExpanded: false,
      alertsFilter: "all",
      activeMonitoringTab: "overview",
      selectedSyncComponents: [],
      loadingTitle: "Please Wait...",
      loadingMessage: "Analyse en cours...",
      cachedSyncSummary: null,
      autoRefreshTimer: null,
      socketReconnectTimer: null,
      socketRetryCount: 0,
      socketMaxRetries: 3,
      lastRefreshedAt: null,
      scheduledTasks: [],
      drpMetrics: null,
      dismissedAutomationNoticeKey: null,
      countdown: { h: 0, m: 0, s: 0 },
      nextRunTarget: null,
      _countdownInterval: null,
    };
  },
  computed: {
    firewallZones() {
      const zoneConfig = [
        { key: "firewall", label: "Firewall", icon: "🔥", names: ["nftables"] },
        { key: "proxy",    label: "Proxy",    icon: "🛡️", names: ["squid"] },
        { key: "ids",      label: "IDS/IPS",  icon: "👁️", names: ["suricata"] },
        { key: "vpn",      label: "VPN",      icon: "🔐", names: ["strongswan", "openvpn"] },
        { key: "dhcp",     label: "DHCP",     icon: "📡", names: ["dnsmasq", "isc-dhcp", "dhcpd"] },
        { key: "dns",      label: "DNS",      icon: "🔍", names: ["named", "unbound", "bind"] },
      ];
      return zoneConfig.map((zone) => {
        const svc = this.services.find((s) =>
          zone.names.some((n) => (s.name || "").toLowerCase().includes(n) || (s.label || "").toLowerCase().includes(n))
        );
        return { ...zone, running: svc ? svc.running : null };
      }).filter((z) => z.running !== null);
    },
    lastRestoreModeLabel() {
      if (!this.lastRestore) return "—";
      const map = { safe: "Safe", complete: "Full", ui_full: "Full UI-safe", full: "Full", selected_components: "Custom" };
      return map[this.lastRestore.mode] || this.lastRestore.mode || "—";
    },
    lastRestoreDurationLabel() {
      const s = this.lastRestore?.duration_seconds || 0;
      if (!s) return "—";
      return s < 60 ? `${Math.round(s)}s` : `${Math.floor(s / 60)}m${Math.round(s % 60)}s`;
    },
    lastRestoreAgo() {
      if (!this.lastRestore?.started_at) return "";
      const diffMs = Date.now() - new Date(this.lastRestore.started_at).getTime();
      const diffH = Math.floor(diffMs / 3600000);
      if (diffH < 1) return "il y a < 1h";
      if (diffH < 24) return `il y a ${diffH}h`;
      const diffD = Math.floor(diffH / 24);
      return `il y a ${diffD} jour${diffD > 1 ? "s" : ""}`;
    },
    visibleAlerts() {
      return (this.overview.alerts || []).filter(
        (alert) => !this.ignoredAlerts.includes(this.alertKey(alert))
      );
    },
    alertsCountBySeverity() {
      const counts = { critical: 0, warning: 0, other: 0 };
      for (const a of this.visibleAlerts) {
        if (a.severity === "critical") counts.critical++;
        else if (a.severity === "warning") counts.warning++;
        else counts.other++;
      }
      return counts;
    },
    filteredAlerts() {
      const severityOrder = { critical: 0, warning: 1 };
      const sorted = [...this.visibleAlerts].sort(
        (a, b) => (severityOrder[a.severity] ?? 9) - (severityOrder[b.severity] ?? 9)
      );
      if (this.alertsFilter === "all") return sorted;
      return sorted.filter((a) => a.severity === this.alertsFilter);
    },
    primaryAlert() {
      return this.visibleAlerts[0] || null;
    },
    latestBackup() {
      return this.overview.cards?.latest_backup || {};
    },
    serviceSummary() {
      return this.overview.cards?.services || { running: 0, total: 0, failing: 0 };
    },
    storageSummary() {
      return this.overview.cards?.backup_storage || {
        used_bytes: 0,
        count: 0,
        disk_used_bytes: 0,
        disk_total_bytes: 0,
      };
    },
    rpoLabel() {
      const hours = this.drpMetrics?.rpo?.hours;
      if (hours === null || hours === undefined) return "—";
      if (hours < 1) return `${Math.round(hours * 60)}min`;
      if (hours < 48) return `${hours.toFixed(1)}h`;
      return `${Math.round(hours / 24)}j`;
    },
    rpoToneClass() {
      const status = this.drpMetrics?.rpo?.status;
      if (status === "critical") return "tone-error";
      if (status === "warning") return "tone-warning";
      return "tone-ok";
    },
    drpGlobalTone() {
      if (!this.drpMetrics) return "loading";
      if (this.drpMetrics.rpo?.status === "critical" || Number(this.drpMetrics.services?.failing || 0) > 0) return "error";
      if (this.drpMetrics.rpo?.status === "warning" || Number(this.drpMetrics.storage?.backup_used_pct || 0) >= 85) return "warning";
      return "ok";
    },
    drpMetricCards() {
      const m = this.drpMetrics || {};
      const backupRate = Number(m.backups?.success_rate ?? 0);
      const restoreRate = Number(m.restores?.success_rate ?? 0);
      const storagePct = Number(m.storage?.backup_used_pct ?? 0);
      const failing = Number(m.services?.failing ?? 0);
      return [
        {
          key: "rpo",
          label: "RPO actuel",
          value: this.rpoLabel,
          hint: m.rpo?.status === "critical" ? "hors SLA, backup requis" : m.rpo?.status === "warning" ? "à surveiller" : "dans le SLA",
          tone: m.rpo?.status === "critical" ? "error" : m.rpo?.status === "warning" ? "warning" : "ok",
          bar: m.rpo?.hours === null || m.rpo?.hours === undefined ? 0 : Math.max(8, Math.min(100, 100 - (Number(m.rpo.hours) / 48) * 100)),
        },
        {
          key: "backup_rate",
          label: "Succès backup",
          value: `${backupRate.toFixed(0)}%`,
          hint: `${m.backups?.successful ?? 0}/${m.backups?.total ?? 0} archives OK`,
          tone: backupRate >= 95 ? "ok" : backupRate >= 75 ? "warning" : "error",
          bar: Math.max(0, Math.min(100, backupRate)),
        },
        {
          key: "restore_rate",
          label: "Succès restore",
          value: `${restoreRate.toFixed(0)}%`,
          hint: `${m.restores?.successful ?? 0}/${m.restores?.total ?? 0} restores OK`,
          tone: restoreRate >= 95 || Number(m.restores?.total || 0) === 0 ? "ok" : restoreRate >= 75 ? "warning" : "error",
          bar: Number(m.restores?.total || 0) === 0 ? 0 : Math.max(0, Math.min(100, restoreRate)),
        },
        {
          key: "storage",
          label: "Stockage backup",
          value: `${storagePct.toFixed(0)}%`,
          hint: `${this.formatSize(m.storage?.backup_free_bytes)} libres`,
          tone: storagePct >= 90 ? "error" : storagePct >= 75 ? "warning" : "ok",
          bar: Math.max(0, Math.min(100, storagePct)),
        },
        {
          key: "services",
          label: "Services critiques",
          value: failing > 0 ? `${failing} down` : "OK",
          hint: `${m.services?.running ?? 0}/${m.services?.total ?? 0} actifs`,
          tone: failing > 0 ? "error" : "ok",
          bar: failing > 0 ? 100 : 100,
        },
      ];
    },
    backupDisk() {
      return this.overview.resources?.backup_disk || { used_bytes: 0, total_bytes: 0, free_bytes: 0 };
    },
    rootDisk() {
      return this.overview.resources?.root_disk || { used_bytes: 0, total_bytes: 0, free_bytes: 0 };
    },
    services() {
      return this.overview.services || [];
    },
    syncSummary() {
      return this.overview.sync || {};
    },
    syncHasResult() {
      return this.hasUsableSyncSummary(this.syncSummary);
    },
    syncDisplayModeLabel() {
      if (this.syncHasResult && this.syncSummary._retained_from_last_scan) {
        return "dernier résultat conservé";
      }
      if (this.syncHasResult) {
        return "résultat du scan";
      }
      return "en attente d'analyse";
    },
    syncResultAgeLabel() {
      if (!this.syncSummary.last_check_at) return "";
      const date = new Date(this.syncSummary.last_check_at);
      if (Number.isNaN(date.getTime())) return "";
      const diffSeconds = Math.max(0, Math.round((Date.now() - date.getTime()) / 1000));
      if (diffSeconds < 60) return "à l'instant";
      if (diffSeconds < 3600) return `il y a ${Math.floor(diffSeconds / 60)} min`;
      if (diffSeconds < 86400) return `il y a ${Math.floor(diffSeconds / 3600)} h`;
      return `il y a ${Math.floor(diffSeconds / 86400)} j`;
    },
    syncStatusLead() {
      if (!this.syncHasResult) {
        return "Aucune analyse affichable pour le moment";
      }
      if (this.syncSummary._retained_from_last_scan) {
        return "Dernier résultat gardé à l'écran";
      }
      return "Résultat de l'analyse active";
    },
    syncStatusDetail() {
      if (!this.syncHasResult) {
        return "Lancez une analyse pour comparer les services, le firewall, le réseau, NAT, VPN, IDS/IPS et proxy.";
      }
      const age = this.syncResultAgeLabel ? ` (${this.syncResultAgeLabel})` : "";
      const drifts = Number(this.syncSummary.desync_detected || 0);
      const driftText = drifts > 0
        ? `${drifts} différence${drifts > 1 ? "s" : ""} détectée${drifts > 1 ? "s" : ""}`
        : "aucune différence détectée";
      return `Auto-refresh actif: les métriques live se mettent à jour, mais ce bloc garde le dernier contrôle complet${age}. ${driftText}.`;
    },
    syncModules() {
      return this.syncHasResult ? (this.syncSummary.modules || []) : [];
    },
    availableSyncComponents() {
      const fallback = ["services", "network", "nat", "vpn", "ids_ips", "proxy"];
      const keys = this.syncSummary.available_components?.length
        ? this.syncSummary.available_components
        : (this.syncModules.length ? this.syncModules.map((module) => module.key) : fallback);

      return keys.map((key) => ({
        key,
        ...this.syncComponentMeta(key),
      }));
    },
    syncPresets() {
      return [
        {
          key: "all",
          label: "Vision globale",
          description: "Passe en revue tout le perimetre critique supervise.",
          components: this.availableSyncComponents.map((component) => component.key),
        },
        {
          key: "critical",
          label: "Essentiels",
          description: "Plateforme, firewall, reseau et VPN: le coeur de l'exploitabilite.",
          components: ["services", "firewall", "network", "vpn"],
        },
        {
          key: "security",
          label: "Securite",
          description: "Controle la defense active: firewall, NAT, IDS/IPS, VPN et proxy.",
          components: ["firewall", "nat", "vpn", "ids_ips", "proxy"],
        },
      ];
    },
    syncSelectedCount() {
      return this.selectedSyncComponents.length || this.availableSyncComponents.length;
    },
    syncAnalyzedCount() {
      return this.syncHasResult ? (this.syncSummary.module_count || this.syncModules.length) : 0;
    },
    syncCoveragePercent() {
      const total = this.availableSyncComponents.length || 1;
      return Math.round((this.syncSelectedCount / total) * 100);
    },
    syncDriftModulesCount() {
      if (!this.syncHasResult) return 0;
      return this.syncModules.filter((module) => module.status !== "ok").length;
    },
    syncHealthyModulesCount() {
      if (!this.syncHasResult) return 0;
      return this.syncModules.filter((module) => module.status === "ok").length;
    },
    filteredSyncModules() {
      if (!this.syncHasResult) return [];
      if (this.syncViewMode === "drift") {
        return this.syncModules.filter((module) => module.status !== "ok");
      }
      if (this.syncViewMode === "ok") {
        return this.syncModules.filter((module) => module.status === "ok");
      }
      return this.syncModules;
    },
    syncSpotlight() {
      if (!this.syncModules.length) return null;

      const worstModule = [...this.syncModules].sort((left, right) => {
        const driftGap = (right.drift_count || 0) - (left.drift_count || 0);
        if (driftGap !== 0) return driftGap;
        return (left.score || 0) - (right.score || 0);
      })[0];

      if (!worstModule) return null;
      if ((worstModule.drift_count || 0) === 0) {
        return {
          tone: "ok",
          label: "Systeme aligne",
          score: 100,
          title: "Aucun module ne ressort en derive sur la selection courante.",
          copy: "La base et les sources systeme racontent la meme chose sur les composants scannes.",
          badge: "stable",
          driftCount: 0,
          highlight: "Le systeme reel et la base sont coherents sur le scope analyse.",
          topDrifts: [
            "Aucun ecart critique detecte.",
            "Tu peux elargir la selection pour controler d'autres composants.",
          ],
        };
      }

      return {
        tone: "warning",
        label: "Focus prioritaire",
        score: worstModule.score ?? 0,
        title: `${worstModule.label} concentre ${worstModule.drift_count} ecart${worstModule.drift_count > 1 ? "s" : ""}.`,
        copy: worstModule.summary || "Commence par ce module pour reduire le bruit avant un restore ou un audit.",
        badge: "a traiter",
        driftCount: worstModule.drift_count || 0,
        highlight: worstModule.drifts?.[0]?.detail || "Des differences entre systeme et base demandent une revue rapide.",
        topDrifts: (worstModule.drifts || []).slice(0, 3).map((item) => item.detail),
      };
    },
    activeSyncPreset() {
      const selected = [...this.selectedSyncComponents].sort().join("|");
      return this.syncPresets.find((preset) => {
        const presetComponents = preset.components
          .filter((component) => this.availableSyncComponents.some((item) => item.key === component))
          .sort()
          .join("|");
        return presetComponents && presetComponents === selected;
      })?.key || null;
    },
    insights() {
      return this.overview.insights || {};
    },
    chartData() {
      return this.overview.charts || {
        resources_history: [],
        backup_health_history: [],
        sync_modules: [],
      };
    },
    integrityIssues() {
      return this.overview.integrity?.issues || [];
    },
    nextBackupLabel() {
      if (this.nextTaskInfo?.nextRun) return this.formatTime(this.nextTaskInfo.nextRun);
      const nextBackup = this.overview.cards?.next_backup || {};
      if (!nextBackup.planned_at) return "Non planifie";
      return this.formatTime(nextBackup.planned_at);
    },
    nextBackupHint() {
      if (this.nextTaskInfo?.nextRunFormatted) {
        return `${this.nextTaskInfo.label} · prévu le ${this.nextTaskInfo.nextRunFormatted}`;
      }
      const nextBackup = this.overview.cards?.next_backup || {};
      if (nextBackup.mode === "scheduled_task") {
        const label = nextBackup.task?.label || "tache planifiee";
        return `${label} · d'apres la planification`;
      }
      return nextBackup.mode === "projection_daily"
        ? "projection sur le rythme observe"
        : "aucune planification detectee";
    },
    enabledTaskCount() {
      return this.scheduledTasks.filter((t) => t.enabled).length;
    },
    allTasksWithNextRun() {
      return this.scheduledTasks
        .map((t) => {
          const nextRun = t.enabled ? this.computeNextRun(t.cron) : null;
          return {
            ...t,
            nextRun,
            nextRunFormatted: nextRun
              ? nextRun.toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })
              : "—",
          };
        })
        .sort((a, b) => {
          if (!a.nextRun) return 1;
          if (!b.nextRun) return -1;
          return a.nextRun - b.nextRun;
        });
    },
    nextTaskInfo() {
      return this.allTasksWithNextRun.find((t) => t.nextRun) || null;
    },
    automationNotice() {
      const task = this.scheduledTasks
        .filter((item) => item.last_queue_reason === "missed_run_catchup" && item.last_queued_for)
        .sort((left, right) => new Date(right.last_queued_at || 0) - new Date(left.last_queued_at || 0))[0];
      if (!task) return null;

      const scheduledAt = new Date(task.last_queued_for);
      const queuedAt = task.last_queued_at ? new Date(task.last_queued_at) : null;
      const finishedAt = task.last_run_at ? new Date(task.last_run_at) : null;
      const referenceTime = finishedAt || queuedAt || scheduledAt;
      if (Number.isNaN(referenceTime.getTime())) return null;

      const ageMs = Date.now() - referenceTime.getTime();
      if (ageMs > 36 * 60 * 60 * 1000) return null;

      const key = `${task.id}-${task.last_queued_for}-${task.last_run_status || "queued"}`;
      if (this.dismissedAutomationNoticeKey === key) return null;

      const scheduledLabel = this.formatTime(scheduledAt);
      const queuedLabel = queuedAt && !Number.isNaN(queuedAt.getTime()) ? this.formatTime(queuedAt) : "maintenant";
      const doneLabel = finishedAt && !Number.isNaN(finishedAt.getTime()) ? this.formatTime(finishedAt) : null;
      const status = String(task.last_run_status || "").toLowerCase();

      if (status === "ok" || status === "success") {
        return {
          key,
          tone: "ok",
          title: "Backup rattrapé automatiquement",
          message: `La machine n'etait pas disponible a ${scheduledLabel}. ${task.label} a ete lance a ${queuedLabel}${doneLabel ? ` et termine a ${doneLabel}` : ""}.`,
          timeLabel: "rattrapage OK",
        };
      }

      if (status === "error" || status === "failed") {
        return {
          key,
          tone: "warning",
          title: "Rattrapage a verifier",
          message: `${task.label} devait partir a ${scheduledLabel}. Asguard a tente un rattrapage a ${queuedLabel}, mais la tache signale une erreur.`,
          timeLabel: "action conseillee",
        };
      }

      return {
        key,
        tone: "info",
        title: "Backup planifie lance maintenant",
        message: `${task.label} devait partir a ${scheduledLabel}. Asguard a detecte le retard et lance le rattrapage.`,
        timeLabel: "en cours",
      };
    },
    integrityLabel() {
      return this.statusMetricLabel(this.overview.integrity?.status);
    },
    integrityClass() {
      return this.statusMetricClass(this.overview.integrity?.status);
    },
    syncLabel() {
      if (this.syncSummary.status === "synchronized") return "Synchronise";
      if (this.syncSummary.status === "drift") return "Ecarts detectes";
      return "Non instrumente";
    },
    syncClass() {
      return this.syncSummary.status === "synchronized" ? "ok" : "warning";
    },
    syncModeLabel() {
      if (this.syncSummary.verification_mode === "dashboard_refresh_scan") {
        return "Refresh / manuel";
      }
      return this.syncSummary.verification_mode_label || "-";
    },
    criticalCoverageLabel() {
      const ok = this.overview.integrity?.critical_components_ok ?? 0;
      const total = this.overview.integrity?.critical_components_total ?? 0;
      if (!total) return "-";
      return `${ok}/${total}`;
    },
    criticalCoverageText() {
      const total = this.overview.integrity?.critical_components_total ?? 0;
      if (!total) return "Aucun composant critique repertorie dans cette archive.";
      return `${this.overview.integrity?.critical_components_ok ?? 0} composant(s) critiques valides sur ${total} attendus pour ce backup.`;
    },
    criticalCoverageItems() {
      return this.overview.integrity?.critical_components || [];
    },
    integrityIssueShortText() {
      const failed = this.overview.integrity?.components_failed ?? 0;
      const skipped = this.overview.integrity?.components_skipped ?? 0;
      if (!failed && !skipped) return "Rien de bloquant";
      if (failed && skipped) return `${failed} failed · ${skipped} skipped`;
      if (failed) return `${failed} failed`;
      return `${skipped} skipped`;
    },
    integrityDriftTooltip() {
      if (this.integrityIssues.length === 0) {
        return "Aucun composant failed ou skipped dans le dernier backup.";
      }
      return this.integrityIssues
        .map((issue) => `${issue.component}: ${issue.status}${issue.message ? ` - ${issue.message}` : ""}`)
        .join("\n");
    },
    syncDriftTooltip() {
      const drifts = this.syncModules.flatMap((module) =>
        (module.drifts || []).map((drift) => `${module.label}: ${drift.detail}`)
      );
      if (drifts.length === 0) {
        return "Aucune derive detectee entre systeme, fichiers de config et base.";
      }
      return drifts.slice(0, 10).join("\n");
    },
    protectionScoreClass() {
      const score = Number(this.insights.protection_score || 0);
      if (score >= 85) return "ok";
      if (score >= 60) return "warning";
      return "error";
    },
    protectionScoreText() {
      const score = Number(this.insights.protection_score || 0);
      if (score >= 85) return "Votre système est bien protégé";
      if (score >= 60) return "Protection partielle — quelques points à améliorer";
      return "Protection insuffisante — action recommandée";
    },
    scoreBreakdown() {
      return this.insights.score_breakdown || [];
    },
    restoreReadinessLabel() {
      if (this.insights.restore_readiness === "ready") {
        const skipped = this.insights.skipped_components?.length || 0;
        const failed = this.insights.failed_components?.length || 0;
        return failed === 0 && skipped > 0 ? "Restore fiable" : "Restore fiable";
      }
      return "Restore a verifier";
    },
    restoreReadinessPill() {
      if (this.insights.restore_readiness === "ready") return "SAIN";
      const failed = this.insights.failed_components?.length || 0;
      return failed > 0 ? "echec detecte" : "a verifier";
    },
    restoreReadinessSubline() {
      const failed = this.insights.failed_components?.length || 0;
      const skipped = this.insights.skipped_components?.length || 0;
      if (failed > 0) return `${failed} composant${failed > 1 ? "s" : ""} en echec dans le dernier backup`;
      if (skipped > 0) return `${skipped} composant${skipped > 1 ? "s" : ""} desactive${skipped > 1 ? "s" : ""} automatiquement, restore non impacte`;
      return "Tous les composants critiques sont presents et valides";
    },
    restoreReadinessClass() {
      return this.insights.restore_readiness === "ready" ? "ok" : "error";
    },
    freshnessClass() {
      const hours = Number(this.insights.freshness_hours);
      if (Number.isNaN(hours)) return "";
      if (hours <= 24) return "ok";
      if (hours <= 48) return "warning";
      return "error";
    },
    freshnessToneClass() {
      const hours = Number(this.insights.freshness_hours);
      if (Number.isNaN(hours)) return "neutral";
      if (hours <= 24) return "ok";
      if (hours <= 48) return "info";
      if (hours <= 72) return "warning";
      return "error";
    },
    freshnessPill() {
      const hours = Number(this.insights.freshness_hours);
      if (Number.isNaN(hours)) return "aucune donnee";
      if (hours <= 24) return "optimal";
      if (hours <= 48) return "confort";
      if (hours <= 72) return "a renouveler";
      return "retard";
    },
    freshnessHeadline() {
      return this.insights.freshness_label || "-";
    },
    freshnessStages() {
      return [
        { key: "ideal", label: "Ideal", range: "<24h", order: 1 },
        { key: "fresh", label: "Stable", range: "24-48h", order: 2 },
        { key: "refresh", label: "Refresh", range: "48-72h", order: 3 },
        { key: "late", label: "Retard", range: ">72h", order: 4 },
      ];
    },
    activeFreshnessStage() {
      const hours = Number(this.insights.freshness_hours);
      if (Number.isNaN(hours)) return "late";
      if (hours <= 24) return "ideal";
      if (hours <= 48) return "fresh";
      if (hours <= 72) return "refresh";
      return "late";
    },
    activeFreshnessStageOrder() {
      return this.freshnessStages.find((stage) => stage.key === this.activeFreshnessStage)?.order || 0;
    },
    freshnessSubline() {
      if (this.insights.freshness_hours === null || this.insights.freshness_hours === undefined) {
        return "Aucun backup recent detecte";
      }
      return `${this.insights.freshness_hours} h depuis le dernier backup`;
    },
    freshnessMeterValue() {
      return Math.max(0, Math.min(100, Number(this.insights.freshness_score || 0)));
    },
    freshnessNarrative() {
      const hours = Number(this.insights.freshness_hours);
      if (Number.isNaN(hours)) {
        return "Lance un backup pour ouvrir une vraie fenetre de restore exploitable.";
      }
      if (hours <= 24) {
        return "Le backup est dans sa meilleure zone de confiance pour un restore rapide.";
      }
      if (hours <= 48) {
        return "Le backup reste lisible et confortable, sans urgence immediate.";
      }
      if (hours <= 72) {
        return "La protection reste valable, mais relancer un backup va remettre la plateforme dans une zone plus sure.";
      }
      return "Le dernier backup est trop ancien pour une lecture sereine. Il vaut mieux le renouveler.";
    },
    primaryRecommendation() {
      return this.insights.recommendations?.[0] || "Surveillance reguliere";
    },
    allRecommendations() {
      const recs = this.insights.recommendations;
      if (Array.isArray(recs) && recs.length) return recs;
      return [this.primaryRecommendation];
    },
    lastRefreshedLabel() {
      if (!this.lastRefreshedAt) return null;
      const diffSeconds = Math.round((Date.now() - this.lastRefreshedAt) / 1000);
      if (diffSeconds < 10) return "Mis a jour a l'instant";
      if (diffSeconds < 60) return `Mis a jour il y a ${diffSeconds}s`;
      return `Mis a jour il y a ${Math.floor(diffSeconds / 60)}min`;
    },
    restoreImpactItems() {
      const NON_CRITICAL = new Set(["vm_snapshot", "vm_snapshot_pre", "vm_snapshot_post"]);
      const skipped = this.insights.skipped_components || [];
      const failed = this.insights.failed_components || [];
      return [
        ...failed.map((item) => ({ ...item, tone: "error" })),
        ...skipped
          .filter((item) => !NON_CRITICAL.has(item.name))
          .map((item) => ({ ...item, tone: "warning" })),
        ...skipped
          .filter((item) => NON_CRITICAL.has(item.name))
          .map((item) => ({ ...item, tone: "neutral", message: item.message || "Desactive automatiquement sur ce deploiement — n'impacte pas le restore." })),
      ].slice(0, 4);
    },
    serviceHealthReadable() {
      const ok = this.insights.service_checks_ok ?? 0;
      const total = this.insights.service_checks_total ?? 0;
      if (!total) return "aucune mesure service";
      return `${ok}/${total} checks OK`;
    },
    vmRuntimeService() {
      return this.services.find((service) => service.category === "vm" || service.name === "vm-runtime") || null;
    },
    servicePulseLabel() {
      if (this.serviceSummary.failing > 0) return `${this.serviceSummary.failing} priorite${this.serviceSummary.failing > 1 ? "s" : ""}`;
      return "stable";
    },
    actionableServiceIssues() {
      return this.services.filter((service) => !service.running);
    },
    prioritizedServices() {
      const downManageable = this.services.filter((service) => !service.running && service.manageable);
      const warningChecks = this.services.filter((service) => !service.running && !service.manageable);
      const healthyCritical = this.services.filter(
        (service) => service.running && ["platform", "data", "security", "network"].includes(service.category)
      );
      const failing = [...downManageable, ...warningChecks];
      const remainingSlots = Math.max(0, 6 - failing.length);
      return [...failing, ...healthyCritical.slice(0, remainingSlots)];
    },
    servicePulseSummary() {
      if (this.actionableServiceIssues.length === 0) {
        return "Aucune interruption critique detectee sur la vue prioritaire.";
      }
      return `${this.actionableServiceIssues.length} element(s) demandent une verification ou une relance.`;
    },
    serviceScopeReadable() {
      return `${this.serviceSummary.total} checks critiques supervises`;
    },
    primaryServiceActionTitle() {
      const firstIssue = this.actionableServiceIssues[0];
      if (!firstIssue) return "Surveillance simple";
      return firstIssue.manageable ? `Relancer ${firstIssue.label || firstIssue.name}` : `Verifier ${firstIssue.label || firstIssue.name}`;
    },
    primaryServiceActionText() {
      const firstIssue = this.actionableServiceIssues[0];
      if (!firstIssue) return "La plateforme est stable sur les services critiques et checks machine.";
      return firstIssue.status_detail || firstIssue.description || "Etat a verifier";
    },
    machineHealthLabel() {
      const cpu = Number(this.liveMetrics.cpu || 0);
      const memory = Number(this.liveMetrics.memory || 0);
      const root = Number(this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes) || 0);
      if (cpu >= 90 || memory >= 90 || root >= 95) return "Sous pression";
      if (cpu >= 70 || memory >= 75 || root >= 85) return "A surveiller";
      return "Confortable";
    },
    aiVerdictLabel() {
      return ({
        stable:   "Stable",
        watch:    "À surveiller",
        high:     "Risque élevé",
        critical: "Critique",
      })[this.aiAnalysis?.scores?.level] || "Stable";
    },
    cockpitMachineTone() {
      const cpu = Number(this.liveMetrics.cpu || 0);
      const memory = Number(this.liveMetrics.memory || 0);
      const root = Number(this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes) || 0);
      if (cpu >= 90 || memory >= 90 || root >= 95) return "error";
      if (cpu >= 70 || memory >= 75 || root >= 85) return "warning";
      return "ok";
    },
    machineHealthScore() {
      const cpu = Number(this.liveMetrics.cpu || 0);
      const memory = Number(this.liveMetrics.memory || 0);
      const root = Number(this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes) || 0);
      const backup = Number(this.diskUsagePercent(this.backupDisk.used_bytes, this.backupDisk.total_bytes) || 0);
      const worst = Math.max(cpu, memory, root, backup);
      return Math.max(0, Math.min(100, Math.round(100 - worst * 0.85)));
    },
    loadAverage1()  { return this.loadAverageNumbers[0] ?? null; },
    loadAverage5()  { return this.loadAverageNumbers[1] ?? null; },
    loadAverage15() { return this.loadAverageNumbers[2] ?? null; },
    cpuStateHint() {
      const v = Number(this.liveMetrics.cpu || 0);
      if (v >= 90) return "Pression CPU forte — vérifier les processus.";
      if (v >= 70) return "Activité CPU soutenue.";
      if (v >= 30) return "Charge CPU modérée.";
      return "CPU au repos.";
    },
    ramStateHint() {
      const v = Number(this.liveMetrics.memory || 0);
      if (v >= 90) return "Mémoire saturée — risque de swap.";
      if (v >= 75) return "Consommation RAM élevée.";
      if (v >= 50) return "Utilisation RAM normale.";
      return "RAM confortable.";
    },
    machinePressurePoints() {
      const points = [];
      const cpu = Number(this.liveMetrics.cpu || 0);
      const memory = Number(this.liveMetrics.memory || 0);
      const root = Number(this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes) || 0);
      const backup = Number(this.diskUsagePercent(this.backupDisk.used_bytes, this.backupDisk.total_bytes) || 0);
      const load1 = this.loadAverage1;
      if (cpu >= 70) points.push({ label: "CPU élevé", detail: `${cpu}% en cours — surveiller les pics.`, tone: cpu >= 90 ? "error" : "warning" });
      if (memory >= 75) points.push({ label: "RAM sous pression", detail: `${memory}% utilisé — possibles swaps.`, tone: memory >= 90 ? "error" : "warning" });
      if (root >= 85) points.push({ label: "Disque système saturé", detail: `${root}% rempli sur /.`, tone: root >= 95 ? "error" : "warning" });
      if (backup >= 85) points.push({ label: "Stockage backup limité", detail: `${backup}% utilisé — appliquer la rétention.`, tone: backup >= 95 ? "error" : "warning" });
      if (load1 !== null && load1 >= 2) points.push({ label: "Charge système élevée", detail: `Load 1 min à ${load1.toFixed(2)}.`, tone: load1 >= 4 ? "error" : "warning" });
      return points;
    },
    machineHealthText() {
      return `CPU ${this.liveMetrics.cpu}% · RAM ${this.liveMetrics.memory}% · disque systeme ${this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes)}%`;
    },
    vmStatusTitle() {
      const detail = this.vmRuntimeService?.status_detail || "";
      if (!detail) return "VM non identifiee";
      if (detail.includes("kvm")) return "VM KVM active";
      if (detail.includes("vmware")) return "VM VMware active";
      if (detail.includes("virtualbox")) return "VM VirtualBox active";
      if (detail.includes("microsoft")) return "VM Hyper-V active";
      if (detail.includes("bare-metal")) return "Machine physique ou VM non detectee";
      return "Environnement virtualise actif";
    },
    vmStatusText() {
      const detail = this.vmRuntimeService?.status_detail || "";
      if (!detail) return "Type d'environnement indisponible.";
      return `${detail.replace("virtualisation:", "").trim()} · disponible maintenant.`;
    },
    uptimeReadableTitle() {
      const raw = String(this.liveMetrics.uptime || "").trim();
      if (!raw) return "-";
      if (raw.includes("day")) return this.uptimeReadableDuration;
      if (raw.includes("hour")) return this.uptimeReadableDuration;
      if (raw.includes("min")) return this.uptimeReadableDuration;
      return raw;
    },
    uptimeReadableDuration() {
      const raw = String(this.liveMetrics.uptime || "").trim();
      if (!raw) return "-";
      return raw
        .replace(/days?/g, "j")
        .replace(/hours?/g, "h")
        .replace(/hour/g, "h")
        .replace(/minutes?/g, "min")
        .replace(/minute/g, "min")
        .replace(/mins?/g, "min");
    },
    uptimeReadableText() {
      const raw = String(this.liveMetrics.uptime || "").trim();
      if (!raw) return "Temps depuis le dernier redemarrage indisponible.";
      if (raw.includes("day")) return `Machine stable depuis ${this.uptimeReadableDuration} sans redemarrage.`;
      if (raw.includes("hour")) return `Machine en ligne depuis ${this.uptimeReadableDuration}.`;
      if (raw.includes("min")) return `Machine relancee il y a ${this.uptimeReadableDuration}.`;
      return `${raw} sans redemarrage.`;
    },
    loadAverageNumbers() {
      return String(this.liveMetrics.loadAverage || "")
        .split(",")
        .map((item) => Number(item.trim()))
        .filter((item) => !Number.isNaN(item));
    },
    loadAverageReadableTitle() {
      const first = this.loadAverageNumbers[0];
      if (first === undefined) return "-";
      if (first < 1) return "Charge legere";
      if (first < 2) return "Charge moderee";
      return "Charge elevee";
    },
    loadAverageReadableText() {
      if (!this.loadAverageNumbers.length) {
        return "Charge moyenne indisponible.";
      }
      return `Moyenne 1/5/15 min: ${this.liveMetrics.loadAverage}`;
    },
    loadAverageHumanHint() {
      const first = this.loadAverageNumbers[0];
      if (first === undefined) return "Lecture indisponible.";
      if (first < 1) return "La machine a de la marge: la charge reste faible sur les 15 dernieres minutes.";
      if (first < 2) return "La machine travaille mais reste globalement confortable.";
      return "La pression systeme monte: verifier CPU, RAM et services si cette charge dure.";
    },
    syncScopeShort() {
      return this.syncSummary.scope_label || "-";
    },
    resourceCockpitMetrics() {
      return [
        {
          label: "CPU",
          value: Math.round(Number(this.liveMetrics.cpu || 0)),
          hint: "pression calcul",
        },
        {
          label: "RAM",
          value: Math.round(Number(this.liveMetrics.memory || 0)),
          hint: "memoire active",
        },
        {
          label: "Systeme",
          value: Number(this.diskUsagePercent(this.rootDisk.used_bytes, this.rootDisk.total_bytes)),
          hint: "disque racine",
        },
        {
          label: "Backup",
          value: Number(this.diskUsagePercent(this.backupDisk.used_bytes, this.backupDisk.total_bytes)),
          hint: "stockage archive",
        },
      ];
    },
    resourceCockpitSeries() {
      return this.resourceCockpitMetrics.map((metric) => metric.value);
    },
    resourcePressureAverage() {
      const values = this.resourceCockpitSeries;
      if (!values.length) return 0;
      return Math.round(values.reduce((sum, value) => sum + Number(value || 0), 0) / values.length);
    },
    resourcePressureClass() {
      if (this.resourcePressureAverage >= 82) return "error";
      if (this.resourcePressureAverage >= 62) return "warning";
      return "ok";
    },
    resourcePressureLabel() {
      if (this.resourcePressureAverage >= 82) return "pression forte";
      if (this.resourcePressureAverage >= 62) return "a surveiller";
      return "confort live";
    },
    resourceCockpitOptions() {
      return {
        chart: {
          sparkline: { enabled: true },
          animations: {
            enabled: true,
            easing: "easeinout",
            speed: 650,
          },
          fontFamily: "inherit",
        },
        colors: ["#2f8de4", "#20a26d", "#f59e0b", "#06b6d4"],
        labels: this.resourceCockpitMetrics.map((metric) => metric.label),
        plotOptions: {
          radialBar: {
            startAngle: -120,
            endAngle: 240,
            hollow: {
              size: "34%",
              background: "#f8fbff",
            },
            track: {
              background: "#edf2f7",
              strokeWidth: "100%",
              margin: 6,
            },
            dataLabels: {
              name: {
                fontSize: "12px",
                color: "#64748b",
                offsetY: 6,
              },
              value: {
                fontSize: "24px",
                fontWeight: 800,
                color: "#0f172a",
                offsetY: -12,
                formatter(value) {
                  return `${Math.round(value)}%`;
                },
              },
              total: {
                show: true,
                label: "Pression",
                color: "#64748b",
                formatter: () => `${this.resourcePressureAverage}%`,
              },
            },
          },
        },
        stroke: {
          lineCap: "round",
        },
        legend: {
          show: false,
        },
      };
    },
    backupTimelinePoints() {
      return (this.chartData.backup_health_history || []).map((item) => {
        const score = Number(item.health_score || 0);
        return {
          label: this.formatCompactDate(item.timestamp),
          score,
          tone: score >= 90 ? "ok" : score >= 70 ? "warning" : "error",
        };
      });
    },
    backupHeatmapSeries() {
      return [
        {
          name: "Sante archive",
          data: this.backupTimelinePoints.map((point) => ({
            x: point.label,
            y: point.score,
          })),
        },
      ];
    },
    backupHeatmapOptions() {
      return {
        chart: {
          toolbar: { show: false },
          fontFamily: "inherit",
          foreColor: "#64748b",
        },
        dataLabels: {
          enabled: true,
          style: {
            colors: ["#0f172a"],
            fontSize: "12px",
            fontWeight: 800,
          },
          formatter(value) {
            return `${Math.round(value)}`;
          },
        },
        plotOptions: {
          heatmap: {
            radius: 13,
            enableShades: false,
            colorScale: {
              ranges: [
                { from: 0, to: 69, color: "#ef4444", name: "fragile" },
                { from: 70, to: 89, color: "#f59e0b", name: "a surveiller" },
                { from: 90, to: 100, color: "#20a26d", name: "sain" },
              ],
            },
          },
        },
        xaxis: {
          labels: {
            style: { fontSize: "11px" },
          },
        },
        yaxis: {
          labels: {
            style: { fontSize: "11px", fontWeight: 700 },
          },
        },
        grid: {
          borderColor: "#edf2f7",
          padding: { left: 8, right: 8 },
        },
        tooltip: {
          y: {
            formatter(value) {
              return `${value}/100`;
            },
          },
        },
      };
    },
    syncScoreAverage() {
      if (!this.syncModules.length) return 0;
      const total = this.syncModules.reduce((sum, module) => sum + Number(module.score || 0), 0);
      return Math.round(total / this.syncModules.length);
    },
    syncRadarSeries() {
      return [
        {
          name: "Cohérence",
          data: this.syncModules.map((module) => Number(module.score || 0)),
        },
      ];
    },
    syncRadarOptions() {
      return {
        chart: {
          toolbar: { show: false },
          fontFamily: "inherit",
          foreColor: "#64748b",
          animations: {
            enabled: true,
            easing: "easeout",
            speed: 650,
          },
        },
        colors: ["#0ea5e9"],
        labels: this.syncModules.map((module) => module.label),
        markers: {
          size: 4,
          colors: ["#ffffff"],
          strokeColors: "#0ea5e9",
          strokeWidth: 2,
        },
        fill: {
          opacity: 0.22,
        },
        stroke: {
          width: 3,
        },
        yaxis: {
          min: 0,
          max: 100,
          tickAmount: 4,
          labels: {
            formatter(value) {
              return `${Math.round(value)}`;
            },
          },
        },
        plotOptions: {
          radar: {
            polygons: {
              strokeColors: "#dbe7f3",
              connectorColors: "#dbe7f3",
              fill: {
                colors: ["#f8fbff", "#ffffff"],
              },
            },
          },
        },
        tooltip: {
          y: {
            formatter(value) {
              return `${value}/100`;
            },
          },
        },
      };
    },
    resourceTrendSeries() {
      const points = this.chartData.resources_history || [];
      return [
        {
          name: "CPU",
          data: points.map((point) => ({
            x: point.timestamp * 1000,
            y: point.cpu,
          })),
        },
        {
          name: "RAM",
          data: points.map((point) => ({
            x: point.timestamp * 1000,
            y: point.memory,
          })),
        },
      ];
    },
    resourceTrendOptions() {
      return {
        chart: {
          toolbar: { show: false },
          zoom: { enabled: false },
          foreColor: "#5f6b7a",
          fontFamily: "inherit",
        },
        stroke: {
          curve: "smooth",
          width: 3.5,
        },
        colors: ["#2f8de4", "#20a26d"],
        dataLabels: { enabled: false },
        markers: {
          size: 0,
          hover: { sizeOffset: 4 },
        },
        fill: {
          type: "gradient",
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.32,
            opacityTo: 0.06,
          },
        },
        grid: {
          borderColor: "#edf0f4",
          strokeDashArray: 5,
        },
        xaxis: {
          type: "datetime",
          labels: {
            datetimeUTC: false,
            style: {
              fontSize: "11px",
            },
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          labels: {
            style: {
              fontSize: "11px",
            },
            formatter(value) {
              return `${Math.round(value)}%`;
            },
          },
        },
        legend: {
          position: "top",
          horizontalAlign: "left",
          fontSize: "12px",
          markers: {
            radius: 12,
          },
        },
        tooltip: {
          x: { format: "HH:mm:ss" },
          y: {
            formatter(value) {
              return `${Math.round(value)}%`;
            },
          },
        },
      };
    },
    backupHealthSeries() {
      return [
        {
          name: "Health",
          data: (this.chartData.backup_health_history || []).map((item) => item.health_score),
        },
      ];
    },
    backupHealthOptions() {
      const points = this.chartData.backup_health_history || [];
      return {
        chart: {
          toolbar: { show: false },
          foreColor: "#5f6b7a",
          fontFamily: "inherit",
        },
        colors: points.map((item) => {
          if (item.status === "ok") return "#20a26d";
          if (item.status === "partial") return "#e7a12d";
          return "#d7584d";
        }),
        plotOptions: {
          bar: {
            borderRadius: 8,
            columnWidth: "54%",
            distributed: true,
          },
        },
        dataLabels: {
          enabled: true,
          offsetY: -8,
          style: {
            fontSize: "11px",
            colors: ["#344054"],
          },
          formatter(value) {
            return `${Math.round(value)}`;
          },
        },
        xaxis: {
          categories: points.map((item) => this.formatCompactDate(item.timestamp)),
          labels: {
            rotate: 0,
            trim: true,
            style: {
              fontSize: "11px",
            },
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          labels: {
            style: {
              fontSize: "11px",
            },
            formatter(value) {
              return `${Math.round(value)}`;
            },
          },
        },
        tooltip: {
          y: {
            formatter(value) {
              return `${value}/100`;
            },
          },
        },
        grid: {
          borderColor: "#edf0f4",
          strokeDashArray: 5,
        },
        legend: { show: false },
      };
    },
    syncDriftSeries() {
      return [
        {
          name: "Ecarts",
          data: (this.chartData.sync_modules || []).map((item) => item.drift_count),
        },
      ];
    },
    syncDriftOptions() {
      const modules = this.chartData.sync_modules || [];
      return {
        chart: {
          type: "bar",
          toolbar: { show: false },
          foreColor: "#5f6b7a",
          fontFamily: "inherit",
        },
        colors: modules.map((item) => (item.drift_count > 0 ? "#d7584d" : "#20a26d")),
        plotOptions: {
          bar: {
            horizontal: true,
            borderRadius: 8,
            barHeight: "58%",
            distributed: true,
          },
        },
        dataLabels: {
          enabled: true,
          textAnchor: "start",
          offsetX: 8,
          style: {
            fontSize: "11px",
            colors: ["#344054"],
          },
          formatter(value) {
            return `${value} ecart${value > 1 ? "s" : ""}`;
          },
        },
        xaxis: {
          categories: modules.map((item) => item.label),
          labels: {
            style: {
              fontSize: "11px",
            },
          },
          min: 0,
          forceNiceScale: true,
        },
        grid: {
          borderColor: "#edf0f4",
          strokeDashArray: 5,
        },
        tooltip: {
          y: {
            formatter(value) {
              return `${value} ecart${value > 1 ? "s" : ""}`;
            },
          },
        },
      };
    },
  },
  mounted() {
    this.hydrateSyncPreferences();
    this.hydrateCachedSyncSummary();
    this.fetchOverview({ skipSyncScan: true, showLoading: false });
    this.fetchLastRestore();
    this.fetchScheduledTasks();
    this.connectLiveSocket();
    this.startAutoRefresh();
    this.startCountdown();
    this.fetchAiAnalysis();
    this._aiPollTimer = window.setInterval(() => this.fetchAiAnalysis(), 8000);
    this.emitter.on("schedule-changed", () => this.fetchScheduledTasks());
  },
  beforeUnmount() {
    this._unmounted = true;
    this.stopAutoRefresh();
    this.stopCountdown();
    if (this._aiPollTimer) { window.clearInterval(this._aiPollTimer); this._aiPollTimer = null; }
    if (this._aiWsDebounce) { window.clearTimeout(this._aiWsDebounce); this._aiWsDebounce = null; }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    if (this.socketReconnectTimer) {
      window.clearTimeout(this.socketReconnectTimer);
      this.socketReconnectTimer = null;
    }
  },
  methods: {
    async fetchAiAnalysis() {
      try {
        const res = await axios.get("/backup/risk-ai-analysis");
        this.aiAnalysis = res.data || { scores: {}, trend: {} };
      } catch (_) { /* keep last value */ }
    },
    openAiRiskCenter(e) {
      try { localStorage.setItem("backup-tab", "AI Risk Center"); } catch {}
      if (this.emitter?.emit) {
        e?.preventDefault?.();
        this.emitter.emit("reload-tabs");
      }
    },
    async fetchLastRestore() {
      try {
        const res = await axios.get("/backup/restore-history");
        const results = res.data?.results || [];
        this.lastRestore = results.find((e) => e.status !== "running") || results[0] || null;
      } catch {
        this.lastRestore = null;
      }
    },
    async fetchScheduledTasks() {
      try {
        const res = await axios.get("/backup/schedule");
        this.scheduledTasks = res.data.tasks || [];
        this._updateNextRunTarget();
      } catch { /* silent */ }
    },
    dismissAutomationNotice(key) {
      this.dismissedAutomationNoticeKey = key;
    },
    taskRunBadge(task) {
      if (task.last_queue_reason !== "missed_run_catchup" || !task.last_queued_for) return null;
      const scheduledAt = new Date(task.last_queued_for);
      const queuedAt = task.last_queued_at ? new Date(task.last_queued_at) : null;
      const referenceTime = queuedAt && !Number.isNaN(queuedAt.getTime()) ? queuedAt : scheduledAt;
      if (Number.isNaN(referenceTime.getTime())) return null;
      if (Date.now() - referenceTime.getTime() > 36 * 60 * 60 * 1000) return null;
      const status = String(task.last_run_status || "").toLowerCase();
      if (status === "ok" || status === "success") {
        return { tone: "ok", label: `rattrape ${this.formatTime(referenceTime)}` };
      }
      if (status === "error" || status === "failed") {
        return { tone: "warning", label: "rattrapage a verifier" };
      }
      return { tone: "info", label: "rattrapage en cours" };
    },
    _updateNextRunTarget() {
      let soonest = null;
      for (const task of this.scheduledTasks.filter((t) => t.enabled)) {
        const nr = this.computeNextRun(task.cron);
        if (nr && (!soonest || nr < soonest)) soonest = nr;
      }
      this.nextRunTarget = soonest;
    },
    computeNextRun(expr) {
      if (!expr) return null;
      const parts = expr.trim().split(/\s+/);
      if (parts.length !== 5) return null;
      const [minPart, hourPart, , , wdayPart] = parts;
      const matchField = (part, val) => {
        if (part === "*") return true;
        if (part.startsWith("*/")) return val % parseInt(part.slice(2)) === 0;
        return parseInt(part) === val;
      };
      const check = new Date();
      check.setSeconds(0, 0);
      check.setTime(check.getTime() + 60000);
      const limit = new Date(check.getTime() + 8 * 24 * 60 * 60 * 1000);
      while (check < limit) {
        if (
          matchField(minPart, check.getMinutes()) &&
          matchField(hourPart, check.getHours()) &&
          matchField(wdayPart, check.getDay())
        ) {
          return new Date(check);
        }
        check.setTime(check.getTime() + 60000);
      }
      return null;
    },
    cronHumanShort(expr) {
      if (!expr) return "—";
      const parts = expr.trim().split(/\s+/);
      if (parts.length !== 5) return expr;
      const [min, hour, , , weekday] = parts;
      if (min.startsWith("*/") && hour === "*") return `toutes les ${min.slice(2)} min`;
      if (min === "0" && hour.startsWith("*/")) return `toutes les ${hour.slice(2)}h`;
      if (!min.includes("*") && !hour.includes("*") && weekday === "*")
        return `chaque jour à ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
      if (!min.includes("*") && !hour.includes("*") && !weekday.includes("*")) {
        const days = ["dim", "lun", "mar", "mer", "jeu", "ven", "sam"];
        return `chaque ${days[parseInt(weekday)] || weekday} à ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
      }
      return expr;
    },
    startCountdown() {
      this._countdownInterval = setInterval(() => {
        const target = this.nextRunTarget;
        if (!target) { this.countdown = { h: 0, m: 0, s: 0 }; return; }
        const diff = Math.max(0, target.getTime() - Date.now());
        if (diff < 60000) this._updateNextRunTarget();
        this.countdown = {
          h: Math.floor(diff / 3600000),
          m: Math.floor((diff % 3600000) / 60000),
          s: Math.floor((diff % 60000) / 1000),
        };
      }, 1000);
    },
    stopCountdown() {
      if (this._countdownInterval) {
        clearInterval(this._countdownInterval);
        this._countdownInterval = null;
      }
    },
    goToScheduleTab() {
      localStorage.setItem("backup-tab", "Schedule");
      this.emitter?.emit("reload-tabs");
    },
    timeUntil(date) {
      if (!date) return "—";
      const diff = Math.max(0, date.getTime() - Date.now());
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      if (h > 0) return `${h}h ${m}m`;
      if (m > 0) return `${m}m`;
      return "< 1m";
    },
    setCsrfHeader() {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    },
    setLoadingState(title, message) {
      this.loadingTitle = title || "Please Wait...";
      this.loadingMessage = message || "Chargement en cours...";
      this.loading = true;
    },
    startAutoRefresh() {
      this.stopAutoRefresh();
      this.autoRefreshTimer = window.setInterval(() => {
        this.fetchOverview({ skipSyncScan: true, showLoading: false });
      }, 45000);
    },
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        window.clearInterval(this.autoRefreshTimer);
        this.autoRefreshTimer = null;
      }
    },
    async fetchOverview(options = {}) {
      const {
        loadingTitle = "Please Wait...",
        loadingMessage = "Chargement en cours...",
        showLoading = true,
        skipSyncScan = false,
      } = options;
      if (showLoading) {
        this.setLoadingState(loadingTitle, loadingMessage);
        this.loading = true;
      }
      try {
        const params = {};
        if (this.selectedSyncComponents.length) {
          params.components = this.selectedSyncComponents.join(",");
        }
        if (skipSyncScan) {
          params.skip_sync_scan = 1;
        }
        const response = await axios.get("/backup/dashboard-overview", { params });
        const nextOverview = response.data || this.overview;
        nextOverview.sync = this.resolveSyncSummaryForDisplay(nextOverview.sync, skipSyncScan);
        this.overview = nextOverview;
        this.updateLiveMetrics(response.data?.live_metrics);
        this.fetchDrpMetrics();
        this.lastRefreshedAt = Date.now();
        const syncedSelection = this.overview.sync?.selected_components || [];
        if (syncedSelection.length) {
          this.selectedSyncComponents = syncedSelection;
          this.persistSyncPreferences();
        }
      } catch (error) {
        this.notify("Impossible de charger le dashboard backup.", "error");
      } finally {
        if (showLoading) {
          this.loading = false;
        }
      }
    },
    async fetchDrpMetrics() {
      try {
        const response = await axios.get("/backup/metrics");
        this.drpMetrics = response.data || null;
      } catch (error) {
        this.drpMetrics = null;
      }
    },
    hasUsableSyncSummary(summary) {
      return Boolean(
        summary &&
        summary.last_check_at &&
        Array.isArray(summary.modules) &&
        summary.modules.length &&
        summary.status !== "idle" &&
        summary.verification_mode !== "manual_on_demand"
      );
    },
    isIdleSyncSummary(summary) {
      return !summary || summary.status === "idle" || summary.verification_mode === "manual_on_demand";
    },
    cloneSyncSummary(summary, extra = {}) {
      return {
        ...JSON.parse(JSON.stringify(summary || {})),
        ...extra,
      };
    },
    resolveSyncSummaryForDisplay(incomingSync, skipSyncScan = false) {
      if (this.hasUsableSyncSummary(incomingSync)) {
        this.cachedSyncSummary = this.cloneSyncSummary(incomingSync);
        this.persistCachedSyncSummary();
        return incomingSync;
      }

      const fallback = this.cachedSyncSummary;
      if ((skipSyncScan || this.isIdleSyncSummary(incomingSync)) && this.hasUsableSyncSummary(fallback)) {
        return this.cloneSyncSummary(fallback, {
          _retained_from_last_scan: true,
          _idle_refresh_scope_label: incomingSync?.scope_label,
        });
      }

      return incomingSync || {};
    },
    persistCachedSyncSummary() {
      if (!this.hasUsableSyncSummary(this.cachedSyncSummary)) return;
      try {
        localStorage.setItem("backup-last-sync-summary", JSON.stringify(this.cachedSyncSummary));
      } catch { /* storage unavailable */ }
    },
    hydrateCachedSyncSummary() {
      try {
        const stored = JSON.parse(localStorage.getItem("backup-last-sync-summary") || "null");
        if (this.hasUsableSyncSummary(stored)) {
          this.cachedSyncSummary = stored;
          this.overview.sync = this.cloneSyncSummary(stored, { _retained_from_last_scan: true });
        }
      } catch {
        this.cachedSyncSummary = null;
      }
    },
    async refreshDashboardAnalysis() {
      await this.fetchOverview({
        loadingTitle: "Please Wait...",
        loadingMessage: "Analyse de synchronisation en cours...",
      });
      await this.scrollToSyncResults();
      this.notify(`Analyse relancee sur ${this.syncSelectedCount} composant${this.syncSelectedCount > 1 ? "s" : ""}.`);
    },
    async scrollToSyncResults() {
      await nextTick();
      const target = this.$refs.syncResultsStart;
      if (target?.scrollIntoView) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    },
    hydrateSyncPreferences() {
      try {
        const storedMonitoringTab = localStorage.getItem("backup-monitoring-tab");
        if (["overview", "analytics"].includes(storedMonitoringTab)) {
          this.activeMonitoringTab = storedMonitoringTab;
        }
        const storedComponents = JSON.parse(localStorage.getItem("backup-sync-components") || "[]");
        if (Array.isArray(storedComponents)) {
          this.selectedSyncComponents = storedComponents.filter((item) => typeof item === "string");
        }
        const storedViewMode = localStorage.getItem("backup-sync-view-mode");
        if (["all", "drift", "ok"].includes(storedViewMode)) {
          this.syncViewMode = storedViewMode;
        }
      } catch (error) {
        this.selectedSyncComponents = [];
        this.syncViewMode = "all";
      }
    },
    setMonitoringTab(tab) {
      if (!["overview", "analytics"].includes(tab)) return;
      this.activeMonitoringTab = tab;
      localStorage.setItem("backup-monitoring-tab", tab);
    },
    persistSyncPreferences() {
      localStorage.setItem("backup-sync-components", JSON.stringify(this.selectedSyncComponents));
      localStorage.setItem("backup-sync-view-mode", this.syncViewMode);
    },
    syncComponentMeta(key) {
      const meta = {
        services: {
          label: "Services & VM",
          short: "SRV",
          description: "Verifie les services critiques de la plateforme, l'etat VM et les checks runtime essentiels.",
        },
        firewall: {
          label: "Firewall",
          short: "FW",
          description: "Controle si les regles firewall actives en base sont bien deployees dans nftables.",
        },
        network: {
          label: "Reseau",
          short: "NET",
          description: "Compare interfaces, adresses et objets reseau entre systeme reel et base.",
        },
        nat: {
          label: "NAT",
          short: "NAT",
          description: "Compare les regles de translation d'adresses entre nftables et la base.",
        },
        vpn: {
          label: "VPN",
          short: "VPN",
          description: "Controle OpenVPN et IPsec, plus les regles systeme liees aux tunnels.",
        },
        ids_ips: {
          label: "IDS / IPS",
          short: "IDS",
          description: "Verifie Suricata, ses interfaces et sa presence effective sur le systeme.",
        },
        proxy: {
          label: "Proxy",
          short: "PRX",
          description: "Compare Squid, ACL, utilisateurs et etat de publication avec la base.",
        },
      };
      return meta[key] || {
        label: key,
        short: String(key || "?").slice(0, 3).toUpperCase(),
        description: "Composant de synchronisation personnalise.",
      };
    },
    integrityStatusLabel(status) {
      if (status === "success") return "OK";
      if (status === "failed") return "failed";
      if (status === "skipped") return "skipped";
      return status || "inconnu";
    },
    serviceCategoryLabel(category) {
      const labels = {
        access: "acces",
        platform: "plateforme",
        data: "data",
        security: "securite",
        network: "reseau",
        application: "metier",
        vm: "vm",
        system: "systeme",
        backup: "backup",
      };
      return labels[category] || category || "service";
    },
    servicePulseReason(service) {
      if (!service.running && service.manageable) {
        return "Service critique a relancer ou verifier rapidement.";
      }
      if (!service.running && !service.manageable) {
        return "Check machine ou stockage a surveiller.";
      }
      return "Service prioritaire actuellement stable.";
    },
    isSyncComponentSelected(componentKey) {
      return this.selectedSyncComponents.includes(componentKey);
    },
    toggleSyncComponent(componentKey) {
      if (this.isSyncComponentSelected(componentKey)) {
        if (this.selectedSyncComponents.length === 1) return;
        this.selectedSyncComponents = this.selectedSyncComponents.filter((item) => item !== componentKey);
      } else {
        this.selectedSyncComponents = [...this.selectedSyncComponents, componentKey];
      }
      this.persistSyncPreferences();
    },
    handleSyncComponentCardClick(componentKey) {
      const existingModule = this.syncModules.find((module) => module.key === componentKey);
      if (existingModule) {
        this.scrollToSyncModule(componentKey);
        return;
      }
      this.toggleSyncComponent(componentKey);
    },
    applySyncPreset(preset) {
      const validComponents = preset.components.filter((component) =>
        this.availableSyncComponents.some((item) => item.key === component)
      );
      if (!validComponents.length) return;
      this.selectedSyncComponents = validComponents;
      this.persistSyncPreferences();
    },
    selectAllSyncComponents() {
      this.selectedSyncComponents = this.availableSyncComponents.map((component) => component.key);
      this.persistSyncPreferences();
    },
    setSyncViewMode(mode, options = {}) {
      this.syncViewMode = mode;
      this.persistSyncPreferences();
      if (options.scrollToResults) {
        nextTick(() => {
          if (options.focusFirst) {
            const firstModule = this.filteredSyncModules[0];
            if (firstModule?.key) {
              this.scrollToSyncModule(firstModule.key);
              return;
            }
          }
          this.scrollToSyncResults();
        });
      }
    },
    scrollToSyncModule(moduleKey) {
      const target = document.getElementById(`sync-module-${moduleKey}`);
      if (target?.scrollIntoView) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      } else {
        this.scrollToSyncResults();
      }
    },
    updateLiveMetrics(data) {
      if (!data) return;
      this.liveMetrics = {
        cpu: Math.round(Number(data.cpu_percentage || data.cpu || 0)),
        memory: Math.round(Number(data.memory_percentage || data.memory || 0)),
        uptime: data.uptime || "",
        loadAverage: data.load_average || data.loadAverage || "",
        currentDate: data.current_date || data.currentDate || "",
      };
    },
    connectLiveSocket() {
      if (this.socket && this.socket.readyState < 2) return;
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      this.socket = new WebSocket(`${protocol}://${window.location.host}/ws/data/`);

      this.socket.onopen = () => {
        this.socketRetryCount = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          this.updateLiveMetrics(JSON.parse(event.data));
          // Push-driven AI refresh: ~2s after each WS frame
          if (!this._aiWsDebounce) {
            this._aiWsDebounce = window.setTimeout(() => {
              this._aiWsDebounce = null;
              this.fetchAiAnalysis();
            }, 2000);
          }
        } catch (error) {
          console.error("backup dashboard live parse error", error);
        }
      };

      this.socket.onerror = () => {
        this.socket?.close();
      };

      this.socket.onclose = () => {
        if (!this._unmounted && this.socketRetryCount < this.socketMaxRetries) {
          this.socketRetryCount += 1;
          const retryDelay = Math.min(30000, 5000 * this.socketRetryCount);
          this.socketReconnectTimer = window.setTimeout(() => {
            this.socketReconnectTimer = null;
            this.connectLiveSocket();
          }, retryDelay);
        }
      };
    },
    alertKey(alert) {
      return `${alert.severity}-${alert.service}-${alert.message}-${alert.time}`;
    },
    ignoreAlert(alert) {
      this.ignoredAlerts = [...this.ignoredAlerts, this.alertKey(alert)];
    },
    async triggerAlertAction(alert) {
      if (!alert?.action) return;

      if (alert.action === "restart_service") {
        await this.restartService(alert.service);
        return;
      }

      if (alert.action === "create_backup") {
        await this.createBackup();
        return;
      }

      if (alert.action === "open_backup") {
        this.goToBackupsTab();
      }
    },
    goToBackupsTab() {
      localStorage.setItem("backup-tab", "Backups");
      if (this.emitter?.emit) {
        this.emitter.emit("reload-tabs");
      }
    },
    async createBackup() {
      this.setLoadingState("Please Wait...", "Creation du backup en cours...");
      this.setCsrfHeader();
      try {
        const response = await axios.post("/backup/create-full-backup");
        this.notify(response.data.message || "Backup lance.");
        localStorage.setItem("backup-tab", "Backups");
        if (this.emitter?.emit) {
          this.emitter.emit("reload-tabs");
        }
        await this.fetchOverview({ skipSyncScan: true, showLoading: false });
      } catch (error) {
        this.notify(
          error.response?.data?.message || "Erreur lors du lancement du backup.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    async startService(service) {
      await this.runServiceAction(service, "start");
    },
    async restartService(service) {
      await this.runServiceAction(service, "restart");
    },
    async runServiceAction(service, action) {
      this.setLoadingState(
        "Please Wait...",
        `${action === "restart" ? "Redemarrage" : "Demarrage"} de ${service} en cours...`
      );
      this.setCsrfHeader();
      try {
        const response = await axios.put("/monitoring/action", { service, action });
        this.notify(response.data.msg || `${service} ${action}`);
        await this.fetchOverview({ skipSyncScan: true, showLoading: false });
        await new Promise((resolve) => {
          window.setTimeout(resolve, 1200);
        });
        await this.fetchOverview({ skipSyncScan: true, showLoading: false });
      } catch (error) {
        this.notify(
          error.response?.data?.msg || `Impossible de ${action} ${service}.`,
          "error"
        );
        await this.fetchOverview({ skipSyncScan: true, showLoading: false });
      } finally {
        this.loading = false;
      }
    },
    statusMetricLabel(status) {
      if (status === "error" || status === "failed") return "Echec";
      if (status === "partial") return "Incomplet";
      return "OK";
    },
    statusMetricClass(status) {
      if (status === "error" || status === "failed") return "error";
      if (status === "partial") return "warning";
      return "ok";
    },
    meterTone(value) {
      const v = Number(value || 0);
      if (v >= 90) return "error";
      if (v >= 70) return "warning";
      return "ok";
    },
    loadToneClass(value) {
      if (value === null || value === undefined) return "tone-neutral";
      if (value >= 4) return "tone-error";
      if (value >= 2) return "tone-warning";
      return "tone-ok";
    },
    loadAverageShortText(value) {
      if (value === null || value === undefined) return "—";
      if (value < 1) return "léger";
      if (value < 2) return "modéré";
      if (value < 4) return "élevé";
      return "saturé";
    },
    setAlertsFilter(filter) {
      this.alertsFilter = filter;
    },
    scoreItemClass(value) {
      const v = Number(value || 0);
      if (v >= 85) return "ok";
      if (v >= 60) return "warning";
      return "error";
    },
    scoreItemFriendlyLabel(item) {
      const map = {
        backup_health: "Qualité des sauvegardes",
        backup: "Qualité des sauvegardes",
        sync: "Cohérence du système",
        synchronisation: "Cohérence du système",
        services: "Services en fonctionnement",
        freshness: "Fraîcheur des sauvegardes",
        fraicheur: "Fraîcheur des sauvegardes",
      };
      return map[item.key] || item.label || item.key;
    },
    scoreItemHint(item) {
      const v = Number(item.value || 0);
      const map = {
        backup_health: v >= 85 ? "Vos archives sont complètes et saines." : v >= 60 ? "Quelques composants de backup sont à vérifier." : "Des problèmes ont été détectés dans vos archives.",
        backup: v >= 85 ? "Vos archives sont complètes et saines." : v >= 60 ? "Quelques composants de backup sont à vérifier." : "Des problèmes ont été détectés dans vos archives.",
        sync: v >= 85 ? "Le système correspond bien à la base de données." : v >= 60 ? "Des petits écarts ont été détectés." : "Des différences importantes entre le système et la base.",
        synchronisation: v >= 85 ? "Le système correspond bien à la base de données." : v >= 60 ? "Des petits écarts ont été détectés." : "Des différences importantes entre le système et la base.",
        services: v >= 85 ? "Tous les services critiques fonctionnent." : v >= 60 ? "Certains services sont dégradés." : "Des services critiques sont arrêtés ou en erreur.",
        freshness: v >= 85 ? "Vos sauvegardes sont récentes et régulières." : v >= 60 ? "La dernière sauvegarde date un peu." : "Vos sauvegardes sont trop anciennes.",
        fraicheur: v >= 85 ? "Vos sauvegardes sont récentes et régulières." : v >= 60 ? "La dernière sauvegarde date un peu." : "Vos sauvegardes sont trop anciennes.",
      };
      const hint = map[item.key];
      if (hint) return `${hint} Représente ${item.weight_percent}% du score total.`;
      return `Représente ${item.weight_percent}% du score total.`;
    },
    moduleFriendlyLabel(key) {
      return this.syncComponentMeta(key).description;
    },
    alertTitle(alert) {
      return `${alert.service} — ${alert.message}`;
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
    formatTime(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    formatSize(bytes) {
      const value = Number(bytes || 0);
      if (!value) return "0 B";
      const units = ["B", "KB", "MB", "GB", "TB"];
      let size = value;
      let unitIndex = 0;
      while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex += 1;
      }
      const precision = size >= 10 || unitIndex === 0 ? 0 : 1;
      return `${size.toFixed(precision)} ${units[unitIndex]}`;
    },
    shortBackupLabel(value) {
      if (!value) return "-";
      const parts = String(value).split("_");
      return parts.slice(-2).join(" ");
    },
    formatCompactDate(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "-";
      return date.toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
      });
    },
    diskUsagePercent(used, total) {
      const totalValue = Number(total || 0);
      if (!totalValue) return 0;
      return Math.round((Number(used || 0) / totalValue) * 100);
    },
    notify(message, color = "success") {
      this.snackbarText = message;
      this.snackbarColor = color;
      this.snackbar = true;
    },
  },
};
</script>

<style scoped>
.drp-live-strip {
  margin: 0 0 18px;
  padding: 14px;
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.drp-live-strip--ok {
  border-color: #bbf7d0;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 48%);
}

.drp-live-strip--warning {
  border-color: #fde68a;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 48%);
}

.drp-live-strip--error {
  border-color: #fecaca;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 48%);
}

.drp-live-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.drp-live-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.drp-live-title strong {
  display: block;
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
}

.drp-live-title small,
.drp-live-updated {
  color: #64748b;
  font-size: 12px;
}

.drp-live-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.13);
  flex: 0 0 auto;
}

.drp-live-strip--warning .drp-live-dot {
  background: #f59e0b;
  box-shadow: 0 0 0 5px rgba(245, 158, 11, 0.16);
}

.drp-live-strip--error .drp-live-dot {
  background: #ef4444;
  box-shadow: 0 0 0 5px rgba(239, 68, 68, 0.16);
}

.drp-live-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.drp-live-btn {
  height: 30px;
  padding: 0 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #f8fafc;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
}

.drp-live-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.drp-metric-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.drp-metric-card {
  min-width: 0;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
}

.drp-metric-label {
  display: block;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.drp-metric-card strong {
  display: block;
  margin-top: 5px;
  color: #0f172a;
  font-size: 22px;
  font-weight: 900;
  line-height: 1.1;
}

.drp-metric-card small {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drp-metric-bar {
  height: 5px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.drp-metric-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #22c55e;
}

.drp-metric-card.tone-warning .drp-metric-bar span {
  background: #f59e0b;
}

.drp-metric-card.tone-error .drp-metric-bar span {
  background: #ef4444;
}

.drp-metric-card.tone-warning strong {
  color: #b45309;
}

.drp-metric-card.tone-error strong {
  color: #b91c1c;
}

@media (max-width: 1100px) {
  .drp-metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .drp-live-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .drp-live-actions {
    width: 100%;
    justify-content: space-between;
  }

  .drp-metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
