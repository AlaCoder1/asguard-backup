<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addRelaysPolicy") }}</span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateRelaysPolicy") }}s</span>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="PolicyName" v-model="name" :placeholder="$t('ztna.policyName')" :rules="rules"
                    persistent-placeholder />
                </v-col>

                <v-col cols="12">
                  <div class="d-flex align-center">
                    <label class="ml-1" for="PROTOCOL">{{
                      $t("ztna.semantic")
                      }}</label>
                    <div class="ml-5 mt-1">
                      <v-menu open-on-hover>
                        <template v-slot:activator="{ props }">
                          <v-btn color="#FAFAFA" v-bind="props">
                            {{ selectedTitle }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item v-for="(item, index) in items" :key="index" @click="selectItem(item)">
                            <v-list-item-title>{{
                              item
                              }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field id="routerR" v-model="routerR" :placeholder="$t('ztna.edgeRelaysRole')" :rules="rules"
                    persistent-placeholder />
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="identityatt" v-model="identityatt" :placeholder="$t('ztna.identityRoleAttribute')"
                    :rules="rules" persistent-placeholder />
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="Description" v-model="Description" placeholder="Description" :rules="rules"
                    persistent-placeholder />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="indigo-darken-3" :rounded="true" large outlined label-color="#213E9F" variant="flat"
              class="mt-3 btn-add" text @click="cancel"><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span></v-btn>
            <!-- <VBtn
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
            </VBtn> -->
            <v-btn large rounded outlined label-color="#213E9F" color="indigo-darken-3"
              variant="flat" class="mt-3 ml-2 btn-add" type="submit">
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'create'">
                {{ $t("buttons.create") }}</span>
              <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                {{ $t("buttons.update") }}</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
      {{ state.textAlert }}
    </v-snackbar>
  </v-row>
</template>
<script>
import axios from "axios";
import { toRefs, ref, watch, reactive, inject } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";

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
    const name = ref("");
    const relayId = ref("");
    const routerR = ref("");
    const identityatt = ref("");
    const Description = ref("");
    const selectedTitle = ref("AllOf");
    const items = ref([ "AllOf" , "AnyOf" ]);

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
      snackbar: false,
      color: "",
      textAlert: "",
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
          name.value = "";
          routerR.value = "";
          identityatt.value = "";
          Description.value = "";
          selectedTitle.value = "AllOf";


        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataHost", data);
        relayId.value = data.id
        name.value = data.name;

        selectedTitle.value = data.semantic;
        Description.value = "";

        let edgeRelay = data.edgeRouterRoles[0].split("#");

        let edgeIdentity = data.identityRoles[0].split("#");

        routerR.value = edgeRelay[1];
        identityatt.value = edgeIdentity[1];

      }
    };

    const submitForm = async () => {

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let routerAttribute = `#${routerR.value}`;
      let identityAttribute = `#${identityatt.value}`;

      let payload = {
        name: name.value,
        semantic: selectedTitle.value,
        edgeRouterRoles: [routerAttribute],
        identityRoles: [identityAttribute],
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_edge_routers_policies/${relayId.value}`, payload, {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            if (response.status == "200") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.message;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            console.log("response", i.response);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
          });
      } else {
        axios
          .post("/ztna/add_edge_routers_policies", payload, {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          })
          .then((response) => {
            if (response.status == "200") {
              state.openModal = false;
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.message;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            console.log("response", i.response);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      }
      // try {
      //   let token = document.getElementById("app").getAttribute("token");
      //   let routerAttribute = `#${routerR.value}`;
      //   let identityAttribute = `#${identityatt.value}`;
      //   const proxyUrl = "https://asguard:3000";
      //   const apiUrl = "/edge/management/v1/edge-router-policies";
      //   const response = await axios.post(
      //     proxyUrl + apiUrl,
      //     {
      //       name: name.value,
      //       semantic: selectedTitle.value,
      //       edgeRouterRoles: [routerAttribute],
      //       identityRoles: [identityAttribute],
      //     },
      //     {
      //       headers: {
      //         "zt-session": token,
      //         "Content-Type": "application/json",
      //       },
      //     }
      //   );
      //   setTimeout(() => {
      //     location.reload();
      //   }, 1000);
      //   emitter.emit("closeRouteModal");
      // } catch (error) {
      //   console.error("Failed to submit form:", error);
      // }
    };
    const resetForm = () => {
      name.value = "";
      routerR.value = "";
      identityR.value = "";
      identityatt.value = "";
      Description.value = "";
      selectedTitle.value = "AllOf";
    };

    const cancel = () => {
      console.log("tes");
      emitter.emit("closeRouteModal");
    };
    const selectItem = (item) => {
      selectedTitle.value = item;
    };

    return {
      state,
      name,
      routerR,
      identityatt,
      Description,
      selectedTitle,
      items,
      rules,
      submitForm,
      resetForm,
      selectItem,
      cancel,
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
