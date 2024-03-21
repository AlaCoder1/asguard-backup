<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create new VLAN</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update VLAN</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interface"
                    label="Parent Interface"
                    item-title="name"
                    item-value="slug"
                    :items="state.listInterfaces"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.interface.$error">
                    {{ v$.interface.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="VLAN Tag"
                    v-model="state.vlanTag"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.vlanTag.$error">
                    {{ v$.vlanTag.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.vlanPriority"
                    label="Vlan priority"
                    item-title="name"
                    item-value="slug"
                    :items="state.listPriority"
                    return-object
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.vlanPriority.$error">
                    {{ v$.vlanPriority.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Description"
                    v-model="state.description"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.description.$error">
                    {{ v$.description.$errors[0].$message }}
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
      getInterface();
    });

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      listInterfaces: [],
      listPriority: [
        "Best Effort ( 0 , default )",
        "Background ( 1, lowest)",
        "Excellent Effort (2)",
        "Critical Applications (3)",
        "Video (4)",
        "Voice (5)",
        "Internetwork Control (6)",
        "Network Control (7)",
      ],
      id: null,
      //
      snackbar: false,
      color: "",
      textAlert: "",
      openModal: false,

      interface: "",
      vlanPriority: "",
      description: "",
      vlanTag: "",
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
          state.vlanTag = "";
          state.vlanPriority = "";
          state.description = "";
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;

        let filtredInterface = state.listInterfaces.filter(
          (i) => i.id === data?.parent_interface
        );
        state.interface = filtredInterface[0];
        state.vlanTag = data.vlan_tag;
        state.vlanPriority = data.vlan_priority;
        state.description = data.description;
      }
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
              !i.ifname.startsWith("vlan")
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
          parent_interface: state.interface?.id,
          vlan_tag: state.vlanTag,
          vlan_priority: state.vlanPriority,
          description: state.description,
        };
        console.log("payload", payload);

        if (modalMode.value === "edit") {
          axios
            .put(`/vlan/updateVlan/${state.id}`, payload)
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
            .post("/vlan/addVlan", payload)
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
      emitter.emit("closeVlanModal");
      if (modalMode.value === "create") {
        state.interface = "";
        state.vlanTag = "";
        state.vlanPriority = "";
        state.description = "";
      }
    };

    const rules = computed(() => {
      return {
        vlanTag: {
          isValidVlanTag: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        vlanPriority: {
          required,
        },

        interface: {
          required,
        },
        description: {
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
