<template>
  <v-app id="inspire">
    <base-layout title="Rules" active-menu="firewall">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.name_interface">
            {{ tab.name_interface }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.name_interface">
            <FirewallComponent :id="tab.name_interface" :activeTab="tab.name_interface" />
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
      activeTab: null,
      interfaces: [],
    };
  },
  computed: {
    tabs() {
      //  convert interfaces from string to array
      return this.interfaces.map(element => ({
        name_interface: element.name_interface,
      }));
    },
  },
  methods: {},
  mounted() {
    this.interfaces = this.$root.$data.interfaces;
    let validJsonString = this.interfaces
      .replace(/'/g, '"')
      .replace(/True/g, 'true')
      .replace(/False/g, 'false')
      .replace(/None/g, 'null');
    let parsedArray = JSON.parse(validJsonString);
    this.interfaces = parsedArray;
  },
};
</script>



