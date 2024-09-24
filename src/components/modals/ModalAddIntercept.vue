<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("ztna.addInterceptConfig") }}</span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("ztna.updateConfig") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field id="ConfigName" v-model="ConfigName" :placeholder="$t('ztna.configName')"
                    :rules="rulesName" persistent-placeholder />
                </v-col>

                <v-col cols="12">
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
                  <v-text-field id="adress" v-model="adress" :placeholder="$t('ztna.address')" :rules="rulesaddress"
                    persistent-placeholder />
                </v-col>

                <v-col cols="6">
                  <v-text-field id="portLow" v-model.number="portLow" :placeholder="$t('ztna.lowPorts')"
                    :rules="rulesNumber" persistent-placeholder outlined dense hide-details="auto" />
                </v-col>
                <v-col cols="6" class="mb-n6">
                  <v-text-field id="portHigh" v-model.number="portHigh" :placeholder="$t('ztna.highPorts')"
                    :rules="rulesNumber" persistent-placeholder outlined dense hide-details="auto" />
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-text-field id="Description" v-model="Description" placeholder="Description"
                    persistent-placeholder />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="indigo-darken-3" :rounded="true" large rounded outlined label-color="#213E9F" variant="flat"
              class="mt-3 btn-add" text @click="cancel"><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span></v-btn>
            <v-btn large rounded outlined label-color="#213E9F" color="indigo-darken-3" :rounded="true" variant="flat"
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
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { toRefs, ref, watch, reactive, inject, onMounted } from "vue";


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
    const ConfigId = ref("");
    const intercept = ref([])
    const adress = ref("");
    const portLow = ref("");
    const portHigh = ref("");
    const Description = ref("");
    const selectedTitle = ref("tcp");
    const items = ["tcp", "udp"];
    const rules = [
      (value) => {
        if (value) return true;

        return "You must enter a value.";
      },
    ];
    const rulesNumber = [
      (value) => {
        if (!value) return true;
        return isNumber(value) ? true : "Please enter a valid number.";
      },
    ];
    const rulesName = [
      (value) => {
        if (!value) return true;
        if (existingName(value)) return "The name already exists";
        return ValidName(value) ? true : "Please enter a valid name.";
      },
    ];
    const rulesaddress = [
      (value) => {
        if (!value) return true;
        return isValidIpOrHostname(value) ? true : "Please enter a valid adress.";
      },
    ];

    function existingName(value) {
      const existingIdentity = intercept.value.find(identity => identity.name === value);

      if (existingIdentity) {
        return true;
      }

      return false;
    }
    const fetchintercept = async () => {
      try {
        const interceptString = await document.getElementById("app").getAttribute("interceptconfigs");
        const interceptObject = JSON.parse(interceptString);

        const interceptArray = Array.isArray(interceptObject) ? interceptObject : [];

        intercept.value = interceptArray.map(identity => ({ name: identity.name }));

        console.log('intercept.value', intercept.value);
      } catch (error) {
        console.error("Failed to fetch intercept:", error);
        intercept.value = [];
      }
    };



    onMounted(() => {
      fetchintercept();
    });
    function isValidIpOrHostname(value) {
      // Regular expression for IPv4
      const ipv4Pattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

      // Regular expression for IPv6
      const ipv6Pattern = /([a-fA-F0-9]{1,4}:){7,7}[a-fA-F0-9]{1,4}|([a-fA-F0-9]{1,4}:){1,7}:|([a-fA-F0-9]{1,4}:){1,6}:[a-fA-F0-9]{1,4}|([a-fA-F0-9]{1,4}:){1,5}(:[a-fA-F0-9]{1,4}){1,2}|([a-fA-F0-9]{1,4}:){1,4}(:[a-fA-F0-9]{1,4}){1,3}|([a-fA-F0-9]{1,4}:){1,3}(:[a-fA-F0-9]{1,4}){1,4}|([a-fA-F0-9]{1,4}:){1,2}(:[a-fA-F0-9]{1,4}){1,5}|[a-fA-F0-9]{1,4}:((:[a-fA-F0-9]{1,4}){1,6})$/;

      // Regular expression for valid hostnames (no pure numeric strings)
      const hostnamePattern = /^[a-zA-Z0-9-]{1,63}(\.[a-zA-Z0-9-]{1,63})*$/;

      // Check if value is a valid IPv4, IPv6, or a hostname (and not a pure number)
      if (ipv4Pattern.test(value) || ipv6Pattern.test(value) || (hostnamePattern.test(value) && !/^\d+$/.test(value))) {
        return true;
      }

      return false;
    }
    function isNumber(value) {
      // Check if value is null or undefined
      if (value == null) return false;

      // Convert to string to handle numeric primitives
      let stringValue = String(value);

      // Remove leading/trailing whitespace
      stringValue = stringValue.trim();

      // Check if empty after trimming
      if (!stringValue.length) return false;

      // Try to parse the string as a float
      let parsedFloat;
      try {
        parsedFloat = parseFloat(stringValue);
      } catch (error) {
        return false;
      }

      // Check if parsedFloat is NaN
      if (isNaN(parsedFloat)) {
        return false;
      }

      // Check if parsedFloat is finite (not Infinity or -Infinity)
      if (!isFinite(parsedFloat)) {
        return false;
      }

      // If all checks pass, it's a valid number
      return true;
    }

    function ValidName(value) {
      const hostnamePattern = /^[a-zA-Z0-9-\s]{1,63}(\.[a-zA-Z0-9-\s]{1,63})*$/;

      if (hostnamePattern.test(value) && !/^\d+$/.test(value)) {
        return true;
      }

      return false;
    }


    const emitter = inject("emitter");

    const { isOpen, editRow, modalMode } = toRefs(props);

    const state = reactive({
      openModal: false,
      snackbar: false,
      color: null,
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

        ConfigId.value = data.id;
        ConfigName.value = data.name;
        adress.value = data.address;
        portLow.value = data.low;
        portHigh.value = data.high;
        Description.value = data.description;
        selectedTitle.value = data.protocol;
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
        },
        Description: Description.value
      };

      let token = document.getElementById("app").getAttribute("token");

      if (modalMode.value === "edit") {
        axios
          .put(`/ztna/update_intercept_config/${ConfigId.value}`, payload, {
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
          .post("/ztna/add_config", payload, {
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
    };


    const selectItem = (item) => {
      selectedTitle.value = item;
    };
    const cancel = () => {
      console.log("test");
      emitter.emit("closeInterceptModal");
      ConfigName.value = "";
      adress.value = "";
      portLow.value = "";
      portHigh.value = "";
      Description.value = "";
      selectedTitle.value = "tcp";
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
      rulesNumber,
      rulesName,
      rulesaddress,
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
