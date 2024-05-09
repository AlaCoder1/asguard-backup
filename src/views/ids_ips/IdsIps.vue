<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.intrusionDetection')">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="$t(tab.label)">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            :value="
              $t(tab.label) === 'CONFIGURATION'
                ? 'CONFIGURATION'
                : 'CONFIGURATION'
            "
          >
            <v-card>
              <v-card-text> <ConfigurationComponent /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            :value="$t(tab.label) === 'RULES' ? 'RULES' : 'REGLES'"
          >
            <v-card>
              <v-card-text>
                <RulesComponent :configInfo="configurationInfo"
              /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            :value="$t(tab.label) === 'ALERTS' ? 'ALERTS' : 'ALERTS'"
          >
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
      activeTab: "",
      tabs: [
        { id: 1, label: "tabs.configuration" },
        { id: 2, label: "tabs.rules" },
        { id: 3, label: "tabs.alerts" },
      ],
      configurationInfo: null,
    };
  },
  watch: {
    activeTab(newVal) {
      let tabs = newVal.split(" ");
      if (tabs.includes("CONFIGURATION") || tabs.includes("CONFIGURATION")) {
        localStorage.setItem("ids", "tabs.configuration");
      } else if (tabs.includes("RULES") || tabs.includes("REGLES")) {
        localStorage.setItem("ids", "tabs.rules");
      } else {
        localStorage.setItem("ids", "tabs.alerts");
      }
    },
  },
  methods: {},

  mounted: async function () {
    this.emitter.on("reload-tabs", () => {
      let tab = this.$t(
        localStorage.getItem("ids") || this.$t("tabs.configuration")
      );
      if (tab) this.activeTab = tab;
    });

    let ids = this.$t(
      localStorage.getItem("ids") || this.$t("tabs.configuration")
    );
    if (ids) this.activeTab = ids;
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
  },
};
</script>
<style>
.ag-paging-row-summary-panel {
  display: none;
}
</style>
