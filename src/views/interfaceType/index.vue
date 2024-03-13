<template>
  <v-app id="inspire">
    <base-layout title="Other Types of Interfaces" active-menu="interface">
      <template #content>
        <div class="mr-3">
          <vlan />
          <assign />
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "@/layouts/layout.vue";
import vlan from "./components/Vlan.vue";
import assign from "./components/Assign.vue";

export default {
  name: "Interface",
  components: {
    vlan,
    assign,
    BaseLayout,
  },
};
</script>
