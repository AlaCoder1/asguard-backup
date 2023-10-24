<template>
  <v-app id="inspire">
    <base-layout title="Rules" active-menu="firewall">
      <template #content>
        <!-- <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.name_interface">
            {{ tab.name_interface }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.name_interface">
            <FirewallComponent :id="tab.name_interface" :activeTab="tab.name_interface" />
          </v-tab-item>
        </v-tabs> -->


        <v-tabs
        v-model="activeTab"
        >
          <v-tab v-for="tab in tabs" :key="tab.name_interface"  :value="tab.name_interface">
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="tab in tabs" :key="tab.name_interface" value="LAN">
            <v-card>
              <v-card-text>   <FirewallComponent :id="tab.name_interface" :activeTab="tab.name_interface" /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.name_interface" value="WAN">
            <v-card>
              <v-card-text>   WAN</v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '../../layouts/layout.vue';
import FirewallComponent from '../../views/firewall/rules/FirewallComponent.vue';

export default {
  components: {
    BaseLayout,
    FirewallComponent
  },
  data() {
    return {
      activeTab: 'LAN',
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
    this.interfaces =   document.getElementById("app").attributes["interfaces"].value;
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



