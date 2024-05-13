<template>
  <v-app id="inspire">
    <base-layout title="List of interface" active-menu="activeTab">
      <template #content>
        <v-tabs
          v-model="activeTab"
          background-color="#f5f5f5"
          color="black"
          :class="{'elevation-0': true}"
          :slider-color="'#FFC300'"
        >
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.name_interface">
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <IfNameComponent
              :id="tab.name_interface"
              :activeTab="activeTab"
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
      activeTab: "",
      interfaces: [],
      IPV4Config: {},
      allStaticGateways: [],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("network-tab", val);
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

    let tab = localStorage.getItem("network-tab")
    if (tab) {
      this.activeTab = tab;
    } else {
      this.activeTab = this.interfaces[0]?.name_interface;
    }

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
