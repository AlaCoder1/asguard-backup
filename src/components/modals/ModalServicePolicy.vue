<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addServicesPolicy") }}</span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateServicePolicy") }}</span>
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
                    <label class="ml-1" for="PROTOCOL">Type</label>
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
                          <v-list-item v-for="(item, index) in semantic" :key="index" @click="selectsemantic(item)">
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
                  <!-- <v-text-field id="serviceRA" v-model="serviceRA" :placeholder="$t('ztna.serviceRoleAttribute')"
                    :rules="rules" persistent-placeholder /> -->
                    <v-select v-model="serviceRA" :label="$t('ztna.serviceRoleAttribute')" density="compact" item-title="name"
                    item-value="id" return-object :rules="rules" :items="ServList" background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')">
                  </v-select>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <!-- <v-text-field id="identityatt" v-model="identityatt" :placeholder="$t('ztna.identityRoleAttribute')"
                    :rules="rules" persistent-placeholder /> -->
                    <v-select v-model="identityatt" :label="$t('ztna.identityRoleAttribute')" density="compact"
                    item-title="name" item-value="id" return-object :rules="rules" :items="identityList"
                    background-color="#fffffff" :no-data-text="$t('certificat.certificatlist')">
                  </v-select>
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

            <v-btn large rounded outlined label-color="#213E9F" color="indigo-darken-3" variant="flat"
              class="mt-3 ml-2 btn-add" type="submit">
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
import { onMounted } from "vue";

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
    const ServList = ref([]);
    const identityList = ref([]);
    const idServ = ref("");
    const serviceRA = ref(null);
    const identityatt = ref(null);
    const Description = ref("");
    const selectedTitle = ref("Dial");
    const selectedsemantic = ref("AllOf");
    const items = ref([
      "Dial",
      "Bind",
      "Invalid",
    ]);
    const semantic = ref(["AllOf", "AnyOf"]);
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
          serviceRA.value = "";
          identityatt.value = "";
          Description.value = "";
          selectedTitle.value = "Dial";
          selectedsemantic.value = "AllOf";
        }
      }
    );
    onMounted(()=>{
      let servicesString = document
        .getElementById("app")
        .getAttribute("services");
      let servicesObject;
      try {
        servicesObject = JSON.parse(servicesString);
      } catch (error) {
        console.error("Failed to parse services string:", error);
      }

      ServList.value = servicesObject

      let IdentitiesString = document
        .getElementById("app")
        .getAttribute("Identities");

      let IdentitiesObject;

      IdentitiesObject = JSON.parse(IdentitiesString);
      identityList.value = IdentitiesObject ? IdentitiesObject : [];
    })
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataHost", data);
        idServ.value = data.id
        name.value = data.name;


        Description.value = data.description;
        selectedTitle.value = data.type;
        selectedsemantic.value = data.semantique;

        let service = "";
        let identity = "";
        for (let i = 0; i < ServList.value.length; i++) {
          if (ServList.value[i].id === data.service) {
            service = ServList.value[i];
            break;  
          }
        }

        for (let i = 0; i < identityList.value.length; i++) {
          if (identityList.value[i].id === data.identity) {
            identity = identityList.value[i];
            break;
          }
        }
        serviceRA.value=service;
        identityatt.value=identity

      }
    };

    const submitForm = async () => {

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;


      let identityAttribute = `#${identityatt.value.attribute_identitie}`;
      let serviceAttribute = `#${serviceRA.value.attribute_service}`;
      let payload = {
        name: name.value,
        type: selectedTitle.value,
        semantic: selectedsemantic.value,
        identityRoles: [identityAttribute],
        serviceRoles: [serviceAttribute],
        Description:Description.value
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_services_policies/${idServ.value}`, payload, {
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
          .post("/ztna/add_services_policies", payload, {
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
      //   let identityAttribute = `#${identityatt.value}`;
      //   let serviceAttribute = `#${serviceRA.value}`;
      //   const proxyUrl = "https://asguard:3000";
      //   const apiUrl = "/edge/management/v1/service-policies";
      //   await axios.post(
      //     proxyUrl + apiUrl,
      //     {
      //       name: name.value,
      //       type: selectedTitle.value,
      //       semantic: selectedsemantic.value,
      //       identityRoles: [identityAttribute],
      //       serviceRoles: [serviceAttribute],
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
      //   emitter.emit("closeServicesModal");
      // } catch (error) {
      //   console.error("Failed to submit form:", error);
      // }
    };
    const resetForm = () => {
      name.value = "";
      serviceRA.value = "";
      identityatt.value = "";
      Description.value = "";
      selectedTitle.value = "Dial";
      selectedsemantic.value = "AllOf";
    };

    const cancel = () => {
      console.log("tes");
      emitter.emit("closeServicesModal");
    };
    const selectItem = (item) => {
      selectedTitle.value = item;
    };
    const selectsemantic = (item) => {
      selectedsemantic.value = item;
    };

    return {
      state,
      name,
      ServList,
      serviceRA,
      identityatt,
      identityList,
      Description,
      selectedTitle,
      items,
      semantic,
      rules,
      submitForm,
      resetForm,
      cancel,
      selectItem,
      selectedsemantic,
      selectsemantic,
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
