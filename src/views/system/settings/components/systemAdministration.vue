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
            item-title="name_interface"
            item-value="id"
            return-object
            multiple
            clearable
            :items="state.mapedInterface"
          ></v-select>
          <v-select
            :label="$t('settings.DetectedNetworkInterfacesWeb')"
            v-model="state.networkInterfaceWEB"
            item-title="name_interface"
            item-value="id"
            return-object
            multiple
            clearable
            :items="state.mapedInterface"
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

          <template v-if="state.protocol === 'HTTP'">
            <v-text-field
              :label="$t('settings.TCPPort')"
              v-model="state.tcpPortHttp"
              placeholder="80"
            ></v-text-field>
          </template>

          <template v-if="state.protocol === 'HTTPS'">
            <!-- <v-text-field
              :label="$t('settings.SSLCertificate')"
              v-model="state.sslCertificate"
            ></v-text-field> -->

            <v-select
              :label="`${$t('settings.SSLCertificate')} *`"
              v-model="state.sslCertificate"
              item-title="name"
              item-value="id"
              :items="state.certificatList"
              :no-data-text="$t('certificat.certificatlist')"
              return-object
            ></v-select>

            <p class="error-feedback mb-5" v-if="v$.sslCertificate.$error">
              {{ v$.sslCertificate.$errors[0].$message }}
            </p>

            <v-text-field
              :label="`${$t('settings.TCPPort')}`"
              v-model="state.tcpPort"
              placeholder="443"
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
import { reactive, onMounted, computed, ref, inject, watch } from "vue";
import ModalAddEditGateway from "@/components/modals/ModalAddEditGateway.vue";
import { v4 as uuidv4 } from "uuid";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";

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

    onMounted(() => {
      let adminSettings =
        document.getElementById("app").attributes["admin_settings"].value;
      const parsedArray = JSON.parse(adminSettings);

      getCertif();
      getInterface();

      populate(parsedArray);

      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
    });

    const populate = (dataAdmin) => {
      console.log("data", dataAdmin);

      let data = dataAdmin[0];

      state.id = data.id;
      state.secureShell = data.enable_ssh;
      state.rootLogin = data.root_login;
      state.authMethod = data.auth_method;
      state.sessionTimeout = data.session_timeout;
      state.protocol = data.protocol_http === true ? "HTTP" : "HTTPS";
      state.password = data.password_length;
      state.loginMsg = data.login_message;

      state.networkInterfaceSSH = data.interfaces_ssh.map((i)=> i.interface);
      state.networkInterfaceWEB = data.interfaces_web.map((i)=> i.interface);


      setTimeout(() => {
        const filtredCertif = state.certificatList.filter(
          (cert) => cert.id === data?.certificat?.id
        );
        state.sslCertificate = filtredCertif[0];
      }, 1000);

      state.tcpPort = data.protocol_http === false ? data?.tcp_port : "";
      state.tcpPortHttp = data.protocol_http === true ? data?.tcp_port : "";
    };

    const state = reactive({
      protocolList: ["HTTP", "HTTPS"],
      mapedInterface: [],
      interfaceWEBList: [],
      certificatList: [],
      mapedInterface: [],
      numPassword: [16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      //Administration
      networkInterfaceSSH: [],
      networkInterfaceWEB: [],
      secureShell: false,
      rootLogin: false,
      authMethod: false,
      sessionTimeout: "",
      protocol: "HTTP",
      sslCertificate: "",
      tcpPort: "",
      tcpPortHttp: "",
      loginMsg: false,
      password: null,
      id: null,
    });

    watch(
      () => state.protocol,
      (val) => {
        if (val === "HTTP") {
          state.sslCertificate = "";
          state.tcpPort = "";
        } else {
          state.tcpPortHttp = "";
        }
      }
    );

    const getCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then((response) => {
        state.certificatList = response.data;
      });
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then((response) => {
        let filtredInterface = response.data.filter(
          (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
        );

        let interfaces = filtredInterface.map((i) => {
          return {
            id: i.id,
            name_interface: i.name_interface,
            address: i.ip_address,
          };
        });

        state.mapedInterface = interfaces;
      });
    };

      const error = computed(() => {
      return t("errors.valueRequired");
    });

    const rules = computed(() => {
      return {
        sslCertificate: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.protocol === "HTTPS")
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

     const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post("/waf/restartNginx");
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      if (result) {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = {
          enable_ssh: state.secureShell,
          root_login: state.rootLogin,
          auth_method: state.authMethod,
          session_timeout: state.sessionTimeout,
          protocol_http: state.protocol === "HTTP" ? true : false,
          password_length: state.password ?? "",
          login_message: state.loginMsg,
          interface_ssh: state.networkInterfaceSSH
            ? state.networkInterfaceSSH?.map((i) => ({
                id: i.id,
                address: i.address,
              }))
            : [],

          interface_web: state.networkInterfaceWEB
            ? state.networkInterfaceWEB?.map((i) => ({
                id: i.id,
                address: i.address,
              }))
            : [],
        };

        if (state.protocol === "HTTP") {
          payload = { ...payload, tcp_port: state.tcpPortHttp };
        }

        if (state.protocol === "HTTPS") {
          payload = {
            ...payload,
            certificat: state.sslCertificate ? state.sslCertificate.id : "",
            tcp_port: state.tcpPort,
          };
        }

        state.loading = true;
        state.isLoadingDialogue = true;

        axios
          .put(`/settings/updateSettings/${state.id}`, payload)
          .then((response) => {
            if (response.status == 200) {
              restartNginx();
              state.loading = false;
              state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                state.snackbar = false;
                location.reload();
              }, 5000);
            }
          })
          .catch((i) => {
            state.loading = false;
            state.isLoadingDialogue = false;
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            }
          });
      } else {
        console.log("error :", v$.value);
      }
    };

    const cancel = () => {};

  

    return {
      v$,
      cancel,
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
  color: red;
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
.text-xs {
  font-size: 12px; 
}
.container {
  height: 50px;
}
</style>
