<template>
  <v-app id="inspire">
    <base-layout title="User and certificate management">
      <template #content>
        <v-tabs background-color="#fff" color="#FFC300" dark v-model="selectedTab">
          <v-tab v-for="tab in tabs" :key="tab.id" :value="tab.value">
            <span style="color: #020202;">{{ tab.value }}</span>
          </v-tab>

          <v-tab-item v-for="tab in tabs" :key="tab.id">
            <!-- UserManagement -->
            <v-card v-if="tab.id === 1">
              <v-card-text>
                <!-- <user-and-certificate-management /> -->
                <data-managment />
              </v-card-text>
            </v-card>
            <!-- CertificatsManagement -->
            <v-card v-if="tab.id === 2">
              <v-card-text>
                <certificats-management />
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';

import DataManagment from '@/pages/user_certificate_managment.vue';
// 
// import UserAndCertificateManagement from './UserAndCertificateManagement.vue';

import CertificatsManagement from '@/pages/certificats-management.vue';

export default {
  name: 'UserAndCertificateManagement',
  components: {
    BaseLayout,
    CertificatsManagement,
    DataManagment
    // UserAndCertificateManagement
  },

  data() {
    return {

      tabs: [
        { id: 1, value: 'User Management' },
        { id: 2, value: 'Certificate Management' },
      ],
      selectedTab: 'User Management',

      tab: null,
      users: [],
      groups: [],
      servers: [],
    };
  },
  methods: {
    setData(Array_String) {
      const validJsonString = Array_String
        .replace(/'/g, '"')
        .replace(/True/g, 'true')
        .replace(/False/g, 'false')
        .replace(/None/g, 'null');

      const parsedArray = JSON.parse(validJsonString);

      // this.users = parsedArray;
      // console.log("parsedarray :"+parsedArray)

      return parsedArray;
    },
    // ... other methods
  },
  beforeMount: async function () {
    // console.log("before mount data.users :" + JSON.stringify(this.$root.$data.users));

    //   parsing users data
    let parsedData = this.setData(this.$root.$data.users);

    this.users = parsedData;
    //   parsing users data


    //   parsing groups data
    let parsedgroupsData = this.setData(this.$root.$data.groups);

    this.groups = parsedgroupsData;
    //   parsing groups data


    // //   parsing servers data
    let parsedserversData = this.setData(this.$root.$data.servers);

    this.servers = parsedserversData;
    // //   parsing servers data


  }
};
</script>
