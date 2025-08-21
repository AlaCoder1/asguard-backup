<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> Create New Client </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Client Name"
                    v-model="state.formData.userName"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.userName.$error"
                  >
                    {{ v$.formData.userName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    label="Client Certificate"
                    v-model="state.formData.clientCertificate"
                    item-title="name"
                    item-value="id"
                    :items="clientCertificateList"
                    return-object
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.clientCertificate.$errors.length"
                  >
                    {{ v$.formData.clientCertificate.$errors?.[0].$message }}
                  </p>
                </v-col>
                <template v-if="addressAny">
                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Address"
                      v-model="state.formData.address"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.formData.address.$error"
                    >
                      {{ v$.formData.address.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">Close</span>
            </v-btn>

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
              <span class="text-white pr-3 pl-3">Create</span>
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
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, ref, onMounted, inject } from "vue";
import VButton from "@/components/VButton.vue";
import { useI18n } from "vue-i18n";

export default {
  name: "Modal_Client",
  components: {
    VButton,
  },
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const { t } = useI18n();
    const emitter = inject("emitter");
    onMounted(() => {
      getAllClientCertif();
    });

    const { isOpen, editRow } = toRefs(props);
    const clientCertificateList = ref([]);
    const state = reactive({
      formData: {
        userName: null,
        clientCertificate: "",
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
      rowEditFilter: null,
      id: "",
    });
    const rules = computed(() => {
      return {
        formData: {
          userName: { required },
          clientCertificate: { required },
          address: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(() => state.rowEditFilter.interface === "Any")
            ),
            isValidlAddress: helpers.withMessage(
              `Format must be like adresse IP : X.X.X.X`,
              helpers.regex(
                /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
              )
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(
      () => isOpen.value,
      (value) => {
        state.openModal = value;
      }
    );
    watch(
      () => editRow.value,
      (editRow) => {
        state.rowEditFilter = editRow;
        state.id = editRow.id;
      }
    );

    const addressAny = computed(() => {
      return state.rowEditFilter.interface === "Any";
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

    const getAllClientCertif = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/certificates/getAllCertificates").then(
        (response) => {
          let mapedListCertif = response.data.filter(
            (i) => i.certificate_type === "client"
          );

          clientCertificateList.value = mapedListCertif.map((i) => {
            return {
              id: i.id,
              name: i.name,
            };
          });
        },
      );
    };

    const closeModal = () => {
      emitter.emit("closeModalCreateClient");
      v$.value.$reset();
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let payload = {};

        if (addressAny) {
          payload = {
            name: state.formData.userName,
            client_cert: state.formData.clientCertificate?.name,
            interface_address: state.formData.address,
          };
        } else {
          payload = {
            name: state.formData.userName,
            client_cert: state.formData.clientCertificate?.name,
          };
        }

        axios
          .post(`/openvpn/generateClientOpenvpn/${state.id}`, payload)
          .then((response) => {
            if (response.status == "201") {
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
        console.log("error :", v$.value);
      }
    };

    return {
      state,
      emitter,
      clientCertificateList,
      v$,
      addressAny,
      getAllClientCertif,
      closeModal,
      submitForm,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}

.actionBtn {
  justify-content: end;
}
</style>
