<template>
  <v-app id="inspire">
    <base-layout title="ZTNA" active-menu="activeTab" ztnaTab="ztna">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs>

        <!-- <v-window v-model="activeTab">
            <v-window-item
              v-for="tab in tabs"
              :key="tab.id"
              value="IDENTITIES"
            >
              <v-card>
                <v-card-text><identities :dataServer="dataServer" /></v-card-text>
              </v-card>
            </v-window-item>
            <v-window-item v-for="tab in tabs" :key="tab.id" value="RELAYS">
              <v-card>
                <v-card-text><routers /></v-card-text>
              </v-card>
            </v-window-item>
            <v-window-item v-for="tab in tabs" :key="tab.id" value="CONFIGURATIONS">
              <v-card>
                <v-card-text><configs /></v-card-text>
              </v-card>
            </v-window-item>
            <v-window v-model="activeTab">
            <v-window-item v-for="tab in tabs" :key="tab.id" value="SERVICES">
              <v-card>
                <v-card-text>
                  <Services />
                </v-card-text>
              </v-card>
            </v-window-item>
            <v-window-item v-for="tab in tabs" :key="tab.id" value="TERMINATORS">
              <v-card>
                <v-card-text>
                    <Terminators 
                />
                </v-card-text>
              </v-card>
            </v-window-item>
            <v-window-item v-for="tab in tabs" :key="tab.id" value="POLICIES">
              <v-card>
                <v-card-text>
                    <Policies 
                />
                </v-card-text>
              </v-card>
            </v-window-item>
           
        
          </v-window>
          </v-window> -->

        <v-window v-model="activeTab">
          <v-window-item
            v-for="(tab, index) in tabs"
            :key="index"
            :value="tab.label"
          >
            <v-card>
              <v-card-text>
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
import BaseLayout from "@/layouts/layout.vue";
import identities from "./identities.vue";
import routers from "./routers.vue";
import configs from "./configs.vue";
// import Terminators from "./terminatorstable.vue";
import Services from "./servicestable.vue";
import Policies from "./policiestable.vue";

export default {
  name: "ZtnaComponent",
  components: {
    BaseLayout,
    identities,
    routers,
    configs,
    // Terminators,
    Services,
    Policies,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "ztna.identite", component: identities },
        { id: 2, label: "ztna.configuration", component: configs },
        { id: 3, label: "ztna.services", component: Services },
        { id: 4, label: "ztna.relays", component: routers },
        // { id: 5, label: "ztna.terminators", component: Terminators },
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
  },
};
</script>
