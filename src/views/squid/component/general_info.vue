<template>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-overlay v-model="state.loading">
      <v-dialog v-model="state.isLoadingDialogue" :scrim="false" persistent width="auto">
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="6">
        <h4>General information</h4>
        <v-divider class="mt-2"></v-divider>

        <v-row class="mt-1">
          <v-col cols="4" class="mt-4">
            <label>Enable</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <v-switch color="indigo" v-model="state.enableState"></v-switch>
          </v-col>

          <v-col cols="4" class="mt-7">
            <label>Proxy port</label>
          </v-col>
          <v-col cols="5" class="mt-3">
            <v-text-field label="Proxy Port" v-model="state.proxyPort"></v-text-field>
            <p class="error-feedback mb-5" v-if="v$.proxyPort.$error">
              {{ v$.proxyPort.$errors[0].$message }}
            </p>
          </v-col>
        </v-row>
        <v-row class="mt-5">
          <div>
            <VButton rounded outlined color="#213E9F" label-color="#ffffff" label="Save" :isLarge="true" class="ml-2"
              @click="saveGeneralInfo" />
          </div>
        </v-row>
      </v-col>

      <squid_auth />
      <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
        {{ state.textAlert }}

        <template v-slot:actions> </template>
      </v-snackbar>
    </v-row>
  </div>
</template>

<script>
import { reactive, ref, computed, onMounted, inject } from "vue";
import useValidate from "@vuelidate/core";
import { required } from "@vuelidate/validators";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import squid_auth from "./squid_auth.vue";
import axios from "axios";

export default {
  components: {
    AgGridVue,
    VButton,
    squid_auth,
  },
  setup() {
    const state = reactive({
      snackbar: false,
      color: "",
      textAlert: "",
      enableState: false,
      proxyPort: "",
      enable: false,
      modalData: {},
      isOpen: null,
      modalMode: "",
      isModalOpen: false,
      editRow: null,
      loading: false,
      isLoadingDialogue: false,
    });

    const rules = computed(() => {
      return {
        proxyPort: { required },
      };
    });

    const v$ = useValidate(rules, state);

    const saveGeneralInfo = async () => {

      const result = await v$.value.$validate();
      console.log("result", result);

      if (result) {
        console.log("state", state);
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        state.loading = true;
        state.isLoadingDialogue = true;

        let payload = {
          enable: state.enableState,
          port: state.proxyPort,
        };

        axios
          .put("/proxy/update_generale_info", payload)
          .then((response) => {
            if (response.status == "200") {
              state.snackbar = true;
              state.loading = false;
              state.isLoadingDialogue = false;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            state.snackbar = true;
            state.loading = false;
            state.isLoadingDialogue = false;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      } else {
        console.log("error", v$.value);
      }
    };
    const getCookie = (name) => {
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
    };

    const populate = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios
        .get("/proxy/get_generale_info")
        .then((response) => {
          if (response.status == "200") {
            console.log("response", response.data);
            state.enableState = response.data.status;
            state.proxyPort = response.data.Port;
          }
        })
        .catch((i) => {
          console.log("error", i);
        });
    };
    onMounted(() => {
      populate();
    });

    return {
      v$,
      state,
      saveGeneralInfo,
    };
  },
};
</script>
<style>
.actionBtn {
  justify-content: end;
}

.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
