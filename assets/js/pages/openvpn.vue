<template>
  <v-app id="inspire">
    <base-layout title="Open VPN" active-menu="CLIENTS">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id">
            {{ tab.label }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.id">
            <ServersOpenvpnComponent v-if="tab.id === 1" />
            <ClientsOpenvpnComponent v-if="tab.id === 2" />
            <MonotoringOpenvpnComponent v-if="tab.id === 3" />
            <ListingOpenvpnComponent v-if="tab.id === 4" />
          </v-tab-item>
        </v-tabs>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import ServersOpenvpnComponent from '@/components/ServersOpenvpnComponent.vue';
import ClientsOpenvpnComponent from '@/components/ClientsOpenvpnComponent.vue';
import MonotoringOpenvpnComponent from '@/components/MonotoringOpenvpnComponent.vue';
import ListingOpenvpnComponent from '@/components/ListingOpenvpnComponent.vue';

export default {
  name: 'SettingsComponent',
  components: {
    BaseLayout,
    ServersOpenvpnComponent,
    ClientsOpenvpnComponent,
    MonotoringOpenvpnComponent,
    ListingOpenvpnComponent,
  },
  data() {
    return {
      activeTab: null,
      tabs: [
        { id: 1, label: 'SERVERS' },
        { id: 2, label: 'CLIENTS' },
        { id: 3, label: 'MONOTORING' },
        { id: 4, label: 'LISTING' },
      ],
    };
  },
  methods: {

  },
};
</script>
