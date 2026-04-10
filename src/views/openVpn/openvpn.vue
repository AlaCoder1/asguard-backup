<template>
  <v-app id="inspire">
    <base-layout title="Open VPN" :active-menu="activeTab">
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

                <helpModal v-if="activeTab === 'tabs.servers'" help="serverVPN" />
                <helpModal v-if="activeTab === 'tabs.clients'" help="clientVPN" />

                <component
                  :is="tab.component"
                  :serverInfo="serverInfo"
                  :dataClient="dataClient"
                  :dataServer="dataServer"
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
import ServersOpenvpnComponent from "./components/ServersOpenvpnComponent.vue";
import MonotoringOpenvpnComponent from "./components/MonotoringOpenvpnComponent.vue";
import ListingOpenvpnComponent from "./components/ListingOpenvpnComponent.vue";
import ClientsOpenvpnComponent from "./components/ClientsOpenvpnComponent.vue";

export default {
  name: "OpenvpnComponent",
  components: {
    BaseLayout,
    ServersOpenvpnComponent,
    MonotoringOpenvpnComponent,
    ListingOpenvpnComponent,
    ClientsOpenvpnComponent,
    helpModal
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      dataClient: null,
      dataServer: null,
      tabs: [
        { id: 1, label: "tabs.servers", component: ServersOpenvpnComponent },
        { id: 2, label: "tabs.clients", component: ClientsOpenvpnComponent },
        {
          id: 3,
          label: "tabs.monitoring",
          component: MonotoringOpenvpnComponent,
        },
        { id: 4, label: "tabs.listing", component: ListingOpenvpnComponent },
      ],
      rowDataServers: [],
      rowDataClients: [],
      serverInfo: null,
    };
  },
  watch: {
    activeTab(val) {
      this.dataClient = val;
      this.dataServer = val;
      localStorage.setItem("openvpn-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("openvpn-tab") || "tabs.servers";
    this.activeTab = tab;

    this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("openvpn-tab") || "tabs.servers";

      if (tab) this.activeTab = tab;
    });

    this.serverInfo =
      document.getElementById("app").attributes["servers"].value;
    this.emitter.on("add-server", () => {
      this.activeTab = "tabs.servers";
    });
    this.emitter.on("add-client", () => {
      this.activeTab = "tabs.clients";
    });
    this.emitter.on("open-listing", () => {
      this.activeTab = "tabs.listing";
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
    this.rowDataClients =
      document.getElementById("app").attributes["clients"].value;
    let validJsonString2 = this.rowDataClients
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray2 = JSON.parse(validJsonString2);
    this.rowDataClients = parsedArray2;
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