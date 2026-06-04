<template>
  <div class="bl-root">

    <!-- ─── Header ─── -->
    <header class="bl-header">
      <div class="bl-header-text">
        <h2>Logs &amp; Audit</h2>
        <p>Vision globale du sous-système backup, restauration et notifications.</p>
      </div>
      <div class="bl-header-actions">
        <label class="bl-live-toggle">
          <input type="checkbox" v-model="liveMode"/>
          <span class="bl-live-pill" :class="{ on: liveMode }">
            <span class="bl-live-dot"></span>{{ liveMode ? 'LIVE' : 'Pause' }}
          </span>
        </label>
        <button class="bl-btn bl-btn-secondary" @click="refreshAll" :disabled="loading">Actualiser</button>
        <button class="bl-btn bl-btn-primary" @click="exportCsv">Exporter CSV</button>
      </div>
    </header>

    <!-- ─── Intelligence des logs — bandeau santé + à retenir ─── -->
    <section class="bl-intel" :class="'tone-' + (intel.overall_state || 'idle')">
      <!-- Bandeau santé : état clair + tendance -->
      <div class="bl-intel-banner">
        <div class="bl-intel-banner-main">
          <span class="bl-intel-status" :class="'st-' + (intel.overall_state || 'idle')">
            <span class="bl-intel-status-dot"></span>
          </span>
          <div class="bl-intel-banner-text">
            <h3 class="bl-intel-headline">{{ headline }}</h3>
            <p class="bl-intel-summary" v-if="intel.summary">{{ intel.summary }}</p>
          </div>
        </div>
        <div class="bl-intel-trend" :class="'trend-' + trendChip.cls">
          <span class="bl-intel-trend-cap">Tendance</span>
          <span class="bl-intel-trend-val">
            <span class="bl-intel-trend-arrow">{{ trendChip.arrow }}</span>{{ trendChip.label }}
          </span>
        </div>
      </div>

      <!-- Ligne de chiffres clés, en langage clair -->
      <div class="bl-intel-statline" v-if="intel.counts">
        <span class="bl-intel-stat ok">{{ intel.counts.backups_ok || 0 }} sauvegardes OK</span>
        <template v-if="intel.counts.backups_ko">
          <span class="bl-intel-stat-sep">·</span>
          <span class="bl-intel-stat ko">{{ intel.counts.backups_ko }} à vérifier</span>
        </template>
        <span class="bl-intel-stat-sep">·</span>
        <span class="bl-intel-stat">{{ intel.counts.errors || 0 }} erreur(s) sur 24 h</span>
      </div>

      <!-- À retenir : liste d'éléments prioritaires en langage clair -->
      <div class="bl-intel-retenir">
        <div class="bl-intel-retenir-cap">À retenir</div>
        <ul class="bl-intel-insights">
          <li v-for="ins in insights" :key="ins.id"
              class="bl-intel-insight" :class="['sev-' + ins.sev, { clickable: ins.incident }]"
              @click="ins.incident && toggleIncident(ins.incident.id)">
            <span class="bl-intel-insight-icon">{{ ins.icon }}</span>
            <div class="bl-intel-insight-body">
              <div class="bl-intel-insight-row">
                <span class="bl-intel-insight-text">{{ ins.text }}</span>
                <span class="bl-intel-insight-when" v-if="ins.when">{{ ins.when }}</span>
              </div>
              <div class="bl-intel-insight-sub" v-if="ins.sub">{{ ins.sub }}</div>
              <!-- Détails repliables (incident uniquement) -->
              <div v-if="ins.incident && expandedIncidents.has(ins.incident.id)"
                   class="bl-intel-insight-events">
                <div v-for="(ev, j) in ins.incident.events" :key="j"
                     class="bl-intel-insight-event" :class="'sev-' + ev.severity">
                  <span class="ev-ts">{{ formatTime(ev.ts) }}</span>
                  <span class="ev-src">{{ ev.source }}</span>
                  <span class="ev-title">{{ ev.title }}</span>
                </div>
              </div>
            </div>
            <span class="bl-intel-insight-chevron" v-if="ins.incident">{{
              expandedIncidents.has(ins.incident.id) ? '▾' : '▸'
            }}</span>
          </li>
        </ul>
      </div>
    </section>

    <!-- ─── KPI row ─── -->
    <section class="bl-kpis">
      <div class="bl-kpi">
        <span class="bl-kpi-label">Événements totaux</span>
        <span class="bl-kpi-value">{{ stats.counts.total }}</span>
        <svg class="bl-spark" :viewBox="`0 0 ${stats.sparkline.length * 4} 24`" preserveAspectRatio="none">
          <polyline :points="sparkPolyline" fill="none" stroke="#7c3aed" stroke-width="1.5"/>
        </svg>
        <span class="bl-kpi-foot">24 dernières heures</span>
      </div>
      <div class="bl-kpi bl-kpi-crit">
        <span class="bl-kpi-label">Critiques</span>
        <span class="bl-kpi-value">{{ stats.counts.critical }}</span>
        <span class="bl-kpi-foot">{{ stats.counts.error }} erreurs · {{ stats.counts.warning }} avertissements</span>
      </div>
      <div class="bl-kpi bl-kpi-ok">
        <span class="bl-kpi-label">Réussites</span>
        <span class="bl-kpi-value">{{ stats.counts.success }}</span>
        <span class="bl-kpi-foot">{{ successRate }}% taux de succès</span>
      </div>
      <div class="bl-kpi">
        <span class="bl-kpi-label">Sources actives</span>
        <span class="bl-kpi-value">{{ Object.keys(stats.by_kind).length }}</span>
        <div class="bl-kind-chips">
          <span v-for="(n, k) in stats.by_kind" :key="k" class="bl-kind-chip" :class="'k-'+k">
            {{ kindLabel(k) }} · {{ n }}
          </span>
        </div>
      </div>
    </section>

    <!-- ═══ Timeline d'audit ═══ -->
    <section class="bl-panel">
      <div class="bl-panel-head bl-panel-head-tabs">
        <div class="bl-tabs">
          <button class="bl-tab" :class="{ active: activeTab === 'all' }" @click="setTab('all')">
            <span>Timeline</span>
            <span class="bl-tab-count">{{ tabCounts.all }}</span>
          </button>
          <button class="bl-tab" :class="{ active: activeTab === 'system_change' }" @click="setTab('system_change')">
            <span>Changements système</span>
            <span class="bl-tab-count">{{ tabCounts.system_change }}</span>
          </button>
          <button class="bl-tab" :class="{ active: activeTab === 'alert' }" @click="setTab('alert')">
            <span>Alertes</span>
            <span class="bl-tab-count">{{ tabCounts.alert }}</span>
          </button>
          <button class="bl-tab" :class="{ active: activeTab === 'auth' }" @click="setTab('auth')">
            <span>Authentification</span>
            <span class="bl-tab-count">{{ tabCounts.auth }}</span>
          </button>
        </div>
        <div class="bl-filters">
          <input v-model="filters.q" type="text" placeholder="Rechercher…" class="bl-search" @input="debouncedReload"/>
          <select v-model="filters.severity" @change="reloadTimeline">
            <option value="all">Toute gravité</option>
            <option value="critical">Critique</option>
            <option value="error">Erreur</option>
            <option value="warning">Avertissement</option>
            <option value="success">Succès</option>
            <option value="info">Info</option>
          </select>
          <select v-model="filters.since" @change="reloadTimeline">
            <option value="24h">24 heures</option>
            <option value="7d">7 jours</option>
            <option value="30d">30 jours</option>
            <option value="">Tout</option>
          </select>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="activeTab === 'all'" class="bl-timeline">
        <article v-for="ev in events" :key="ev.kind + ev.ref_id + ev.ts" class="bl-event">
          <div class="bl-event-rail">
            <div class="bl-event-dot" :class="'k-'+ev.kind"></div>
            <div class="bl-event-line"></div>
          </div>
          <div class="bl-event-body">
            <div class="bl-event-row">
              <span class="bl-event-source" :class="'k-'+ev.kind">{{ ev.source }}</span>
              <span class="bl-event-sev" :class="ev.severity">{{ sevLabel(ev.severity) }}</span>
              <span class="bl-event-time">{{ formatTime(ev.ts) }}</span>
            </div>
            <div class="bl-event-title">{{ ev.title }}</div>
            <div class="bl-event-detail">{{ ev.detail }}</div>
            <code v-if="ev.ref_id" class="bl-event-ref" :title="ev.ref_id">{{ shortRef(ev.ref_id) }}</code>
          </div>
        </article>
        <div v-if="!events.length" class="bl-empty">Aucun événement ne correspond aux filtres.</div>
      </div>

      <!-- System Changes view -->
      <div v-else-if="activeTab === 'system_change'" class="bl-changes">
        <div v-if="events.length" class="bl-changes-table">
          <div class="bl-changes-row bl-changes-head">
            <div class="bl-c-time">Heure</div>
            <div class="bl-c-entity">Objet</div>
            <div class="bl-c-action">Action</div>
            <div class="bl-c-desc">Description</div>
          </div>
          <div v-for="ev in events" :key="'c-' + ev.ts + ev.ref_id" class="bl-changes-row">
            <div class="bl-c-time">{{ formatTime(ev.ts) }}</div>
            <div class="bl-c-entity">
              <span class="bl-c-entity-icon"></span>
              <span>{{ ev.entity || ev.source }}</span>
            </div>
            <div class="bl-c-action">
              <span class="bl-c-action-pill" :class="'a-' + (ev.action || 'other').toLowerCase()">
                {{ ev.action || sevLabel(ev.severity) }}
              </span>
            </div>
            <div class="bl-c-desc">
              <div class="bl-c-title">{{ ev.title }}</div>
              <div class="bl-c-detail" v-if="ev.detail">{{ ev.detail }}</div>
            </div>
          </div>
        </div>
        <div v-else class="bl-empty">
          Aucun changement système enregistré sur la période.
          <div class="bl-empty-hint">
            Les ajouts/suppressions de règles, configurations VPN, certificats, services et interfaces apparaîtront ici.
          </div>
        </div>
      </div>

      <!-- Alerts / Auth views (same template) -->
      <div v-else class="bl-timeline">
        <article v-for="ev in events" :key="'x-' + ev.ts + ev.ref_id" class="bl-event">
          <div class="bl-event-rail">
            <div class="bl-event-dot" :class="'k-'+ev.kind"></div>
            <div class="bl-event-line"></div>
          </div>
          <div class="bl-event-body">
            <div class="bl-event-row">
              <span class="bl-event-source" :class="'k-'+ev.kind">{{ ev.source }}</span>
              <span class="bl-event-sev" :class="ev.severity">{{ sevLabel(ev.severity) }}</span>
              <span class="bl-event-time">{{ formatTime(ev.ts) }}</span>
            </div>
            <div class="bl-event-title">{{ ev.title }}</div>
            <div class="bl-event-detail">{{ ev.detail }}</div>
          </div>
        </article>
        <div v-if="!events.length" class="bl-empty">
          {{ activeTab === 'alert' ? 'Aucune alerte sur la période.' : 'Aucune connexion enregistrée sur la période.' }}
        </div>
      </div>
    </section>

    <!-- ═══ Activité serveur — parsed system logs ═══ -->
    <section class="bl-panel bl-serv">
      <div class="bl-panel-head">
        <div class="bl-panel-title">
          <h3>Activité serveur</h3>
          <span class="bl-panel-meta">{{ serverEntries.length }} lignes · journalctl</span>
        </div>
        <div class="bl-serv-controls">
          <select v-model="serverUnit" @change="onServerUnitChange" class="bl-serv-select">
            <option v-for="u in serverUnits" :key="u" :value="u">{{ u }}</option>
          </select>
          <input v-model="serverFilter" type="text" placeholder="Filtrer…" class="bl-search bl-serv-search"/>
          <span class="bl-serv-counts">
            <span class="bl-serv-count bl-c-success">{{ serverCounts.success || 0 }} ok</span>
            <span class="bl-serv-count bl-c-warning">{{ serverCounts.warning || 0 }} warn</span>
            <span class="bl-serv-count bl-c-error">{{ serverCounts.error || 0 }} err</span>
          </span>
          <button class="bl-mini-btn bl-mini-btn--refresh"
                  :class="{ spinning: serverRefreshing }"
                  @click="manualReloadServer" title="Actualiser maintenant">↻</button>
          <button class="bl-mini-btn bl-mini-btn--follow"
                  :class="{ active: serverAutoScroll }"
                  @click="toggleAutoScroll"
                  :title="serverAutoScroll ? 'Désactiver le suivi automatique de la fin' : 'Activer le suivi automatique de la fin'">⇣</button>
        </div>
      </div>

      <!-- Diagnostic banner — shown when the selected unit is failed/inactive.
           Pulls the cause + last "since" timestamp from the backend so the
           operator knows WHY the service is down without scrolling logs. -->
      <div v-if="serverDiag && serverDiag.is_failed" class="bl-serv-diag bl-serv-diag--err">
        <div class="bl-serv-diag-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="13"/>
            <circle cx="12" cy="16.5" r="0.6" fill="currentColor"/>
          </svg>
        </div>
        <div class="bl-serv-diag-body">
          <div class="bl-serv-diag-head">
            <strong>{{ serverUnit }} est en échec</strong>
            <span class="bl-serv-diag-state">{{ serverDiag.active_state }} / {{ serverDiag.sub_state }}<span v-if="serverDiag.exit_code && serverDiag.exit_code !== '0'"> · exit {{ serverDiag.exit_code }}</span></span>
          </div>
          <div class="bl-serv-diag-cause" v-if="serverDiag.cause">{{ serverDiag.cause }}</div>
          <div class="bl-serv-diag-cause bl-serv-diag-cause--unknown" v-else>
            Cause technique non identifiée dans les 8 dernières lignes du journal.
            Consultez le flux ci-dessous.
          </div>
          <div class="bl-serv-diag-meta" v-if="serverDiag.since">Depuis : {{ serverDiag.since }}</div>
        </div>
      </div>
      <div v-else-if="serverDiag && serverDiag.active_state === 'active'" class="bl-serv-diag bl-serv-diag--ok">
        <span class="bl-serv-diag-pulse"></span>
        <span><strong>{{ serverUnit }}</strong> · {{ serverDiag.active_state }} / {{ serverDiag.sub_state }}<span v-if="serverDiag.since"> · depuis {{ serverDiag.since }}</span></span>
      </div>
      <div class="bl-serv-body" ref="servRef">
        <div v-if="!filteredServer.length" class="bl-empty">
          Aucune activité serveur pour {{ serverUnit }} sur la fenêtre actuelle.
        </div>
        <div v-for="(e, i) in filteredServer" :key="i" class="bl-serv-row" :class="'lvl-'+e.level">
          <span class="bl-serv-ts">{{ e.ts || '—' }}</span>
          <span class="bl-serv-src">{{ e.source }}</span>

          <!-- HTTP request: badges + path + status -->
          <template v-if="e.category === 'http'">
            <span class="bl-serv-method" :class="'m-' + e.method.toLowerCase()">{{ e.method }}</span>
            <span class="bl-serv-path">{{ e.path }}</span>
            <span class="bl-serv-status" :class="statusClass(e.status)">{{ e.status }}</span>
            <span class="bl-serv-user">{{ e.user }}</span>
          </template>

          <!-- Structured log: level badge + summary -->
          <template v-else-if="e.category === 'log'">
            <span class="bl-serv-lvl" :class="'lvl-' + e.level">{{ levelLabel(e.level) }}</span>
            <span class="bl-serv-msg">{{ e.summary }}</span>
          </template>

          <!-- Raw fallback -->
          <template v-else>
            <span class="bl-serv-lvl" :class="'lvl-' + e.level">{{ levelLabel(e.level) }}</span>
            <span class="bl-serv-msg bl-serv-msg-raw">{{ e.summary }}</span>
          </template>
        </div>
      </div>
    </section>

    <transition name="bl-toast">
      <div v-if="toast.show" class="bl-toast" :class="toast.kind">{{ toast.message }}</div>
    </transition>

  </div>
</template>

<script>
import axios from "axios";
const API = "/backup";

export default {
  name: "BackupLogs",
  data() {
    return {
      loading: false, liveMode: true,
      stats: { counts: { total: 0, info: 0, success: 0, warning: 0, error: 0, critical: 0 },
               by_kind: {}, sparkline: new Array(24).fill(0) },
      events: [], filteredCount: 0,
      activeTab: "all",
      tabCounts: { all: 0, system_change: 0, alert: 0, auth: 0 },
      filters: { q: "", severity: "all", since: "24h" },

      // AI Log Intelligence — anomaly / incident / forecast snapshot
      // produced by backend log_intelligence.logs_intelligence.
      intel: {
        overall_state: "idle",        // healthy | watch | degraded | critical
        summary: "",
        anomalies: [],
        incidents: [],
        forecast: { predicted_state: "idle", confidence_pct: 0,
                    rationale: "", series: [] },
        stats: { events_analyzed: 0 },
      },
      // Set of incident IDs the user expanded to see the underlying events.
      // Vue 3's reactivity tracks the Set reference, so toggleIncident() must
      // assign a fresh Set rather than mutating in place.
      expandedIncidents: new Set(),

      // Server activity (parsed journalctl)
      serverUnit: "uvicorn",
      serverUnits: ["uvicorn", "nginx", "postgresql", "strongswan", "ipsec",
                    "squid", "nftables", "suricata", "sshd",
                    "openvpn-server@server", "dhcpd4", "dhcpd6"],
      serverEntries: [], serverCounts: { info: 0, success: 0, warning: 0, error: 0 },
      serverDiag: null,             // { active_state, sub_state, cause, since, exit_code, is_failed }
      serverFilter: "", serverAutoScroll: true,
      serverRefreshing: false,      // drives the ↻ spin animation

      _timers: {}, _searchTimer: null,
      toast: { show: false, message: "", kind: "info" },
    };
  },
  computed: {
    sparkPolyline() {
      const data = this.stats.sparkline;
      if (!data.length) return "";
      const max = Math.max(1, ...data);
      return data.map((v, i) => `${i * 4},${24 - (v / max) * 20}`).join(" ");
    },
    successRate() {
      const c = this.stats.counts;
      const denom = c.success + c.error + c.critical;
      return denom ? Math.round((c.success / denom) * 100) : 100;
    },

    // ── Intelligence des logs ───────────────────────────────────────────
    // Plain-language headline for the health banner (no model jargon).
    headline() {
      return { healthy:  "Système sain", watch:    "Vigilance",
               degraded: "Dégradé",      critical: "Critique",
               idle:     "Analyse en cours" }[this.intel.overall_state] || "—";
    },
    // Trend chip — derived from the forecast direction, shown as a simple
    // arrow + word. No percentage, no slope, no confidence figure.
    trendChip() {
      const f = this.intel.forecast || {};
      const dir = f.direction
        || ({ stable: "flat", watch: "flat", risk: "up" }[f.predicted_state] || "flat");
      return {
        up:   { cls: "up",   arrow: "↗", label: "En hausse" },
        down: { cls: "down", arrow: "↘", label: "En baisse" },
        flat: { cls: "flat", arrow: "→", label: "Stable" },
      }[dir];
    },
    // Single prioritized "À retenir" feed merging failed backups, correlated
    // incidents and anomalies into plain-language items. Incidents stay
    // expandable so an operator can drill into the underlying events.
    insights() {
      const out = [];
      const c = this.intel.counts || {};
      if (c.backups_ko) {
        out.push({
          id: "bko", sev: "warning", icon: "⚠",
          text: `${c.backups_ko} sauvegarde${c.backups_ko > 1 ? "s" : ""} en échec — à vérifier`,
        });
      }
      for (const inc of (this.intel.incidents || [])) {
        const comps = (inc.components || []).join(", ");
        out.push({
          id: "inc-" + inc.id,
          sev: inc.severity || "warning",
          icon: inc.severity === "critical" ? "⛔" : "⚠",
          text: inc.root_cause || (comps ? `Incident sur ${comps}` : "Incident détecté"),
          sub: comps ? `${comps} · ${inc.event_count} événements` : "",
          when: this.relativeTime(inc.started_at),
          incident: inc,
        });
      }
      for (const a of (this.intel.anomalies || [])) {
        out.push({
          id: "anom-" + a.id,
          sev: a.severity || "info",
          icon: "ℹ",
          text: a.title || `Pic d'activité sur « ${a.source} »`,
          sub: a.detail || "",
        });
      }
      if (!out.length) {
        out.push({ id: "ok", sev: "success", icon: "✓",
                   text: "Aucune anomalie inhabituelle détectée." });
      }
      return out;
    },
    filteredServer() {
      if (!this.serverFilter) return this.serverEntries;
      const q = this.serverFilter.toLowerCase();
      return this.serverEntries.filter(e =>
        ((e.path || "") + " " + (e.summary || "") + " " + (e.method || "")
         + " " + String(e.status || "")).toLowerCase().includes(q)
      );
    },
  },
  mounted() {
    this.refreshAll();
    this.scheduleLive();
    this.loadIntelligence();
  },
  beforeUnmount() { this.clearTimers(); },
  watch: {
    liveMode(v) { v ? this.scheduleLive() : this.clearTimers(); },
  },
  methods: {
    clearTimers() {
      Object.values(this._timers).forEach(clearInterval);
      this._timers = {};
    },
    scheduleLive() {
      this.clearTimers();
      this._timers.stats    = setInterval(this.reloadStats,        8000);
      this._timers.timeline = setInterval(this.reloadTimeline,     5000);
      this._timers.server   = setInterval(this.reloadServer,       4000);
      // Intelligence is a heavier compute, refresh slower (15 s) — anomalies
      // and incidents don't change second-by-second, and we don't want the
      // 24h aggregator running 12× per minute.
      this._timers.intel    = setInterval(this.loadIntelligence,  15000);
    },
    debouncedReload() {
      clearTimeout(this._searchTimer);
      this._searchTimer = setTimeout(this.reloadTimeline, 400);
    },
    setTab(tab) { this.activeTab = tab; this.reloadTimeline(); },

    async refreshAll() {
      this.loading = true;
      await Promise.all([this.reloadStats(), this.reloadTimeline(), this.reloadServer()]);
      this.loading = false;
    },

    async reloadServer() {
      try {
        const { data } = await axios.get(`${API}/logs/tail`, {
          params: { unit: this.serverUnit, lines: 120 },
        });
        this.serverEntries = data.entries || [];
        this.serverCounts  = data.counts  || { info: 0, success: 0, warning: 0, error: 0 };
        this.serverDiag    = data.diagnostic || null;
        if (this.serverAutoScroll) {
          this.$nextTick(() => {
            const el = this.$refs.servRef;
            if (el) el.scrollTop = el.scrollHeight;
          });
        }
      } catch (e) {
        this.serverEntries = [{ ts: "", source: "—", level: "error",
                                category: "raw", summary: `Erreur lecture ${this.serverUnit}` }];
        this.serverDiag = null;
      }
    },

    // User-triggered refresh — same as the timer-driven one, but with a
    // visible spin animation + toast so the operator KNOWS the click worked.
    async manualReloadServer() {
      if (this.serverRefreshing) return;
      this.serverRefreshing = true;
      try {
        await this.reloadServer();
        this.showToast(`Logs ${this.serverUnit} actualisés (${this.serverEntries.length} lignes)`, "success");
      } finally {
        // Keep the spinner visible for ≥350 ms so even a sub-100 ms reload
        // is perceived as a real action by the user.
        setTimeout(() => { this.serverRefreshing = false; }, 350);
      }
    },

    // Toggle auto-scroll + visible feedback. When turning it ON, immediately
    // scroll to the bottom so the user sees what "follow the tail" means.
    toggleAutoScroll() {
      this.serverAutoScroll = !this.serverAutoScroll;
      if (this.serverAutoScroll) {
        this.$nextTick(() => {
          const el = this.$refs.servRef;
          if (el) el.scrollTop = el.scrollHeight;
        });
        this.showToast("Suivi de la fin activé", "success");
      } else {
        this.showToast("Suivi de la fin désactivé", "info");
      }
    },

    // Called when the unit dropdown changes. Resets the diagnostic banner so
    // we never show the previous unit's status next to a fresh log feed.
    onServerUnitChange() {
      this.serverDiag = null;
      this.serverEntries = [];
      this.reloadServer();
    },

    // Tiny toast helper — reuses the existing toast slot at the bottom of
    // the page. Auto-dismisses after 2.2 s.
    showToast(message, kind = "info") {
      this.toast = { show: true, message, kind };
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => { this.toast.show = false; }, 2200);
    },

    statusClass(s) {
      if (s < 300) return "ok";
      if (s < 400) return "redir";
      if (s < 500) return "warn";
      return "err";
    },
    levelLabel(l) {
      return { info: "INFO", success: "OK", warning: "WARN", error: "ERR" }[l] || l;
    },

    async reloadStats() {
      try {
        const { data } = await axios.get(`${API}/logs/stats`);
        this.stats = data;
      } catch (e) {}
    },

    async reloadTimeline() {
      try {
        const params = { limit: 500 };
        if (this.filters.q)                  params.q = this.filters.q;
        if (this.filters.severity !== "all") params.severity = this.filters.severity;
        if (this.filters.since)              params.since = this.filters.since;
        const { data } = await axios.get(`${API}/logs/timeline`, { params });
        const all = data.events || [];

        const counts = { all: all.length, system_change: 0, alert: 0, auth: 0 };
        for (const e of all) {
          const c = e.category || "operation";
          if (counts[c] !== undefined) counts[c]++;
        }
        this.tabCounts = counts;

        const filtered = this.activeTab === "all"
          ? all : all.filter(e => (e.category || "operation") === this.activeTab);
        this.events = filtered.slice(0, 200);
      } catch (e) {}
    },

    // ── AI Log Intelligence ─────────────────────────────────────────────
    // Single GET → backend computes anomalies + incidents + 30-min forecast
    // + NL summary in one pass. We don't merge incrementally because the
    // detection thresholds depend on the *full* 24h baseline anyway.
    async loadIntelligence() {
      try {
        const { data } = await axios.get(`${API}/logs/intelligence`);
        this.intel = data;
      } catch (e) { /* transient errors are harmless — UI keeps last snapshot */ }
    },

    toggleIncident(id) {
      // Replace the Set reference so Vue 3 detects the change.
      const next = new Set(this.expandedIncidents);
      next.has(id) ? next.delete(id) : next.add(id);
      this.expandedIncidents = next;
    },

    stateLabel(s) {
      return { healthy:  "Sain",       watch:    "Vigilance",
               degraded: "Dégradé",    critical: "Critique",
               idle:     "Initialisation" }[s] || "—";
    },

    relativeTime(iso) {
      if (!iso) return "—";
      const diff = (Date.now() - new Date(iso).getTime()) / 1000;
      if (diff < 60)    return "à l'instant";
      if (diff < 3600)  return `il y a ${Math.round(diff / 60)} min`;
      if (diff < 86400) return `il y a ${Math.round(diff / 3600)} h`;
      return `il y a ${Math.round(diff / 86400)} j`;
    },

    exportCsv() {
      const rows = [["timestamp", "kind", "severity", "source", "title", "detail", "ref"]];
      for (const e of this.events) {
        rows.push([e.ts, e.kind, e.severity, e.source, e.title, e.detail, e.ref_id]);
      }
      const csv = rows.map(r => r.map(c =>
        `"${String(c || "").replace(/"/g, '""')}"`).join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `asguard_logs_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    },

    kindLabel(k) {
      return { backup: "Backups", restore: "Restaurations", snapshot: "Snapshots",
               migration: "Migration", notify: "Notifs" }[k] || k;
    },
    sevLabel(s) {
      return { info: "Info", success: "Succès", warning: "Avert.",
               error: "Erreur", critical: "Critique" }[s] || s;
    },
    formatTime(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      const now = new Date();
      const sameDay = d.toDateString() === now.toDateString();
      if (sameDay) return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      return d.toLocaleString("fr-FR", { day: "2-digit", month: "short",
                                          hour: "2-digit", minute: "2-digit" });
    },
    shortRef(r) { return (r || "").length > 28 ? r.slice(0, 28) + "…" : r; },

    flash(message, kind = "info") {
      this.toast = { show: true, message, kind };
      clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => { this.toast.show = false; }, 4500);
    },
  },
};
</script>

<style scoped lang="scss" src="../../../assets/scss/BackupLogs.scss"></style>
