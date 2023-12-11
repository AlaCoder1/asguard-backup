<template>
  <v-app id="inspire">
    <base-layout title="ClamaV" active-menu="activeTab">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ tab.label }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="Configuration & Updates"
          >
            <v-card>
              <v-card-text><config /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="Scan">
            <v-card>
              <v-card-text></v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import config from "./config.vue";

export default {
  name: "ClamaV",
  components: {
    BaseLayout,
    config,
  },
  data() {
    return {
      activeTab: "Configuration & Updates",
      tabs: [
        { id: 1, label: "Configuration & Updates" },
        { id: 2, label: "Scan" },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("clamav-tab", val);
      this.dataServer = val;
    },
  },
  mounted: async function () {
    let tab = localStorage.getItem("clamav-tab") || "Configuration & Updates";
    this.activeTab = tab;
  },
};
</script>
