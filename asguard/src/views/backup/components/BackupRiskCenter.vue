<template>
  <div class="rc-cockpit" :class="riskLevelClass">

    <!-- Animated mesh background -->
    <div class="rc-mesh">
      <div class="rc-mesh-blob rc-mesh-1"></div>
      <div class="rc-mesh-blob rc-mesh-2"></div>
      <div class="rc-mesh-blob rc-mesh-3"></div>
    </div>

    <!-- ═══════════════ AI COMMAND HERO — particle core + diagnostic ═══════════════ -->
    <header class="rc-command">
      <!-- LEFT: the signature particle core IS the hero -->
      <div class="rc-command-left">
        <RiskParticleField :score="score" :level="level" style="height:100%; min-height:340px;" />
        <div class="rc-command-overlay">
          <span class="rc-pulse-pill" :class="riskLevelClass">
            <span class="rc-pulse-dot"></span>{{ riskLevelLabel }}
          </span>
          <span class="rc-overlay-since">{{ stableSinceLabel }}</span>
        </div>
        <div class="rc-command-delta" :class="deltaClass">
          <i :class="deltaIcon"></i>{{ deltaLabel }}
        </div>
      </div>

      <!-- RIGHT: AI diagnostic -->
      <div class="rc-command-right">
        <h1 class="rc-headline">{{ heroTitle }}</h1>
        <div class="rc-ai-speech">
          <div class="rc-ai-avatar">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M9.5 2A2.5 2.5 0 0 0 7 4.5v15A2.5 2.5 0 0 0 9.5 22h5a2.5 2.5 0 0 0 2.5-2.5v-15A2.5 2.5 0 0 0 14.5 2z"/>
              <circle cx="12" cy="10" r="1.5" fill="currentColor"/>
              <path d="M9 14h6M10 17h4"/>
            </svg>
            <span class="rc-ai-think"></span>
          </div>
          <div class="rc-ai-bubble">
            <p>{{ ai.explanation || 'Analyse des signaux en cours…' }}</p>
            <p v-if="predictiveLabel" class="rc-ai-eta">{{ predictiveLabel }}</p>
            <small>Moteur prédictif Asguard · analyse en temps réel</small>
          </div>
        </div>
        <div class="rc-duo">
          <div class="rc-duo-card" :class="trendClass">
            <i :class="trendIcon"></i>
            <div><span>Tendance</span><strong>{{ trendLabel }}</strong><small>{{ trendDetail }}</small></div>
          </div>
          <div class="rc-duo-card">
            <i class="mdi mdi-radar"></i>
            <div><span>Projection 15 min</span><strong :class="forecastClass">{{ ai.trend.forecast_15min ?? score }}<em>/100</em></strong><small>fiabilité {{ Math.round((ai.trend.confidence || 0.5) * 100) }}%</small></div>
          </div>
        </div>
      </div>
    </header>

    <!-- ═══════════════ MODULES IA — each block is an intelligent tool ═══════════════ -->
    <section class="rc-tools">
      <div class="rc-tool">
        <div class="rc-tool-icon"><i class="mdi mdi-radar"></i></div>
        <div class="rc-tool-body">
          <span>Moteur prédictif</span>
          <strong :class="forecastClass">{{ ai.trend?.forecast_15min ?? score }}<em>/100 à 15 min</em></strong>
        </div>
        <span class="rc-tool-dot rc-dot-on"></span>
      </div>
      <div class="rc-tool" :class="{ 'rc-tool-alert': anomalyCount > 0 }">
        <div class="rc-tool-icon"><i class="mdi mdi-flash"></i></div>
        <div class="rc-tool-body">
          <span>Détecteur d'anomalies</span>
          <strong>{{ anomalyCount }}<em>signal(s) hors normal</em></strong>
        </div>
        <span class="rc-tool-dot" :class="anomalyCount > 0 ? 'rc-dot-warn' : 'rc-dot-on'"></span>
      </div>
      <div class="rc-tool" :class="{ 'rc-tool-alert': (ai.compound?.count || 0) >= 2 }">
        <div class="rc-tool-icon"><i class="mdi mdi-vector-link"></i></div>
        <div class="rc-tool-body">
          <span>Risque composé</span>
          <strong>{{ ai.compound?.count || 0 }}<em>signaux corrélés</em></strong>
        </div>
        <span class="rc-tool-dot" :class="(ai.compound?.count || 0) >= 2 ? 'rc-dot-warn' : 'rc-dot-on'"></span>
      </div>
      <div class="rc-tool" :class="capacityClass && 'rc-tool-alert'">
        <div class="rc-tool-icon"><i class="mdi mdi-harddisk"></i></div>
        <div class="rc-tool-body">
          <span>Prévision capacité</span>
          <strong>{{ ai.capacity?.disk_pct ?? 0 }}%<em>{{ capacityLabel }}</em></strong>
        </div>
        <span class="rc-tool-dot" :class="capacityClass ? 'rc-dot-warn' : 'rc-dot-on'"></span>
      </div>
      <div class="rc-tool" :class="{ 'rc-tool-alert': playbook.length > 0 }">
        <div class="rc-tool-icon"><i class="mdi mdi-auto-fix"></i></div>
        <div class="rc-tool-body">
          <span>Auto-remédiation</span>
          <strong>{{ playbook.length }}<em>action(s) prête(s)</em></strong>
        </div>
        <span class="rc-tool-dot" :class="playbook.length ? 'rc-dot-warn' : 'rc-dot-on'"></span>
      </div>
      <div class="rc-tool">
        <div class="rc-tool-icon"><i class="mdi mdi-speedometer"></i></div>
        <div class="rc-tool-body">
          <span>Analyse de dérive</span>
          <strong>{{ slopeDisplay }}<em>pts/min · {{ trendLabel }}</em></strong>
        </div>
        <span class="rc-tool-dot rc-dot-on"></span>
      </div>
    </section>

    <!-- ═══════════════ AUTO-PILOT — autonomous remediation ═══════════════ -->
    <section class="rc-autopilot">
      <article class="rc-panel rc-ap-panel" :class="{ 'rc-ap-on': autopilot.config.enabled }">
        <div class="rc-ap-left">
          <div class="rc-ap-head">
            <div class="rc-ap-icon"><i class="mdi mdi-robot"></i></div>
            <div class="rc-ap-title">
              <span class="rc-kicker">Auto-Pilot</span>
              <h2>Réparation autonome</h2>
            </div>
            <button class="rc-ap-switch" :class="{ on: autopilot.config.enabled }"
                    type="button" @click="toggleAutopilot"
                    :aria-label="autopilot.config.enabled ? 'Désactiver' : 'Activer'">
              <span class="rc-ap-knob"></span>
            </button>
          </div>
          <p class="rc-ap-desc">
            Activé, le moteur <strong>détecte et corrige seul</strong> : service critique arrêté → relance ·
            mémoire saturée → libération des caches · disque plein → purge des journaux.
            Chaque intervention est <strong>notifiée</strong> et <strong>journalisée</strong>, avec un délai
            anti-boucle de {{ autopilot.config.cooldown_min || 30 }} min.
          </p>
          <div class="rc-ap-rules">
            <span :class="{ on: autopilot.config.rules?.services }"><i class="mdi mdi-cog-refresh"></i>Services</span>
            <span :class="{ on: autopilot.config.rules?.ram }"><i class="mdi mdi-memory"></i>RAM ≥ {{ autopilot.config.ram_threshold_pct || 90 }}%</span>
            <span :class="{ on: autopilot.config.rules?.disk }"><i class="mdi mdi-harddisk"></i>Disque ≥ {{ autopilot.config.disk_threshold_pct || 90 }}%</span>
          </div>
        </div>
        <div class="rc-ap-journal">
          <div class="rc-ap-journal-head">
            <strong><i class="mdi mdi-history"></i> Journal des interventions</strong>
            <span>{{ autopilot.interventions || 0 }} au total</span>
          </div>
          <div v-if="!autopilot.journal.length" class="rc-ap-empty">
            {{ autopilot.config.enabled
               ? '✅ Aucune intervention nécessaire — le système est sain.'
               : 'Active l’Auto-Pilot pour que l’IA répare toute seule.' }}
          </div>
          <div v-for="(e, i) in autopilot.journal.slice(0, 5)" :key="i"
               class="rc-ap-entry" :class="e.ok ? 'ok' : 'ko'">
            <i :class="e.ok ? 'mdi mdi-check-circle' : 'mdi mdi-alert-circle'"></i>
            <div class="rc-ap-entry-body">
              <strong>{{ e.title }}</strong>
              <small>{{ e.trigger }}</small>
            </div>
            <span class="rc-ap-ts">{{ new Date(e.ts).toLocaleTimeString() }}</span>
          </div>
        </div>
      </article>
    </section>

    <!-- ═══════════════ RISK TIMELINE + INSIGHTS (new) ═══════════════ -->
    <section class="rc-timeline-row">
      <article class="rc-panel rc-timeline-panel">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">Chronologie</span>
            <h2>Risque — {{ riskTimeline.length }} dernières mesures</h2>
          </div>
          <span class="rc-live-pill"><span class="rc-live-dot"></span>Live</span>
        </div>
        <div class="rc-wave">
          <svg :viewBox="`0 0 ${riskWave.W} ${riskWave.H}`" preserveAspectRatio="none" class="rc-wave-svg">
            <defs>
              <linearGradient :id="waveGradId" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" :stop-color="waveColor" stop-opacity="0.38"/>
                <stop offset="60%" :stop-color="waveColor" stop-opacity="0.10"/>
                <stop offset="100%" :stop-color="waveColor" stop-opacity="0"/>
              </linearGradient>
              <filter :id="waveGlowId" x="-20%" y="-40%" width="140%" height="180%">
                <feGaussianBlur stdDeviation="2.5" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
            </defs>
            <!-- threshold guides -->
            <line v-for="t in riskWave.thresholds" :key="t.label"
                  x1="0" :y1="t.y" :x2="riskWave.W" :y2="t.y"
                  :stroke="t.c" stroke-width="1" stroke-dasharray="3 6" opacity="0.45"
                  vector-effect="non-scaling-stroke"/>
            <path v-if="riskWave.area" :d="riskWave.area" :fill="`url(#${waveGradId})`"/>
            <path v-if="riskWave.line" :d="riskWave.line" fill="none" :stroke="waveColor"
                  stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                  :filter="`url(#${waveGlowId})`" vector-effect="non-scaling-stroke"/>
            <circle v-if="riskWave.line" :cx="riskWave.dotX" :cy="riskWave.dotY" r="6"
                    :fill="waveColor" class="rc-wave-ping" vector-effect="non-scaling-stroke"/>
            <circle v-if="riskWave.line" :cx="riskWave.dotX" :cy="riskWave.dotY" r="3.5"
                    fill="#fff" :stroke="waveColor" stroke-width="2.5" vector-effect="non-scaling-stroke"/>
          </svg>
          <div v-if="!riskTimeline.length" class="rc-heat-empty">Collecte de l'historique…</div>
          <div class="rc-wave-scale"><span>100</span><span>75</span><span>55</span><span>35</span><span>0</span></div>
        </div>
        <div class="rc-heat-legend">
          <span><i class="rc-dot rc-band-watch"></i>Seuil surveiller (35)</span>
          <span><i class="rc-dot rc-band-high"></i>Élevé (55)</span>
          <span><i class="rc-dot rc-band-critical"></i>Critique (75)</span>
        </div>
        <div class="rc-insight-row">
          <div class="rc-insight">
            <span>Ton normal</span><strong>{{ insight.baseline }}<i>/100</i></strong>
          </div>
          <div class="rc-insight" :class="insight.vs_normal > 0 ? 'rc-ins-up' : (insight.vs_normal < 0 ? 'rc-ins-down' : '')">
            <span>Écart vs normal</span><strong>{{ insight.vs_normal > 0 ? '+' : '' }}{{ insight.vs_normal }}<i>pts</i></strong>
          </div>
          <div class="rc-insight">
            <span>Pic récent</span><strong>{{ insight.peak }}<i>/100</i></strong>
          </div>
          <div class="rc-insight" :class="`rc-alert-${insight.alert_likelihood}`">
            <span>Probabilité d'alerte</span><strong>{{ insight.alert_likelihood }}</strong>
          </div>
        </div>
      </article>
    </section>

    <!-- ═══════════════ NEURAL NETWORK + LIVE FEED ═══════════════ -->
    <section class="rc-neural-row">

      <!-- Neural network visualization -->
      <article class="rc-panel rc-neural">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">Analyse neurale</span>
            <h2>Pondération des signaux</h2>
          </div>
          <span class="rc-live-pill"><span class="rc-live-dot"></span>Live</span>
        </div>

        <div class="rc-neural-canvas">
          <svg viewBox="0 0 400 280" class="rc-neural-svg">
            <!-- Connection lines -->
            <g class="rc-neural-lines">
              <line v-for="(node, idx) in neuralNodes" :key="`l-${idx}`"
                    x1="200" y1="140"
                    :x2="node.x" :y2="node.y"
                    :stroke-width="1 + node.intensity * 4"
                    :class="`rc-line-${node.tone}`"
                    :style="{ opacity: 0.3 + node.intensity * 0.6 }"/>
            </g>

            <!-- Pulse animation along lines (when intense) -->
            <g class="rc-neural-pulses">
              <circle v-for="(node, idx) in activePulseNodes" :key="`p-${idx}`"
                      r="3" :class="`rc-pulse-${node.tone}`"
                      :style="getPulseStyle(node)"/>
            </g>

            <!-- Central brain -->
            <g class="rc-neural-brain" :class="riskLevelClass">
              <circle cx="200" cy="140" r="42" class="rc-brain-glow"/>
              <circle cx="200" cy="140" r="32" class="rc-brain-core"/>
              <text x="200" y="138" text-anchor="middle" class="rc-brain-num">{{ score }}</text>
              <text x="200" y="155" text-anchor="middle" class="rc-brain-lbl">RISK</text>
            </g>

            <!-- Outer nodes -->
            <g v-for="(node, idx) in neuralNodes" :key="`n-${idx}`" class="rc-neural-node">
              <circle :cx="node.x" :cy="node.y" r="28"
                      :class="['rc-node-bg', `rc-node-${node.tone}`]"/>
              <text :x="node.x" :y="node.y - 4" text-anchor="middle" class="rc-node-name">{{ node.short }}</text>
              <text :x="node.x" :y="node.y + 9" text-anchor="middle" class="rc-node-val">{{ node.value }}</text>
            </g>
          </svg>

          <!-- Legend below -->
          <div class="rc-neural-legend">
            <div v-for="node in neuralNodes" :key="node.name"
                 class="rc-legend-item" :class="`rc-legend-${node.tone}`">
              <span class="rc-legend-dot"></span>
              <span class="rc-legend-name">{{ node.label }}</span>
              <span class="rc-legend-weight">{{ node.weight }}%</span>
            </div>
          </div>
        </div>
      </article>

      <!-- Live activity feed -->
      <article class="rc-panel rc-feed">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">Activité IA</span>
            <h2>Décisions en temps réel</h2>
          </div>
          <button class="rc-icon-btn" :disabled="loading" @click="refresh">
            <i class="mdi mdi-refresh" :class="{ 'rc-spin': loading }"></i>
          </button>
        </div>

        <div class="rc-feed-list">
          <transition-group name="rc-feed-entry">
            <div v-for="entry in feedEntries" :key="entry.id" class="rc-feed-item" :class="`rc-feed-${entry.tone}`">
              <div class="rc-feed-icon"><i :class="entry.icon"></i></div>
              <div class="rc-feed-body">
                <div class="rc-feed-top">
                  <strong>{{ entry.title }}</strong>
                  <small>{{ entry.time }}</small>
                </div>
                <p>{{ entry.message }}</p>
              </div>
            </div>
          </transition-group>
        </div>
      </article>
    </section>

    <!-- ═══════════════ FORECAST CHART ═══════════════ -->
    <section class="rc-panel rc-forecast-panel">
      <div class="rc-panel-head">
        <div>
          <span class="rc-kicker">Projection prédictive</span>
          <h2>Évolution + horizon 15 min</h2>
        </div>
        <div class="rc-forecast-legend">
          <span><span class="rc-leg-dot rc-leg-actual"></span>Mesuré</span>
          <span><span class="rc-leg-dot rc-leg-forecast"></span>Forecast</span>
          <span><span class="rc-leg-dot rc-leg-band"></span>Bande de confiance</span>
        </div>
      </div>
      <apexchart height="280" type="line" :options="forecastChart.options" :series="forecastChart.series"/>
    </section>

    <!-- ═══════════════ CONTRIBUTORS + LIVE METRICS + PLAYBOOK ═══════════════ -->
    <section class="rc-3col">

      <!-- Contributors -->
      <article class="rc-panel">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">Top facteurs</span>
            <h2>Contributeurs au score</h2>
          </div>
        </div>
        <div class="rc-contrib-list">
          <div v-for="(c, idx) in contributors" :key="c.name" class="rc-contrib"
               :class="contribTone(c)">
            <div class="rc-contrib-rank">{{ idx + 1 }}</div>
            <div class="rc-contrib-body">
              <div class="rc-contrib-top">
                <strong>{{ c.label }}</strong>
                <span class="rc-contrib-val">{{ c.value }}</span>
              </div>
              <div class="rc-contrib-bar">
                <div class="rc-contrib-fill" :style="{ width: contribBarWidth(c) }"></div>
                <div class="rc-contrib-glow"></div>
              </div>
              <div class="rc-contrib-foot">
                <span><i class="mdi mdi-gauge"></i>{{ Math.round(c.pressure) }}/100</span>
                <span v-if="c.anomaly > 5" class="rc-anom"><i class="mdi mdi-flash"></i>+{{ Math.round(c.anomaly) }}</span>
              </div>
            </div>
          </div>
        </div>
      </article>

      <!-- Live metrics with sparklines -->
      <article class="rc-panel">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">Signaux temps réel</span>
            <h2>Mesures live</h2>
          </div>
          <span class="rc-live-pill"><span class="rc-live-dot"></span>{{ lastRefreshLabel }}</span>
        </div>
        <div class="rc-metrics-grid">
          <div v-for="m in liveMetricsCards" :key="m.label" class="rc-metric-card" :class="m.tone">
            <div class="rc-metric-top">
              <div class="rc-metric-label">
                <i :class="m.icon"></i>{{ m.label }}
              </div>
              <strong>{{ m.value }}</strong>
            </div>
            <svg class="rc-sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
              <path :d="sparkPath(m.history)" :class="`rc-spark-${m.tone}`" fill="none" stroke-width="1.6"/>
              <path :d="sparkAreaPath(m.history)" :class="`rc-spark-area-${m.tone}`"/>
            </svg>
            <small class="rc-metric-caption">{{ m.caption }}</small>
          </div>
        </div>
      </article>

      <!-- AI Playbook -->
      <article class="rc-panel">
        <div class="rc-panel-head">
          <div>
            <span class="rc-kicker">IA Playbook</span>
            <h2>Actions suggérées</h2>
          </div>
          <span class="rc-count-pill">{{ playbook.length }}</span>
        </div>
        <div class="rc-playbook">
          <div v-for="(action, idx) in playbook" :key="action.title"
               class="rc-action" :class="`rc-action-${action.priority || 'info'}`">
            <div class="rc-action-num">{{ idx + 1 }}</div>
            <div class="rc-action-icon"><i :class="action.icon"></i></div>
            <div class="rc-action-body">
              <strong>{{ action.title }}</strong>
              <small>{{ action.detail }}</small>
              <div v-if="action.action" class="rc-action-btns">
                <button
                  class="rc-btn"
                  :class="action.action_kind === 'intrusive' ? 'rc-btn-warn' : 'rc-btn-primary'"
                  :disabled="!!runningActions[action.action]"
                  @click="runAction(action)"
                >
                  <i v-if="runningActions[action.action]" class="mdi mdi-loading rc-spin"></i>
                  <i v-else :class="action.action_kind === 'intrusive' ? 'mdi mdi-play-protected-content' : 'mdi mdi-play-circle'"></i>
                  {{ action.action_label || 'Exécuter' }}
                </button>
                <button
                  v-if="action.action_secondary"
                  class="rc-btn rc-btn-ghost"
                  :disabled="!!runningActions[action.action_secondary]"
                  @click="runAction(action, true)"
                >
                  <i v-if="runningActions[action.action_secondary]" class="mdi mdi-loading rc-spin"></i>
                  <i v-else class="mdi mdi-magnify"></i>
                  {{ action.action_secondary_label || 'Diagnostiquer' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </article>
    </section>

    <!-- ═══════════════ ACTION RESULTS PANEL ═══════════════ -->
    <section v-if="actionResults.length" class="rc-panel rc-results-panel">
      <div class="rc-panel-head">
        <div>
          <span class="rc-kicker">Résultats actions</span>
          <h2>Sortie des commandes exécutées</h2>
        </div>
      </div>
      <div class="rc-results-list">
        <div v-for="r in actionResults" :key="r.id" class="rc-result" :class="r.ok ? 'rc-result-ok' : 'rc-result-err'">
          <div class="rc-result-head">
            <strong>
              <i :class="r.ok ? 'mdi mdi-check-circle' : 'mdi mdi-alert-circle'"></i>
              {{ r.title }}
            </strong>
            <span class="rc-result-meta">
              <span v-if="r.kind === 'intrusive'" class="rc-result-badge rc-result-intrusive">intrusive</span>
              <small>{{ r.time }}</small>
              <button class="rc-result-close" @click="clearResult(r.id)" title="Fermer"><i class="mdi mdi-close"></i></button>
            </span>
          </div>
          <pre class="rc-result-output">{{ r.output }}</pre>
        </div>
      </div>
    </section>

    <!-- ═══════════════ CONFIRM MODAL ═══════════════ -->
    <div v-if="pendingConfirm" class="rc-modal-backdrop" @click.self="cancelPending">
      <div class="rc-modal">
        <div class="rc-modal-icon"><i class="mdi mdi-alert"></i></div>
        <h3>Confirmer l'action</h3>
        <p>
          Vous allez exécuter <strong>{{ pendingConfirm.title }}</strong>.
          Cette action modifie l'état du système. Continuer&nbsp;?
        </p>
        <div class="rc-modal-actions">
          <button class="rc-btn rc-btn-ghost" @click="cancelPending">Annuler</button>
          <button class="rc-btn rc-btn-warn" @click="confirmPending">
            <i class="mdi mdi-play-protected-content"></i> Exécuter
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import VueApexCharts from "vue3-apexcharts";
import RiskParticleField from "./RiskParticleField.vue";

export default {
  name: "BackupRiskCenter",
  components: { apexchart: VueApexCharts, RiskParticleField },
  setup() {
    const loading = ref(false);
    const lastUpdatedAt = ref(null);
    const pollTimer = ref(null);
    const socket = ref(null);

    const ai = ref({
      model: {}, scores: { smoothed: 0, level: "stable", delta: 0, level_since: null },
      trend: { direction: "stable", forecast_15min: 0, slope_per_min: 0, confidence: 0.5 },
      contributors: [], all_contributors: [], features: {}, history: [],
      recommendations: [], explanation: "", confidence: 60,
    });

    const overview = ref({
      cards: {}, live_metrics: {}, services: [], resources: { backup_disk: {}, root_disk: {} }, alerts: [],
    });

    const liveMetrics = ref({ cpu: 0, memory: 0, uptime: "", loadAverage: "" });
    const liveBuffer = ref({ cpu: [], memory: [], load: [] });
    const feedEntries = ref([]);
    let feedSeq = 0;

    const updateLive = (data) => {
      if (!data) return;
      const newCpu = Math.round(Number(data.cpu_percentage ?? data.cpu ?? liveMetrics.value.cpu ?? 0));
      const newRam = Math.round(Number(data.memory_percentage ?? data.memory ?? liveMetrics.value.memory ?? 0));
      const newLoad = parseFloat(String(data.load_average || data.loadAverage || "0").split(",")[0]) || 0;
      liveMetrics.value = {
        cpu: newCpu, memory: newRam,
        uptime: data.uptime || liveMetrics.value.uptime || "",
        loadAverage: data.load_average || data.loadAverage || liveMetrics.value.loadAverage || "",
      };
      liveBuffer.value.cpu = [...liveBuffer.value.cpu, newCpu].slice(-30);
      liveBuffer.value.memory = [...liveBuffer.value.memory, newRam].slice(-30);
      liveBuffer.value.load = [...liveBuffer.value.load, newLoad].slice(-30);
    };

    const pushFeed = (entry) => {
      feedEntries.value = [{ id: ++feedSeq, time: new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }), ...entry }, ...feedEntries.value].slice(0, 8);
    };

    const refresh = async () => {
      loading.value = true;
      try {
        const [ovRes, aiRes] = await Promise.all([
          axios.get("/backup/dashboard-overview", { params: { skip_sync_scan: 1 } }),
          axios.get("/backup/risk-ai-analysis"),
        ]);
        const prevScore = ai.value.scores?.smoothed || 0;
        overview.value = ovRes.data || overview.value;
        ai.value = { ...ai.value, ...(aiRes.data || {}) };
        updateLive(ovRes.data?.live_metrics);
        lastUpdatedAt.value = new Date();

        // Generate AI feed entry from analysis
        const newScore = ai.value.scores?.smoothed || 0;
        const level = ai.value.scores?.level || "stable";
        const top = ai.value.contributors?.[0];
        const dir = ai.value.trend?.direction;

        if (Math.abs(newScore - prevScore) >= 3) {
          pushFeed({
            tone: newScore > prevScore ? "warn" : "ok",
            icon: newScore > prevScore ? "mdi mdi-trending-up" : "mdi mdi-trending-down",
            title: `Score ${newScore > prevScore ? "↑" : "↓"} ${newScore}`,
            message: top ? `${top.label} (${top.value}) reste le facteur dominant` : "Analyse mise à jour",
          });
        }
        if (top && top.anomaly > 30) {
          pushFeed({
            tone: "warn", icon: "mdi mdi-flash",
            title: `Anomalie ${top.label} détectée`,
            message: `Écart +${Math.round(top.anomaly)} pts vs baseline historique (valeur ${top.value})`,
          });
        }
        if (dir === "rising" && (ai.value.trend?.slope_per_min || 0) > 1.5) {
          pushFeed({
            tone: "warn", icon: "mdi mdi-trending-up",
            title: "Tendance haussière confirmée",
            message: `+${ai.value.trend.slope_per_min} pts/min · forecast ${ai.value.trend.forecast_15min}/100 dans 15 min`,
          });
        }
        if (level === "stable" && newScore < 30 && feedEntries.value.length === 0) {
          pushFeed({
            tone: "ok", icon: "mdi mdi-shield-check",
            title: "Système nominal",
            message: "Tous les signaux sont dans les seuils normaux",
          });
        }
      } catch (e) {
        console.error("risk center refresh", e);
      } finally {
        loading.value = false;
      }
    };

    // Debounce AI refresh so WS frames don't hammer the backend (~1s frames)
    let _wsRefreshTimer = null;
    const scheduleWsRefresh = () => {
      if (_wsRefreshTimer) return;
      _wsRefreshTimer = window.setTimeout(() => {
        _wsRefreshTimer = null;
        refresh();
      }, 2000);
    };

    const connectSocket = () => {
      try {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        socket.value = new WebSocket(`${protocol}://${window.location.host}/ws/data/`);
        socket.value.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            updateLive(data);
            // Push-driven AI: re-evaluate ~2s after a WS frame arrives
            scheduleWsRefresh();
          } catch (err) {}
        };
      } catch (e) { console.error(e); }
    };

    onMounted(() => {
      pushFeed({ tone: "info", icon: "mdi mdi-brain", title: "Assistant analyse initialisé", message: "Moteur d’analyse prêt — signaux en cours" });
      refresh();
      connectSocket();
      // Safety-net poll (WS may be unavailable) — every 8s
      pollTimer.value = window.setInterval(refresh, 8000);
    });

    onBeforeUnmount(() => {
      if (pollTimer.value) window.clearInterval(pollTimer.value);
      if (_wsRefreshTimer) window.clearTimeout(_wsRefreshTimer);
      if (socket.value) socket.value.close();
    });

    // ─────────── action runner (advice / do-it-yourself) ───────────
    const actionResults = ref([]);
    const runningActions = ref({});
    const pendingConfirm = ref(null);

    const _csrf = () => {
      const m = document.cookie.match(/csrftoken=([^;]+)/);
      return m ? m[1] : "";
    };

    const _appendResult = (entry) => {
      actionResults.value = [{
        id: ++feedSeq,
        time: new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        ...entry,
      }, ...actionResults.value].slice(0, 6);
    };

    const _doRun = async (actionKey, opts = {}) => {
      runningActions.value = { ...runningActions.value, [actionKey]: true };
      try {
        const res = await axios.post(`/backup/risk-action/${actionKey}`,
          opts.confirm ? { confirm: true } : {},
          { headers: { "X-CSRFToken": _csrf() } });
        const data = res.data || {};
        _appendResult({
          action: actionKey,
          title: data.title || actionKey,
          kind: data.kind || "safe",
          ok: !!data.ok,
          output: data.output || data.error || "(aucune sortie)",
        });
        pushFeed({
          tone: data.ok ? "ok" : "warn",
          icon: data.ok ? "mdi mdi-check-circle" : "mdi mdi-alert",
          title: `Action: ${data.title || actionKey}`,
          message: data.ok ? "Exécutée avec succès" : (data.error || "Échec"),
        });
        // Force a quick AI re-eval so the UI reflects post-action state
        scheduleWsRefresh();
      } catch (e) {
        const respData = e?.response?.data || {};
        if (respData.needs_confirm) {
          pendingConfirm.value = { action: actionKey, title: respData.title || actionKey };
        } else {
          _appendResult({
            action: actionKey,
            title: respData.title || actionKey,
            kind: "safe",
            ok: false,
            output: respData.error || e.message || "Échec inconnu",
          });
        }
      } finally {
        runningActions.value = { ...runningActions.value, [actionKey]: false };
      }
    };

    const runAction = (rec, secondary = false) => {
      const key = secondary ? rec.action_secondary : rec.action;
      const kind = rec.action_kind || "safe";
      if (!key) return;
      // Intrusive primary action → confirm modal
      if (!secondary && kind === "intrusive") {
        pendingConfirm.value = { action: key, title: rec.action_label || rec.title };
        return;
      }
      _doRun(key);
    };

    const confirmPending = () => {
      if (!pendingConfirm.value) return;
      const key = pendingConfirm.value.action;
      pendingConfirm.value = null;
      _doRun(key, { confirm: true });
    };
    const cancelPending = () => { pendingConfirm.value = null; };
    const clearResult = (id) => {
      actionResults.value = actionResults.value.filter(r => r.id !== id);
    };

    // ─────────── computed ───────────
    const score = computed(() => Math.round(Number(ai.value.scores?.smoothed ?? 0)));
    const scoreTens = computed(() => Math.floor(score.value / 10));
    const scoreOnes = computed(() => score.value % 10);
    const level = computed(() => ai.value.scores?.level || "stable");
    const delta = computed(() => Number(ai.value.scores?.delta || 0));
    // Predictive one-liner: time-to-threshold ETA, else compound-risk warning.
    const predictiveLabel = computed(() => {
      const t = ai.value.trend || {};
      const c = ai.value.compound || {};
      if (t.time_to_critical_min != null)
        return `⏱ Niveau critique dans ~${t.time_to_critical_min} min si la tendance se maintient`;
      if (t.time_to_high_min != null)
        return `⏱ Niveau élevé dans ~${t.time_to_high_min} min si la tendance se maintient`;
      if ((c.count || 0) >= 2)
        return `⚡ ${c.count} signaux sous tension simultanément — risque composé`;
      return "";
    });
    // Disk capacity forecast (days-to-full).
    const capacityLabel = computed(() => {
      const c = ai.value.capacity || {};
      if (c.eta_days != null) return `plein dans ~${c.eta_days} j (${c.rate_per_day}%/j)`;
      if (c.trend === "stable") return "stable — aucun risque";
      if (c.trend === "collecting") return "analyse en cours…";
      return "suivi actif";
    });
    const capacityClass = computed(() => {
      const p = Number(ai.value.capacity?.disk_pct ?? 0);
      const eta = ai.value.capacity?.eta_days;
      if (p >= 90 || (eta != null && eta <= 7)) return "rc-level-critical";
      if (p >= 80 || (eta != null && eta <= 30)) return "rc-level-high";
      return "";
    });
    // NEW viz — risk timeline heatmap (recent history → colored bars).
    const riskTimeline = computed(() =>
      (ai.value.history || []).slice(-40).map((p) => {
        const s = Math.round(Number(p.score || 0));
        const band = s >= 75 ? "critical" : s >= 55 ? "high" : s >= 35 ? "watch" : "stable";
        return { score: s, band, ts: p.ts };
      })
    );
    // NEW analysis — now vs your normal.
    const insight = computed(() =>
      ai.value.insight || { baseline: 0, vs_normal: 0, alert_likelihood: "faible", peak: 0 }
    );
    // NEW premium viz — smooth glowing risk wave (spline area) with thresholds.
    const waveColor = computed(() => ({
      stable: "#22c55e", watch: "#f59e0b", high: "#f97316", critical: "#ef4444",
    }[level.value]));
    const waveGradId = "rcWaveFill";
    const waveGlowId = "rcWaveGlow";
    const riskWave = computed(() => {
      const pts = riskTimeline.value;
      const W = 800, H = 150, pad = 12;
      const yOf = (s) => H - pad - (Math.max(0, Math.min(100, s)) / 100) * (H - 2 * pad);
      const thresholds = [
        { y: yOf(35), c: "#f59e0b", label: "watch" },
        { y: yOf(55), c: "#f97316", label: "high" },
        { y: yOf(75), c: "#ef4444", label: "critical" },
      ];
      const n = pts.length;
      if (n < 2) return { line: "", area: "", dotX: W, dotY: H - pad, thresholds, W, H };
      const xy = pts.map((p, i) => [(i / (n - 1)) * W, yOf(p.score)]);
      let line = `M ${xy[0][0].toFixed(1)} ${xy[0][1].toFixed(1)}`;
      for (let i = 0; i < n - 1; i++) {
        const p0 = xy[i - 1] || xy[i], p1 = xy[i], p2 = xy[i + 1], p3 = xy[i + 2] || xy[i + 1];
        const c1x = p1[0] + (p2[0] - p0[0]) / 6, c1y = p1[1] + (p2[1] - p0[1]) / 6;
        const c2x = p2[0] - (p3[0] - p1[0]) / 6, c2y = p2[1] - (p3[1] - p1[1]) / 6;
        line += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
      }
      return { line, area: `${line} L ${W} ${H} L 0 ${H} Z`,
               dotX: xy[n - 1][0], dotY: xy[n - 1][1], thresholds, W, H };
    });

    // ── Auto-Pilot (autonomous remediation) ──────────────────────────────
    const autopilot = ref({
      config: { enabled: false, rules: {}, ram_threshold_pct: 90, disk_threshold_pct: 90, cooldown_min: 30 },
      journal: [], interventions: 0,
    });
    const loadAutopilot = async () => {
      try {
        const { data } = await axios.get("/backup/autopilot/status");
        if (data && data.config) autopilot.value = data;
      } catch (e) { /* backend unreachable — keep last state */ }
    };
    const toggleAutopilot = async () => {
      try {
        const { data } = await axios.post("/backup/autopilot/config",
          { enabled: !autopilot.value.config.enabled });
        if (data && data.ok) autopilot.value.config = data.config;
      } catch (e) { /* ignore */ }
    };
    let apTimer = null;
    onMounted(() => { loadAutopilot(); apTimer = setInterval(loadAutopilot, 30000); });
    onBeforeUnmount(() => { if (apTimer) clearInterval(apTimer); });

    const riskLevelLabel = computed(() => ({
      stable: "Stable", watch: "À surveiller", high: "Risque élevé", critical: "Critique",
    }[level.value]));
    const riskLevelClass = computed(() => `rc-level-${level.value}`);
    const heroTitle = computed(() => ({
      stable: "Tout est sous contrôle",
      watch: "Vigilance recommandée",
      high: "Risque élevé détecté",
      critical: "Action immédiate requise",
    }[level.value]));

    const gaugeColor = computed(() => ({
      stable: "#22c55e", watch: "#f59e0b", high: "#f97316", critical: "#ef4444",
    }[level.value]));

    const gaugeFillStyle = computed(() => {
      const circumference = 2 * Math.PI * 80;
      const offset = circumference * (1 - score.value / 100);
      return {
        strokeDasharray: circumference,
        strokeDashoffset: offset,
      };
    });

    const deltaIcon = computed(() => {
      if (delta.value > 0) return "mdi mdi-arrow-up-bold";
      if (delta.value < 0) return "mdi mdi-arrow-down-bold";
      return "mdi mdi-equal";
    });
    const deltaClass = computed(() => {
      if (delta.value > 2) return "rc-delta-up";
      if (delta.value < -2) return "rc-delta-down";
      return "rc-delta-flat";
    });
    const deltaLabel = computed(() => delta.value === 0 ? "stable" : `${delta.value > 0 ? '+' : ''}${delta.value}`);

    const stableSinceLabel = computed(() => {
      const since = ai.value.scores?.level_since;
      if (!since) return "";
      const secs = Math.max(0, (Date.now() - new Date(since).getTime()) / 1000);
      if (secs < 60) return "Niveau confirmé à l'instant";
      if (secs < 3600) return `Stable depuis ${Math.floor(secs / 60)} min`;
      return `Stable depuis ${Math.floor(secs / 3600)}h`;
    });

    const trendClass = computed(() => `rc-trend-${ai.value.trend?.direction || "stable"}`);
    const trendIcon = computed(() => ({
      rising: "mdi mdi-trending-up", falling: "mdi mdi-trending-down", stable: "mdi mdi-trending-neutral",
    }[ai.value.trend?.direction] || "mdi mdi-trending-neutral"));
    const trendLabel = computed(() => ({
      rising: "En hausse", falling: "En baisse", stable: "Plateau",
    }[ai.value.trend?.direction] || "Plateau"));
    const trendDetail = computed(() => {
      const slope = ai.value.trend?.slope_per_min || 0;
      if (Math.abs(slope) < 0.5) return "Mouvement < 0.5 pts/min";
      return `${slope > 0 ? '+' : ''}${slope.toFixed(1)} pts/min`;
    });
    const forecastClass = computed(() => {
      const f = ai.value.trend?.forecast_15min || 0;
      if (f >= 75) return "rc-forecast-critical";
      if (f >= 55) return "rc-forecast-high";
      if (f >= 35) return "rc-forecast-watch";
      return "rc-forecast-stable";
    });

    // Default skeleton nodes used when backend has no data yet
    const DEFAULT_NODES = [
      { name: "cpu", label: "CPU", short: "CPU", weight_pct: 22 },
      { name: "ram", label: "Mémoire", short: "RAM", weight_pct: 24 },
      { name: "load", label: "Charge système", short: "LOAD", weight_pct: 12 },
      { name: "disk", label: "Disque /", short: "DISK", weight_pct: 14 },
      { name: "services", label: "Services critiques", short: "SVC", weight_pct: 18 },
      { name: "backup", label: "Backup health", short: "BKP", weight_pct: 10 },
    ];

    const neuralNodes = computed(() => {
      const all = ai.value.all_contributors || ai.value.contributors || [];
      const positions = [
        { x: 60, y: 60 },    // top-left
        { x: 340, y: 60 },   // top-right
        { x: 30, y: 200 },   // bottom-left
        { x: 200, y: 250 },  // bottom-center
        { x: 370, y: 200 },  // bottom-right
        { x: 200, y: 30 },   // top-center
      ];
      const shorts = { cpu: "CPU", ram: "RAM", load: "LOAD", disk: "DISK", services: "SVC", backup: "BKP" };
      // Always render 6 nodes — fallback to defaults when contributors are empty
      const source = all.length > 0 ? all.slice(0, 6) : DEFAULT_NODES;
      return source.map((c, i) => {
        const pressure = Number(c.pressure ?? 0);
        const tone = pressure >= 70 ? "danger" : pressure >= 45 ? "warn" : "ok";
        return {
          name: c.name,
          label: c.label,
          short: shorts[c.name] || (c.short || c.name.slice(0, 4).toUpperCase()),
          value: c.value || "—",
          weight: c.weight_pct || 0,
          tone,
          pressure,
          intensity: Math.min(1, pressure / 100),
          x: positions[i].x, y: positions[i].y,
        };
      });
    });

    const slopeDisplay = computed(() => {
      const s = Number(ai.value.trend?.slope_per_min || 0);
      return s === 0 ? "0.0" : `${s > 0 ? '+' : ''}${s.toFixed(1)}`;
    });

    const anomalyCount = computed(() => {
      const all = ai.value.all_contributors || ai.value.contributors || [];
      return all.filter(c => (c.anomaly || 0) > 5).length;
    });

    const activePulseNodes = computed(() => neuralNodes.value.filter(n => n.intensity > 0.4));

    const getPulseStyle = (node) => ({
      animation: `rc-pulse-flow 2s ease-in-out infinite`,
      animationDelay: `${node.x / 200}s`,
      offsetPath: `path("M 200 140 L ${node.x} ${node.y}")`,
    });

    // Contributors
    const contributors = computed(() => ai.value.contributors || []);
    const contribTone = (c) => c.pressure >= 70 ? "rc-contrib-danger" : c.pressure >= 45 ? "rc-contrib-warn" : "rc-contrib-ok";
    const contribBarWidth = (c) => `${Math.max(2, Math.round(c.pressure))}%`;

    // Live metrics cards with sparklines
    const liveMetricsCards = computed(() => {
      const cpu = liveMetrics.value.cpu;
      const ram = liveMetrics.value.memory;
      const disk = Math.round(ai.value.features?.root_disk_usage || 0);
      const tone = (v, h, m) => v >= h ? "danger" : v >= m ? "warn" : "ok";
      return [
        { label: "CPU", value: `${cpu}%`, icon: "mdi mdi-chip", tone: tone(cpu, 85, 70), history: liveBuffer.value.cpu, caption: "Charge processeur live" },
        { label: "RAM", value: `${ram}%`, icon: "mdi mdi-memory", tone: tone(ram, 90, 75), history: liveBuffer.value.memory, caption: "Mémoire vive utilisée" },
        { label: "Load", value: liveBuffer.value.load[liveBuffer.value.load.length - 1]?.toFixed(2) || "—", icon: "mdi mdi-speedometer", tone: tone(parseFloat(liveBuffer.value.load[liveBuffer.value.load.length - 1] || 0) * 25, 75, 50), history: liveBuffer.value.load.map(x => x * 25), caption: "Load average 1 min" },
        { label: "Disk /", value: `${disk}%`, icon: "mdi mdi-harddisk", tone: tone(disk, 90, 75), history: [disk, disk, disk], caption: "Volume système" },
      ];
    });

    // SVG sparkline path
    const sparkPath = (history) => {
      if (!history || history.length < 2) return "M0,15 L100,15";
      const max = Math.max(...history, 1);
      const step = 100 / (history.length - 1);
      return history.map((v, i) => `${i === 0 ? 'M' : 'L'}${(i * step).toFixed(1)},${(30 - (v / max) * 28).toFixed(1)}`).join(" ");
    };
    const sparkAreaPath = (history) => {
      if (!history || history.length < 2) return "";
      const max = Math.max(...history, 1);
      const step = 100 / (history.length - 1);
      let p = `M0,30 `;
      history.forEach((v, i) => { p += `L${(i * step).toFixed(1)},${(30 - (v / max) * 28).toFixed(1)} `; });
      p += `L100,30 Z`;
      return p;
    };

    // Forecast chart with confidence band
    const forecastChart = computed(() => {
      const hist = ai.value.history || [];
      // Ensure we always have at least one actual point to anchor the forecast
      let actual = hist.map(h => Number(h.score) || 0);
      if (actual.length === 0) actual = [score.value || 0];

      const last = actual[actual.length - 1];
      const forecastValue = Number(ai.value.trend?.forecast_15min ?? last);
      const conf = Number(ai.value.trend?.confidence ?? 0.5);
      const slope = (forecastValue - last) / 8;

      // Create 8 forecast points + confidence bands
      const future = [];
      const futureLow = [];
      const futureHigh = [];
      for (let i = 1; i <= 8; i++) {
        const v = last + slope * i;
        future.push(Math.round(Math.max(0, Math.min(100, v))));
        const band = (1 - conf) * 25 * (i / 8);
        futureLow.push(Math.max(0, Math.round(v - band)));
        futureHigh.push(Math.min(100, Math.round(v + band)));
      }

      const allCats = [
        ...actual.map((_, i) => `T-${actual.length - i - 1}`),
        ...future.map((_, i) => `+${(i + 1) * 2}m`),
      ];

      const actualLen = actual.length;
      const futureLen = future.length;
      const padBefore = Math.max(0, actualLen - 1);

      const actualSeries = [...actual, ...new Array(futureLen).fill(null)];
      const forecastSeries = [...new Array(padBefore).fill(null), last, ...future];
      const lowSeries = [...new Array(actualLen).fill(null), ...futureLow];
      const highSeries = [...new Array(actualLen).fill(null), ...futureHigh];

      return {
        series: [
          { name: "Mesuré", type: "area", data: actualSeries },
          { name: "Forecast", type: "line", data: forecastSeries },
          { name: "Band high", type: "line", data: highSeries },
          { name: "Band low", type: "line", data: lowSeries },
        ],
        options: {
          chart: { toolbar: { show: false }, fontFamily: "Nunito, sans-serif", animations: { speed: 600 } },
          colors: ["#7c3aed", "#a78bfa", "#ddd6fe", "#ddd6fe"],
          stroke: { curve: "smooth", width: [3, 2.5, 1, 1], dashArray: [0, 6, 0, 0] },
          fill: { type: ["gradient", "solid", "solid", "solid"], gradient: { shadeIntensity: 0.6, opacityFrom: 0.4, opacityTo: 0.05 }, opacity: [0.4, 1, 0.15, 0.15] },
          markers: { size: 0 },
          dataLabels: { enabled: false },
          xaxis: { categories: allCats, labels: { style: { fontSize: "10px", colors: "#94a3b8" } } },
          yaxis: { min: 0, max: 100, tickAmount: 4, labels: { style: { fontSize: "10px", colors: "#94a3b8" } } },
          grid: { borderColor: "#f1f5f9" },
          legend: { show: false },
          annotations: {
            xaxis: [{ x: `T-0`, borderColor: "#7c3aed", strokeDashArray: 0, label: { text: "Maintenant", style: { background: "#7c3aed", color: "#fff", fontSize: "10px", padding: { top: 4, bottom: 4, left: 8, right: 8 } } } }],
            yaxis: [
              { y: 35, borderColor: "#06b6d4", strokeDashArray: 4, label: { text: "Watch", style: { background: "#06b6d4", color: "#fff", fontSize: "9px" }, position: "left" } },
              { y: 55, borderColor: "#f59e0b", strokeDashArray: 4, label: { text: "High", style: { background: "#f59e0b", color: "#fff", fontSize: "9px" }, position: "left" } },
              { y: 75, borderColor: "#ef4444", strokeDashArray: 4, label: { text: "Critical", style: { background: "#ef4444", color: "#fff", fontSize: "9px" }, position: "left" } },
            ],
          },
          tooltip: { y: { formatter: v => v == null ? "—" : `${v}/100` } },
        },
      };
    });

    const playbook = computed(() => {
      const recs = ai.value.recommendations || [];
      if (recs.length) return recs;
      return [{ title: "Surveillance continue", detail: "Tous les signaux sont normaux", icon: "mdi mdi-monitor-dashboard", priority: "info" }];
    });

    const lastRefreshLabel = computed(() => lastUpdatedAt.value ? lastUpdatedAt.value.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "…");

    return {
      loading, ai, score, level, scoreTens, scoreOnes, riskLevelLabel, riskLevelClass, heroTitle, predictiveLabel,
      capacityLabel, capacityClass, riskTimeline, insight,
      riskWave, waveColor, waveGradId, waveGlowId,
      autopilot, toggleAutopilot,
      gaugeColor, gaugeFillStyle, deltaIcon, deltaClass, deltaLabel, stableSinceLabel,
      trendClass, trendIcon, trendLabel, trendDetail, forecastClass,
      neuralNodes, activePulseNodes, getPulseStyle, slopeDisplay, anomalyCount,
      contributors, contribTone, contribBarWidth,
      liveMetricsCards, sparkPath, sparkAreaPath,
      forecastChart, playbook, feedEntries, lastRefreshLabel, refresh,
      // action runner
      actionResults, runningActions, pendingConfirm,
      runAction, confirmPending, cancelPending, clearResult,
    };
  },
};
</script>

<style scoped lang="scss" src="../../../assets/scss/BackupRiskCenter.scss"></style>
