<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.logManagement')" active-menu="Key_Pair">
      <template #content>
        <v-tabs
          v-model="activeTab"
          background-color="#f5f5f5"
          color="black"
          :class="{ 'elevation-0': true }"
          :slider-color="'#FFC300'"
        >
          <v-tab v-for="tab in tabs" :key="tab.name" :value="tab.name">
            <span style="color: #020202">{{ tab.name }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="tab in tabs" :key="tab.name" :value="tab.name">
            <v-card>
              <v-card-text>
                <helpModal />
                <log :id="tab.name" :uuid="tab.uuid" :activeTab="activeTab" />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
import BaseLayout from "../../layouts/layout.vue";
import log from "./log.vue";
import helpModal from "@/components/modals/help.vue";

export default {
  components: {
    BaseLayout,
    log,
    helpModal,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      logsManagement: [],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("log-rotate", val);
    },
  },
  computed: {
    tabs() {
      const result = Object.keys(this.logsManagement[0]).map((key) => ({
        uuid: uuidv4(),
        name: key,
      }));
      return result;
    },
  },
  mounted() {
    let services = document.getElementById("app").attributes["logrotate"].value;
    let validJsonString = services
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let logData = JSON.parse(validJsonString);
    this.logsManagement = [logData];

    let tab = localStorage.getItem("log-rotate");
    if (tab) {
      this.activeTab = tab;
    } else {
      this.activeTab = this.tabs[0]?.name;
    }
  },
  methods: {},
};
</script>
