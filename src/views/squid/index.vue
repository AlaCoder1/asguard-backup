<template>
  <v-app id="inspire">
    <base-layout title="Proxy" active-menu="Key_Pair">
      <template #content>
        <v-alert
          v-model="state.serverStatus"
          density="compact"
          type="warning"
          :title="$t('squid.restart')"
        ></v-alert>
        <helpModal />

        <div class="mr-6 ml-3">
          <general_info />
          <list />
          <acl_list />
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import helpModal from "@/components/modals/help.vue";

import { onMounted, reactive } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import general_info from "./component/general_info.vue";
import list from "./component/list.vue";
import acl_list from "./component/acl_list.vue";

export default {
  name: "Proxy",
  components: {
    BaseLayout,
    general_info,
    acl_list,
    list,
    helpModal
  },

  setup() {
    const state = reactive({
      serverStatus: true,
    });
    onMounted(() => {
      const statusServerAttribute =
        document.getElementById("app").attributes["statusServer"].value;
      const statusServer = JSON.parse(statusServerAttribute);
      state.serverStatus = statusServer;
    });

    return {
      state,
    };
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