<template>
  <div class="mt-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("requiredfield.attente") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <div class="ml-3 mr-3">
      <h4>{{ $t("settings.SystemAdministration") }}</h4>
      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row>
      <v-col cols="10">
        <v-col cols="8" class="mb-n6">
          <v-select
            :label="$t('settings.DetectedNetworkInterfacesSSH')"
            v-model="state.networkInterfaceSSH"
            item-title="name"
            item-value="id"
            return-object
            clearable
            :items="state.interfaceSSHList"
          ></v-select>
          <v-select
            :label="$t('settings.DetectedNetworkInterfacesWeb')"
            v-model="state.networkInterfaceWEB"
            item-title="name"
            item-value="id"
            return-object
            clearable
            :items="state.interfaceWEBList"
          ></v-select>
          <v-row>
            <v-col cols="4">
              <label>{{ $t("settings.SecureShellServer") }}</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" hide-details v-model="state.secureShell" />
              <label class="ml-2">{{ $t("settings.EnableSecureShell") }}</label>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="4">
              <label>{{ $t("settings.RootLogin") }}</label>
            </v-col>

            <v-col cols="6" class="mb-n6">
              <input type="checkbox" hide-details v-model="state.rootLogin" />
              <label class="ml-2">{{
                $t("settings.PermitRootUserLogin")
              }}</label>
            </v-col>
          </v-row>

          <v-row class="mb-1">
            <v-col cols="4">
              <label>{{ $t("settings.AuthenticationMethod") }}</label>
            </v-col>
            <v-col cols="6">
              <input type="checkbox" hide-details v-model="state.authMethod" />
              <label class="ml-2">{{
                $t("settings.PermitPasswordLogin")
              }}</label>
            </v-col>
          </v-row>

          <v-text-field
            v-model="state.sessionTimeout"
            :label="$t('settings.SessionTimeout')"
            class="mb-n6"
          ></v-text-field>

          <v-row>
            <v-col cols="4" align-self="center">
              <label>{{ $t("settings.Protocol") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-radio-group v-model="state.protocol" inline>
                <v-row>
                  <v-col cols="4" v-for="pro in state.protocolList" :key="pro">
                    <v-radio :label="pro" :value="pro"></v-radio>
                  </v-col>
                </v-row>
              </v-radio-group>
            </v-col>
          </v-row>

          <template v-if="state.protocol === 'HTTPS'">
            <v-text-field
              :label="$t('settings.SSLCertificate')"
              v-model="state.sslCertificate"
            ></v-text-field>
            <v-text-field
              :label="$t('settings.TCPPort')"
              v-model="state.tcpPort"
            ></v-text-field>
          </template>

          <v-row class="mb-1">
            <v-col cols="4">
              <label>{{ $t("settings.LoginMessages") }}</label>
            </v-col>
            <v-col cols="6">
              <input type="checkbox" hide-details v-model="state.loginMsg" />
              <label class="ml-2">{{
                $t("settings.DisableWebGUISuccessfulLoginsLogging")
              }}</label>
            </v-col>
          </v-row>

          <!-- <v-text-field
            :label="$t('settings.Password')"
            v-model="state.password"
          ></v-text-field> -->
          <v-select
            :label="$t('settings.PasswordLengthSetting')"
            v-model="state.password"
            clearable
            :items="state.numPassword"
          ></v-select>
        </v-col>
      </v-col>
    </v-row>

    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
            :isLarge="true"
            class="ml-2"
            @click="submitForm"
          />
        </div>
      </v-col>
    </v-row>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";
import ModalAddEditGateway from "@/components/modals/ModalAddEditGateway.vue";
import { v4 as uuidv4 } from "uuid";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf } from "@vuelidate/validators";

export default {
  name: "AdministrationSystem",
  components: {
    VButton,
    AgGridVue,
    ModalAddEditGateway,
  },

  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const emitter = inject("emitter");
    const state = reactive({
      protocolList: ["HTTP", "HTTPS"],
      interfaceSSHList: [],
      interfaceWEBList: [],
      numPassword: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      //Administration
      networkInterfaceSSH: null,
      networkInterfaceWEB: null,
      secureShell: false,
      rootLogin: false,
      authMethod: false,
      sessionTimeout: "",
      protocol: "HTTP",
      sslCertificate: "",
      tcpPort: "",
      loginMsg: false,
      password: "",
    });

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

    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
    });

    const submitForm = async () => {
      // const result = await v$.value.$validate();
      // if (result) {
      //   const csrfToken = getCookie("csrftoken");
      //   axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      //   let dns_server = rowDataGateway.value.map((i) => {
      //     return {
      //       dns_server: i.dns_server,
      //       gateway: i.gateway ?? "",
      //       interface_id: i.info.interface_id ?? i.info.interface ?? null,
      //       name_interface:
      //         i.info.name_interface ?? i.info.name_interface ?? "",
      //       ...(i.gateway ? { metric: i.info.metric ?? "" } : {}),
      //     };
      //   });
      //   let payload = {
      //     hostname: state.hostName,
      //     domain: `${state.domain}`,
      //     timezone: state.timeZone.name,
      //     dns_servers: dns_server,
      //   };
      //   state.loading = true;
      //   state.isLoadingDialogue = true;
      //   axios
      //     .put(`/settings/generale_settings/1`, payload)
      //     .then((response) => {
      //       if (response.status == 200) {
      //         state.loading = false;
      //         state.isLoadingDialogue = false;
      //         state.snackbar = true;
      //         state.color = "success";
      //         state.textAlert = response.data.msg;
      //         setTimeout(() => {
      //           state.snackbar = false;
      //           location.reload();
      //         }, 1000);
      //       }
      //     })
      //     .catch((i) => {
      //       state.loading = false;
      //       state.isLoadingDialogue = false;
      //       if (i.response.status === 500) {
      //         state.snackbar = true;
      //         state.color = "red";
      //         state.textAlert = t("errors.errorServer");
      //       } else {
      //         state.snackbar = true;
      //         state.color = "red";
      //         state.textAlert = i.response.data.msg;
      //       }
      //     });
      // } else {
      //   console.log("v$", v$.value);
      // }
    };

    const cancel = () => {};
    const Formatdomain = computed(() => {
      return t("errors.Formatdomain");
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const rules = computed(() => {
      return {};
    });

    const v$ = useValidate(rules, state);

    return {
      v$,
      cancel,
      getCookie,
      submitForm,
      state,
      emitter,
      overlayTemplate,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: orange;
  font-size: 0.85em;
}

.label-style {
  color: #020202;
  font-family: Nunito;
  font-size: 15px;
  font-style: normal;
  font-weight: 300;
  line-height: normal;
}
/* CSS to style the text */
.text-xs {
  font-size: 12px; /* Example font size for small text */
}
.container {
  height: 50px;
}
</style>
