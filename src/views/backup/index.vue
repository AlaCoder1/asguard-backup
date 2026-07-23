<template>
  <v-app id="inspire">
    <base-layout title="Backup & Restore" :active-menu="activeTab">

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
import RestoreHistory from "./components/RestoreHistory.vue";
import VmSnapshot from "./components/VmSnapshot.vue";
import BackupLogs from "./components/BackupLogs.vue";

export default {
  name: "BackupIndex",
  components: {
    BaseLayout,
    Backups,
    RestoreHistory,
    VmSnapshot,
    BackupLogs,
  },
  inject: ["emitter"],


  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "Backups", component: Backups },
        { id: 2, label: "Historique Restores", component: RestoreHistory },
        { id: 3, label: "Snapshot", component: VmSnapshot },
        { id: 4, label: "Logs", component: BackupLogs },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("backup-tab", val);
    },
  },
  mounted() {
    const DEFAULT_TAB = "Backups";
    const upgradeKey = "backup-drp-metrics-ui";
    if (localStorage.getItem(upgradeKey) !== "v3-clean") {
      localStorage.setItem("backup-tab", DEFAULT_TAB);
      localStorage.setItem(upgradeKey, "v3-clean");
    }
    const savedTab = localStorage.getItem("backup-tab") || DEFAULT_TAB;
    this.activeTab = this.tabs.some((tab) => tab.label === savedTab)
      ? savedTab
      : DEFAULT_TAB;

    this.emitter.on("reload-tabs", () => {
      const tab = localStorage.getItem("backup-tab") || DEFAULT_TAB;
      this.activeTab = this.tabs.some((item) => item.label === tab)
        ? tab
        : DEFAULT_TAB;
    });

  },

};
</script>

