<template>
  <div class="ml-3">
    <authorites :authoritesData="authoritesData" />
    <certificats :certifData="certifData" :authoritesData="authoritesData" />
    <revocation :authoritesData="authoritesData" />
  </div>
</template>

<script>
import axios from "axios";
import { AgGridVue } from "ag-grid-vue3";
import authorites from "./components/authorites.vue";
import certificats from "./components/certificats.vue";
import revocation from "./components/revocation.vue";
export default {
  name: "CertificatsManagement",
  components: {
    AgGridVue,
    authorites,
    certificats,
    revocation,
  },
  props: {},
  data() {
    return {
      authoritesData: null,
      certifData: null,
    };
  },
  beforeMount: async function () {
    this.getCertif();
    this.getAllCertif();
  },
  methods: {
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    getAllCertif() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertAuth").then(
        (response) => {
          this.authoritesData = response.data;
        },
        (error) => {
          console.log(error);
        }
      );
    },

    getCertif() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          this.certifData = response.data;
        },
        (error) => {
          console.log(error);
        }
      );
    },
  },
};
</script>
<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
