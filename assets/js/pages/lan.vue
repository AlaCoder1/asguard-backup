<template>
  <v-app id="inspire">
    <base-layout title="LAN/WAN" active-menu="lan">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id">
            {{ tab.label }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.id">
            <LanComponent v-if="tab.id === 1" />
            <WanComponent v-if="tab.id === 2" />
          </v-tab-item>
        </v-tabs>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import LanComponent from '@/components/network/LanComponent.vue';
import WanComponent from '@/components/network/WanComponent.vue';

export default {
  components: {
    BaseLayout,
    LanComponent,
    WanComponent,
  },
  data() {
    return {
      activeTab: null,
      tabs: [
        { id: 1, label: 'LAN' },
        { id: 2, label: 'WAN' },
      ],
    };
  },
  methods: {

  },
};
</script>

