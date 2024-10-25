<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addRelaysPolicy") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateRelaysPolicy") }}</span
            >
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="PolicyName"
                    v-model="name"
                    :placeholder="$t('ztna.policyName')"
                    :rules="rulesName"
                    persistent-placeholder
                  />
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
                          <v-list-item
                            v-for="(item, index) in items"
                            :key="index"
                            @click="selectItem(item)"
                          >
                            <v-list-item-title>{{ item }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="routerR"
                    :label="$t('ztna.edgeRelaysRole')"
                    density="compact"
                    item-title="attribute_relay"
                    item-value="id"
                    return-object
                    :rules="rules"
                    :items="routersList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
                  </v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field id="identityatt" v-model="identityatt" :placeholder="$t('ztna.identityRoleAttribute')"
                    :rules="rules" persistent-placeholder /> -->
                  <v-select
                    v-model="identityatt"
                    :label="$t('ztna.identityRoleAttribute')"
                    density="compact"
                    item-title="attribute_identitie"
                    item-value="id"
                    return-object
                    :rules="rules"
                    :items="identityList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
                  </v-select>
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
              outlined
              label-color="#213E9F"
              variant="flat"
              class="mt-3 btn-add"
              text
              @click="cancel"
              ><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span
              ></v-btn
            >
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
            <v-btn
              large
              rounded
              outlined
              label-color="#213E9F"
              color="indigo-darken-3"
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
import { toRefs, ref, watch, reactive, inject, onMounted } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";

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
    const { t } = useI18n();
    const name = ref("");
    const RelayPolicies = ref([]);
    const relayId = ref("");
    const routerR = ref("");
    const identityatt = ref("");
    const Description = ref("");
    const selectedTitle = ref("AllOf");
    const items = ref(["AllOf", "AnyOf"]);
    const routersList = ref([]);
    const identityList = ref([]);

    const rules = [
      (value) => {
        if (value) return true;
        return "You must enter a value.";
      },
    ];
    const rulesName = [
      (value) => {
        if (!value) return true;
        if (existingName(value)) return "The name already exists";
        return ValidName(value) ? true : "Please enter a valid name.";
      },
    ];
    function existingName(value) {
      const existingIdentity = RelayPolicies.value.find(
        (identity) => identity.name === value
      );

      if (existingIdentity) {
        return true;
      }

      return false;
    }
    const fetchRelayPolicies = async () => {
      try {
        const RelayPoliciesString = await document
          .getElementById("app")
          .getAttribute("router_policies");
        const RelayPoliciesObject = JSON.parse(RelayPoliciesString);

        const RelayPoliciesArray = Array.isArray(RelayPoliciesObject)
          ? RelayPoliciesObject
          : [];

        RelayPolicies.value = RelayPoliciesArray.map((identity) => ({
          name: identity.name,
        }));

        console.log("RelayPolicies.value", RelayPolicies.value);
      } catch (error) {
        console.error("Failed to fetch RelayPolicies:", error);
        RelayPolicies.value = [];
      }
    };

    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);
    function ValidName(value) {
      const hostnamePattern = /^[a-zA-Z0-9-\s]{1,63}(\.[a-zA-Z0-9-\s]{1,63})*$/;

      if (hostnamePattern.test(value) && !/^\d+$/.test(value)) {
        return true;
      }

      return false;
    }
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
    onMounted(() => {
      fetchRelayPolicies();
      let routersString = document
        .getElementById("app")
        .getAttribute("routers");
      let routersObject;
      routersObject = JSON.parse(routersString);
      console.log("routersObject00--------------:", routersObject);
      routersList.value = routersObject ? routersObject : [];

      let IdentitiesString = document
        .getElementById("app")
        .getAttribute("Identities");

      let IdentitiesObject;

      IdentitiesObject = JSON.parse(IdentitiesString);
      identityList.value = IdentitiesObject ? IdentitiesObject : [];
    });
    const populate = (data) => {
      if (modalMode.value === "edit") {
        relayId.value = data.id;
        name.value = data.name;

        selectedTitle.value = data.semantique;
        Description.value = data.description;
        let relay = "";
        let identity = "";
        for (let i = 0; i < routersList.value.length; i++) {
          if (routersList.value[i].id === data.relay) {
            relay = routersList.value[i];
            break;
          }
        }

        for (let i = 0; i < identityList.value.length; i++) {
          if (identityList.value[i].id === data.identity) {
            identity = identityList.value[i];
            break;
          }
        }
        routerR.value = relay;
        identityatt.value = identity;
      }
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let routerAttribute = `#${routerR.value.attribute_relay}`;
      let identityAttribute = `#${identityatt.value.attribute_identitie}`;
      let payload = {
        name: name.value,
        semantic: selectedTitle.value,
        edgeRouterRoles: [routerAttribute],
        identityRoles: [identityAttribute],
        Description: Description.value,
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
      routersList,
      identityList,
      items,
      rules,
      submitForm,
      resetForm,
      selectItem,
      cancel,
      rulesName,
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
