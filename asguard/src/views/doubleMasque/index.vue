<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.Dmasque')">
      <template #content>
        <!-- <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ $t(tab.label) }}</span>
          </v-tab>
        </v-tabs> -->

        <v-window v-model="activeTab">
          <v-window-item>
            <v-card>
              <v-card-text>
                <helpModal />
                <doubleMasque />
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
import doubleMasque from "../doubleMasque/doubleMasque.vue";

export default {
  name: "IdsIpsComponent",
  components: {
    BaseLayout,
    doubleMasque,
    helpModal,
  },
  inject: ["emitter"],
  data() {
    return {
      activeTab: "",
      tabs: [
        {
          id: 1,
          label: "tabs.configuration",
          component: doubleMasque,
        },
      ],
      configurationInfo: null,
    };
  },
  watch: {
    activeTab(newVal) {
      localStorage.setItem("Dmasque", newVal);
    },
  },
  methods: {},

  mounted: async function () {
    this.emitter.on("reload-tabs", () => {
      let tab = localStorage.getItem("Dmasque") || "tabs.configuration";
      if (tab) this.activeTab = tab;
    });

    let ids = localStorage.getItem("Dmasque") || "tabs.configuration";

    if (ids) this.activeTab = ids;
  },
};
</script>
<style>
.ag-paging-row-summary-panel {
  display: none;
}

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
