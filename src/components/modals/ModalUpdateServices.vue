<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="updateServices">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ $t("ztna.updateService") }}</span>
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
              {{ $t("buttons.update") }}
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
    selectedId: {
      type: [String, Number],
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

    const { isOpen, selectedId } = toRefs(props);

    const state = reactive({
      openModal: false,
      itemId: null,
    });

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
      }
    );
    watch(
      () => selectedId.value,
      (val) => {
        console.log(val);
        state.itemId = val;
      }
    );

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

    const updateServices = async () => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};

        if (name.value.trim() !== "") {
          requestBody.name = name.value;
        }
        if (serviceAtt.value.trim() !== "") {
          requestBody.serviceAtt = serviceAtt.value;
        }
        if (encryptionRequired.value) {
          requestBody.encryptionRequired = true;
        }
        if (host.value.trim() !== "") {
          requestBody.host = host.value;
        }
        if (intercept.value.trim() !== "") {
          requestBody.intercept = intercept.value;
        }
        if (configs.value.length > 0) {
          requestBody.configs = configs.value;
        }

        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/services/${state.itemId}`;
        const response = await axios.patch(proxyUrl + apiUrl, requestBody, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        });
        console.log("here");
        setTimeout(() => {
          location.reload();
        }, 1000);
      } catch (error) {
        console.error(
          "Failed to update item:",
          error.response ? error.response.data : error.message
        );
      }
    };

    const cancel = () => {
      emitter.emit("closeUpdateModal");
    };

    return {
      state,
      cancel,
      emitter,
      serviceAtt,
      configs,
      name,
      updateServices,
      Description,
      intercept,
      host,
      rules,
      selectedId,
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
