<template>
  <v-app id="inspire">
    <base-layout title="User and certificate management">
      <template #content>
        <v-tabs
          v-model="selectedTab"
          background-color="#fff"
          color="#FFC300"
          dark
        >
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.value">
            <span style="color: #020202">{{ tab.value }}</span>
          </v-tab>
        </v-tabs>

        <v-window v-model="selectedTab">
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="User Management"
          >
            <v-card>
              <v-card-text><data-managment /></v-card-text>
            </v-card>
          </v-window-item>
          <v-window-item
            v-for="tab in tabs"
            :key="tab.id"
            value="Certificate Management"
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
//
// import UserAndCertificateManagement from './UserAndCertificateManagement.vue';

import CertificatsManagement from "../certificates/certificats-management.vue";

export default {
  name: "UserAndCertificateManagement",
  components: {
    BaseLayout,
    CertificatsManagement,
    DataManagment,
    // UserAndCertificateManagement
  },

  data() {
    return {
      tabs: [
        { id: 1, value: "User Management" },
        { id: 2, value: "Certificate Management" },
      ],
      selectedTab: "User Management",

      tab: null,
      users: [],
      groups: [],
      servers: [],
    };
  },
  watch: {
    selectedTab(val) {
      localStorage.setItem("user-tab", val);
    },
  },
  methods: {
    setData(Array_String) {
      const validJsonString = Array_String.replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");

      const parsedArray = JSON.parse(validJsonString);

      // this.users = parsedArray;
      // console.log("parsedarray :"+parsedArray)

      return parsedArray;
    },
    // ... other methods
  },
  mounted() {
    let tab = localStorage.getItem("user-tab") || "User Management";
    this.selectedTab = tab;
  },
  beforeMount: async function () {
    // console.log("before mount data.users :" + JSON.stringify(this.$root.$data.users));

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
