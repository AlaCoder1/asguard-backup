<template>
  <v-app id="inspire">
    <base-layout title="DHCPv4" active-menu="activeTab">
      <template #content>
        <v-tabs
          v-model="activeTab"
          background-color="#f5f5f5"
          color="black"
          :class="{ 'elevation-0': true }"
          :slider-color="'#FFC300'"
        >
          <v-tab
            v-for="tab in tabs"
            :key="tab.interface"
            :value="tab.name_interface"
          >
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <ConfigServerDhcp4Component
              :id="tab.name_interface"
              :activeTab="activeTab"
              :configInfo="tab"
            />
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../layouts/layout.vue";
import ConfigServerDhcp4Component from "./components/ConfigServerDhcp4Component.vue";
export default {
  name: "Dhcp4ServerComponent",
  components: {
    BaseLayout,
    ConfigServerDhcp4Component,
  },
  data() {
    return {
      activeTab: "",
      interfaces: [],
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
          enable_dhcpv4: element.enable_dhcpv4,
          subnet_addr: element.subnet_addr,
          subnet_mask: element.subnet_mask,
          available_range: element.available_range,
          range_from: element.range_from,
          range_to: element.range_to,
          dns_server: element.dns_server,
          gateway: element.gateway,
          domain_name: element.domain_name,
          id: element.id,
          ranges_address: element.ranges_address,
        };
      });
    },
  },
  beforeMount: async function () {
    this.interfaces =
      document.getElementById("app").attributes["list_dhcp4_server"].value;
    let validJsonString = this.interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.interfaces = parsedArray;
    let tab = localStorage.getItem("network-tab");
    if (tab) {
      this.activeTab = tab;
    } else {
      this.activeTab = this.interfaces[0]?.name_interface;
    }
  },
};
</script>
<style>
.ag-paging-row-summary-panel {
  display: none;
}
</style>
