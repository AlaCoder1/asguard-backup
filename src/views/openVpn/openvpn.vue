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
      activeTab: 'MONOTORING',
      tabs: [
        { id: 1, label: "SERVERS" },
        { id: 2, label: "CLIENTS" },
        { id: 3, label: "MONOTORING" },
        { id: 4, label: "LISTING" },
      ],
    };
  },
  methods: {},
};
</script>
