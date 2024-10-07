<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addServices") }}</span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateService") }}</span>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="ServiceName" v-model="name" :placeholder="$t('ztna.serviceName')" :rules="rules"
                    persistent-placeholder />
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="ServiceAttribute" v-model="serviceAtt" :placeholder="$t('ztna.serviceAttribute')"
                    :rules="rules" persistent-placeholder />
                </v-col>

                <v-col cols="12" class="mb-n3">
                  <label for="Tunneler" class="mr-3">{{
                    $t("ztna.encryption")
                    }}</label>
                  <input type="checkbox" id="encryptionRequired" value="encryptionRequired"
                    v-model="encryptionRequired" />
                </v-col>

                <v-col cols="6">
                  <!-- <v-text-field id="intercept" v-model="intercept" placeholder="INTERCEPT" :rules="rules"
                    persistent-placeholder class="mr-6" outlined dense hide-details="auto" /> -->

                    <v-select
                    v-model="intercept"
                    label="INTERCEPT"
                    density="compact"
                    item-title="name"
                    item-value="id"
                    return-object
                     :rules="rules"
                    :items="interceptList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
                  </v-select>

                </v-col>
                <v-col cols="6" class="mb-n6">
                  <!-- <v-text-field id="host" v-model="host" :placeholder="$t('ztna.host')" :rules="rules"
                    persistent-placeholder outlined dense hide-details="auto" /> -->

                    <v-select
                    v-model="host"
                    :label="$t('ztna.host')"
                    density="compact"
                    item-title="name"
                    item-value="id"
                    return-object
                     :rules="rules"
                    :items="hostList"
                    background-color="#fffffff"
                    :no-data-text="$t('certificat.certificatlist')"
                  >
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
                {{ $t("buttons.close") }}</span
              ></v-btn>
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
import { toRefs, ref, watch, reactive, inject,onMounted } from "vue";
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
    const servId = ref("");
    const serviceAtt = ref("");
    const encryptionRequired = ref(false);
    const intercept = ref("");
    const host = ref("");
    const Description = ref("");
    const rules = [
      (value) => {
        if (value) return true;
        return "You must enter a value.";
      },
    ];
    const interceptList = ref([]);
    const hostList = ref([]);
    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      openModal: false,
      snackbar: false,
      color: null,
      textAlert: "",
    });

    onMounted(()=>{
      fetchHostConfigs()
      fetchInterceptConfigs()
    })

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
          serviceAtt.value = "";
          encryptionRequired.value = false;
          host.value = "";
          intercept.value = "";
          configs.value = "";
          Description.value = "";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataService", data);
        servId.value = data.id
        name.value = data.name;
        serviceAtt.value = data.attribute_service;
        encryptionRequired.value = data.encryption;
        Description.value = "";
        let hostobj = "";
        let interceptobj = "";
        for (let i = 0; i < hostList.value.length; i++) {
          if (hostList.value[i].id === data.host) {
            hostobj = hostList.value[i];
            break;  
          }
        }

        for (let i = 0; i < interceptList.value.length; i++) {
          if (interceptList.value[i].id === data.intercept) {
            interceptobj = interceptList.value[i];
            break;
          }
        }
        host.value=hostobj;
        intercept.value=interceptobj
  }
    };
    const fetchInterceptConfigs = () => {
      let configsString = document
        .getElementById("app")
        .getAttribute("interceptconfigs");
      let configsObject;

      try {
        configsObject = JSON.parse(configsString);
      } catch (error) {
        console.error("Failed to parse configs string:", error);
      }
      
      interceptList.value = configsObject;
      console.log('intercept',interceptList.value)
    };

    const fetchHostConfigs = () => {
      let configsString = document
        .getElementById("app")
        .getAttribute("hostconfigs");
      let configsObject;

      try {
        configsObject = JSON.parse(configsString);
      } catch (error) {
        console.error("Failed to parse configs string:", error);
      }
        
      hostList.value = configsObject;
      console.log('host,',hostList.value)
    };

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        name: name.value,
        roleAttributes: [serviceAtt.value],
        encryptionRequired: encryptionRequired.value,
        configs: [intercept.value.ref_intercept, host.value.ref_host]
      };

      let token = document.getElementById("app").getAttribute("token");


      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_services/${servId.value}`, payload, {
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
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      } else {
        axios
          .post("/ztna/add_services", payload, {
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
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      }
      // try {
      //   fetchConfigs();
      //   let token = document.getElementById("app").getAttribute("token");
      //   let hostId = configs.value.find(
      //     (config) => config.name === host.value
      //   ).id;
      //   let interceptId = configs.value.find(
      //     (config) => config.name === intercept.value
      //   ).id;
      //   const proxyUrl = "https://asguard:3000";
      //   const apiUrl = "/edge/management/v1/services";
      //   const response = await axios.post(
      //     proxyUrl + apiUrl,
      //     {
      //       name: name.value,
      //       roleAttributes: [serviceAtt.value],
      //       encryptionRequired: encryptionRequired.value,
      //       configs: [hostId, interceptId],
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
      serviceAtt.value = "";
      encryptionRequired.value = false;
      Description.value = "";
      selectedTitle.value = "SmartRouting";
      selectedConfig.value = "Host V1 Config";
      selectedTerminator.value = "Ter1";
    };

    const cancel = () => {
      console.log("tes");
      emitter.emit("closeServicesModal");
    };

    return {
      state,
      name,
      interceptList,
      hostList,
      serviceAtt,
      encryptionRequired,
      Description,
      rules,
      host,
      hostList,
      interceptList,
      intercept,
      submitForm,
      resetForm,
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
