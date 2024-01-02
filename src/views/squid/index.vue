<template>
  <v-app id="inspire">
    <base-layout title="Proxy" active-menu="Key_Pair">
      <template #content>
        <div class="mr-6 ml-3">
          <general_info />
          <list />
          <acl_list />
        </div>
      </template>
    </base-layout>
    <!-- <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay> -->
    <!-- <v-snackbar
      location="top"
      v-model="state.snackbarServer"
      vertical
      color="#213E9F"
    >
      <div class="text-subtitle-1 pb-2">
        Please restart the service for the modifications to take effect
        <v-icon
          style="cursor: pointer"
          icon="mdi mdi-restart"
          size="x-large"
          @click="restart"
        ></v-icon>
      </div>

      <template v-slot:actions>
        <v-btn color="white" @click="state.snackbarServer = false">
          Close
        </v-btn>
      </template>
    </v-snackbar> -->

    <!-- <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar> -->
  </v-app>
</template>

<script>
import axios from "axios";
import { onMounted, reactive } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import general_info from "./component/general_info.vue";
import list from "./component/list.vue";
import acl_list from "./component/acl_list.vue";

export default {
  name: "Proxy",
  components: {
    BaseLayout,
    general_info,
    acl_list,
    list,
  },

  setup() {
    // const state = reactive({
    //   textAlert: "",
    //   color: "",
    //   snackbarServer: false,
    //   snackbar: false,
    //   loading: false,
    //   isLoadingDialogue: false,
    // });
    // onMounted(() => {
    //   state.snackbarServer = true;
    // });
    // const restart = () => {
    //   console.log("oui");
    //   state.loading = true;
    //   state.isLoadingDialogue = true;

    //   const csrfToken = getCookie("csrftoken");
    //   axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

    //   axios
    //     .post("/proxy/restart")
    //     .then((response) => {
    //       state.snackbar = true;
    //       state.color = "success";
    //       state.textAlert = response.data.msg;
    //       state.loading = false;
    //       state.isLoadingDialogue = false;

    //       // setTimeout(() => {
    //       //   location.reload();
    //       // }, 1000);
    //     })
    //     .catch((i) => {
    //       console.log('i.response.data.msg',i.response.data.msg)
    //       state.snackbar = true;
    //       state.color = "red";
    //       state.textAlert = i.response.data.msg;
    //       state.loading = false;
    //       state.isLoadingDialogue = false;
    //     });
    // };
    // const getCookie = (name) => {
    //   let cookieValue = null;
    //   if (document.cookie && document.cookie !== "") {
    //     const cookies = document.cookie.split(";");
    //     for (let i = 0; i < cookies.length; i++) {
    //       const cookie = cookies[i].trim();
    //       if (cookie.substring(0, name.length + 1) === name + "=") {
    //         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    //         break;
    //       }
    //     }
    //   }
    //   return cookieValue;
    // };
    // return {
    //   state,
    //   restart,
    // };
  },
};
</script>
