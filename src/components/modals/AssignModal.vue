<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("typeInterface.createNewInterface") }} Interface</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("buttons.update") }} Interface</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
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
                <v-col cols="12" class="mb-n6">
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

      emitter.on("list-assing", (data) => {
        state.rowList = data;
      });
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      rowList: [],
      listVlan: [],
      listVlanAssing: [],
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,
      interface: "",
      name_interface: "",
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
          state.interface = "";
          state.name_interface = "";
          state.id = null;

          if (state.rowList.length == 0) {
            state.listVlanAssing = [...state.listVlan];
          } else {
            const differentValues = filterDifferentValues(
              state.rowList,
              state.listVlan
            );
            state.listVlanAssing = [...differentValues];
          }
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
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        let filtredInterface = state.listVlan.filter(
          (i) => i.id === data?.id_vlan
        );
        state.interface = filtredInterface[0];
        state.name_interface = data.name_interface;
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
        let payload = {
          id: state.interface.id,
          name_interface: state.name_interface,
        };

        if (modalMode.value === "edit") {
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
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
        } else {
          localStorage.setItem("network-tab", state.name_interface);
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
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            });
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
        name_interface: {
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
