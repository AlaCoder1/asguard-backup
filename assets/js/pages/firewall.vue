<template>
  <v-app id="inspire">
    <base-layout title="Firewall" active-menu="firewall">
      <template #content>
        <FirewallComponent />
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
    };
  },
  beforeMount() {
    this.firewall = this.$root.$data.firewall;
  },
};
</script>

