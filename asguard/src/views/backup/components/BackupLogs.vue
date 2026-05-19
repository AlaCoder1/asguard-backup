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

    <!-- ═══════════════════════════════════════════════════════════════ -->
    <!-- ═══ CHAOS ENGINEERING LAB  (split view: scenarios | terminal) ═══ -->
    <!-- ═══════════════════════════════════════════════════════════════ -->
    <section class="bl-chaos">
      <div class="bl-chaos-banner">
        <div class="bl-chaos-banner-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </div>
        <div class="bl-chaos-banner-text">
          <h3>Chaos Engineering Lab</h3>
          <p>Inspiré <strong>Netflix Chaos Monkey</strong> · Tester la résilience en conditions réelles</p>
        </div>
        <span class="bl-chaos-badge">PFE Innovation</span>
      </div>

      <div class="bl-chaos-body">
        <!-- LEFT: scenarios list -->
        <div class="bl-chaos-left">
          <div class="bl-chaos-section-head">
            <span>Scénarios de chaos</span>
            <span class="bl-chaos-count">{{ scenarios.length }} disponibles</span>
          </div>
          <div class="bl-chaos-list">
            <article v-for="s in scenarios" :key="s.id"
                     class="bl-chaos-item" :class="['sev-'+s.severity, { selected: selectedScenario === s.id }]"
                     @click="selectedScenario = s.id">
              <div class="bl-chaos-item-bolt">
                <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
              </div>
              <div class="bl-chaos-item-body">
                <div class="bl-chaos-item-name">{{ s.label }}</div>
                <div class="bl-chaos-item-sub">{{ s.short || s.description.split('.')[0] }}</div>
              </div>
              <span class="bl-chaos-item-sev" :class="s.severity">{{ severityFr(s.severity) }}</span>
            </article>
          </div>
          <button class="bl-chaos-launch"
                  :class="{ running: isRunning }"
                  :disabled="!selectedScenario || isRunning"
                  @click="launchSelected">
            <svg v-if="!isRunning" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <svg v-else class="bl-spin" viewBox="0 0 50 50" width="14" height="14">
              <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5"
                      stroke-linecap="round" stroke-dasharray="80"/>
            </svg>
            {{ isRunning ? 'CHAOS EN COURS…' : 'LANCER LE CHAOS' }}
          </button>
        </div>

        <!-- RIGHT: live terminal -->
        <div class="bl-chaos-right">
          <div class="bl-chaos-section-head">
            <span>Réaction du système</span>
            <span class="bl-chaos-status" :class="chaosStatusClass">
              <span class="bl-chaos-status-dot"></span>{{ chaosStatusLabel }}
            </span>
          </div>
          <div class="bl-chaos-terminal" ref="termRef">
            <div v-if="!chaosOutput.length" class="bl-chaos-term-empty">
              # Aucun scénario lancé pour l'instant.<br/>
              # Sélectionnez un scénario à gauche puis cliquez sur LANCER LE CHAOS.
            </div>
            <div v-for="(ln, i) in chaosOutput" :key="i" class="bl-chaos-term-line" :class="'sev-'+ln.severity">
              <span class="bl-chaos-term-ts">{{ ln.ts }}</span>
              <span class="bl-chaos-term-text">{{ ln.line }}</span>
            </div>
          </div>
          <div class="bl-chaos-progress" v-if="currentChaos">
            <div class="bl-chaos-progress-meta">
              <span class="bl-chaos-progress-phase">{{ currentChaos.phase || '—' }}</span>
              <span class="bl-chaos-progress-pct">{{ currentChaos.progress_pct || 0 }}%</span>
            </div>
            <div class="bl-chaos-progress-bar">
              <span :style="{ width: (currentChaos.progress_pct || 0) + '%' }"
                    :class="'sev-' + (currentChaos.status === 'error' ? 'error' :
                                       currentChaos.status === 'done'  ? 'ok'   : 'warning')"></span>
            </div>
          </div>
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
const LS_KEY = "asguard_chaos_active_job";

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

      // Chaos
      scenarios: [], selectedScenario: null,
      currentChaos: null,        // { job_id, status, phase, progress_pct, output, ... }
      chaosOutput: [],

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
    isRunning() {
      return this.currentChaos && this.currentChaos.status === "running";
    },
    chaosStatusLabel() {
      if (!this.currentChaos) return "Inactif";
      if (this.currentChaos.status === "running") return "En cours";
      if (this.currentChaos.status === "done")    return "Terminé";
      if (this.currentChaos.status === "error")   return "Erreur";
      return this.currentChaos.status;
    },
    chaosStatusClass() {
      if (!this.currentChaos) return "off";
      return this.currentChaos.status;
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
    this.loadScenarios().then(() => this.tryResumeFromLocalStorage());
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
      this._timers.stats    = setInterval(this.reloadStats,    8000);
      this._timers.timeline = setInterval(this.reloadTimeline, 5000);
      this._timers.server   = setInterval(this.reloadServer,   4000);
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

    async loadScenarios() {
      try {
        const { data } = await axios.get(`${API}/logs/chaos/scenarios`);
        // Add a short tagline per scenario for the compact card
        const tags = {
          cpu_burst:     "Sature 4 cœurs CPU pendant 60s",
          service_drill: "Tue squid · attente détection · auto-restart",
          dr_drill:      "Exercice de reprise complet (PRA)",
        };
        this.scenarios = (data.scenarios || []).map(s => ({ ...s, short: tags[s.id] || "" }));
      } catch (e) {}
    },

    async tryResumeFromLocalStorage() {
      try {
        const saved = localStorage.getItem(LS_KEY);
        if (!saved) return;
        const { job_id, scenario } = JSON.parse(saved);
        if (!job_id) return;
        const { data } = await axios.get(`${API}/logs/chaos/status/${job_id}`);
        if (data && data.status) {
          this.currentChaos     = data;
          this.chaosOutput      = data.output || [];
          this.selectedScenario = scenario || data.scenario;
          if (data.status === "running") {
            this.flash("Reprise du scénario en cours…", "info");
            this.pollChaos(job_id);
          } else {
            // Already finished while we were away — show toast + clear
            this.flash(
              data.status === "done"
                ? `Scénario terminé : ${data.scenario_label || data.scenario}`
                : `Scénario en erreur : ${data.message || ""}`,
              data.status === "done" ? "success" : "error"
            );
            localStorage.removeItem(LS_KEY);
          }
        }
      } catch (e) {
        localStorage.removeItem(LS_KEY);
      }
    },

    async launchSelected() {
      if (!this.selectedScenario || this.isRunning) return;
      const id = this.selectedScenario;
      try {
        const { data } = await axios.post(`${API}/logs/chaos/run/${id}`);
        if (data.ok) {
          this.currentChaos = { job_id: data.job_id, scenario: id,
                                status: "running", progress_pct: 0,
                                phase: "Initialisation", output: [] };
          this.chaosOutput = [];
          localStorage.setItem(LS_KEY, JSON.stringify({ job_id: data.job_id, scenario: id }));
          this.pollChaos(data.job_id);
          this.flash(`Scénario « ${this.scenarios.find(s => s.id === id)?.label} » lancé`, "info");
        } else {
          this.flash(data.error || "Échec lancement", "error");
        }
      } catch (e) { this.flash("Erreur réseau", "error"); }
    },

    async pollChaos(jobId) {
      clearInterval(this._timers.chaos);
      this._timers.chaos = setInterval(async () => {
        try {
          const { data } = await axios.get(`${API}/logs/chaos/status/${jobId}`);
          this.currentChaos = data;
          this.chaosOutput  = data.output || [];
          this.$nextTick(() => {
            const t = this.$refs.termRef;
            if (t) t.scrollTop = t.scrollHeight;
          });
          if (data.status === "done" || data.status === "error") {
            clearInterval(this._timers.chaos);
            localStorage.removeItem(LS_KEY);
            this.flash(
              data.status === "done"
                ? `Scénario terminé · ${data.scenario_label || data.scenario}`
                : `Erreur : ${data.message || ""}`,
              data.status === "done" ? "success" : "error"
            );
            await this.reloadTimeline();
            await this.reloadStats();
          }
        } catch (e) { /* tolerate transient errors */ }
      }, 1500);
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
               migration: "Migration", notify: "Notifs", chaos: "Chaos" }[k] || k;
    },
    sevLabel(s) {
      return { info: "Info", success: "Succès", warning: "Avert.",
               error: "Erreur", critical: "Critique" }[s] || s;
    },
    severityFr(s) {
      return { warning: "Avertissement", critical: "Critique", info: "Info" }[s] || s;
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

<style scoped>
.bl-root {
  padding: 20px 22px 40px;
  font-size: 13px; color: #0f172a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* ── Header ──────────────────────────────────── */
.bl-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 24px; padding: 18px 22px; margin-bottom: 18px;
  background: #fff; border: 1px solid #e9d5ff; border-radius: 10px;
  position: relative; overflow: hidden;
}
.bl-header::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: linear-gradient(180deg, #7c3aed 0%, #5b21b6 100%);
}
.bl-header h2 { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: -0.01em; }
.bl-header p  { margin: 4px 0 0; font-size: 12.5px; color: #64748b; line-height: 1.5; }
.bl-header-actions { display: flex; gap: 8px; align-items: center; }

.bl-btn {
  padding: 8px 14px; font-size: 12.5px; font-weight: 600;
  border-radius: 6px; border: 1px solid transparent; cursor: pointer;
  transition: all 0.15s;
}
.bl-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.bl-btn-primary {
  background: linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%);
  color: #fff; border-color: #6d28d9;
  box-shadow: 0 4px 10px rgba(124, 58, 237, 0.25);
}
.bl-btn-primary:hover:not(:disabled) { background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%); }
.bl-btn-secondary { background: #fff; color: #0f172a; border-color: #cbd5e1; }
.bl-btn-secondary:hover:not(:disabled) { background: #f8fafc; border-color: #94a3b8; }

.bl-live-toggle { cursor: pointer; }
.bl-live-toggle input { display: none; }
.bl-live-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 11px; background: #f1f5f9;
  border: 1px solid #cbd5e1; border-radius: 999px;
  font-size: 11.5px; font-weight: 700; color: #475569;
  transition: all 0.15s;
}
.bl-live-pill.on { background: #fef2f2; border-color: #fecaca; color: #b91c1c; }
.bl-live-dot { width: 7px; height: 7px; border-radius: 50%; background: #94a3b8; }
.bl-live-pill.on .bl-live-dot {
  background: #dc2626; animation: bl-pulse 1.6s infinite;
  box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4);
}
@keyframes bl-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
  50%      { box-shadow: 0 0 0 6px rgba(220, 38, 38, 0); }
}

/* ── KPI row ──────────────────────────────── */
.bl-kpis {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 12px; margin-bottom: 18px;
}
.bl-kpi {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 14px 16px;
  display: flex; flex-direction: column; gap: 4px;
}
.bl-kpi-label {
  font-size: 10.5px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.6px;
}
.bl-kpi-value {
  font-size: 28px; font-weight: 800; color: #0f172a; line-height: 1;
  font-variant-numeric: tabular-nums;
}
.bl-kpi-foot { font-size: 11px; color: #94a3b8; }
.bl-spark { width: 100%; height: 24px; margin-top: 4px; }
.bl-kpi-crit .bl-kpi-value { color: #b91c1c; }
.bl-kpi-crit { border-left: 3px solid #dc2626; }
.bl-kpi-ok   .bl-kpi-value { color: #047857; }
.bl-kpi-ok   { border-left: 3px solid #10b981; }
.bl-kind-chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.bl-kind-chip {
  font-size: 10px; font-weight: 600; padding: 2px 7px;
  background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px;
  color: #475569;
}
.k-backup    { --kc: #2563eb; }
.k-restore   { --kc: #7c3aed; }
.k-snapshot  { --kc: #c026d3; }
.k-migration { --kc: #0891b2; }
.k-notify    { --kc: #b45309; }
.k-chaos     { --kc: #dc2626; }
.k-auth      { --kc: #ea580c; }
.bl-kind-chip.k-backup    { color: #1e40af; background: #eff6ff; border-color: #bfdbfe; }
.bl-kind-chip.k-restore   { color: #5b21b6; background: #faf5ff; border-color: #ddd6fe; }
.bl-kind-chip.k-snapshot  { color: #86198f; background: #fdf4ff; border-color: #f5d0fe; }
.bl-kind-chip.k-migration { color: #155e75; background: #ecfeff; border-color: #a5f3fc; }
.bl-kind-chip.k-notify    { color: #92400e; background: #fffbeb; border-color: #fde68a; }
.bl-kind-chip.k-chaos     { color: #991b1b; background: #fef2f2; border-color: #fecaca; }

/* ═══════════════════════════════════════════════ */
/* ═══ CHAOS LAB                                 ═══ */
/* ═══════════════════════════════════════════════ */
.bl-chaos {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 18px;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.06);
}
.bl-chaos-banner {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #faf5ff 0%, #ede9fe 50%, #fce7f3 100%);
  border-bottom: 1px solid #e9d5ff;
  position: relative;
}
.bl-chaos-banner-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f59e0b 0%, #dc2626 100%);
  color: #fff;
  border-radius: 8px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}
.bl-chaos-banner-text { flex: 1; min-width: 0; }
.bl-chaos-banner-text h3 {
  margin: 0; font-size: 16px; font-weight: 800;
  color: #5b21b6; letter-spacing: -0.01em;
}
.bl-chaos-banner-text p {
  margin: 2px 0 0; font-size: 12px; color: #7c3aed; font-weight: 500;
}
.bl-chaos-banner-text strong { color: #5b21b6; }
.bl-chaos-badge {
  flex-shrink: 0;
  background: #ede9fe;
  color: #5b21b6;
  border: 1px solid #c4b5fd;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 10.5px; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.6px;
}

.bl-chaos-body {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 0;
  background: #f8fafc;
}
.bl-chaos-left, .bl-chaos-right {
  padding: 16px 18px;
  display: flex; flex-direction: column; gap: 12px;
  min-width: 0;
}
.bl-chaos-left { border-right: 1px solid #e2e8f0; background: #fff; }

.bl-chaos-section-head {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12.5px; font-weight: 700; color: #0f172a;
}
.bl-chaos-count {
  font-size: 10.5px; font-weight: 700;
  color: #b45309; background: #fffbeb;
  border: 1px solid #fde68a;
  padding: 2px 9px;
  border-radius: 999px;
}

/* Scenario list */
.bl-chaos-list { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.bl-chaos-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.bl-chaos-item:hover {
  border-color: #c4b5fd;
  transform: translateX(2px);
}
.bl-chaos-item.selected {
  border-color: #dc2626;
  background: #fef2f2;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}
.bl-chaos-item.sev-warning.selected  { border-color: #f59e0b; background: #fffbeb; box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.12); }
.bl-chaos-item-bolt {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  background: #fef3c7; color: #b45309;
  border-radius: 6px;
  flex-shrink: 0;
}
.bl-chaos-item.sev-critical .bl-chaos-item-bolt { background: #fee2e2; color: #b91c1c; }
.bl-chaos-item-body { flex: 1; min-width: 0; }
.bl-chaos-item-name { font-weight: 700; color: #0f172a; font-size: 13.5px; }
.bl-chaos-item-sub  {
  font-size: 11px; color: #64748b; margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bl-chaos-item-sev {
  font-size: 9.5px; font-weight: 800;
  padding: 3px 9px;
  border-radius: 999px;
  text-transform: uppercase; letter-spacing: 0.5px;
  border: 1px solid;
  flex-shrink: 0;
}
.bl-chaos-item-sev.warning  { color: #b45309; background: #fffbeb; border-color: #fde68a; }
.bl-chaos-item-sev.critical { color: #b91c1c; background: #fef2f2; border-color: #fecaca; }
.bl-chaos-item-sev.info     { color: #1e40af; background: #eff6ff; border-color: #bfdbfe; }

/* Big launch button */
.bl-chaos-launch {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px 16px;
  font-size: 13.5px; font-weight: 800;
  letter-spacing: 0.6px; text-transform: uppercase;
  color: #fff;
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(220, 38, 38, 0.32);
  transition: all 0.15s;
}
.bl-chaos-launch:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(220, 38, 38, 0.42);
  background: linear-gradient(180deg, #f87171 0%, #ef4444 100%);
}
.bl-chaos-launch:disabled {
  opacity: 0.6; cursor: not-allowed;
  background: linear-gradient(180deg, #94a3b8 0%, #64748b 100%);
  box-shadow: none;
}
.bl-chaos-launch.running {
  background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.42);
  opacity: 1;
}
.bl-spin { animation: bl-spin 0.9s linear infinite; }
@keyframes bl-spin { to { transform: rotate(360deg); } }

/* Status pill on the right */
.bl-chaos-status {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 10.5px; font-weight: 700;
  border: 1px solid;
}
.bl-chaos-status.off     { color: #64748b; background: #f1f5f9; border-color: #cbd5e1; }
.bl-chaos-status.running { color: #b45309; background: #fffbeb; border-color: #fde68a; }
.bl-chaos-status.done    { color: #047857; background: #ecfdf5; border-color: #a7f3d0; }
.bl-chaos-status.error   { color: #b91c1c; background: #fef2f2; border-color: #fecaca; }
.bl-chaos-status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor;
}
.bl-chaos-status.running .bl-chaos-status-dot { animation: bl-pulse 1.6s infinite; }

/* Live terminal */
.bl-chaos-terminal {
  flex: 1;
  min-height: 280px; max-height: 380px;
  background: #0a0f1c;
  border-radius: 8px;
  padding: 12px 0;
  overflow-y: auto;
  font-family: ui-monospace, "SF Mono", "Cascadia Code", monospace;
  font-size: 12px; line-height: 1.55;
}
.bl-chaos-term-empty {
  padding: 24px 16px; color: #475569; line-height: 1.7;
}
.bl-chaos-term-line {
  display: flex; gap: 10px;
  padding: 1px 14px;
  color: #cbd5e1;
  transition: background 0.1s;
}
.bl-chaos-term-line:hover { background: rgba(124, 58, 237, 0.08); }
.bl-chaos-term-ts {
  color: #475569;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  width: 56px;
}
.bl-chaos-term-text { flex: 1; min-width: 0; word-break: break-word; }
.bl-chaos-term-line.sev-info  .bl-chaos-term-text { color: #93c5fd; }
.bl-chaos-term-line.sev-warn  .bl-chaos-term-text { color: #fcd34d; }
.bl-chaos-term-line.sev-error .bl-chaos-term-text { color: #fca5a5; font-weight: 600; }
.bl-chaos-term-line.sev-ok    .bl-chaos-term-text { color: #86efac; }

/* Progress bar at bottom of terminal */
.bl-chaos-progress { margin-top: 2px; }
.bl-chaos-progress-meta {
  display: flex; justify-content: space-between;
  font-size: 11px; color: #475569;
  margin-bottom: 4px;
}
.bl-chaos-progress-phase { font-weight: 600; color: #0f172a; }
.bl-chaos-progress-pct   { font-weight: 700; font-variant-numeric: tabular-nums; color: #7c3aed; }
.bl-chaos-progress-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}
.bl-chaos-progress-bar > span {
  display: block; height: 100%;
  transition: width 0.3s ease;
}
.bl-chaos-progress-bar > span.sev-warning {
  background: linear-gradient(90deg, #f59e0b 0%, #dc2626 100%);
}
.bl-chaos-progress-bar > span.sev-ok {
  background: linear-gradient(90deg, #10b981 0%, #047857 100%);
}
.bl-chaos-progress-bar > span.sev-error {
  background: linear-gradient(90deg, #dc2626 0%, #7f1d1d 100%);
}

/* ── Timeline panel ─────────────────────── */
.bl-panel {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  overflow: hidden;
}
.bl-panel-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #faf5ff 100%);
}
.bl-panel-head-tabs {
  flex-direction: column; align-items: stretch;
  gap: 10px; padding: 0 16px;
}
.bl-tabs {
  display: flex; gap: 0;
  margin: 0 -16px; padding: 0 16px;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #faf5ff 100%);
}
.bl-tab {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 12px 14px;
  background: transparent; border: none;
  border-bottom: 2px solid transparent;
  font-size: 12.5px; font-weight: 600;
  color: #64748b; cursor: pointer; transition: all 0.15s;
  margin-bottom: -1px;
}
.bl-tab:hover { color: #0f172a; }
.bl-tab.active {
  color: #5b21b6;
  border-bottom-color: #7c3aed;
  background: rgba(124, 58, 237, 0.04);
}
.bl-tab-count {
  display: inline-block;
  padding: 1px 8px;
  background: #f1f5f9; color: #475569;
  border-radius: 999px;
  font-size: 10.5px; font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.bl-tab.active .bl-tab-count { background: #ede9fe; color: #5b21b6; }
.bl-panel-head-tabs .bl-filters { padding: 0 0 10px; }

.bl-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.bl-filters select, .bl-search {
  padding: 5px 10px; font-size: 11.5px; font-family: inherit;
  border: 1px solid #cbd5e1; border-radius: 5px; background: #fff;
}
.bl-filters select:focus, .bl-search:focus {
  outline: none; border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}
.bl-search { min-width: 180px; }

.bl-timeline { max-height: 560px; overflow-y: auto; padding: 6px 0; }
.bl-event {
  display: flex; gap: 0; padding: 10px 16px 6px;
  transition: background 0.12s;
}
.bl-event:hover { background: #faf5ff; }
.bl-event-rail {
  display: flex; flex-direction: column; align-items: center;
  flex-shrink: 0; width: 18px; padding-top: 6px;
}
.bl-event-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--kc, #94a3b8);
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px var(--kc, #94a3b8);
  flex-shrink: 0;
}
.bl-event-line {
  flex: 1; width: 2px; background: #e9d5ff;
  margin-top: 4px; margin-bottom: -10px; min-height: 12px;
}
.bl-event:last-child .bl-event-line { display: none; }
.bl-event-body { flex: 1; min-width: 0; padding-left: 12px; }
.bl-event-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 11px; margin-bottom: 3px;
}
.bl-event-source { font-weight: 700; color: var(--kc, #475569); font-size: 11px; }
.bl-event-time {
  margin-left: auto; font-size: 11px; color: #94a3b8;
  font-variant-numeric: tabular-nums;
}
.bl-event-title { font-weight: 600; color: #0f172a; font-size: 12.5px; line-height: 1.35; }
.bl-event-detail { font-size: 11.5px; color: #64748b; margin-top: 2px; line-height: 1.45; }
.bl-event-ref {
  display: inline-block; margin-top: 4px; font-size: 10px;
  background: #f1f5f9; border: 1px solid #e2e8f0;
  border-radius: 3px; padding: 1px 6px; color: #475569;
  font-family: ui-monospace, "SF Mono", monospace;
}
.bl-event-sev {
  font-size: 9.5px; font-weight: 700; padding: 2px 7px;
  border-radius: 3px;
  text-transform: uppercase; letter-spacing: 0.5px;
  border: 1px solid;
}
.bl-event-sev.info     { color: #1e3a8a; background: #eff6ff; border-color: #bfdbfe; }
.bl-event-sev.success  { color: #065f46; background: #ecfdf5; border-color: #a7f3d0; }
.bl-event-sev.warning  { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.bl-event-sev.error    { color: #7f1d1d; background: #fef2f2; border-color: #fecaca; }
.bl-event-sev.critical { color: #fff;    background: #b91c1c; border-color: #b91c1c; }

.bl-empty { padding: 40px 20px; text-align: center; font-size: 12px; color: #94a3b8; }
.bl-empty-hint { font-size: 11px; color: #cbd5e1; margin-top: 8px; }

/* System Changes table */
.bl-changes { max-height: 560px; overflow-y: auto; }
.bl-changes-table { display: flex; flex-direction: column; }
.bl-changes-row {
  display: grid;
  grid-template-columns: 95px 170px 110px 1fr;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 12px;
  align-items: start;
  transition: background 0.1s;
}
.bl-changes-row:hover { background: #faf5ff; }
.bl-changes-head {
  background: #f8fafc;
  font-size: 10.5px; font-weight: 700;
  color: #475569;
  text-transform: uppercase; letter-spacing: 0.6px;
  position: sticky; top: 0; z-index: 2;
  border-bottom: 2px solid #ddd6fe;
}
.bl-changes-head:hover { background: #f8fafc; }
.bl-c-time {
  color: #94a3b8; font-variant-numeric: tabular-nums; font-size: 11.5px;
}
.bl-c-entity {
  display: flex; align-items: center; gap: 7px;
  font-weight: 600; color: #0f172a;
}
.bl-c-entity-icon {
  width: 6px; height: 28px;
  border-radius: 3px;
  background: #7c3aed;
  flex-shrink: 0;
}
.bl-c-action-pill {
  display: inline-block; padding: 2px 9px; border-radius: 4px;
  font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.4px;
  border: 1px solid;
}
.bl-c-action-pill.a-créé,
.bl-c-action-pill.a-démarré { color: #065f46; background: #ecfdf5; border-color: #a7f3d0; }
.bl-c-action-pill.a-supprimé,
.bl-c-action-pill.a-arrêté  { color: #7f1d1d; background: #fef2f2; border-color: #fecaca; }
.bl-c-action-pill.a-modifié,
.bl-c-action-pill.a-redémarré { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.bl-c-action-pill.a-résolu  { color: #1e40af; background: #eff6ff; border-color: #bfdbfe; }
.bl-c-action-pill.a-other,
.bl-c-action-pill.a-       { color: #475569; background: #f1f5f9; border-color: #cbd5e1; }
.bl-c-title  { font-weight: 600; color: #0f172a; font-size: 12.5px; }
.bl-c-detail { font-size: 11px; color: #64748b; margin-top: 2px; }

/* ── Server Activity (parsed journalctl) ─────────── */
.bl-serv { margin-top: 18px; }
.bl-serv-controls {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.bl-serv-select {
  padding: 5px 10px;
  font-size: 11.5px; font-family: ui-monospace, "SF Mono", monospace;
  font-weight: 700;
  border: 1px solid #cbd5e1; border-radius: 5px;
  background: #fff;
}
.bl-serv-search { min-width: 160px; }
.bl-serv-counts {
  display: flex; gap: 6px;
  padding-left: 4px;
  border-left: 1px solid #e2e8f0; margin-left: 4px;
}
.bl-serv-count {
  font-size: 10.5px; font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid;
}
.bl-serv-count.bl-c-success { color: #065f46; background: #ecfdf5; border-color: #a7f3d0; }
.bl-serv-count.bl-c-warning { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.bl-serv-count.bl-c-error   { color: #7f1d1d; background: #fef2f2; border-color: #fecaca; }
.bl-mini-btn {
  padding: 4px 9px;
  background: #fff; color: #475569;
  border: 1px solid #cbd5e1; border-radius: 5px;
  font-size: 12px; cursor: pointer;
  transition: all 0.15s;
}
.bl-mini-btn:hover { background: #f1f5f9; border-color: #7c3aed; color: #5b21b6; }
.bl-mini-btn:active { transform: scale(0.92); }
.bl-mini-btn.active { background: #7c3aed; border-color: #7c3aed; color: #fff;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.18); }
.bl-mini-btn.spinning { animation: bl-spin 0.6s linear; pointer-events: none; }
@keyframes bl-spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }

/* Diagnostic banner — shows above the log feed when the selected unit is
   failed/inactive. Gives the operator the technical cause without scrolling. */
.bl-serv-diag {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 12px 14px; margin: 0 12px 8px;
  border-radius: 8px;
  font-size: 12.5px;
}
.bl-serv-diag--err {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fca5a5;
  color: #7f1d1d;
}
.bl-serv-diag--ok {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 8px 14px;
  align-items: center;
}
.bl-serv-diag-icon { color: #dc2626; flex-shrink: 0; margin-top: 1px; }
.bl-serv-diag-body { flex: 1; }
.bl-serv-diag-head {
  display: flex; justify-content: space-between; gap: 12px;
  align-items: baseline; margin-bottom: 4px;
}
.bl-serv-diag-head strong { font-size: 13px; }
.bl-serv-diag-state {
  font-size: 11px; padding: 2px 8px; border-radius: 999px;
  background: rgba(220, 38, 38, 0.15); color: #991b1b;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
}
.bl-serv-diag-cause {
  font-size: 12.5px; color: #7f1d1d;
  background: rgba(255,255,255,0.6);
  padding: 6px 10px; border-radius: 6px;
  border-left: 3px solid #dc2626;
  margin-bottom: 4px;
  line-height: 1.5;
}
.bl-serv-diag-cause--unknown {
  color: #78350f; border-left-color: #d97706;
  background: rgba(255,251,235,0.7); font-style: italic;
}
.bl-serv-diag-meta { font-size: 11px; color: #9f1239; opacity: 0.85; }
.bl-serv-diag-pulse {
  width: 8px; height: 8px; border-radius: 50%; background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
  animation: bl-pulse 1.6s ease-in-out infinite; flex-shrink: 0;
}
@keyframes bl-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25); }
  50%      { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0.0); }
}

.bl-serv-body {
  max-height: 480px;
  overflow-y: auto;
  background: #f8fafc;
  padding: 4px 0;
}
.bl-serv-row {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 16px;
  font-size: 12px;
  font-family: ui-monospace, "SF Mono", "Cascadia Code", monospace;
  border-bottom: 1px solid #eef2f7;
  transition: background 0.1s;
}
.bl-serv-row:hover { background: rgba(124, 58, 237, 0.04); }
.bl-serv-row.lvl-error    { background: rgba(220, 38, 38, 0.04); }
.bl-serv-row.lvl-warning  { background: rgba(245, 158, 11, 0.04); }
.bl-serv-row.lvl-success  { background: rgba(16, 185, 129, 0.025); }

.bl-serv-ts {
  width: 64px; flex-shrink: 0;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
  font-size: 11px;
}
.bl-serv-src {
  width: 90px; flex-shrink: 0;
  color: #475569;
  font-weight: 600;
  font-size: 11px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* HTTP method badge */
.bl-serv-method {
  display: inline-block;
  width: 52px; flex-shrink: 0;
  text-align: center;
  padding: 2px 0;
  border-radius: 4px;
  font-size: 10px; font-weight: 800;
  letter-spacing: 0.5px;
  color: #fff;
}
.bl-serv-method.m-get    { background: #2563eb; }
.bl-serv-method.m-post   { background: #16a34a; }
.bl-serv-method.m-put    { background: #d97706; }
.bl-serv-method.m-patch  { background: #d97706; }
.bl-serv-method.m-delete { background: #dc2626; }
.bl-serv-method.m-options{ background: #64748b; }

.bl-serv-path {
  flex: 1; min-width: 0;
  color: #1e1b4b;
  font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.bl-serv-status {
  width: 52px; flex-shrink: 0;
  text-align: center;
  padding: 2px 0;
  border-radius: 4px;
  font-size: 10.5px; font-weight: 800;
  border: 1px solid;
  font-variant-numeric: tabular-nums;
}
.bl-serv-status.ok    { color: #065f46; background: #ecfdf5; border-color: #a7f3d0; }
.bl-serv-status.redir { color: #1e40af; background: #eff6ff; border-color: #bfdbfe; }
.bl-serv-status.warn  { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.bl-serv-status.err   { color: #fff;    background: #b91c1c; border-color: #b91c1c; }

.bl-serv-user {
  width: 96px; flex-shrink: 0; text-align: right;
  font-size: 10.5px; color: #64748b;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Non-HTTP rows: level badge + message */
.bl-serv-lvl {
  width: 52px; flex-shrink: 0;
  text-align: center;
  padding: 2px 0;
  border-radius: 4px;
  font-size: 10px; font-weight: 800;
  border: 1px solid;
}
.bl-serv-lvl.lvl-info     { color: #1e40af; background: #eff6ff; border-color: #bfdbfe; }
.bl-serv-lvl.lvl-success  { color: #065f46; background: #ecfdf5; border-color: #a7f3d0; }
.bl-serv-lvl.lvl-warning  { color: #78350f; background: #fffbeb; border-color: #fde68a; }
.bl-serv-lvl.lvl-error    { color: #fff;    background: #b91c1c; border-color: #b91c1c; }

.bl-serv-msg {
  flex: 1; min-width: 0;
  color: #334155;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.bl-serv-msg-raw { color: #64748b; font-style: italic; }

/* Toast */
.bl-toast {
  position: fixed; bottom: 20px; right: 20px;
  padding: 11px 18px; background: #fff; border-radius: 6px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  font-size: 12.5px; font-weight: 600;
  border-left: 3px solid; z-index: 9999;
  max-width: 380px;
}
.bl-toast.success { color: #047857; border-color: #10b981; }
.bl-toast.error   { color: #b91c1c; border-color: #dc2626; }
.bl-toast.info    { color: #5b21b6; border-color: #7c3aed; }
.bl-toast-enter-active, .bl-toast-leave-active { transition: all 0.25s; }
.bl-toast-enter-from, .bl-toast-leave-to { opacity: 0; transform: translateX(20px); }

@media (max-width: 960px) {
  .bl-chaos-body { grid-template-columns: 1fr; }
  .bl-chaos-left { border-right: none; border-bottom: 1px solid #e2e8f0; }
  .bl-kpis { grid-template-columns: repeat(2, 1fr); }
}
</style>
