<template>
  <v-app id="inspire">
    <base-layout title="Settings" :active-menu="activeTab">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ tab.label }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="tab in tabs" :key="tab.id" value="General">
            <v-card>
              <v-card-text>
                <helpModal />

                <generalParams />
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
import helpModal from "@/components/modals/help.vue";

export default {
  name: "Settings",
  components: {
    BaseLayout,
    generalParams,
    helpModal,
  },
  data() {
    return {
      activeTab: "General",
      tabs: [{ id: 1, label: "General" }],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("settings-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("settings-tab") || "General";
    this.activeTab = tab;
  },
};
</script>
