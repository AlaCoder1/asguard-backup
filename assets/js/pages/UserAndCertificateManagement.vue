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
                <user-management />
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
import CertificatsManagement from '@/pages/certificats-management.vue'
import UserManagement from '@/pages/user-management.vue'

export default {
  name: 'UserAndCertificateManagement',
  components: {
    BaseLayout,
    CertificatsManagement,
    UserManagement
  },
  data() {
    return {
      tabs: [
        { id: 1, value: 'User Management' },
        { id: 2, value: 'Certificate Management' },
      ],
      selectedTab: 'User Management',
    };
  },
};
</script>
