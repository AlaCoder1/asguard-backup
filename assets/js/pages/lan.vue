<template>
  <v-app id="inspire">
    <base-layout title="LAN/WAN" active-menu="lan">
      <template #content>
        <network-manager />
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import NetworkManager from '@/components/NetworkManager.vue';

export default {
  name: 'LanComponent',
  components: {
    BaseLayout,
    NetworkManager
  },
  data() {
    return {

    };
  },
  methods: {

  },
};
</script>

