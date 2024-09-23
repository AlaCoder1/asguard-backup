<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="UpdateHost">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.updateHostConfig") }}</span>
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
    const configs = ref([]);
    const ConfigName = ref("");
    const adress = ref("");
    const port = ref();
    const Description = ref("");
    const selectedTitle = ref("tcp");
    const hostId = ref("");
    const items = [{ title: "tcp" }, { title: "udp" }];
    const rules = [(value) => !!value || "You must enter a value."];

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
        configsObject = { data: [] }; // Default to an empty array if parsing fails
      }
      configs.value = configsObject.data;
    };
    const UpdateHost = async () => {
      try {
        fetchConfigs();
        let token = document.getElementById("app").getAttribute("token");
        let requestBody = {};

        const targetConfig = configs.value.find(
          (config) => config.id === state.itemId
        );

        if (targetConfig) {
          let dataObject = JSON.parse(JSON.stringify(targetConfig.data));

          if (adress.value.trim() !== "") {
            dataObject.address = adress.value;
          }

          if (Number.isFinite(Number(port.value))) {
            dataObject.port = Number(port.value);
          }

          if (selectedTitle.value.trim() !== "") {
            dataObject.protocol = selectedTitle.value.trim();
          }

          if (Object.keys(dataObject).length > 0) {
            requestBody.data = dataObject;
          }

          requestBody.name = ConfigName.value.trim();
          requestBody.configTypeId = "NH5p4FpGR";
        } else {
          console.log("Configuration not found");
        }

        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/configs/${state.itemId}`;
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
    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };

    const cancel = () => {
      emitter.emit("closeUpdateHostModal");
    };

    return {
      state,
      cancel,
      emitter,
      ConfigName,
      adress,
      port,
      Description,
      selectedTitle,
      items,
      selectItem,
      hostId,
      UpdateHost,
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
