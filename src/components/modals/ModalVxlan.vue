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
                    :label="$t('typeInterface.VXLANNetworkIdentifie')"
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
                    :label="$t('typeInterface.multicastGroup')"
                    v-model="state.multicast"
                  ></v-text-field>
                  <p class="error-feedback mb-5" v-if="v$.multicast.$error">
                    {{ v$.multicast.$errors[0].$message }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.device"
                    :label="$t('typeInterface.device')"
                    item-title="name"
                    item-value="slug"
                    :items="state.listDevice"
                    return-object
                    :no-data-text="$t('certificat.certificatlist')"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.device.$error">
                    {{ v$.device.$errors[0].$message }}
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
    onMounted(() => {});

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
      vlanPriority: "",
      sourceAddress: "",
      vni: "",
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
          state.vlanPriority = "";
          state.sourceAddress = "";
        }
      }
    );

    const populate = (data) => {
      if (modalMode.value === "edit") {
        //   state.id = data.id;
        //   let filtredInterface = state.listInterfaces.filter(
        //     (i) => i.id === data?.parent_interface
        //   );
        //   state.interface = filtredInterface[0];
        //   state.vni = data.vlan_tag;
        //   state.vlanPriority = data.vlan_priority;
        //   state.sourceAddress = data.description;
        // }
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
      // const result = await v$.value.$validate();
      // const csrfToken = getCookie("csrftoken");
      // axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      // if (result) {
      //   let payload = {
      //     parent_interface: state.interface?.id,
      //     vlan_tag: state.vni,
      //     vlan_priority: state.vlanPriority,
      //     description: state.description,
      //   };
      //   console.log("payload", payload);
      //   if (modalMode.value === "edit") {
      //     axios
      //       .put(`/vlan/updateVlan/${state.id}`, payload)
      //       .then((response) => {
      //         if (response.status == "200") {
      //           state.snackbar = true;
      //           state.color = "success";
      //           state.textAlert = response.data.msg;
      //           setTimeout(() => {
      //             location.reload();
      //           }, 1000);
      //         }
      //       })
      //       .catch((i) => {
      //         state.snackbar = true;
      //         state.color = "red";
      //         state.textAlert = i.response.data.msg;
      //       });
      //   } else {
      //     axios
      //       .post("/vlan/addVlan", payload)
      //       .then((response) => {
      //         if (response.status == "200") {
      //           state.openModal = false;
      //           state.snackbar = true;
      //           state.color = "success";
      //           state.textAlert = response.data.msg;
      //           setTimeout(() => {
      //             location.reload();
      //           }, 1000);
      //         }
      //       })
      //       .catch((i) => {
      //         state.snackbar = true;
      //         state.color = "red";
      //         state.textAlert = i.response.data.msg;
      //       });
      //   }
      // } else {
      //   console.log("v$", v$.value);
      // }
    };

    const closeModal = () => {
      emitter.emit("closeVxlanModal");
      if (modalMode.value === "create") {
        state.device = "";
        state.vni = "";
        state.multicast = "";
        state.sourceAddress = "";
      }
    };

    const rules = computed(() => {
      return {
        vni: {
          isValidvni: helpers.withMessage(
            `Champs can include only Numbers.`,

            helpers.regex(/^[0-9]+$/)
          ),
        },

        device: {
          required,
        },

        multicast: {
          required,
        },
        sourceAddress: {
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
