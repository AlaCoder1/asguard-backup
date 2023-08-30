<template>
  <v-app id="inspire">
    <base-layout title="Rules" active-menu="firewall">
      <template #content>
        <v-tabs v-model="activeTab">
            <v-tab v-for="tab in tabs" :key="tab.id">
              {{ tab.label }}
            </v-tab>
            <v-tab-item v-for="tab in tabs" :key="tab.id">
              <FirewallComponent v-if="tab.id == 1" activeTab="Flottant" />
              <FirewallComponent v-if="tab.id == 2" activeTab="LAN" />
              <FirewallComponent v-if="tab.id == 3" activeTab="Loopback" />
              <FirewallComponent v-if="tab.id == 4" activeTab="WAN" />
            </v-tab-item>
          </v-tabs>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import FirewallComponent from '@/components/firewall/FirewallComponent.vue';

export default {
  components: {
    BaseLayout,
    FirewallComponent
},
  data() {
    return {
       activeTab: 0,
      tabs: [
        { id: 1, label: 'Flottant' },
        { id: 2, label: 'LAN' },
        { id: 3, label: 'Loopback' },
        { id: 4, label: 'WAN' },
      ],
      firewall: ""
    };
  },
  beforeMount() {
    this.firewall = this.$root.$data.firewall;
  },
};
</script>

