<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addServices") }}</span
            >
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateService") }}</span
            >
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="ServiceName"
                    v-model="name"
                    :placeholder="$t('ztna.serviceName')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    id="ServiceAttribute"
                    v-model="serviceAtt"
                    :placeholder="$t('ztna.serviceAttribute')"
                    :rules="rules"
                    persistent-placeholder
                  />
                </v-col>

                <v-col cols="12" class="mb-n3">
                  <label for="Tunneler" class="mr-3">{{
                    $t("ztna.encryption")
                  }}</label>
                  <input
                    type="checkbox"
                    id="encryptionRequired"
                    value="encryptionRequired"
                    v-model="encryptionRequired"
                  />
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    id="intercept"
                    v-model="intercept"
                    placeholder="INTERCEPT"
                    :rules="rules"
                    persistent-placeholder
                    class="mr-6"
                    outlined
                    dense
                    hide-details="auto"
                  />
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field
                    id="host"
                    v-model="host"
                    :placeholder="$t('ztna.host')"
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
                    :rules="rules"
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
              >{{ $t("buttons.close") }}</v-btn
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
  </v-row>
</template>

<script>
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
    const name = ref("");
    const serviceAtt = ref("");
    const encryptionRequired = ref(false);
    const host = ref("");
    const configs = ref([]);
    const intercept = ref("");
    const Description = ref("");
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
          // ConfigName.value = "";
          // adress.value = "";
          // portLow.value = "";
          // portHigh.value = "";
          // Description.value = "";
          // selectedTitle.value = "tcp";
        }
      }
    );
    const populate = (data) => {
      if (modalMode.value === "edit") {
        console.log("dataService", data);
      }
    };
    const fetchConfigs = () => {
      let configsString = document
        .getElementById("app")
        .getAttribute("configs");
      let configsObject;

      try {
        configsObject = JSON.parse(configsString);
      } catch (error) {
        console.error("Failed to parse configs string:", error);
      }
      configs.value = configsObject.data;
    };

    const submitForm = async () => {
      try {
        fetchConfigs();
        let token = document.getElementById("app").getAttribute("token");
        let hostId = configs.value.find(
          (config) => config.name === host.value
        ).id;
        let interceptId = configs.value.find(
          (config) => config.name === intercept.value
        ).id;
        const proxyUrl = "https://asguard:3000";
        const apiUrl = "/edge/management/v1/services";
        const response = await axios.post(
          proxyUrl + apiUrl,
          {
            name: name.value,
            roleAttributes: [serviceAtt.value],
            encryptionRequired: encryptionRequired.value,
            configs: [hostId, interceptId],
          },
          {
            headers: {
              "zt-session": token,
              "Content-Type": "application/json",
            },
          }
        );
        setTimeout(() => {
          location.reload();
        }, 1000);
        emitter.emit("closeServicesModal");
      } catch (error) {
        console.error("Failed to submit form:", error);
      }
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
      serviceAtt,
      encryptionRequired,
      Description,
      rules,
      host,
      configs,
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
