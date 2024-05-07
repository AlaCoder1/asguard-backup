<template>
  <v-app id="inspire">
    <base-layout title="Sdwan" :active-menu="activeTab">
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
              <v-card-text>
                <ConfigurationComponent />
              </v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="Visualization"
          >
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
import BaseLayout from "@/layouts/layout.vue";
import ConfigurationComponent from "./components/ConfigurationComponent.vue";

export default {
  name: "Sdwan",
  components: {
    BaseLayout,
    ConfigurationComponent,
  },
  data() {
    return {
      activeTab: "Configuration",
      tabs: [
        { id: 1, label: "Configuration" },
        { id: 2, label: "Visualization" },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("sdwan-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("sdwan-tab") || "Configuration";
    this.activeTab = tab;
  },
};
</script>

