<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("typeInterface.createNew") }} VXLAN</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("buttons.update") }} VXLAN</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('typeInterface.VXLANInterfaceName')"
                    v-model="state.interfaceName"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.interfaceName.$error">
                    {{ v$.interfaceName.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('typeInterface.VXLANNetworkIdentifier')"
                    v-model="state.vni"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.vni.$error">
                    {{ v$.vni.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('typeInterface.sourceAddress')"
                    v-model="state.sourceAddress"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.sourceAddress.$error">
                    {{ v$.sourceAddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('firewall.daddr')"
                    v-model="state.daddress"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.daddress.$error">
                    {{ v$.daddress.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('firewall.dport')"
                    v-model.number="state.dport"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.dport.$error">
                    {{ v$.dport.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.device"
                    :label="$t('typeInterface.parentDevice')"
                    item-title="name"
                    item-value="id"
                    :items="state.listDevice"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.device.$error">
                    {{ v$.device.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('typeInterface.connectionName')"
                    v-model="state.connectionName"
                    :readonly="modalMode === 'edit' ? true : false"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.connectionName.$error"
                  >
                    {{ v$.connectionName.$errors[0].$message }}
                  </p>
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
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      listDevice: [],
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      device: "",
      sourceAddress: "",
      vni: "",
      interfaceName: "",
      connectionName: "",
      daddress: "",
      dport: "",
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
          state.device = "";
          state.vni = "";
          state.dport = "";
          state.interfaceName = "";
          state.connectionName = "";
          state.sourceAddress = "";
          state.daddress = "";
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("data", data);

        let filtredInterface = state.listDevice.filter(
          (i) => i.id === data?.parent_interface
        );
        state.id = data.id;
        state.device = filtredInterface[0];
        state.vni = data.vxlan_id;
        state.connectionName = data.vxlan_connection_uuid;
        state.interfaceName = data.vxlan_interface_name;
        state.dport = data.vxlan_destination_port;
        state.daddress = data.vxlan_destination_address;
        state.sourceAddress = data.vxlan_source_address;
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

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) =>
              !i.ifname.startsWith("tun_") &&
              !i.ifname.startsWith("tap_") &&
              !i.ifname.startsWith("vlan") &&
              !i.name_interface.startsWith("vxlan") &&
              !i.name_interface.startsWith("VXLAN")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.listDevice = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const submitForm = async () => {
      const result = await v$.value.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (result) {
        let payload = {
          parent_interface: state.device.id,
          vxlan_id: state.vni,
          vxlan_destination_port: state.dport,
          vxlan_interface_name: state.interfaceName,
          vxlan_connection_uuid: state.connectionName,
          vxlan_source_address: state.sourceAddress,
          vxlan_destination_address: state.daddress,
        };
        if (modalMode.value === "edit") {
          axios
            .put(`/vxlan/updateVxlan/${state.id}`, payload)
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
          axios
            .post("/vxlan/addVxlan", payload)
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
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeVxlanModal");
      if (modalMode.value === "create") {
        state.device = "";
        state.vni = "";
        state.connectionName = "";
        state.interfaceName = "";
        state.dport = "";
        state.daddress = "";
        state.sourceAddress = "";
      }
    };

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champInclude = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const champNoInclude = computed(() => {
      return t("errors.ChampNoInclude");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });

    const rules = computed(() => {
      return {
        vni: {
          required: helpers.withMessage(error, required),
          isValidvni: helpers.withMessage(
            champInclude,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        device: {
          required: helpers.withMessage(error, required),
        },
        connectionName: {
          required: helpers.withMessage(error, required),
        },
        // interfaceName: {
        //   required: helpers.withMessage(error, required),
        //   isValidName: helpers.withMessage(
        //     champNoInclude,

        //     helpers.regex(
        //       /^(?=.*[a-zA-Z])[a-zA-Z0-9-]{1,63}(\.[a-zA-Z0-9-]{1,63})*$/
        //     )
        //   ),
        // },
        interfaceName: {
          required: helpers.withMessage(error, required),
          isValidName: helpers.withMessage(
            champNoInclude,

            (value) => {
              const regex =
                /^(?=.*[a-zA-Z])[a-zA-Z0-9-]{1,63}(\.[a-zA-Z0-9-]{1,63})*$/;
              if (!regex.test(value)) return false;
              return !/\btest\b/i.test(value);
            }
          ),
        },

        dport: {
          required: helpers.withMessage(error, required),
          isValidDport: helpers.withMessage(
            champInclude,
            helpers.regex(/^[0-9]+$/)
          ),
        },
        daddress: {
          required: helpers.withMessage(error, required),
          isValidDAddress: helpers.withMessage(
            formaaddress,
            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        sourceAddress: {
          required: helpers.withMessage(error, required),
          isValidSourceAddress: helpers.withMessage(
            formaaddress,
            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
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
