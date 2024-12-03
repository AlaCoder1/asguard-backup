<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addService") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateService") }} Relay Policy
            </span>
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
                            {{ selectedsemantic }}
                          </v-btn>
                        </template>

                        <v-list>
                          <v-list-item
                            v-for="(item, index) in semantic"
                            :key="index"
                            @click="selectsemantic(item)"
                          >
                            <v-list-item-title>{{ item }}</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>
                  </div>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field id="serviceRA" v-model="serviceRA" :placeholder="$t('ztna.serviceRoleAttribute')"
                    :rules="rules" persistent-placeholder /> -->

                  <v-select
                    v-model="serviceRA"
                    :label="$t('ztna.serviceRoleAttribute')"
                    density="compact"
                    item-title="attribute_service"
                    item-value="id"
                    return-object
                    :rules="rules"
                    :items="ServList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
                  </v-select>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field id="routerR" v-model="routerR" :placeholder="$t('ztna.edgeRelaysRole')" :rules="rules"
                    persistent-placeholder /> -->
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
                  <v-text-field
                    id="name_description"
                    v-model="name_description"
                    placeholder="Description"
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
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { onMounted } from "vue";
import { toRefs, ref, watch, reactive, inject } from "vue";
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
    const idServRouter = ref("");
    const SerRelPolicies = ref([]);
    const ServList = ref([]);
    const routersList = ref([]);
    const name = ref("");
    const serviceRA = ref(null);
    const routerR = ref(null);
    const name_description = ref(null);
    const selectedsemantic = ref("AllOf");
    const semantic = ref(["AllOf", "AnyOf"]);
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
      const existingIdentity = SerRelPolicies.value.find(
        (identity) => identity.name === value
      );

      if (existingIdentity) {
        return true;
      }

      return false;
    }
    const fetchSerRelPolicies = async () => {
      try {
        const SerRelPoliciesString = await document
          .getElementById("app")
          .getAttribute("service_edge_router_policies");
        const SerRelPoliciesObject = JSON.parse(SerRelPoliciesString);

        const SerRelPoliciesArray = Array.isArray(SerRelPoliciesObject)
          ? SerRelPoliciesObject
          : [];

        SerRelPolicies.value = SerRelPoliciesArray.map((identity) => ({
          name: identity.name,
        }));

        console.log("SerRelPolicies.value", SerRelPolicies.value);
      } catch (error) {
        console.error("Failed to fetch SerRelPolicies:", error);
        SerRelPolicies.value = [];
      }
    };

    const emitter = inject("emitter");
    function ValidName(value) {
      const hostnamePattern = /^[a-zA-Z0-9-\s]{1,63}(\.[a-zA-Z0-9-\s]{1,63})*$/;

      if (hostnamePattern.test(value) && !/^\d+$/.test(value)) {
        return true;
      }

      return false;
    }
    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      openModal: false,
      snackbar: false,
      color: "",
      textAlert: "",
    });
    onMounted(() => {
      fetchSerRelPolicies();
      let servicesString = document
        .getElementById("app")
        .getAttribute("services");
      let servicesObject;
      try {
        servicesObject = JSON.parse(servicesString);
      } catch (error) {
        console.error("Failed to parse services string:", error);
      }

      ServList.value = servicesObject;

      let routersString = document
        .getElementById("app")
        .getAttribute("routers");
      let routersObject;
      routersObject = JSON.parse(routersString);
      routersList.value = routersObject ? routersObject : [];
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
          serviceRA.value = "";
          routerR.value = "";
          name_description.value = "";
          selectedsemantic.value = "AllOf";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("name_description", data.description);

        idServRouter.value = data.id;
        name.value = data.name;
        selectedsemantic.value = data.semantique;
        name_description.value = data.description;
        console.log("namcription", name_description.value);

        let relay = "";
        let service = "";
        for (let i = 0; i < routersList.value.length; i++) {
          if (routersList.value[i].id === data.relay) {
            relay = routersList.value[i];
            break;
          }
        }

        for (let i = 0; i < ServList.value.length; i++) {
          if (ServList.value[i].id === data.service) {
            service = ServList.value[i];
            break;
          }
        }
        routerR.value = relay;
        serviceRA.value = service;
      }
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      let routerAttribute = `#${routerR.value.attribute_relay}`;
      let serviceAttribute = `#${serviceRA.value.attribute_service}`;
      let payload = {
        name: name.value,
        semantic: selectedsemantic.value,
        edgeRouterRoles: [routerAttribute],
        serviceRoles: [serviceAttribute],
        Description: name_description.value,
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(
            `/ztna/update_services_edge_routers_policies/${idServRouter.value}`,
            payload,
            {
              headers: {
                "zt-session": token,
                "Content-Type": "application/json",
              },
            }
          )
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
          .post("/ztna/add_services_edge_routers_policies", payload, {
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
      serviceRA.value = "";
      routerR.value = "";
      name_description.value = "";
      selectedsemantic.value = "AllOf";
    };

    const cancel = () => {
      emitter.emit("closeServiceRouterPolicyModal");
    };
    const selectsemantic = (item) => {
      selectedsemantic.value = item;
    };

    return {
      state,
      name,
      serviceRA,
      routerR,
      routersList,
      ServList,
      name_description,
      semantic,
      rules,
      submitForm,
      resetForm,
      cancel,
      selectedsemantic,
      selectsemantic,
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
