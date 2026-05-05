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
        <span class="rh-stat-label">Restores total</span>
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
        placeholder="Rechercher par backup ID, mode, job…"
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
            <th>Date</th>
            <th>Backup source</th>
            <th>Mode</th>
            <th>Statut</th>
            <th>Composants</th>
            <th>Durée</th>
            <th>Stabilisation</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="entry in filteredEntries" :key="entry.job_id">
            <tr
              class="rh-row"
              :class="{ expanded: expandedJob === entry.job_id }"
              @click="toggleExpand(entry.job_id)"
            >
              <td class="rh-expand-cell">
                <span class="rh-expand-icon">{{ expandedJob === entry.job_id ? '▾' : '▸' }}</span>
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

            <!-- Expanded detail row -->
            <tr v-if="expandedJob === entry.job_id" class="rh-detail-row">
              <td colspan="8">
                <div class="rh-detail-panel">

                  <!-- Job ID -->
                  <div class="rh-detail-jobid">
                    <span class="rh-detail-label">Job ID</span>
                    <code>{{ entry.job_id }}</code>
                  </div>

                  <!-- Impact summary banner -->
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

                  <!-- Per-component detail table -->
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
                          <td>
                            <span class="rh-cd-name">{{ c.name }}</span>
                          </td>
                          <td>
                            <span class="rh-cd-area">{{ componentDescription(c.name) }}</span>
                          </td>
                          <td>
                            <span class="rh-cd-msg" :title="c.message">{{ c.message || '—' }}</span>
                          </td>
                          <td>
                            <span v-if="c.file" class="rh-cd-file" :title="c.file">{{ shortFile(c.file) }}</span>
                            <span v-else class="rh-cd-empty">—</span>
                          </td>
                          <td>
                            <span v-if="c.size_mb" class="rh-cd-size">{{ c.size_mb }} Mo</span>
                            <span v-else class="rh-cd-empty">—</span>
                          </td>
                          <td>
                            <span class="rh-cd-dur">{{ formatDuration(c.duration_seconds) }}</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="rh-detail-empty" style="margin: 8px 0 16px">Aucun détail disponible (restore en cours ou ancien job).</div>

                  <div class="rh-detail-grid">

                    <!-- Timing -->
                    <div class="rh-detail-section">
                      <div class="rh-detail-title">🕐 Chronologie</div>
                      <div class="rh-timing-list">
                        <div class="rh-timing-item">
                          <span>Début</span>
                          <span>{{ formatDateTime(entry.started_at) }}</span>
                        </div>
                        <div class="rh-timing-item">
                          <span>Fin</span>
                          <span>{{ formatDateTime(entry.finished_at) }}</span>
                        </div>
                        <div class="rh-timing-item">
                          <span>Durée totale</span>
                          <strong>{{ formatDuration(entry.duration_seconds) }}</strong>
                        </div>
                      </div>
                    </div>

                    <!-- Slowest components -->
                    <div v-if="entry.slowest_components && entry.slowest_components.length > 0" class="rh-detail-section">
                      <div class="rh-detail-title">⏱ Composants les plus lents</div>
                      <div class="rh-slowest-list">
                        <div
                          v-for="s in entry.slowest_components"
                          :key="s.name"
                          class="rh-slowest-item"
                        >
                          <span class="rh-slowest-name">{{ s.name }}</span>
                          <div class="rh-slowest-bar-wrap">
                            <div
                              class="rh-slowest-bar"
                              :style="{ width: slowestBarWidth(s.duration_seconds, entry.slowest_components) + '%' }"
                            ></div>
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
      expandedJob: null,
      statusFilters: [
        { label: "Tous", value: "all" },
        { label: "Succès", value: "success" },
        { label: "Partiel", value: "partial_success" },
        { label: "Erreur", value: "error" },
        { label: "En cours", value: "running" },
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
    filteredEntries() {
      let list = this.entries;
      if (this.activeFilter !== "all") {
        list = list.filter((e) => e.status === this.activeFilter);
      }
      if (this.search.trim()) {
        const q = this.search.trim().toLowerCase();
        list = list.filter(
          (e) =>
            (e.backup_id || "").toLowerCase().includes(q) ||
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
    modeLabel(mode) {
      const map = { safe: "Safe", complete: "Full", full: "Full", selected_components: "Custom" };
      return map[mode] || mode || "—";
    },
    statusLabel(status) {
      const map = { success: "Vérifié", partial_success: "Partiel", error: "Erreur", running: "En cours", queued: "En attente" };
      return map[status] || status || "—";
    },
    stabLabel(s) {
      if (s === "success") return "OK";
      if (s === "partial") return "Partiel";
      if (!s) return "—";
      return s;
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

<style scoped>
.restore-history-page {
  padding: 24px;
  min-height: 400px;
  position: relative;
}

/* Loading */
.rh-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}
.rh-loading-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 16px 28px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  font-size: 14px;
  color: #444;
}
.rh-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #e0e0e0;
  border-top-color: #1565c0;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Stats bar */
.rh-stats-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #f8f9fc;
  border-radius: 12px;
  border: 1px solid #e8eaf0;
}
.rh-stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  padding: 8px 14px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e4ec;
}
.rh-stat-card.success { border-color: #a5d6a7; background: #f1f8e9; }
.rh-stat-card.danger  { border-color: #ef9a9a; background: #fff3f3; }
.rh-stat-value { font-size: 22px; font-weight: 700; color: #1a237e; line-height: 1.2; }
.rh-stat-label { font-size: 11px; color: #78909c; margin-top: 2px; text-align: center; }
.rh-refresh-btn {
  margin-left: auto;
  padding: 8px 18px;
  border: 1.5px solid #1565c0;
  border-radius: 8px;
  background: #fff;
  color: #1565c0;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s;
}
.rh-refresh-btn:hover:not(:disabled) { background: #e3f2fd; }
.rh-refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Filters */
.rh-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.rh-search {
  flex: 1;
  min-width: 220px;
  padding: 8px 14px;
  border: 1.5px solid #dde1ea;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: #fff;
}
.rh-search:focus { border-color: #1565c0; }
.rh-filter-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.rh-chip {
  padding: 5px 12px;
  border: 1.5px solid #dde1ea;
  border-radius: 20px;
  background: #fff;
  font-size: 12px;
  color: #546e7a;
  cursor: pointer;
  transition: all 0.15s;
}
.rh-chip.active { border-color: #1565c0; background: #1565c0; color: #fff; }
.rh-chip:hover:not(.active) { border-color: #90a4ae; }

/* Empty */
.rh-empty {
  text-align: center;
  padding: 60px 20px;
  color: #90a4ae;
}
.rh-empty-icon { font-size: 40px; margin-bottom: 10px; }

/* Table */
.rh-table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #e8eaf0; }
.rh-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.rh-table thead tr {
  background: #f3f5fa;
  border-bottom: 2px solid #e0e4ec;
}
.rh-table th {
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #546e7a;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.rh-row {
  border-bottom: 1px solid #f0f2f7;
  cursor: pointer;
  transition: background 0.1s;
}
.rh-row:hover { background: #f5f7fc; }
.rh-row.expanded { background: #eef2fb; }
.rh-table td { padding: 10px 14px; vertical-align: middle; }
.rh-expand-cell { width: 28px; color: #90a4ae; }
.rh-expand-icon { font-size: 14px; }

/* Date */
.rh-date-primary { font-weight: 600; color: #263238; font-size: 13px; }
.rh-date-secondary { font-size: 11px; color: #90a4ae; }

/* Backup ID */
.rh-backup-id {
  font-family: monospace;
  font-size: 12px;
  color: #37474f;
  background: #f0f2f7;
  padding: 2px 7px;
  border-radius: 4px;
}

/* Mode badge */
.rh-mode-badge {
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: #e8eaf0;
  color: #455a64;
}
.rh-mode-badge.complete, .rh-mode-badge.full { background: #e3f2fd; color: #1565c0; }
.rh-mode-badge.safe { background: #e8f5e9; color: #2e7d32; }
.rh-mode-badge.selected_components { background: #fff3e0; color: #e65100; }

/* Status badge */
.rh-status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  display: inline-block;
}
.rh-status-badge.success { background: #e8f5e9; color: #2e7d32; }
.rh-status-badge.partial_success { background: #fff8e1; color: #f57f17; }
.rh-status-badge.error { background: #ffebee; color: #c62828; }
.rh-status-badge.running { background: #e3f2fd; color: #1565c0; }
.rh-status-badge.queued { background: #f3e5f5; color: #6a1b9a; }

/* Component pills */
.rh-comp-pills { display: flex; gap: 6px; }
.rh-pill {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.rh-pill.ok   { background: #e8f5e9; color: #2e7d32; }
.rh-pill.fail { background: #ffebee; color: #c62828; }
.rh-pill.skip { background: #f0f2f7; color: #78909c; }

/* Duration */
.rh-duration { font-weight: 600; color: #37474f; font-size: 13px; }

/* Stabilisation */
.rh-stab-badge {
  padding: 2px 9px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}
.rh-stab-badge.success { background: #e8f5e9; color: #2e7d32; }
.rh-stab-badge.partial { background: #fff8e1; color: #f57f17; }
.rh-stab-badge.unknown { background: #f0f2f7; color: #90a4ae; }

/* Detail panel */
.rh-detail-row td { padding: 0; }
.rh-detail-panel {
  background: #f8faff;
  border-top: 2px solid #c5cae9;
  padding: 20px 24px;
}
.rh-detail-jobid {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-size: 12px;
}
.rh-detail-label { font-weight: 600; color: #78909c; text-transform: uppercase; font-size: 11px; }
code {
  background: #e8eaf0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #37474f;
}
.rh-detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.rh-detail-section {
  background: #fff;
  border: 1px solid #e0e4ec;
  border-radius: 8px;
  padding: 14px 16px;
}
.rh-detail-title {
  font-weight: 700;
  font-size: 12px;
  color: #455a64;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.rh-text-danger { color: #c62828 !important; }
.rh-detail-empty { font-size: 12px; color: #90a4ae; }
.rh-comp-list { display: flex; flex-wrap: wrap; gap: 5px; }
.rh-comp-tag {
  padding: 2px 9px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}
.rh-comp-tag.ok   { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.rh-comp-tag.fail { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }

/* Slowest components */
.rh-slowest-list { display: flex; flex-direction: column; gap: 8px; }
.rh-slowest-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.rh-slowest-name { width: 90px; font-weight: 500; color: #37474f; flex-shrink: 0; }
.rh-slowest-bar-wrap { flex: 1; background: #e8eaf0; border-radius: 4px; height: 6px; overflow: hidden; }
.rh-slowest-bar { height: 100%; background: #1565c0; border-radius: 4px; transition: width 0.3s; }
.rh-slowest-dur { width: 36px; text-align: right; color: #546e7a; font-weight: 600; flex-shrink: 0; }

/* Timing */
.rh-timing-list { display: flex; flex-direction: column; gap: 6px; }
.rh-timing-item { display: flex; justify-content: space-between; font-size: 12px; color: #546e7a; }
.rh-timing-item strong { color: #263238; }

/* Impact banner */
.rh-impact-banner {
  background: linear-gradient(135deg, #f0f4ff 0%, #f8faff 100%);
  border: 1px solid #c5cae9;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 18px;
}
.rh-impact-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.rh-impact-title {
  font-weight: 700;
  font-size: 12px;
  color: #1a237e;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}
.rh-impact-subtitle {
  font-size: 12px;
  color: #546e7a;
  font-style: italic;
}
.rh-impact-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.rh-impact-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 1.5px solid transparent;
  cursor: default;
  transition: transform 0.1s;
}
.rh-impact-chip:hover { transform: translateY(-1px); }
.rh-impact-chip.success { background: #e8f5e9; border-color: #a5d6a7; color: #1b5e20; }
.rh-impact-chip.failed  { background: #ffebee; border-color: #ef9a9a; color: #b71c1c; }
.rh-impact-icon { font-size: 14px; line-height: 1; }
.rh-impact-label { white-space: nowrap; }
.rh-impact-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.rh-impact-dot.success { background: #43a047; }
.rh-impact-dot.failed  { background: #e53935; }

/* Component detail table */
.rh-comp-detail-section {
  margin-bottom: 16px;
}
.rh-comp-detail-section .rh-detail-title {
  font-weight: 700;
  font-size: 12px;
  color: #455a64;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.rh-comp-detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e4ec;
}
.rh-comp-detail-table thead tr {
  background: #f3f5fa;
  border-bottom: 1.5px solid #e0e4ec;
}
.rh-comp-detail-table th {
  padding: 7px 12px;
  text-align: left;
  font-weight: 600;
  color: #78909c;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.rh-comp-detail-table td {
  padding: 7px 12px;
  vertical-align: middle;
  border-bottom: 1px solid #f0f2f7;
}
.rh-comp-detail-table tbody tr:last-child td { border-bottom: none; }
.rh-cd-row-failed { background: #fffbfb; }
.rh-cd-row-success { background: #fff; }
.rh-cd-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
}
.rh-cd-status.success { background: #e8f5e9; color: #2e7d32; }
.rh-cd-status.failed  { background: #ffebee; color: #c62828; }
.rh-cd-name {
  font-family: monospace;
  font-size: 11px;
  font-weight: 600;
  color: #37474f;
  background: #f0f2f7;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}
.rh-cd-area {
  color: #455a64;
  font-size: 12px;
  white-space: nowrap;
}
.rh-cd-msg {
  color: #546e7a;
  font-size: 12px;
  max-width: 320px;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rh-cd-file {
  font-family: monospace;
  font-size: 11px;
  color: #546e7a;
  white-space: nowrap;
}
.rh-cd-size { color: #78909c; white-space: nowrap; }
.rh-cd-dur  { font-weight: 600; color: #37474f; white-space: nowrap; }
.rh-cd-empty { color: #bdbdbd; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
