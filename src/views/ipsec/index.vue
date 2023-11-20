<template>
  <v-app id="inspire">
    <base-layout title="IPSEC" active-menu="CONFIGURATION">
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
            <v-card> </v-card>
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
export default {
  name: "IpsecComponent",
  components: {
    BaseLayout,
    ipsecAdvancedParams
  },
  data() {
    return {
      activeTab: "IPESEC : CUSTOM TUNNEL SETTINGS",
      tabs: [
        { id: 1, label: "CONFIGURATION" },
        { id: 2, label: "MONITORING" },
        { id: 3, label: "IPESEC : CUSTOM TUNNEL SETTINGS" },
      ],
    };
  },
  methods: {},
};
</script>
