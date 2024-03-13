<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create new Interface</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update Interface</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    :readonly="modalMode === 'edit' ? true : false"
                    v-model="state.interface"
                    label="New interface"
                    item-title="vlan"
                    item-value="id"
                    :items="state.listVlan"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Name Interface"
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
              <span class="text-white pr-3 pl-3">Close</span>
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
              <span class="text-white pr-3 pl-3">{{ modalMode }}</span>
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
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      id: null,
      listVlan: [],
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
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        let filtredInterface = state.listVlan.filter((i) => i.id === data?.id);
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
          axios
            .post("/vlan/assignVlanInterface", payload)
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

    const closeModal = () => {
      emitter.emit("closeAssignModal");
      if (modalMode.value === "create") {
        state.interface = "";
        state.name_interface = "";
      }
    };

    const rules = computed(() => {
      return {
        interface: {
          required,
        },
        name_interface: {
          required,
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
