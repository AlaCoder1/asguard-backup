<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.settings')" :active-menu="activeTab">
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
                <helpModal v-if="activeTab === 'settings.General'"  help="settings" />
                <helpModal v-if="activeTab === 'settings.Administration'"  help="administration" />

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
import BaseLayout from "@/layouts/layout.vue";
import generalParams from "./components/generalParams.vue";
import systemAdministration from "./components/systemAdministration.vue";
import helpModal from "@/components/modals/help.vue";

export default {
  name: "Settings",
  components: {
    BaseLayout,
    generalParams,
    systemAdministration,
    helpModal,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "settings.General", component: generalParams },
        { id: 2, label: "settings.Administration", component: systemAdministration },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("settings-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("settings-tab") || "settings.General";
    this.activeTab = tab;

    this.emitter.on("reload-tabs", () => {
    let tab = localStorage.getItem("settings-tab") || "settings.General";
    if (tab) this.activeTab = tab;
    });

  },
};
</script>
