<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              Create New DNAT Rule</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              Update DNAT Rule</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="4" align-self="center">
                  <label>Activate</label>
                </v-col>
                <v-col cols="8" class="mb-n6">
                  <input type="checkbox" v-model="state.activateStatus" />
                  <label class="ml-2"> Activate rule</label>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.interfaces"
                    label="Interface"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.tcpIpVersion"
                    label="Select TCP/IP version"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.protocol"
                    label="Select Protocol"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.source"
                    label="select source"
                    item-title="name"
                    item-value="id"
                    :items="state.mapedInterface"
                    clearable
                    return-object
                  ></v-select>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Enter source address"
                    v-model="state.sourceAddress"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.sourcePrefix"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="6" class="mb-n6 mt-3">
                  <span>Source Port Range</span>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    label="From"
                    v-model="state.sourceRangeFrom"
                    :items="numberList"
                  ></v-select>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    label="To"
                    v-model="state.sourceRangeTo"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Enter External address"
                    v-model="state.externalAddress"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.externalPrefix"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="7" class="mb-n6">
                  <v-text-field
                    label="Enter Internal address"
                    v-model="state.internalAddress"
                  ></v-text-field>
                </v-col>
                <v-col cols="1" class="mb-n6">
                  <div class="ml-1 mt-5">/</div>
                </v-col>
                <v-col cols="4" class="mb-n6">
                  <v-select
                    label="Prefix"
                    v-model="state.internalPrefix"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-radio-group v-model="state.checkInterface" inline>
                    <v-row>
                      <v-col cols="6" v-for="area in state.isCombo" :key="area">
                        <v-radio :label="area" :value="area"></v-radio>
                      </v-col>
                    </v-row>
                  </v-radio-group>
                </v-col>

                <v-col cols="6" class="mb-n6 mt-3">
                  <span>destination port range</span>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    label="From"
                    v-model="state.destinationRangeFrom"
                    :items="numberList"
                  ></v-select>
                </v-col>
                <v-col cols="3" class="mb-n6">
                  <v-select
                    label="To"
                    v-model="state.destinationRangeTo"
                    :items="numberList"
                  ></v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    label="Port"
                    v-model="state.port"
                    :items="numberList"
                  ></v-select>
                </v-col>
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
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3" style="color: #213e9f">Cancel</span>
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
import { toRefs, watch, reactive, computed, inject, onMounted } from "vue";
import { required, helpers } from "@vuelidate/validators";
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
      //list
      isCombo: ["Frowarding", "Port Frowardin"],
      //
      activateStatus: "",
      interface: "",
      tcpIpVersion: "",
      protocol: "",
      source: "",
      sourceAddress: "",
      sourcePrefix: "",
      destination: "",
      checkInterface: "",

      //
      sourceRangeFrom: "",
      sourceRangeTo: "",
      internalPrefix: "",
      internalAddress: "",
      externalPrefix: "",
      externalAddress: "",
      description: "",
      port: "",
      destinationRangeTo: "",
      destinationRangeFrom: "",
      checkInterface: "",
    });

    onMounted(() => {
      getInterface();
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
        // populate(val);
      }
    );
    watch(
      () => modalMode.value,
      () => {
        if (modalMode.value === "create") {
          state.areaName = "";
          state.interfaces = [];
        }
      }
    );
    //   const populate = (data) => {
    //     if (modalMode.value === "edit") {
    //       state.areaName = data.name;
    //       state.id = data.id;

    //       let filtredInterface = [];
    //       data?.members.forEach((e) => {
    //         filtredInterface = [
    //           ...filtredInterface,
    //           ...state.mapedInterface.filter((i) => i.name === e),
    //         ];
    //       });
    //       state.interfaces = filtredInterface;
    //     }
    //   };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const closeModal = () => {
      emitter.emit("closeDnatModal");
      if (modalMode.value === "create") {
      }
    };

    const submitForm = async () => {
      console.log("state", state);
      // const result = await v$.value.$validate();
      // const csrfToken = getCookie("csrftoken");
      // axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      // if (result && isMoreThanTwo.value) {
      //   let nameInterface = state.interfaces.map((e) => e.id);
      //   let payload = {
      //     name: state.areaName,
      //     members: nameInterface,
      //   };
      //   console.log("payload", payload);
      //   if (modalMode.value === "edit") {
      //     axios
      //       .put(`/sdwan/updateArea/${state.id}`, payload)
      //       .then((response) => {
      //         if (response.status == "201") {
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
      //         state.textAlert = i.response.data.response;
      //       });
      //   } else {
      //     axios
      //       .post("/sdwan/createArea", payload)
      //       .then((response) => {
      //         if (response.status == "201") {
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
      //         state.textAlert = i.response.data.error;
      //       });
      //   }
      // } else {
      //   console.log("v$", v$.value);
      // }
    };

    //   const rules = computed(() => {
    //     return {
    //       interfaces: { required, isMoreThanTwo },
    //       areaName: {
    //         required,
    //         isValidkeyName: helpers.withMessage(
    //           `Champs can include only letters & Numbers & underscores & hyphens without space.`,

    //           helpers.regex(/^[A-Za-z0-9_\-]+$/)
    //         ),
    //       },
    //     };
    //   });

    //   const v$ = useValidate(rules, state);

    return {
      state,
      // v$,
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
.actionBtn {
  justify-content: center;
}
.scroller {
  overflow: auto;
}
</style>
