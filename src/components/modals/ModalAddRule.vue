<template>
  <v-row justify="center">
    <el-dialog
      :close-on-click-modal="false"
      :show-close="false"
      :title="modalModeRule === 'create' ? 'Create New Rule' : 'Edit Rule'"
      v-model="state.openModalRule"
      persistent
      width="600"
    >
      <form ref="myForm" @submit.prevent="submitForm">
        <template v-if="modalModeRule === 'create'">
          <v-row>
            <v-col cols="12" class="mb-n6">
              <v-text-field
                label="Enter Rule Name"
                v-model="state.formData.ruleName"
              ></v-text-field>
              <p class="error-feedback mb-5" v-if="v$.formData.ruleName.$error">
                {{ v$.formData.ruleName.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row>
            <template v-if="!state.formData.time">
              <v-col cols="12" class="mb-n6">
                <v-select
                  label="Enter Routage Type"
                  v-model="state.formData.routageType"
                  item-title="name"
                  item-value="slug"
                  :items="routagType"
                  return-object
                ></v-select>

                <p
                  class="error-feedback mb-5"
                  v-if="v$.formData.routageType.$error"
                >
                  {{ v$.formData.routageType.$errors[0].$message }}
                </p>
              </v-col>
            </template>
            <template v-else>
              <v-col cols="12" class="mb-n6">
                <v-select
                  label="Enter Routage Type"
                  v-model="state.formData.routageTypeDomain"
                  item-title="name"
                  item-value="slug"
                  :items="routagTypeDomain"
                  return-object
                ></v-select>

                <p
                  class="error-feedback mb-5"
                  v-if="v$.formData.routageTypeDomain.$error"
                >
                  {{ v$.formData.routageTypeDomain.$errors[0].$message }}
                </p>
              </v-col>
            </template>
            <template v-if="state.formData.routageType.slug === 'subnet'">
              <v-col cols="12" class="mb-n6">
                <v-row>
                  <v-col cols="7">
                    <v-text-field
                      label="Value"
                      v-model="state.formData.value"
                    ></v-text-field>

                    <p
                      class="error-feedback mb-5"
                      v-if="v$.formData.value.$errors.length"
                    >
                      {{ v$.formData.value.$errors?.[0].$message }}
                    </p>
                  </v-col>
                  <v-col cols="1">
                    <div class="ml-1 mt-5">/</div>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      label="Prefix"
                      v-model="state.formData.prefix"
                    ></v-text-field>
                    <p
                      class="error-feedback mb-5"
                      v-if="v$.formData.prefix.$errors.length"
                    >
                      {{ v$.formData.prefix.$errors?.[0].$message }}
                    </p>
                  </v-col>
                </v-row>
              </v-col>
            </template>

            <template v-if="isIps || isDomains">
              <v-col cols="12" class="mb-n6">
                <v-text-field
                  label="Value"
                  v-model="state.formData.value2"
                ></v-text-field>

                <p
                  class="error-feedback mb-5"
                  v-if="v$.formData.value2.$errors.length"
                >
                  {{ v$.formData.value2.$errors?.[0].$message }}
                </p>
              </v-col>
            </template>
            <template v-if="isTimeAndDomains">
              <v-col cols="12" class="mb-n6">
                <v-text-field
                  label="Value"
                  v-model="state.formData.valueDomainTime"
                ></v-text-field>

                <p
                  class="error-feedback mb-5"
                  v-if="v$.formData.valueDomainTime.$errors.length"
                >
                  {{ v$.formData.valueDomainTime.$errors?.[0].$message }}
                </p>
              </v-col>
            </template>
          </v-row>
        </template>

        <v-row>
          <template v-if="!state.formData.time">
            <v-col cols="6">
              <label>Allowed by authentification</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.allodwedAuth" />
              <label class="ml-2">Activate Allowed by authentification</label>
            </v-col>
            <v-col cols="6">
              <label>Status</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.status" />
              <label class="ml-2">Activate rule</label>
            </v-col>
          </template>
          <template v-if="!state.formData.allodwedAuth">
            <v-col cols="6">
              <label>By time</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.time" />
              <label class="ml-2">block by time</label>
            </v-col>
          </template>

          <template v-if="state.formData.time">
            <v-col cols="12" class="mb-n6">
              <v-select
                v-model="state.formData.days"
                label="Days"
                multiple
                :items="daysArray"
                item-title="name"
                item-value="slug"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="6">
              <el-time-picker
                v-model="state.formData.from"
                style="height: 55px"
                class="w-100"
                size="large"
                format="HH:mm"
                placeholder="From"
              />
            </v-col>
            <v-col cols="6">
              <el-time-picker
                v-model="state.formData.to"
                style="height: 55px"
                class="w-100"
                size="large"
                format="HH:mm"
                placeholder="To"
              />
            </v-col>
          </template>
        </v-row>
      </form>
      <template #footer>
        <span class="dialog-footer">
          <v-btn
            color="indigo-darken-3"
            :rounded="true"
            large
            rounded
            outlined
            label-color="#213E9F"
            variant="flat"
            @click="closeModal"
            class="mt-3 btn-add"
          >
            <span class="text-white pr-3 pl-3">Close</span>
          </v-btn>

          <v-btn
            large
            rounded
            outlined
            label-color="#213E9F"
            @click="submitForm"
            color="indigo-darken-3"
            :rounded="true"
            variant="flat"
            class="mt-3 ml-2 btn-add"
          >
            <span class="text-white pr-3 pl-3">{{
              modalModeRule === "create" ? "Create" : "Edit"
            }}</span>
          </v-btn>
        </span>
      </template>
    </el-dialog>

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
import dayjs from "dayjs";
import useValidate from "@vuelidate/core";
import { helpers, requiredIf, required } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject, ref } from "vue";
import VButton from "@/components/VButton.vue";
export default {
  name: "Modal_User_Squid",
  components: {
    VButton,
  },
  props: {
    isOpenModal: {
      type: Boolean,
      required: true,
    },
    editRowRule: {
      type: Object,
      Array,
      required: true,
    },
    modalModeRule: {
      type: Object,
      Array,
      String,
      required: true,
    },
  },
  setup(props) {
    const { isOpenModal, editRowRule, modalModeRule } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      formData: {
        days: [],
        time: null,
        from: null,
        to: null,
        routageType: "",
        routageTypeDomain: "",
        value: "",
        value2: "",
        prefix: "",
        valueDomainTime: "",
        ruleName: null,
        allodwedAuth: false,
        status: false,
      },
      openModalRule: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });

    const routagType = ref([
      { name: "subnet", slug: "subnet" },
      { name: "ips", slug: "ips" },
      { name: "domains", slug: "domains" },
    ]);
    const routagTypeDomain = ref([{ name: "domains", slug: "domains" }]);

    const daysArray = ref([
      { name: "Monday", slug: "M" },
      { name: "Tuesday", slug: "T" },
      { name: "Wednesday", slug: "W" },
      { name: "Thursday", slug: "H" },
      { name: "Friday", slug: "F" },
      { name: "Saturday", slug: "A" },
      { name: "Sunday", slug: "S" },
    ]);

    const rules = computed(() => {
      return {
        formData: {
          ruleName: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(() => modalModeRule.value === "create")
            ),
          },

          value: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageType.slug === "subnet"
              )
            ),
            isValidValue: helpers.withMessage(
              `Format must be like adresse IP : X.X.X.X`,

              helpers.regex(/^[0-9.]+$/)
            ),
          },

          value2: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  (modalModeRule.value === "create" &&
                    state.formData.routageType.slug === "ips") ||
                  state.formData.routageType.slug === "domains"
              )
            ),
          },
          valueDomainTime: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageTypeDomain.slug === "domains"
              )
            ),
          },
          routageType: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(() => modalModeRule.value === "create")
            ),
          },
          routageTypeDomain: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => modalModeRule.value === "create" && state.formData.time
              )
            ),
          },
          prefix: {
            required: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageType.slug === "subnet"
              )
            ),
            isValidPrefix: helpers.withMessage(
              `Champs can include only Numbers.`,

              helpers.regex(/^[0-9]+$/)
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);

    const isSubnet = computed(() => {
      return state.formData.routageType.slug === "subnet";
    });
    const isIps = computed(() => {
      return state.formData.routageType.slug === "ips";
    });
    const isDomains = computed(() => {
      return state.formData.routageType.slug === "domains";
    });
    const isTimeAndDomains = computed(() => {
      return state.formData.routageTypeDomain.slug === "domains";
    });

    watch(
      state,
      () => {
        console.log("stat", state);
        if (state.formData.time) {
          state.formData.routageType = "";
          state.formData.status = false;
          state.formData.value = "";
          state.formData.value2 = "";
          state.formData.prefix = "";
        }
        if (!state.formData.time) {
          state.formData.routageTypeDomain = "";
          state.formData.days = [];
          state.formData.from = false;
          state.formData.to = false;
          state.formData.valueDomainTime = "";
        }
      },
      { immediate: true }
    );

    watch(
      () => isDomains.value,
      (val) => {
        v$.value.$reset();
      }
    );
    watch(
      () => isSubnet.value,
      (val) => {
        v$.value.$reset();
      }
    );
    watch(
      () => isIps.value,
      (val) => {
        v$.value.$reset();
      }
    );
    watch(
      () => isOpenModal.value,
      (val) => {
        console.log("val", val);
        state.openModalRule = val;
        v$.value.$reset();
      }
    );
    watch(
      () => editRowRule.value,
      (val) => {
        console.log("val", val);
      }
    );
    watch(
      () => modalModeRule.value,
      (val) => {
        console.log("modalModeRule", val);
      }
    );
    const closeModal = () => {
      emitter.emit("closeAddRuleModal");
      v$.value.$reset();

      state.formData.days = null;
      state.formData.time = null;
      state.formData.from = null;
      state.formData.to = null;
      state.formData.routageType = "";
      state.formData.value = "";
      state.formData.value2 = "";
      state.formData.ruleName = null;
      state.formData.prefix = "";
      state.formData.allodwedAuth = false;
      state.formData.status = false;
    };
    const submitForm = async () => {
      let from = dayjs(state.formData.from).format("HH:mm");
      let to = dayjs(state.formData.to).format("HH:mm");
      console.log("from", from);
      console.log("to", to);
      const result = await v$.value.$validate();
      console.log("result", result);

      if (result) {
        console.log("state", state);
      } else {
        console.log("error", v$.value);
        console.log("stateaa", state.formData);
      }
    };

    return {
      state,
      v$,
      isDomains,
      isTimeAndDomains,
      isSubnet,
      isIps,
      routagType,
      routagTypeDomain,
      emitter,
      daysArray,
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
.btnAction {
  display: flex !important;
  justify-content: end !important;
}
.dialog-footer button:first-child {
  margin-right: 10px;
}
</style>
