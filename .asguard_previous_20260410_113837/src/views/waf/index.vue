<template>
  <v-app id="inspire">
    <base-layout title="Waf">
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
              <v-card-header> 
                <helpModal v-if="activeTab === 'tabs.configuration'" help="wafConfig" />
                <helpModal v-if="activeTab === 'tabs.rules'" help="wafRules" />
                <helpModal v-if="activeTab === 'tabs.application'" help="wafApplications" />
                <helpModal v-if="activeTab === 'tabs.alerts'" help="wafalerts" />

              </v-card-header>
              <v-card-text>
                <component :is="tab.component" />
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

import wafConfiguration from "./components/wafConfiguration.vue";
import wafRules from "./components/wafRules.vue";
import wafAPP from "./components/wafApp.vue";
import wafAlerts from "./components/wafAlerts.vue";
import BaseLayout from "@/layouts/layout.vue";

export default {
  name: "Waf",
  components: {
    BaseLayout,
    wafConfiguration,
    wafRules,
    wafAPP,
    wafAlerts,
    helpModal,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "tabs.configuration", component: wafConfiguration },
        { id: 2, label: "tabs.rules", component: wafRules },
        { id: 3, label: "tabs.application", component: wafAPP },
        { id: 4, label: "tabs.alerts", component: wafAlerts },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("waf-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("waf-tab") || "tabs.configuration";
    this.activeTab = tab;

    this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("waf-tab") || "tabs.configuration";
      if (tab) this.activeTab = tab;
    });
  },
};
</script>
<style>
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
