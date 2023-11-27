<template>
  <v-app id="inspire">
    <base-layout title="Site to site VPN" active-menu="activeTab">
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
            value="TUNNEL CONFIGURATION"
          >
            <v-card>
              <v-card-text><ipsecAdvancedParams /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="LISTING">
            <v-card>
              <v-card-text><ConfigurationList /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="MONITORING">
            <v-card> </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import ipsecAdvancedParams from "./ipsecAdvancedParams.vue";
import ConfigurationList from "./component/configurationList.vue";
export default {
  name: "IpsecComponent",
  components: {
    BaseLayout,
    ipsecAdvancedParams,
    ConfigurationList,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "TUNNEL CONFIGURATION",
      tabs: [
        { id: 1, label: "TUNNEL CONFIGURATION" },
        { id: 2, label: "LISTING" },
        { id: 3, label: "MONITORING" },
      ],
      rowDataServers: [],
      serverInfo: null,
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("ipsec-tab", val);
    },
  },
  mounted: async function () {
    let tab = localStorage.getItem("ipsec-tab") || "TUNNEL CONFIGURATION";
    this.activeTab = tab;

    this.serverInfo =
      document.getElementById("app").attributes["servers"].value;
    this.emitter.on("add-server", () => {
      this.activeTab = "TUNNEL CONFIGURATION";
    });

    this.rowDataServers =
      document.getElementById("app").attributes["servers"].value;
    let validJsonString = this.rowDataServers
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.rowDataServers = parsedArray;
  },
};
</script>
