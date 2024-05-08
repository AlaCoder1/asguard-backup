<template>
  <v-app id="inspire">
    <base-layout
      :title="$t('subtitle.intrusionDetection')"
      active-menu="CONFIGURATION"
    >
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
            value="CONFIGURATION"
          >
            <v-card>
              <v-card-text> <ConfigurationComponent /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="RULES">
            <v-card>
              <v-card-text>
                <RulesComponent :configInfo="configurationInfo"
              /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="ALERTS">
            <v-card>
              <v-card-text>
                <AlertsComponent :configInfo="configurationInfo"
              /></v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import AlertsComponent from "./components/AlertsComponent.vue";
import RulesComponent from "./components/RulesComponent.vue";
import ConfigurationComponent from "./components/ConfigurationComponent.vue";

export default {
  name: "IdsIpsComponent",
  components: {
    BaseLayout,
    ConfigurationComponent,
    RulesComponent,
    AlertsComponent,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "CONFIGURATION",
      tabs: [
        { id: 1, label: "CONFIGURATION" },
        { id: 2, label: "RULES" },
        { id: 3, label: "ALERTS" },
      ],
      configurationInfo: null,
    };
  },
  watch: {
    activeTab(newVal) {
      localStorage.setItem("ids", newVal);
    },
  },
  methods: {},

  mounted: async function () {
    let ids = localStorage.getItem("ids") || "CONFIGURATION";
    this.activeTab = ids;
    this.rowDataConfiguration =
      document.getElementById("app").attributes[
        "general_config_suricata"
      ].value;
    let validJsonString = this.rowDataConfiguration
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.rowDataConfiguration = parsedArray;
    this.configurationInfo = this.rowDataConfiguration.configuration.id;
    console.log(this.rowDataConfiguration);
  },
};
</script>
<style>
.ag-paging-row-summary-panel {
  display: none;
}
</style>
