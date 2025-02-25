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
                <helpModal help="sdwan" />

                <ConfigurationComponent />
              </v-card-text>
            </v-card>
          </v-window-item>
          <!-- <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="Visualization"
          >
            <v-card>
              <v-card-text> </v-card-text>
            </v-card>
          </v-window-item> -->
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import ConfigurationComponent from "./components/ConfigurationComponent.vue";
import helpModal from "@/components/modals/help.vue";

export default {
  name: "Sdwan",
  components: {
    BaseLayout,
    ConfigurationComponent,
    helpModal
  },
  data() {
    return {
      activeTab: "Configuration",
      tabs: [
        { id: 1, label: "Configuration" },
        // { id: 2, label: "Visualization" },
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

