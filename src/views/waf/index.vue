<template>
  <v-app id="inspire">
    <base-layout title="Waf" :active-menu="activeTab">
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
            value="Configuration"
          >
            <v-card>
              <v-card-text> <wafConfiguration /> </v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="RULES">
            <v-card>
              <v-card-text><wafRules /> </v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="ALERTS">
            <v-card>
              <v-card-text> </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import wafConfiguration from "./components/wafConfiguration.vue";
import wafRules from "./components/wafRules.vue";
import BaseLayout from "@/layouts/layout.vue";

export default {
  name: "Waf",
  components: {
    BaseLayout,
    wafConfiguration,
    wafRules,
  },
  data() {
    return {
      activeTab: "Configuration",
      tabs: [
        { id: 1, label: "Configuration" },
        { id: 2, label: "RULES" },
        { id: 3, label: "ALERTS" },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("waf-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("waf-tab") || "Configuration";
    this.activeTab = tab;
  },
};
</script>
