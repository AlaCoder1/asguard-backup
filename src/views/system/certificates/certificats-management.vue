<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.cert')">
      <template #content>
        <helpModal />
        <div class="ml-5 mr-5 mb-5">
          <authorites :authoritesData="authoritesData" />
          <certificats
            :certifData="certifData"
            :authoritesData="authoritesData"
          />
          <revocation :authoritesData="authoritesData" />
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import BaseLayout from "../../../layouts/layout.vue";
import axios from "axios";
import { AgGridVue } from "ag-grid-vue3";
import authorites from "./components/authorites.vue";
import certificats from "./components/certificats.vue";
import revocation from "./components/revocation.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import helpModal from "@/components/modals/help.vue";

export default {
  name: "CertificatsManagement",
  components: {
    BaseLayout,
    AgGridVue,
    authorites,
    certificats,
    revocation,
    helpModal,
  },
  props: {},
  data() {
    return {
      authoritesData: [],
      certifData: [],
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
.btn-add {
  background: #213e9f;
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
