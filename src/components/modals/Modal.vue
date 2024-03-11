<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create New Server</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update Server</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Enter name"
                    v-model="state.name"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.name.$error">
                    {{ v$.name.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Enter Hostname or IP @ (url)"
                    v-model="state.hostIp"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.hostIp.$error">
                    {{ v$.hostIp.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Search Base"
                    v-model="state.searchBase"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.searchBase.$error">
                    {{ v$.searchBase.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Port"
                    v-model="state.port"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.port.$error">
                    {{ v$.port.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field
                    label="User DN"
                    v-model="state.userDn"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.userDn.$error">
                    {{ v$.userDn.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field
                    label="Password "
                    v-model="state.password"
                    :append-inner-icon="state.show1 ? 'mdi-eye' : 'mdi-eye-off'"
                    prepend-inner-icon="mdi-lock-outline"
                    :type="state.show1 ? 'text' : 'password'"
                    @click:append-inner="state.show1 = !state.show1"
                  ></v-text-field>

                  <p class="error-feedback mb-5" v-if="v$.password.$error">
                    {{ v$.password.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="7" align-self="center">
                  <label>TLS/ SSL encryption (chiffrement)</label>
                </v-col>
                <v-col cols="5" class="mb-n6">
                  <input type="checkbox" v-model="state.activateStatus" />
                  <label class="ml-2"> Active ecnryption</label>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions class="mt-3 actionBtnServer">
            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{ modalMode }}</span>
            </v-btn>
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3 text-white" style="color: #213e9f"
                >Close</span
              >
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>

    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, watch, reactive, computed, inject, onMounted, ref } from "vue";
import { required, helpers, requiredIf, email } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
    modalMode: {
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      show1: "",
      name: "",
      hostIp: "",
      port: "",
      userDn: "",
      searchBase: "",
      password: "",
      activateStatus: false,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );
    watch(
      () => modalMode.value,
      () => {
        if (modalMode.value === "create") {
          state.name = "";
          state.hostIp = "";
          state.port = "";
          state.userDn = "";
          state.searchBase = "";
          state.password = "";
          state.activateStatus = false;
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        state.name = data.server_name;
        state.hostIp = data.server_url;
        state.port = data.port;
        state.userDn = data.bind_user_dn;
        state.searchBase = data.search_base;
        state.password = "";
        state.activateStatus = data.ssl_tls_activation;
      }
    };

    const closeModal = () => {
      emitter.emit("closeServerModal");
      if (modalMode.value === "create") {
        state.name = "";
        state.hostIp = "";
        state.port = "";
        state.userDn = "";
        state.searchBase = "";
        state.password = "";
        state.activateStatus = false;
      }
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          server_name: state.name,
          server_url: state.hostIp,
          port: state.port,
          search_base: state.searchBase,
          bind_user_dn: state.userDn,
          bind_user_password: state.password,
          ssl_tls_activation: state.activateStatus,
        };
        if (modalMode.value === "edit") {
          axios
            .put(`/ldap/updateldap_Server/${state.id}`, payload)
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
        } else {
          axios
            .post("/ldap/CreateServer", payload)
            .then((response) => {
              if (response.status == "200") {
                state.openModal = false;
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const rules = computed(() => {
      return {
        name: { required },
        hostIp: {
          isValidHostIp: helpers.withMessage(
            `Format must be like adresse IP : X.X.X.X`,

            helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          ),
        },
        searchBase: { required },

        port: {
          isValidlPort: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },
        userDn: {
          required: helpers.withMessage("Value is required", required),
        },
        password: { required },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      v$,
      emitter,
      submitForm,
      closeModal,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.actionBtnServer {
  justify-content: end;
  display: flex;
}
.scroller {
  overflow: auto;
}
</style>
