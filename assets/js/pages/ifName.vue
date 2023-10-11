<template>
  <v-app id="inspire">
    <base-layout title="List of interface">
      <template #content>
        <v-tabs 
         background-color="#fff" color="#FFC300" dark @change="handleTabChange">
          <v-tab v-for="tab in tabs" :key="tab.id">
             <span style="color: #020202;">{{ tab.name_interface }}</span>
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.name_interface">
            <IfNameComponent :id="tab.name_interface" :activeTab="activeTabValue" />
          </v-tab-item>
        </v-tabs>
      </template>
    </base-layout>  
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import IfNameComponent from '@/components/network/IfNameComponent.vue';

export default {
  components: {
    BaseLayout,
    IfNameComponent
  },
  data() {
    return {
      activeTabValue: "",
      interfaces: [],
      IPV4Config: {},
      allStaticGateways: [],
    };
  },
   methods: {
     handleTabChange(newTabValue) {
       console.log("newTabValue "+ this.tabs[newTabValue].name_interface);   
       this.activeTabValue = this.tabs[newTabValue].name_interface;
    },
  },
  computed: {
    tabs() {
      return this.interfaces.map(element => {
        return {
          name_interface: element.name_interface,
        };
      });
      
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

