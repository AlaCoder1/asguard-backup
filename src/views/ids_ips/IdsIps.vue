<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.intrusionDetection')">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="(tab, index) in tabs"
            :key="index"
            :value="tab.label"
          >
            <v-card>
              <v-card-text>
                <helpModal />

                <component
                  :is="tab.component"
                  :configInfo="configurationInfo"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import helpModal from "@/components/modals/help.vue";

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
    helpModal
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        {
          id: 1,
          label: "tabs.configuration",
          component: ConfigurationComponent,
        },
        { id: 2, label: "tabs.rules", component: RulesComponent },
        { id: 3, label: "tabs.alerts", component: AlertsComponent },
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
    this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("ids") || "tabs.configuration";
      if (tab) this.activeTab = tab;
    });

    let ids = localStorage.getItem("ids") || "tabs.configuration";

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
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}
.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>
