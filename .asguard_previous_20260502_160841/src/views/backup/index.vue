<template>
  <v-app id="inspire">
    <base-layout title="Backup & Restore" :active-menu="activeTab">
      <template #content>
        <div class="backup-content">
          <div class="backup-alert-pill">
            <span class="warning-icon">△</span>
            Alertes non configurées
          </div>

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
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "Dashboard & Monitoring", component: BackupDashboardMonitoring },
        { id: 2, label: "Backups", component: Backups },
        { id: 3, label: "Historique Restores", component: RestoreHistory },
        { id: 4, label: "VM Snapshot", component: VmSnapshot },
        { id: 5, label: "Schedule", component: BackupSchedule },
        { id: 6, label: "Cloud Storage", component: BackupCloud },
        { id: 7, label: "Alertes & Mailing", component: BackupAlertsMailing },
        { id: 8, label: "Logs", component: BackupLogs },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("backup-tab", val);
    },
  },
  mounted() {
    const savedTab = localStorage.getItem("backup-tab") || "Backups";
    this.activeTab = this.tabs.some((tab) => tab.label === savedTab)
      ? savedTab
      : "Backups";

    this.emitter.on("reload-tabs", () => {
      const tab = localStorage.getItem("backup-tab") || "Backups";
      this.activeTab = this.tabs.some((item) => item.label === tab)
        ? tab
        : "Backups";
    });
  },
};
</script>
