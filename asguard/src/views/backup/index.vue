<template>
  <v-app id="inspire">
    <base-layout title="Backup & Restore" :active-menu="activeTab">

      <!-- Status pill dans la toolbar, à côté du titre -->
      <template #toolbar-status>
        <div class="bap-toolbar-pills">
          <div
            v-if="notifStore.notificationsConfigured"
            class="bap-pill bap-pill--live"
            title="Notifications actives — système surveillé"
          >
            <span class="bap-dot"></span>
            <span class="bap-label">LIVE</span>
            <span class="bap-sep"></span>
            <span class="bap-clock">{{ liveClock }}</span>
          </div>
          <div
            v-else
            class="bap-pill bap-pill--warn"
            title="Cliquer pour configurer les alertes"
            @click="activeTab = 'Alertes & Mailing'"
          >
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M6.5 1L12 11.5H1L6.5 1z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M6.5 5v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="6.5" cy="9.5" r=".7" fill="currentColor"/></svg>
            Alertes non configurées
          </div>
        </div>
      </template>

      <template #content>
        <div class="backup-content">
          <v-tabs v-model="activeTab" class="backup-tabs">
            <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
              <span>{{ tab.label }}</span>
            </v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <v-window-item
              v-for="tab in tabs"
              :key="tab.id"
              :value="tab.label"
            >
              <component :is="tab.component" />
            </v-window-item>
          </v-window>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import Backups from "./components/Backups.vue";
import VmSnapshot from "./components/VmSnapshot.vue";
import BackupSchedule from "./components/BackupSchedule.vue";
import BackupAlertsMailing from "./components/BackupAlertsMailing.vue";
import BackupLogs from "./components/BackupLogs.vue";
import BackupDashboardMonitoring from "./components/BackupDashboardMonitoring.vue";
import RestoreHistory from "./components/RestoreHistory.vue";
import BackupCloud from "./components/BackupCloud.vue";
import BackupRiskCenter from "./components/BackupRiskCenter.vue";
import { useNotifStore } from "@/store/modules/notifications.js";

export default {
  name: "BackupIndex",
  components: {
    BaseLayout,
    Backups,
    VmSnapshot,
    BackupSchedule,
    BackupAlertsMailing,
    BackupLogs,
    BackupDashboardMonitoring,
    RestoreHistory,
    BackupCloud,
    BackupRiskCenter,
  },
  inject: ["emitter"],

  setup() {
    const notifStore = useNotifStore();
    return { notifStore };
  },

  data() {
    return {
      activeTab: "",
      liveClock: "",
      _clockInterval: null,
      tabs: [
        { id: 1, label: "Dashboard & Monitoring", component: BackupDashboardMonitoring },
        { id: 2, label: "AI Risk Center", component: BackupRiskCenter },
        { id: 3, label: "Backups", component: Backups },
        { id: 4, label: "Historique Restores", component: RestoreHistory },
        { id: 5, label: "VM Snapshot", component: VmSnapshot },
        { id: 6, label: "Schedule", component: BackupSchedule },
        { id: 7, label: "Cloud Storage", component: BackupCloud },
        { id: 8, label: "Alertes & Mailing", component: BackupAlertsMailing },
        { id: 9, label: "Logs", component: BackupLogs },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("backup-tab", val);
    },
  },
  mounted() {
    const upgradeKey = "backup-drp-metrics-ui";
    if (localStorage.getItem(upgradeKey) !== "v2") {
      localStorage.setItem("backup-tab", "Dashboard & Monitoring");
      localStorage.setItem(upgradeKey, "v2");
    }
    const savedTab = localStorage.getItem("backup-tab") || "Dashboard & Monitoring";
    this.activeTab = this.tabs.some((tab) => tab.label === savedTab)
      ? savedTab
      : "Dashboard & Monitoring";

    this.emitter.on("reload-tabs", () => {
      const tab = localStorage.getItem("backup-tab") || "Dashboard & Monitoring";
      this.activeTab = this.tabs.some((item) => item.label === tab)
        ? tab
        : "Dashboard & Monitoring";
    });

    const tick = () => {
      this.liveClock = new Date().toTimeString().slice(0, 8);
    };
    tick();
    this._clockInterval = setInterval(tick, 1000);
  },

  beforeUnmount() {
    if (this._clockInterval) clearInterval(this._clockInterval);
  },
};
</script>

<style scoped>
/* ── Status pills dans la toolbar ──────────────────────── */
.bap-toolbar-pills {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.bap-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.4px;
  padding: 5px 12px 5px 8px;
  white-space: nowrap;
  cursor: default;
  user-select: none;
  transition: box-shadow 0.2s, transform 0.15s;
}

.bap-pill--drp {
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
  border: 1px solid #93c5fd;
  color: #1d4ed8;
  box-shadow: 0 1px 4px rgba(59,130,246,0.14);
  cursor: pointer;
}

.bap-pill--drp:hover {
  box-shadow: 0 2px 9px rgba(59,130,246,0.22);
  transform: translateY(-1px);
}

/* LIVE pill */
.bap-pill--live {
  background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
  border: 1px solid #86efac;
  color: #15803d;
  box-shadow: 0 1px 4px rgba(34,197,94,0.12);
}
.bap-pill--live:hover {
  box-shadow: 0 2px 8px rgba(34,197,94,0.2);
  transform: translateY(-1px);
}

/* Warning pill */
.bap-pill--warn {
  background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%);
  border: 1px solid #fbbf24;
  color: #b45309;
  box-shadow: 0 1px 4px rgba(245,158,11,0.12);
  cursor: pointer;
}
.bap-pill--warn:hover {
  box-shadow: 0 2px 8px rgba(245,158,11,0.25);
  transform: translateY(-1px);
}

/* Dot animé */
.bap-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
  animation: bap-pulse 2s ease-in-out infinite;
}

.bap-dot--blue {
  background: #3b82f6;
  animation: bap-pulse-blue 2s ease-in-out infinite;
}

@keyframes bap-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }
  50%       { box-shadow: 0 0 0 4px rgba(34,197,94,0); }
}

@keyframes bap-pulse-blue {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.48); }
  50%       { box-shadow: 0 0 0 4px rgba(59,130,246,0); }
}

.bap-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

/* Séparateur vertical */
.bap-sep {
  display: inline-block;
  width: 1px;
  height: 13px;
  background: rgba(21,128,61,0.25);
  flex-shrink: 0;
}

.bap-clock {
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.2px;
  color: #166534;
}
</style>
