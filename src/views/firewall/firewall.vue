<template>
  <v-app id="inspire">
    <base-layout title="Rules">
      <template #content>
        <v-tabs
          v-model="selectedTab"
          background-color="#f5f5f5"
          color="black"
          :class="{ 'elevation-0': true }"
          :slider-color="'#FFC300'"
          @change="handleTabChange"
        >
          <v-tab
            v-for="tab in tabs"
            :key="tab.name_interface"
          >
            <span style="color: #020202">{{ tab.name_interface }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="selectedTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.name_interface"
            :value="tab.name_interface"
          >
            <v-card>
              <v-card-text>
                <FirewallComponent
                  :id="tab.name_interface"
                  :activeTab="selectedTab"
              /></v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../layouts/layout.vue";
import FirewallComponent from "../../views/firewall/rules/FirewallComponent.vue";

export default {
  components: {
    BaseLayout,
    FirewallComponent,
  },
  data() {
    return {
      selectedTab: "",
      activeTab: "",
      interfaces: [],
    };
  },
  computed: {
    tabs() {
      return this.interfaces.map((element) => ({
        name_interface: element.name_interface,
      }));
    },
  },
  methods: {
    handleTabChange(newTabValue) {
      this.activeTab = this.tabs[newTabValue].name_interface;
    },
  },
  mounted() {
    this.interfaces =
      document.getElementById("app").attributes["interfaces"].value;
    let validJsonString = this.interfaces
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.interfaces = parsedArray;
    this.selectedTab = this.interfaces[0].name_interface;
    console.log(this.selectedTab);
  },
};
</script>
