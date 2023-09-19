<template>
  <v-app id="inspire">
    <base-layout title="List of interface" :activeMenu="activeTab">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id">
            {{ tab.name_interface }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.id">
            <LanComponent v-if="tab.name_interface === 'LAN'" activeTab="LAN" />
            <WanComponent v-if="tab.name_interface === 'WAN'" activeTab="WAN" />
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
      activeTab: 0,
      interfaces: [],
      IPV4Config: {},
      allStaticGateways: [],
    };
  },
  computed: {
    tabs() {
      return this.interfaces.map(element => ({
        name_interface: element.name_interface,
      }));
    },
  },
  mounted() {
    this.interfaces = this.$root.$data.interfaces;
    let validJsonString = this.interfaces
      .replace(/'/g, '"')
      .replace(/True/g, 'true')
      .replace(/False/g, 'false')
      .replace(/None/g, 'null');
    let parsedArray = JSON.parse(validJsonString);
    this.interfaces = parsedArray;

    this.IPV4Config = this.$root.$data.IPV4Config;
    validJsonString = this.IPV4Config
      .replace(/'/g, '"')
      .replace(/True/g, 'true')
      .replace(/False/g, 'false')
      .replace(/None/g, 'null');
    parsedArray = JSON.parse(validJsonString);
    this.IPV4Config = parsedArray;

    this.allStaticGateways = this.$root.$data.allStaticGateways;
    validJsonString = this.allStaticGateways
      .replace(/'/g, '"')
      .replace(/True/g, 'true')
      .replace(/False/g, 'false')
      .replace(/None/g, 'null');
    parsedArray = JSON.parse(validJsonString);
    this.allStaticGateways = parsedArray;
  },
};
</script>

