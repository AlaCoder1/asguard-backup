<template>
  <v-app id="inspire">
    <base-layout title="Rules" active-menu="firewall">
      <template #content>
        <v-tabs v-model="activeTab">
          <v-tab v-for="tab in tabs" :key="tab.name_interface">
            {{ tab.name_interface }}
          </v-tab>
          <v-tab-item v-for="tab in tabs" :key="tab.name_interface">
            <FirewallComponent 
            :id="tab.name_interface" 
            :activeTab="tab.name_interface"
            />
          </v-tab-item>
        </v-tabs>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import FirewallComponent from '@/components/firewall/FirewallComponent.vue';
import axios from 'axios';

export default {
  components: {
    BaseLayout,
    FirewallComponent
  },
  data() {
    return {
      activeTab: null,
      tabs: [],
    };
  },
  methods: {
    getAllInterfaces() {
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }
      const csrfToken = getCookie('csrftoken')
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

      axios
        .get("http://127.0.0.1:8000/network/AllInterfaces")
        .then(response => {
          response.data.forEach(element => {
            this.tabs.push({
              name_interface: element.name_interface
            });
          });
        })
        .catch(error => {
          console.log(error);
        });
    },
  },
  mounted() {
    this.getAllInterfaces();
  },
};
</script>

