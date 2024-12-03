<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("typeInterface.createNewInterface") }} Interface</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    :readonly="modalMode === 'edit' ? true : false"
                    v-model="state.typeV"
                    :label="$t('typeInterface.selectType')"
                    :items="state.listType"
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.typeV.$error">
                    {{ v$.typeV.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    :readonly="modalMode === 'edit' ? true : false"
                    :label="$t('typeInterface.newInterface')"
                    item-title="vlan"
                    item-value="id"
                    :items="state.listVlanAssing"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>
                <!-- <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('typeInterface.nameInterface')"
                    v-model="state.name_interface"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.name_interface.$error"
                  >
                    {{ v$.name_interface.$errors[0].$message }}
                  </p>
                </v-col> -->
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
              v-if="modalMode === 'create'"
              large
              rounded
              outlined
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">
                {{ $t("buttons.create") }}</span
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
    const emitter = inject("emitter");
    const { t } = useI18n();

    onMounted(() => {
      let vlanList =
        document.getElementById("app").attributes["list_vlan"].value;
      const parsedArray = JSON.parse(vlanList);

      state.listVlan = parsedArray.map((e) => {
        return {
          id: e.id,
          vlan: `VLAN : ${e.vlan_tag}`,
        };
      });
      let vxlanList =
        document.getElementById("app").attributes["list_vxlan"].value;
      const parsedVXLANArray = JSON.parse(vxlanList);
      state.listVxlan = parsedVXLANArray.map((e) => {
        return {
          id: e.id,
          vlan: `VXLAN : ${e.vxlan_id}`,
          vxlan_interface_name: e.vxlan_interface_name,
        };
      });

      emitter.on("list-assing", (data) => {
        state.rowList = data;
      });
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      rowList: [],
      listVlan: [],
      listVxlan: [],
      listType: ["VLAN", "VXLAN"],
      listVlanAssing: [],
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,
      interface: "",
      name_interface: "",
      typeV: "",
    });

    watch(
      () => state.typeV,
      (val) => {
        if (modalMode.value != "edit") state.interface = "";
        if (val === "VLAN") {
          if (state.rowList.length == 0) {
            state.listVlanAssing = [...state.listVlan];
          } else {
            const differentValues = filterDifferentValues(
              state.rowList,
              state.listVlan
            );
            state.listVlanAssing = [...differentValues];
          }
        } else if (val === "VXLAN") {
          if (state.rowList.length == 0) {
            state.listVlanAssing = [...state.listVxlan];
          } else {
            const differentValues = filterDifferentValuesVXLAN(
              state.rowList,
              state.listVxlan
            );
            state.listVlanAssing = [...differentValues];
          }
        }
      }
    );

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
          state.interface = "";
          state.name_interface = "";
          state.typeV = "";
          state.id = null;
        }
      }
    );
    function filterDifferentValues(array1, array2) {
      const differentValues = [];

      // array1.forEach((obj1) => {
      //   if (!array2.some((obj2) => obj2.id === obj1.id_vlan)) {
      //     differentValues.push(obj1);

      //   }
      // });
      array2.forEach((obj2) => {
        if (!array1.some((obj1) => obj1.id_vlan === obj2.id)) {
          differentValues.push(obj2);
        }
      });
      return differentValues;
    }
    function filterDifferentValuesVXLAN(array1, array2) {
      const differentValues = [];

      // array1.forEach((obj1) => {
      //   if (!array2.some((obj2) => obj2.id === obj1.id_vlan)) {
      //     differentValues.push(obj1);

      //   }
      // });
      array2.forEach((obj2) => {
        if (!array1.some((obj1) => obj1.id_vxlan === obj2.id)) {
          differentValues.push(obj2);
        }
      });
      return differentValues;
    }
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        let filtredInterfaceVxlan = state.listVxlan.filter(
          (i) => i.id === data?.id_vxlan
        );
        let filtredInterfaceVlan = state.listVlan.filter(
          (i) => i.id === data?.id_vlan
        );
        state.interface = filtredInterfaceVxlan[0] ?? filtredInterfaceVlan[0];
        // state.name_interface = data.name_interface;

        let type = data.network_port.split(" ");
        if (type[0] === "VXLAN") state.typeV = "VXLAN";
        else state.typeV = "VLAN";
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
        if (modalMode.value === "edit") {
          if (state.typeV === "VLAN") {
            let payload = {
              id: state.interface.id,
              // name_interface: state.name_interface,
            };
            axios
              .put(`/vlan/updateVlanInterface/${state.id}`, payload)
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
          } else if (state.typeV === "VXLAN") {
            let payload = {
              // name_interface: state.name_interface,
            };
            axios
              .put(`/vxlan/updateVxlanInterface/${state.id}`, payload)
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
          }
        } else if (modalMode.value === "create") {
          if (state.typeV === "VLAN") {
            let payload = {
              id: state.interface.id,
            };
            const transformedString = state.interface?.vlan.replace(" : ", "");
            localStorage.setItem("network-tab", transformedString);

            axios
              .post("/vlan/assignVlanInterface", payload)
              .then((response) => {
                if (response.status == "200") {
                  state.openModal = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;

                  setTimeout(() => {
                    window.location.href = "/interfaces/list-of-interface";
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
          } else if (state.typeV === "VXLAN") {
            let payload = {
              ifname: state.interface.vxlan_interface_name,
              // name_interface: state.name_interface,
            };

            const transformedString = state.interface?.vlan.replace(" : ", "");

            localStorage.setItem("network-tab", transformedString);

            axios
              .post("/vxlan/assignVxlanInterface", payload)
              .then((response) => {
                if (response.status == "200") {
                  state.openModal = false;
                  state.snackbar = true;
                  state.color = "success";
                  state.textAlert = response.data.msg;

                  setTimeout(() => {
                    window.location.href = "/interfaces/list-of-interface";
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
        }
      } else {
        console.log("v$", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeAssignModal");
      if (modalMode.value === "create") {
        state.interface = "";
        state.name_interface = "";
        state.typeV = "";
        state.id = null;
      }
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const rules = computed(() => {
      return {
        interface: {
          required: helpers.withMessage(error, required),
        },
        // name_interface: {
        //   required: helpers.withMessage(error, required),
        // },
        typeV: {
          required: helpers.withMessage(error, required),
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
