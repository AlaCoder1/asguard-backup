<template>
  <!-- <v-app id="inspire">
    <TheSidebarVue style="width: auto;"/>
    <TheHeadingVue />
    <v-main >
      <v-toolbar dark fixed app class="asguard_toolbar">
        <v-toolbar-title>
          {{ title }}
        </v-toolbar-title>
        <v-spacer />
        <div v-if="back">
          <v-btn>
            {{ titleback }}
          </v-btn>
        </div>
      </v-toolbar>
      <slot name="content"></slot>
    </v-main>
    <TheFooter />
  </v-app> -->

  <v-layout>
    <TheHeadingVue />

    <TheSidebarVue />

    <v-main class="ml-20">
      <v-toolbar dark fixed app class="asguard_toolbar">
        <v-toolbar-title>
          {{ title }}
        </v-toolbar-title>
        <v-spacer />
        <div v-if="back">
          <v-btn>
            {{ titleback }}
          </v-btn>
        </div>
      </v-toolbar>
      <slot name="content"></slot>
    </v-main>

    <TheFooter />
  </v-layout>
</template>

<script>
import TheSidebarVue from "./TheSidebar.vue";
import TheHeadingVue from "./TheHeading.vue";
import TheFooter from "./TheFooter.vue";

export default {
  name: "BaseLayout",
  components: {
    TheHeadingVue,
    TheSidebarVue,
    TheFooter,
  },
  props: {
    title: {
      type: String,
      default: "Asguard",
    },
    back: {
      type: Boolean,
      default: false,
    },
    urlback: {
      type: String,
      default: "/",
    },
    titleback: {
      type: String,
      default: "Back",
    },
  },
};
</script>

<style>
/* .v-main {
  padding-top: 0px;
  left: 0;
  right: 0;
  
} */


.asguard_toolbar {
  background-color: #f8f8f8;
  color: #020202;
  font-family: OpenSans;
  font-size: 30px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  left: 0;
  right: 0;
  display: flex;
}


.ag-paging-row-summary-panel {
  display: none;
}
</style>
