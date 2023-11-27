<template>
  <v-app id="inspire">
    <base-layout title="IPSEC" active-menu="activeTab">
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
              <v-card-text><ConfigurationList/></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="MONITORING">
            <v-card> </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="IPESEC : CUSTOM TUNNEL SETTINGS"
          >
            <v-card>
              <v-card-text><ipsecAdvancedParams/></v-card-text>
            </v-card>
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
    ConfigurationList
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "CONFIGURATION",
      tabs: [
        { id: 1, label: "CONFIGURATION" },
        { id: 2, label: "MONITORING" },
        { id: 3, label: "IPESEC : CUSTOM TUNNEL SETTINGS" },
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
    let tab = localStorage.getItem("ipsec-tab") || "CONFIGURATION";
    this.activeTab = tab;

    this.serverInfo =
      document.getElementById("app").attributes["servers"].value;
    this.emitter.on("add-server", () => {
      this.activeTab = "IPESEC : CUSTOM TUNNEL SETTINGS";
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
