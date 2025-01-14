<template>
  <v-app id="inspire">
    <base-layout :title="$t('tabs.NAT')" :active-menu="activeTab">
      <template #content>
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
                <component :is="tab.component" />
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
import Snat from "./components/Snat.vue";
import OneToOne from "./components/OneToOne.vue";
import Dnat from "./components/Dnat.vue";
import helpModal from "@/components/modals/help.vue";


export default {
  name: "Nat",
  components: {
    BaseLayout,
    Snat,
    OneToOne,
    Dnat,
    helpModal
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        { id: 1, label: "tabs.SNAT", component: Snat },
        { id: 2, label: "tabs.OneToOne", component: OneToOne },
        { id: 3, label: "tabs.DNAT", component: Dnat },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("nat-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("nat-tab") || "tabs.SNAT";
    this.activeTab = tab;

    this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("nat-tab") || "tabs.SNAT";
      if (tab) this.activeTab = tab;
    });
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