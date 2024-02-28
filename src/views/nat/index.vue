<template>
  <v-app id="inspire">
    <base-layout title="Nat" :active-menu="activeTab">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.label">
            <span style="color: #020202">{{ tab.label }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item v-for="tab in tabs" :key="tab.id" value="SNAt">
            <v-card>
              <v-card-text>
                <Snat />
              </v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="One-to-One">
            <v-card>
              <v-card-text> <OneToOne /> </v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item v-for="tab in tabs" :key="tab.id" value="DNAT">
            <v-card>
              <v-card-text><Dnat /> </v-card-text>
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

export default {
  name: "Sdwan",
  components: {
    BaseLayout,
    Snat,
    OneToOne,
    Dnat,
  },
  data() {
    return {
      activeTab: "SNAt",
      tabs: [
        { id: 1, label: "SNAt" },
        { id: 2, label: "One-to-One" },
        { id: 3, label: "DNAT" },
      ],
    };
  },
  watch: {
    activeTab(val) {
      localStorage.setItem("nat-tab", val);
    },
  },

  mounted: async function () {
    let tab = localStorage.getItem("nat-tab") || "SNAt";
    this.activeTab = tab;
  },
};
</script>
