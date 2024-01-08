<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline"
            >{{ modalMode === "create" ? "Add new" : "Update" }} Rule</span
          >
        </v-card-title>
        <v-card-text>
          <v-select
            :items="['accept', 'drop', 'reject']"
            label="Policy"
            v-model="state.formData.policy"
          ></v-select>
          <p class="error-feedback mb-5" v-if="v$.formData.policy.$error">
            {{ v$.formData.policy.$errors[0].$message }}
          </p>
          <v-textarea
            variant="filled"
            auto-grow
            rows="2"
            row-height="20"
            label="Rule Description"
            v-model="state.formData.rule_description"
            outlined
          ></v-textarea>
          <p
            class="error-feedback mb-5"
            v-if="v$.formData.rule_description.$error"
          >
            {{ v$.formData.rule_description.$errors[0].$message }}
          </p>
          <v-select
            :items="[
              'tcp',
              'udp',
              'icmp',
              'icmp type echo-request',
              'icmp type echo-reply',
              'all',
            ]"
            v-model="state.formData.protocol"
            label="Protocol"
            outlined
          ></v-select>
          <p class="error-feedback mb-5" v-if="v$.formData.protocol.$error">
            {{ v$.formData.protocol.$errors[0].$message }}
          </p>
          <v-row>
            <v-col cols="6">
              <v-text-field
                label="Src Address"
                v-model="state.formData.saddr"
                outlined
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.formData.saddr.$error">
                {{ v$.formData.saddr.$errors[0].$message }}
              </p>
            </v-col>
            <v-col cols="6">
              <v-text-field
                :readonly="state.isAll"
                label="Src Port"
                v-model="state.formData.sport"
                outlined
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.formData.sport.$error">
                {{ v$.formData.sport.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                label="Dst Address"
                v-model="state.formData.daddr"
                outlined
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.formData.daddr.$error">
                {{ v$.formData.daddr.$errors[0].$message }}
              </p>
            </v-col>
            <v-col cols="6">
              <v-text-field
                :readonly="state.isAll"
                label="Dst Port"
                v-model="state.formData.dport"
                outlined
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.formData.dport.$error">
                {{ v$.formData.dport.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>
        </v-card-text>
        <div class="container">
          <div class="row justify-content-center">
            <br />
            <div class="col-12 d-flex justify-center">
              <VButton
                rounded
                outlined
                border-color="'#213E9F'"
                color="#ffffff"
                label-color="#213E9F"
                label="cancel"
                :isLarge="true"
                @click="cancel"
              />
              <VButton
                rounded
                outlined
                color="#213E9F"
                label-color="#ffffff"
                label="save"
                :isLarge="true"
                class="ml-2"
                @click="submitForm"
              />
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
import useValidate from "@vuelidate/core";
import {
  sameAs,
  helpers,
  requiredIf,
  email,
  required,
} from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject, onMounted } from "vue";
import VButton from "@/components/VButton.vue";
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
      type: Object,
      Array,
      String,
      required: true,
    },
  },
  setup(props) {
    const { isOpen, editRow, modalMode } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      isAll: false,
      nameInter: "",
      formData: {
        policy: "",
        rule_description: "",
        protocol: "",
        saddr: "",
        sport: "",
        daddr: "",
        dport: "",
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rules = computed(() => {
      return {
        formData: {
          policy: {
            required,
          },
          protocol: {
            required,
          },
          rule_description: {
            required,
          },

          sport: {
            // requiredIfFuction: helpers.withMessage(
            //   "Value is required",
            //   requiredIf(() => state.formData.protocol !== "all")
            // ),

            isValidSport: helpers.withMessage(
              `Champs can include only Numbers.`,

              helpers.regex(/^[0-9]+$/)
            ),
          },

          daddr: {
            isValidDaddr: helpers.withMessage(
              `Format must be like adresse IP : X.X.X.X`,

              helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
            ),
          },

          saddr: {
            isValidSaddr: helpers.withMessage(
              `Format must be like adresse IP : X.X.X.X`,

              helpers.regex(/^(\d{1,3}\.){3}\d{1,3}$/)
            ),
          },

          dport: {
            isValidSport: helpers.withMessage(
              `Champs can include only Numbers.`,

              helpers.regex(/^[0-9]+$/)
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);
    watch(
      state,
      (val) => {
        console.log("valState", val);
        if (state.formData.protocol === "all") {
          state.isAll = true;
          state.formData.sport = "";
          state.formData.dport = "";
        } else {
          state.isAll = false;
        }
      },
      { immediate: true }
    );

    watch(
      () => editRow.value,
      (val) => {
        console.log("val", val);
      }
    );
    watch(
      () => modalMode.value,
      (val) => {
        console.log("modalMode", val);
      }
    );
    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
        v$.value.$reset();
      }
    );

    onMounted(() => {
      let nameInterface = localStorage.getItem("firewall-tab");
      state.nameInter = nameInterface;
    });
    const closeModal = () => {
      emitter.emit("closeSquidUserModal");
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
      console.log("result", result);

      if (result) {
        let payload = {};
        if (state.formData.protocol === "all") {
          payload = {
            type_rule: "inbound",
            policy: state.formData.policy,
            rule_description: state.formData.rule_description,
            protocol: state.formData.protocol,
            saddr: state.formData.saddr,
            daddr: state.formData.daddr,
          };
        } else {
          payload = {
            type_rule: "inbound",
            policy: state.formData.policy,
            rule_description: state.formData.rule_description,
            protocol: state.formData.protocol,
            saddr: state.formData.saddr,
            sport: state.formData.sport,
            daddr: state.formData.daddr,
            dport: state.formData.dport,
          };
        }
        axios
          .post(`/rules/addRule/${state.nameInter}`, payload)
          .then((response) => {
            console.log("re", response);
            if (response.status == "200") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.response;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            console.log("res", i.response);
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
          });
      } else {
        console.log("error", v$.value);
      }
    };

    return {
      state,
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
