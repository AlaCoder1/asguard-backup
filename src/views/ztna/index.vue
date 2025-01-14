<template>
  <v-app id="inspire">
    <base-layout title="ZTNA" active-menu="activeTab" ztnaTab="ztna">

      <template #content>
        <v-alert v-model="isZTNArunning" density="compact" type="warning"
          ><span style="font-size: 19px"
            >{{ $t("ztna.ZTNAStatus") }}
          </span>
        </v-alert>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs>
        <v-window v-model="activeTab">
          <v-window-item
            v-for="(tab, index) in tabs"
            :key="index"
            :value="tab.label"
          >
            <v-card>
              <v-card-text>
                <helpModal />
                <component :is="tab.component" :dataServer="dataServer" />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import helpModal from "@/components/modals/help.vue";

import BaseLayout from "@/layouts/layout.vue";
import identities from "./identities.vue";
import routers from "./routers.vue";
import configs from "./configs.vue";
import Services from "./servicestable.vue";
import Policies from "./policiestable.vue";

export default {
  name: "ZtnaComponent",
  components: {
    BaseLayout,
    identities,
    routers,
    configs,
    Services,
    Policies,
    helpModal
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      isZTNArunning: false,
      tabs: [
        { id: 1, label: "ztna.identities", component: identities },
        { id: 2, label: "ztna.configurations", component: configs },
        { id: 3, label: "ztna.services", component: Services },
        { id: 4, label: "ztna.relays", component: routers },
        { id: 5, label: "ztna.policies", component: Policies },
      ],
      rowDataServers: [],
      serverInfo: null,
      dataServer: null,
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("identities", val);
    },
  },
  mounted: async function () {
    let tab = localStorage.getItem("identities") || "ztna.identite";
    this.activeTab = tab;

   this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("identities") || "ztna.identite";
      if (tab) this.activeTab = tab;
    });
    this.checkZTNA();
  },
  methods: {
    checkZTNA() {
      let token = document.getElementById("app").getAttribute("token");
      if (token && token === "null") {
        this.isZTNArunning = true;
      }
    },
  },
};
</script>
<style>
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}
.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>