<template>
  <v-app id="inspire">
    <base-layout title="Open VPN" active-menu="CLIENTS">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ tab.label }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="tab in tabs" :key="tab.id" value="SERVERS">
            <v-card>
              <v-card-text> <ServersOpenvpnComponent /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="CLIENTS">
            <v-card>
              <v-card-text> <ClientsOpenvpnComponent /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="MONOTORING">
            <v-card>
              <v-card-text> <MonotoringOpenvpnComponent /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="LISTING">
            <v-card>
              <v-card-text> <ListingOpenvpnComponent /></v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import ServersOpenvpnComponent from "./components/ServersOpenvpnComponent.vue";
import ClientsOpenvpnComponent from "./components/ClientsOpenvpnComponent.vue";
import MonotoringOpenvpnComponent from "./components/MonotoringOpenvpnComponent.vue";
import ListingOpenvpnComponent from "./components/ListingOpenvpnComponent.vue";

export default {
  name: "OpenvpnComponent",
  components: {
    BaseLayout,
    ServersOpenvpnComponent,
    ClientsOpenvpnComponent,
    MonotoringOpenvpnComponent,
    ListingOpenvpnComponent,
  },
  data() {
    return {
      activeTab: 'SERVERS',
      tabs: [
        { id: 1, label: "SERVERS" },
        { id: 2, label: "CLIENTS" },
        { id: 3, label: "MONOTORING" },
        { id: 4, label: "LISTING" },
      ],
      rowDataServers: [],
      rowDataClients: [],
    };
  },
  methods: {},

  mounted: async function () {
    console.log("mounted");
    console.log(this.rowDataServers);
    console.log(
      "document.getElementById('app')",
      document.getElementById("app").attributes["servers"].value
    );

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
