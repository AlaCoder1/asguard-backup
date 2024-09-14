<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addInterceptConfig") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateConfig") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="ConfigName"
                    v-model="ConfigName"
                    :placeholder="$t('ztna.configName')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" v-if="modalMode === 'create'">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="PROTOCOL">{{
                      $t("ztna.protocol")
                    }}</label>
                    <div class="ml-5 mt-1">
                      <v-menu open-on-hover>
                        <template v-slot:activator="{ props }">
                          <v-btn color="#FAFAFA" v-bind="props">
                            {{ selectedTitle }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item
                            v-for="(item, index) in items"
                            :key="index"
                            @click="selectItem(item)"
                          >
                            <v-list-item-title>{{
                              item.title
                            }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6" v-if="modalMode === 'create'">
                  <v-text-field
                    id="adress"
                    v-model="adress"
                    :placeholder="$t('ztna.address')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="6" v-if="modalMode === 'create'">
                  <v-text-field
                    id="portLow"
                    v-model.number="portLow"
                    :placeholder="$t('ztna.lowPorts')"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col> 
                <v-col cols="6" class="mb-n6" v-if="modalMode === 'create'">
                  <v-text-field
                    id="portHigh"
                    v-model.number="portHigh"
                    :placeholder="$t('ztna.highPorts')"
                    :rules="rules"
                    persistent-placeholder
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="Description"
                    v-model="Description"
                    placeholder="Description"
                    persistent-placeholder
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              text
              @click="cancel"
              >{{ $t("buttons.close") }}</v-btn
            >
            <!-- <v-btn
              color="red"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              type="reset"
            >
              Reset
            </v-btn> -->
            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 ml-2 btn-add"
              type="submit"
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
  </v-row>
</template>

<script>
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { toRefs, ref, watch, reactive, inject } from "vue";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    modalMode: {
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
  },

  setup(props) {
    const ConfigName = ref("");
    const adress = ref("");
    const portLow = ref("");
    const portHigh = ref("");
    const Description = ref("");
    const selectedTitle = ref("tcp");
    const items = [{ title: "tcp" }, { title: "udp" }];
    const rules = [
      (value) => {
        if (value) return true;

        return "You must enter a value.";
      },
    ];
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      openModal: false,
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
          ConfigName.value = "";
          adress.value = "";
          portLow.value = "";
          portHigh.value = "";
          Description.value = "";
          selectedTitle.value = "tcp";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataConfigInter", data);
      }
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
            name: ConfigName.value,
            configTypeId: "g7cIWbcGg",
            data: {
              addresses: [adress.value],
              portRanges: [
                {
                  high: Number(portHigh.value),
                  low: Number(portLow.value),
                },
              ],
              protocols: [selectedTitle.value],
            }
      };

      let token = document.getElementById("app").getAttribute("token");
      console.log("payload", payload);
      console.log("token", token);

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_config/${ConfigId.value}`, payload,{
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            if (response.status == "201") {
              // state.snackbar = true;
              // state.color = "success";
              // state.textAlert = response.data.msg;
              setTimeout(() => {
                // location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            // state.snackbar = true;
            // state.color = "red";
            // state.textAlert = i.response.data.response;
          });
      } else {
        axios
          .post("/ztna/add_config", payload, {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            console.log('re',response)
            if (response.status == "201") {
              // state.openModal = false;
              // state.snackbar = true;
              // state.color = "success";
              // state.textAlert = response.data.msg;

              setTimeout(() => {
                // location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            console.log('re',u.response)

            // state.snackbar = true;
            // state.color = "red";
            // state.textAlert = i.response.data.error;
          });
      }
    };

    // const submitForm = async () => {
    //   try {
    //     let token = document.getElementById("app").getAttribute("token");

    //     const proxyUrl = "https://asguard:3000";
    //     const apiUrl = "/edge/management/v1/configs";
    //     const response = await axios.post(
    //       proxyUrl + apiUrl,
    //       {
    //         name: ConfigName.value,
    //         configTypeId: "g7cIWbcGg",
    //         data: {
    //           addresses: [adress.value],
    //           portRanges: [
    //             {
    //               high: Number(portHigh.value),
    //               low: Number(portLow.value),
    //             },
    //           ],
    //           protocols: [selectedTitle.value],
    //         },
    //       },
    //       {
    //         headers: {
    //           "zt-session": token,
    //           "Content-Type": "application/json",
    //         },
    //       }
    //     );
    //     setTimeout(() => {
    //       location.reload();
    //     }, 1000);
    //     emitter.emit("closeInterceptModal");
    //   } catch (error) {
    //     console.error("Failed to submit form !!:", error);
    //   }
    // };
    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };
    const cancel = () => {
      console.log("test");
      emitter.emit("closeInterceptModal");
    };

    return {
      state,
      cancel,
      emitter,
      ConfigName,
      adress,
      portLow,
      portHigh,
      Description,
      selectedTitle,
      items,
      selectItem,
      rules,
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
  justify-content: center;
}

.red-asterisk {
  color: rgb(147, 3, 3);
  font-size: 1.6em;
}
</style>
