<template>
  <v-app id="inspire">
    <base-layout title="List of interface">
      <template #content>
        <v-tabs
          v-model="selectedTab"
          background-color="#f5f5f5"
          color="black"
          :class="{'elevation-0': true}"
          :slider-color="'#FFC300'"
          @change="handleTabChange"
        >
          <v-tab v-for="tab in tabs" :key="tab.id">
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="selectedTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <IfNameComponent
              :id="tab.name_interface"
              :activeTab="selectedTab"
            />
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../layouts/layout.vue";
import IfNameComponent from "../../views/network/components/IfNameComponent.vue";

export default {
  components: {
    BaseLayout,
    IfNameComponent,
  },
  data() {
    return {
      selectedTab: "",
      activeTabValue: "",
      interfaces: [],
      IPV4Config: {},
      allStaticGateways: [],
    };
  },
  methods: {
    handleTabChange(newTabValue) {
      this.activeTabValue = this.tabs[newTabValue].name_interface;
    },
  },
  computed: {
    tabs() {
      return this.interfaces.map((element) => {
        return {
          name_interface: element.name_interface,
        };
      });
    },
  },
  beforeMount: async function () {
    this.interfaces =
      document.getElementById("app").attributes["interfaces"].value;
    let validJsonString = this.interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.interfaces = parsedArray;

    this.IPV4Config =
      document.getElementById("app").attributes["IPV4Config"].value;
    validJsonString = this.IPV4Config.replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    parsedArray = JSON.parse(validJsonString);
    this.IPV4Config = parsedArray;

    this.allStaticGateways =
      document.getElementById("app").attributes["allStaticGateways"].value;
    validJsonString = this.allStaticGateways
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    parsedArray = JSON.parse(validJsonString);
    this.allStaticGateways = parsedArray;
  },
};
</script>
