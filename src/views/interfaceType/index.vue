<template>
  <v-app id="inspire">
    <base-layout
      :title="$t('typeInterface.otherTypesOfInterfaces')"
      active-menu="interface"
    >
      <template #content>
        <helpModal />
        <div class="mr-3">
          <vlan />
          <vxlan />
          <assign />
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import vlan from "./components/Vlan.vue";
import vxlan from "./components/Vxlan.vue";
import assign from "./components/Assign.vue";
import helpModal from "@/components/modals/help.vue";

export default {
  name: "Interface",
  components: {
    vlan,
    vxlan,
    assign,
    BaseLayout,
    helpModal,
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
