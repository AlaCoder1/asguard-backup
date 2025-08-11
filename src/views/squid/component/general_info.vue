<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text v-html="overlayMessage"> </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="6">
        <h4>
          {{ $t("dhcpV4.generalInformation") }}
          <i
            v-if="!state.enableState"
            class="mdi mdi-play-circle"
            style="color: #4caf50; font-size: 20px; cursor: pointer"
            :title="$t('sdwan.startServer')"
            @click="startStopRestartServer('Start')"
          ></i>
          <i
            v-if="state.enableState"
            class="mdi mdi-stop-circle"
            :title="$t('sdwan.stop')"
            style="color: #b00020; font-size: 20px; cursor: pointer"
            @click="startStopRestartServer('Stop')"
          ></i>
          <i
            v-if="state.enableState"
            class="mdi mdi-reload"
            :title="$t('interface.restart')"
            style="color: #4caf50; font-size: 20px; cursor: pointer"
            @click="startStopRestartServer('Restart')"
          ></i>
        </h4>
        <v-divider class="mt-2"></v-divider>
        <v-card class="mt-3">
          <v-row class="mt-1 ml-1">
            <v-col cols="4" class="mt-7">
              <label>{{ $t("squid.proxyPort") }}*</label>
            </v-col>
            <v-col cols="5" class="mt-3">
              <v-text-field
                :label="$t('squid.proxyPort')"
                v-model="state.proxyPort"
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.proxyPort.$error">
                {{ v$.proxyPort.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-end mt-1 mb-2">
            <div>
              <VButton
                rounded
                outlined
                color="#213E9F"
                label-color="#ffffff"
                :label="$t('buttons.save')"
                :isLarge="true"
                class="mr-4"
                @click="saveGeneralInfo"
              />
            </div>
          </v-row>
        </v-card>
      </v-col>

      <squid_auth />
      <v-dialog v-model="state.dialogServer" max-width="500px">
        <v-card>
          <v-card-title class="headline">{{
            $t(state.statusServer)
          }}</v-card-title>
          <v-card-text
            >{{ $t("squid.etesVouSur") }} {{ $t(state.statusServer) }}
            {{ $t("squid.thisRule") }}</v-card-text
          >
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue darken-1"
              text
              @click="state.dialogServer = false"
              >{{ $t("buttons.cancel") }}</v-btn
            >
            <v-btn color="blue darken-1" text @click="confirmationServerState"
              >{{ $t(state.statusServer) }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-snackbar
        :timeout="2000"
        v-model="state.snackbar"
        location="bottom right"
        :color="state.color"
      >
        {{ state.textAlert }}

        <template v-slot:actions> </template>
      </v-snackbar>
    </v-row>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import { reactive, computed, onMounted, ref } from "vue";
import axios from "axios";
import squid_auth from "./squid_auth.vue";
import useValidate from "@vuelidate/core";
import { required, helpers } from "@vuelidate/validators";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  components: {
    AgGridVue,
    VButton,
    squid_auth,
  },
  setup() {
    const { t } = useI18n();
    const current_user = ref();
    const last_Subscription = ref([]);
    const state = reactive({
      dialogServer: false,
      isviewModal: false,
      viewModal: false,
      statusServer: null,
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

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const overlayMessage = computed(() => {
      current_user.value = user_privilege();
      console.log("current_user", current_user.value);
      if (current_user.value === "viewer" || current_user.value === "default") {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      } else if (!last_Subscription.value.includes("Proxy")) {
        return `${t(
          "firewall.msg_subscription"
        )}<br /><a href="/asguard/license/" class="white-link"> ${t(
          "firewall.sub_page"
        )}</a>`;
      } else {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      }
    });
    const nbre = computed(() => {
      return t("Waf.nombreMustBe");
    });
    const and = computed(() => {
      return t("Waf.and");
    });
    const rules = computed(() => {
      return {
        proxyPort: {
          required: helpers.withMessage(error, required),
          interval: helpers.withMessage(
            `${nbre.value} 1024 ${and.value} 65535`,
            (value) => {
              const num = Number(value);
              return !isNaN(num) && num >= 1024 && num <= 65535;
            }
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    const saveGeneralInfo = async () => {
      const user = user_privilege("Proxy");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("Proxy")
      ) {
        const result = await v$.value.$validate();

        if (result) {
          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
          state.loading = true;
          state.isLoadingDialogue = true;

          let payload = {
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
              state.loading = false;
              state.isLoadingDialogue = false;

              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        } else {
          console.log("error", v$.value);
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
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
    const confirmationServerState = () => {
      let status = state.statusServer.toLowerCase();
      state.dialogServer = false;
      state.loading = true;
      state.isLoadingDialogue = true;

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .post(`/proxy/${status}`)
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.msg;
          state.loading = false;
          state.isLoadingDialogue = false;

          setTimeout(() => {
            location.reload();
          }, 1000);
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
    };

    const startStopRestartServer = (item) => {
      const user = user_privilege("Proxy");
      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        last_Subscription.value.includes("Proxy")
      ) {
        state.dialogServer = true;
        state.statusServer = item;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    const populate = () => {
      const generalInfoAttribute =
        document.getElementById("app").attributes["generalInfo"].value;
      const generalInfo = JSON.parse(generalInfoAttribute);
      state.enableState = generalInfo.status;
      console.log("generalInfo.status", generalInfo.status);
      state.proxyPort = generalInfo.Port;
    };
    onMounted(() => {
      populate();
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription", last_Subscription.value);
    });

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    return {
      v$,
      close,
      overlayMessage,
      state,
      saveGeneralInfo,
      startStopRestartServer,
      confirmationServerState,
    };
  },
};
</script>
<style>
.white-link {
  color: white;
  text-decoration: underline;
}
.actionBtn {
  justify-content: end;
}

.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
