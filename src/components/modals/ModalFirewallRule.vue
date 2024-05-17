<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline" v-if="modalMode === 'create'">
            {{ $t("firewall.add_rule") }}
          </span>
          <span class="headline" v-if="modalMode === 'edit'">
            {{ $t("firewall.update_rule") }}
          </span>
        </v-card-title>
        <v-card-text>
          <v-select
            :items="policyList"
            :label="$t('firewall.policy')"
            :no-data-text="$t('nat.msg_no_data')"
            v-model="state.formData.policy"
          ></v-select>
          <p class="error-feedback mb-5" v-if="v$.formData.policy.$error">
            {{ v$.formData.policy.$errors[0].$message }}
          </p>

          <v-textarea
            rows="1"
            row-height="15"
            class="mt-3"
            v-model="state.formData.rule_description"
            :label="$t('firewall.description')"
            variant="outlined"
          ></v-textarea>

          <p
            class="error-feedback mb-5"
            v-if="v$.formData.rule_description.$error"
          >
            {{ v$.formData.rule_description.$errors[0].$message }}
          </p>
          <v-select
            :items="protocolList"
            v-model="state.formData.protocol"
            :no-data-text="$t('nat.msg_no_data')"
            :label="$t('firewall.protocol')"
            outlined
          ></v-select>
          <p class="error-feedback mb-5" v-if="v$.formData.protocol.$error">
            {{ v$.formData.protocol.$errors[0].$message }}
          </p>
          <v-row>
            <v-col :cols="state.isAll ? 12 : 6" class="mb-n6">
              <v-text-field
                :label="$t('firewall.saddr')"
                v-model="state.formData.saddr"
                outlined
              ></v-text-field>
              <!-- <p class="error-feedback mb-5" v-if="v$.formData.saddr.$error">
                {{ v$.formData.saddr.$errors[0].$message }}
              </p> -->
            </v-col>
            <v-col cols="6" class="mb-n6">
              <v-text-field
                v-if="!state.isAll"
                :readonly="state.isAll"
                :label="$t('firewall.sport')"
                v-model="state.formData.sport"
                outlined
              ></v-text-field>
              <!-- <p class="error-feedback mb-5" v-if="v$.formData.sport.$error">
                {{ v$.formData.sport.$errors[0].$message }}
              </p> -->
            </v-col>
          </v-row>
          <v-row>
            <v-col :cols="state.isAll ? 12 : 6">
              <v-text-field
                :label="$t('firewall.daddr')"
                v-model="state.formData.daddr"
                outlined
              ></v-text-field>
              <!-- <p class="error-feedback mb-5" v-if="v$.formData.daddr.$error">
                {{ v$.formData.daddr.$errors[0].$message }}
              </p> -->
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-if="!state.isAll"
                :readonly="state.isAll"
                :label="$t('firewall.dport')"
                v-model="state.formData.dport"
                outlined
              ></v-text-field>
              <!-- <p class="error-feedback mb-5" v-if="v$.formData.dport.$error">
                {{ v$.formData.dport.$errors[0].$message }}
              </p> -->
            </v-col>
          </v-row>
        </v-card-text>
        <div class="container">
          <div class="row justify-content-center">
            <br />
            <div class="col-12 d-flex justify-center">
              <v-btn
                rounded
                outlined
                color="#213E9F"
                :isLarge="true"
                variant="outlined"
                class="ml-2"
                @click="closeModal"
              >
                <span style="color: #213e9f" class="pr-3 pl-3">{{
                  $t("buttons.close")
                }}</span>
              </v-btn>
              <v-btn
                rounded
                outlined
                color="#213E9F"
                label-color="#ffffff"
                :disabled="equal"
                :isLarge="true"
                class="ml-2"
                @click="submitForm"
              >
                <span
                  class="text-white pr-3 pl-3"
                  v-if="modalMode === 'create'"
                >
                  {{ $t("buttons.create") }}</span
                >
                <span class="text-white pr-3 pl-3" v-if="modalMode === 'edit'">
                  {{ $t("buttons.update") }}</span
                >
              </v-btn>
            </div>
          </div>
        </div>
        <br />
      </v-card>
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
import { useI18n } from "vue-i18n";
import useValidate from "@vuelidate/core";
import {
  sameAs,
  helpers,
  requiredIf,
  email,
  required,
} from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject, onMounted, ref } from "vue";
import VButton from "@/components/VButton.vue";
import { v4 as uuidv4 } from "uuid";
export default {
  name: "Modal_User_Squid",
  components: {
    VButton,
  },
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: true,
    },
    modalMode: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { isOpen, editRow, modalMode } = toRefs(props);
    const emitter = inject("emitter");
    const { t } = useI18n();
    const policyList = ref(["accept", "drop", "reject"]);
    const protocolList = ref([
      "tcp",
      "udp",
      "icmp",
      "icmp type echo-request",
      "icmp type echo-reply",
      "all",
    ]);
    const state = reactive({
      isAll: false,
      id: "",
      interUuid: "",
      nameInter: "",
      formData: {
        policy: "",
        rule_description: "",
        protocol: "",
        saddr: "ALL",
        sport: "ALL",
        daddr: "ALL",
        dport: "ALL",
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
      editValue: null,
      type_rule: "",
      status: "",
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const onlynumbers = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const formaaddress = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const rules = computed(() => {
      return {
        formData: {
          policy: {
            required: helpers.withMessage(error, required),
          },
          protocol: {
            required: helpers.withMessage(error, required),
          },
          rule_description: {
            required: helpers.withMessage(error, required),
          },

          // sport: {
          //   // requiredIfFuction: helpers.withMessage(
          //   //   "Value is required",
          //   //   requiredIf(() => state.formData.protocol !== "all")
          //   // ),

          //   isValidSport: helpers.withMessage(
          //     `Champs can include only Numbers.`,

          //     helpers.regex(/^[0-9]+$/)
          //   ),
          // },

          // daddr: {
          //   // isValidDaddr: helpers.withMessage(
          //   //   `Format must be like adresse IP : X.X.X.X`,

          //   //   helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          //   // ),
          //   isValidDaddr: helpers.withMessage(
          //     `Format must be like : X.X.X.X/X`,
          //     helpers.regex(
          //       /^(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/(32|3[01]|[1-2]?[1-9]))$/
          //     )
          //   ),
          // },

          // saddr: {
          //   isValidSaddr: helpers.withMessage(
          //     `Format must be like : X.X.X.X/X`,
          //     helpers.regex(
          //       /^(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/(32|3[01]|[1-2]?[1-9]))$/
          //     )
          //   ),
          // },
          // // saddr: {
          // //   isValidSaddr: helpers.withMessage(
          // //     `Format must be like adresse IP : X.X.X.X`,

          // //     helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
          // //   ),
          // // },

          // dport: {
          //   isValidSport: helpers.withMessage(
          //     `Champs can include only Numbers.`,

          //     helpers.regex(/^[0-9]+$/)
          //   ),
          // },
        },
      };
    });

    const v$ = useValidate(rules, state);
    watch(
      state,
      () => {
        if (
          state.formData.protocol === "all" ||
          state.formData.protocol === "icmp" ||
          state.formData.protocol === "icmp type echo-request" ||
          state.formData.protocol === "icmp type echo-reply"
        ) {
          state.isAll = true;
          state.formData.sport = "ALL";
          state.formData.dport = "ALL";
        } else {
          state.isAll = false;
        }
        if (state.formData.saddr === "") state.formData.saddr = "ALL";
        if (state.formData.sport === "") state.formData.sport = "ALL";
        if (state.formData.daddr === "") state.formData.daddr = "ALL";
        if (state.formData.dport === "") state.formData.dport = "ALL";
      },
      { immediate: true }
    );

    watch(
      () => editRow.value,
      (val) => {
        populate(val);
      }
    );
    watch(
      () => modalMode.value,
      (val) => {
        if (val === "create") {
          state.formData.policy = "";
          state.formData.rule_description = "";
          state.formData.protocol = "";
          state.formData.saddr = "ALL";
          state.formData.sport = "ALL";
          state.formData.daddr = "ALL";
          state.formData.dport = "ALL";
        }
      }
    );
    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
        v$.value.$reset();
      }
    );

    const equal = computed(() => {
      // let obj1 = { ...editRow.value };
      let obj1 = {
        daddr: editRow.value.daddr ?? "ALL",
        dport: editRow.value.dport ?? "ALL",
        saddr: editRow.value.saddr ?? "ALL",
        sport: editRow.value.sport ?? "ALL",
        policy: editRow.value.policy,
        protocol: editRow.value.protocol,
        rule_description: editRow.value.rule_description,
        id: editRow.value.id,
        uuid: editRow.value.uuid,
        type_rule: editRow.value.type_rule,
        status: editRow.value.status,
      };
      let obj2 = {
        daddr: state.formData.daddr ?? "ALL",
        dport: state.formData.dport ?? "ALL",
        saddr: state.formData.saddr ?? "ALL",
        sport: state.formData.sport ?? "ALL",
        policy: state.formData.policy,
        protocol: state.formData.protocol,
        rule_description: state.formData.rule_description,
        id: state.id,
        uuid: state.editValue,
        type_rule: state.type_rule,
        status: state.status,
      };

      const deepEqual = (obj1, obj2) => {
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);

        if (keys1.length !== keys2.length) {
          return false;
        }

        for (const key of keys1) {
          if (typeof obj1[key] === "object" && typeof obj2[key] === "object") {
            if (!deepEqual(obj1[key], obj2[key])) {
              return false;
            }
          } else {
            if (obj1[key] !== obj2[key]) {
              return false;
            }
          }
        }
        return true;
      };

      return deepEqual(obj1, obj2);
    });

    onMounted(() => {
      let nameInterface = localStorage.getItem("firewall-tab");
      state.nameInter = nameInterface;

      emitter.on("interface-uuid", (uuid) => {
        state.interUuid = uuid;
      });
    });
    const closeModal = () => {
      emitter.emit("closFirewallInboundModal");
      if (modalMode.value === "create") {
        state.formData.policy = "";
        state.formData.rule_description = "";
        state.formData.protocol = "";
        state.formData.saddr = "ALL";
        state.formData.sport = "ALL";
        state.formData.daddr = "ALL";
        state.formData.dport = "ALL";
      }
    };
    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.id = data.id;
        let filtredPolicy = policyList.value.filter((i) => i === data?.policy);
        let filtredProtocol = protocolList.value.filter(
          (i) => i === data?.protocol
        );

        state.formData.policy = filtredPolicy[0];
        state.formData.rule_description = data.rule_description;
        state.formData.protocol = filtredProtocol[0];
        state.formData.saddr = data.saddr;
        state.formData.sport = data.sport;
        state.formData.daddr = data.daddr;
        state.formData.dport = data.dport;
        state.editValue = data.uuid;

        (state.status = data.status), (state.type_rule = data.type_rule);
      }
    };
    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };
    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const result = await v$.value.$validate();

      if (result) {
        let payload = {};
        if (
          state.formData.protocol === "all" ||
          state.formData.protocol === "icmp" ||
          state.formData.protocol === "icmp type echo-request" ||
          state.formData.protocol === "icmp type echo-reply"
        ) {
          payload = {
            uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
            type_rule: "inbound",
            policy: state.formData.policy,
            rule_description: state.formData.rule_description,
            protocol: state.formData.protocol,
            saddr: state.formData.saddr,
            daddr: state.formData.daddr,
            id: modalMode.value === "edit" ? state.id : "",
            interUuid: state.interUuid,
            status: modalMode.value === "create" ? "new" : "old",
          };
        } else {
          payload = {
            uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
            type_rule: "inbound",
            policy: state.formData.policy,
            rule_description: state.formData.rule_description,
            protocol: state.formData.protocol,
            saddr: state.formData.saddr,
            sport: state.formData.sport,
            daddr: state.formData.daddr,
            dport: state.formData.dport,
            id: modalMode.value === "edit" ? state.id : "",
            interUuid: state.interUuid,
            status: modalMode.value === "create" ? "new" : "old",
          };
        }
        if (modalMode.value === "edit") {
          // axios
          //   .put(`/rules/updateRule/${state.nameInter}`, payload)
          //   .then((response) => {
          //     console.log("re", response);
          //     if (response.status == "200") {
          //       state.snackbar = true;
          //       state.color = "success";
          //       state.textAlert = response.data.response;
          //       setTimeout(() => {
          //         location.reload();
          //       }, 1000);
          //     }
          //   })
          //   .catch((i) => {
          //     console.log("res", i.response);
          //     state.snackbar = true;
          //     state.color = "red";
          //     state.textAlert = i.response.data.response;
          //   });
          emitter.emit("edit-firewallRule", payload);
          emitter.emit("old-row", editRow.value);
        } else if (modalMode.value === "create") {
          // axios
          //   .post(`/rules/addRule/${state.nameInter}`, payload)
          //   .then((response) => {
          //     console.log("re", response);
          //     if (response.status == "200") {
          //       state.snackbar = true;
          //       state.color = "success";
          //       state.textAlert = response.data.response;
          //       setTimeout(() => {
          //         location.reload();
          //       }, 1000);
          //     }
          //   })
          //   .catch((i) => {
          //     console.log("res", i.response);
          //     state.snackbar = true;
          //     state.color = "red";
          //     state.textAlert = i.response.data.response;
          //   });
          emitter.emit("add-firewallRule", payload);
        }

        closeModal();
        v$.value.$reset();
      } else {
        console.log("error", v$.value);
      }
    };

    return {
      state,
      equal,
      policyList,
      protocolList,
      v$,
      emitter,
      closeModal,
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
</style>
