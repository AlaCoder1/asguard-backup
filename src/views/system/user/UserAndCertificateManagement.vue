<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.userCertificatemanagement')">
      <template #content>
        <v-tabs
          v-model="selectedTab"
          background-color="#fff"
          color="#FFC300"
          dark
        >
          <v-tab v-for="tab in tabs" :key="tab.id" :value="$t(tab.value)">
            <span style="color: #020202">{{ $t(tab.value) }} </span>
          </v-tab>
        </v-tabs>

        <v-window v-model="selectedTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            :value="
              $t(tab.value) === 'User Management'
                ? 'User Management'
                : 'Gestion des utilisateurs'
            "
          >
            <v-card>
              <v-card-text><data-managment /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            :value="
              $t(tab.value) === 'Certificate Management'
                ? 'Certificate Management'
                : 'Gestion des certificats'
            "
          >
            <v-card>
              <v-card-text><certificats-management /></v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../../layouts/layout.vue";
import DataManagment from "../user/user_certificate_managment.vue";
import CertificatsManagement from "../certificates/certificats-management.vue";

export default {
  name: "UserAndCertificateManagement",
  inject: ["emitter"],
  components: {
    BaseLayout,
    CertificatsManagement,
    DataManagment,
  },

  data() {
    return {
      localStorageValue: localStorage.getItem("lang-slug"),
      tabs: [
        { id: 1, value: "tabs.userManagement" },
        { id: 2, value: "tabs.certificateManagement" },
      ],
      selectedTab: "",

      tab: null,
      users: [],
      groups: [],
      servers: [],
    };
  },
  watch: {
    selectedTab(val) {
      let tabs = val.split(" ");
      if (tabs.includes("utilisateurs") || tabs.includes("User")) {
        localStorage.setItem("user-tab", "tabs.userManagement");
      } else {
        localStorage.setItem("user-tab", "tabs.certificateManagement");
      }
    },
  },
  methods: {
    setData(Array_String) {
      // const validJsonString = Array_String.replace(/'/g, '"')
      //   .replace(/True/g, "true")
      //   .replace(/False/g, "false")
      //   .replace(/None/g, "null");

      const parsedArray = JSON.parse(Array_String);

      return parsedArray;
    },
  },
  mounted() {
    this.emitter.on("reload-tabs", () => {
      let tab = this.$t(
        localStorage.getItem("user-tab") || this.$t("tabs.userManagement")
      );
      if (tab) this.selectedTab = tab;
    });
    let tab = this.$t(
      localStorage.getItem("user-tab") || this.$t("tabs.userManagement")
    );
    if (tab) this.selectedTab = tab;
  },

  beforeMount: async function () {
    //   parsing users data
    let userData = document.getElementById("app").attributes["users"].value;
    let parsedData = this.setData(userData);

    this.users = parsedData;
    //   parsing users data

    //   parsing groups data
    let groupData = document.getElementById("app").attributes["groups"].value;
    let parsedgroupsData = this.setData(groupData);

    this.groups = parsedgroupsData;
    //   parsing groups data

    // //   parsing servers data
    let serversData =
      document.getElementById("app").attributes["servers"].value;
    let parsedserversData = this.setData(serversData);

    this.servers = parsedserversData;
    // //   parsing servers data
  },
};
</script>
