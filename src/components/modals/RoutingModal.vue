<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("routing.createRoute") }} Route</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("buttons.update") }} Route</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('routing.network')"
                    v-model="state.network"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.network.$error">
                    {{ v$.network.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.gateway"
                    label="Gateway"
                    item-title="name"
                    item-value="id"
                    :items="state.listGateway"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.gateway.$error">
                    {{ v$.gateway.$errors[0].$message }}
                  </p>
                </v-col>
                <template v-if="state.gateway.name === 'Other'">
                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Gateway Address"
                      v-model="state.gatewayAddress"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.gatewayAddress.$error"
                    >
                      {{ v$.gatewayAddress.$errors[0].$message }}
                    </p>
                  </v-col>
                  <v-col cols="12" class="mb-n6">
                    <v-select
                      v-model="state.interface"
                      label="Parent Interface"
                      item-title="name"
                      item-value="slug"
                      :items="state.listInterfaces"
                      return-object
                      :no-data-text="$t('certificat.certificatlist')"
                    ></v-select>
                    <p class="error-feedback mb-5" v-if="v$.interface.$error">
                      {{ v$.interface.$errors[0].$message }}
                    </p>
                  </v-col>

                  <v-col cols="12" class="mb-n6">
                    <v-text-field
                      label="Metric"
                      v-model="state.metric"
                    ></v-text-field>
                    <p class="error-feedback mb-5" v-if="v$.metric.$error">
                      {{ v$.metric.$errors[0].$message }}
                    </p>
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Description"
                    v-model="state.description"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span
              >
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                {{ $t("buttons.update") }}</span
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
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
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
    const { t } = useI18n();
    const emitter = inject("emitter");
    onMounted(() => {
      getInterface();

      let allListGateway =
        document.getElementById("app").attributes["listAllGateway"].value;

      const validJsonString = allListGateway
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);

      let gateway = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.gwname,
        };
      });

      let listGat = [{ id: 0, name: "Other" }];
      var combinedArray = [...gateway, ...listGat];
      state.listGateway = combinedArray;
    });

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) =>
              !i.ifname.startsWith("tun_") &&
              !i.ifname.startsWith("tap_") &&
              !i.name_interface.startsWith("VLAN") &&  
              !i.name_interface.startsWith("VXLAN") 
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.listInterfaces = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      listGateway: [],
      listInterfaces: [],
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,
      gateway: "",
      description: "",
      network: "",
      //
      gatewayAddress: "",
      metric: "",
      interface: "",
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => state.gateway,
      (val) => {
        if (val.slug != "Other") {
          state.gatewayAddress = "";
          state.metric = " ";
          state.interface = "";
        }
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
          state.id = null;
          state.gateway = "";
          state.description = "";
          state.network = "";
          state.gatewayAddress = "";
          state.metric = "";
          state.interface = "";
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let filtredGateway = state.listGateway.filter(
          (i) => i.id === data?.gateway
        );
        state.gateway = filtredGateway[0];
        // if (filtredGateway.length == 0) {
        //   state.gateway = { id: 0, name: "Other" };
        // } else {

        // }
        state.network = data.destination_address;
        state.description = data.description;
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

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (result) {
        let gateway = null;

        if (state.gateway.name === "Other") {
          gateway = {
            gateway_address: state.gatewayAddress,
            interface: state.interface.id,
            metric: state.metric,
          };
        } else {
          gateway = state.gateway.id;
        }

        let payload = {
          destination_address: state.network,
          gateway_create: state.gateway.name === "Other" ? true : false,
          gateway: gateway,
          description: state.description,
        };
        if (modalMode.value === "edit") {
          console.log("edit");
          axios
            .put(`/routing/updateRouting/${state.id}`, payload)
            .then((response) => {
              if (response.status == "201") {
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
          axios
            .post("/routing/createRouting", payload)
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
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeRoutingModal");

      if (modalMode.value === "create") {
        state.id = null;
        state.gateway = "";
        state.description = "";
        state.network = "";
        state.gatewayAddress = "";
        state.metric = "";
        state.interface = "";
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const addressForma = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    

    const rules = computed(() => {
      return {
        network: {
          required: helpers.withMessage(error, required),
          isValidlNetwork: helpers.withMessage(
            addressForma,
            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },

        gateway: {
          required: helpers.withMessage(error, required),
        },

        //

        gatewayAddress: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.gateway.name === "Other")
          ),
          isValidGateway: helpers.withMessage(
            addressForma,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        interface: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.gateway.name === "Other")
          ),
        },
        metric: {
          // isValidMetric: helpers.withMessage(
          //   `Champs can include only Numbers.`,

          //   helpers.regex(/^[0-9]+$/)
          // ),
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => state.gateway.name === "Other")
          ),
          isValidMetric: helpers.withMessage(
            onlynumbers,

            helpers.regex(/^[0-9]+$/)
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      emitter,
      v$,
      closeModal,
      submitForm,
      getCookie,
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
  justify-content: center;
}
</style>
