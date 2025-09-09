<template>
  <v-row justify="center">
    <el-dialog
      v-model="state.openModalRule"
      :close-on-click-modal="false"
      :show-close="false"
      :title="
        modalModeRule === 'create'
          ? $t('sdwan.createNewRule')
          : $t('sdwan.updateRule')
      "
      width="600"
      style="margin-top: 50px"
    >
      <form ref="myForm" @submit.prevent="submitForm">
        <v-row>
          <v-col cols="12" class="mb-n6">
            <v-text-field
              :label="`${$t('sdwan.ruleName')} *`"
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
                :label="`${$t('squid.routageType')} *`"
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
                :label="`${$t('squid.routageType')} *`"
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
                    :label="$t('squid.value')"
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
                  <!-- <v-text-field
                      :label="$t('sdwan.prefix')"
                      v-model="state.formData.prefix"
                    ></v-text-field> -->
                  <v-select
                    v-model="state.formData.prefix"
                    :label="$t('sdwan.prefix')"
                    :no-data-text="$t('nat.msg_no_data')"
                    :items="numberList"
                  ></v-select>
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

          <template v-if="isDomains">
            <v-col cols="12" class="mb-n6">
              <v-text-field
                :label="$t('squid.value')"
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
          <template v-if="isIps">
            <v-col cols="12" class="mb-n6">
              <v-text-field
                :label="$t('squid.value')"
                v-model="state.formData.valueIp"
              ></v-text-field>

              <p
                class="error-feedback mb-5"
                v-if="v$.formData.valueIp.$errors.length"
              >
                {{ v$.formData.valueIp.$errors?.[0].$message }}
              </p>
            </v-col>
          </template>
          <template v-if="isTimeAndDomains && state.formData.time">
            <v-col cols="12" class="mb-n6">
              <v-text-field
                :label="$t('squid.value')"
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

        <v-row>
          <template v-if="!state.formData.time">
            <v-col cols="6">
              <label>{{ $t("squid.allowedAuthentification") }}</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.allodwedAuth" />
              <label class="ml-2">{{ $t("squid.activateAllowed") }}</label>
            </v-col>
            <v-col cols="6">
              <label>{{ $t("squid.status") }}</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.status" />
              <label class="ml-2">{{ $t("squid.activateRule") }}</label>
            </v-col>
          </template>
          <template v-if="!state.formData.allodwedAuth">
            <v-col cols="6">
              <label>{{ $t("squid.byTime") }}</label>
            </v-col>
            <v-col cols="6" class="mb-n6">
              <input type="checkbox" v-model="state.formData.time" />
              <label class="ml-2">{{ $t("squid.blockTime") }}</label>
            </v-col>
          </template>

          <template v-if="state.formData.time">
            <v-col cols="12" class="mb-n6">
              <v-select
                v-model="state.formData.days"
                :label="$t('squid.days')"
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
                value-format="HH:mm"
                :placeholder="$t('squid.from')"
              />
            </v-col>
            <v-col cols="6">
              <el-time-picker
                v-model="state.formData.to"
                style="height: 55px"
                class="w-100"
                size="large"
                format="HH:mm"
                value-format="HH:mm"
                :placeholder="$t('squid.to')"
              />
            </v-col>
            <p class="error-feedback mb-5 ml-4" v-if="isValidTime">
              {{ $t("squid.errorTime") }}
            </p>
          </template>
        </v-row>
      </form>
      <template #footer>
        <div class="d-flex justify-content-between">
          <div class="text-start align-end mt-5">
            <span class="text-sm">
              <span class="text-red text-lg">*</span>
              {{ $t("errors.oblig") }}</span
            >
          </div>
          <v-spacer></v-spacer>

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
              <span class="text-white pr-3 pl-3">{{
                $t("buttons.close")
              }}</span>
            </v-btn>

            <v-btn
              large
              rounded
              outlined
              :disabled="isValidTime"
              label-color="#213E9F"
              @click="submitForm"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 ml-2 btn-add"
            >
              <span
                class="text-white pr-3 pl-3"
                v-if="modalModeRule === 'create'"
              >
                {{ $t("buttons.create") }}</span
              >
              <span
                class="text-white pr-3 pl-3"
                v-if="modalModeRule === 'edit'"
              >
                {{ $t("buttons.update") }}</span
              >
            </v-btn>
          </span>
        </div>
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
import { useI18n } from "vue-i18n";
import axios from "axios";
import dayjs from "dayjs";
import useValidate from "@vuelidate/core";
import { helpers, requiredIf, required } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject, ref } from "vue";
import VButton from "@/components/VButton.vue";
import { id } from "@/mixins/storage_language.js";
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
      String,
      required: true,
    },
  },

  setup(props) {
    const { t } = useI18n();
    const { isOpenModal, editRowRule, modalModeRule } = toRefs(props);
    const emitter = inject("emitter");
    const numberList = ref(Array.from({ length: 33 }, (_, i) => i));

    const state = reactive({
      formData: {
        days: [],
        time: false,
        from: "",
        to: "",
        routageType: "",
        routageTypeDomain: "",
        value: "",
        value2: "",
        valueIp: "",
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
      rowEdit: null,
    });

    const routagType = ref([
      { name: "subnet", slug: "subnet" },
      { name: "ips", slug: "ip" },
      { name: "domains", slug: "domain" },
    ]);
    const routagTypeDomain = ref([{ name: "domains", slug: "domain" }]);

    const Monday = computed(() => {
      return t("Monday");
    });
    const Tuesday = computed(() => {
      return t("Tuesday");
    });
    const Wednesday = computed(() => {
      return t("Wednesday");
    });
    const Thursday = computed(() => {
      return t("Thursday");
    });
    const Friday = computed(() => {
      return t("Friday");
    });
    const Saturday = computed(() => {
      return t("Saturday");
    });
    const Sunday = computed(() => {
      return t("Sunday");
    });

    const daysArray = ref([
      { name: Monday, slug: "M" },
      { name: Tuesday, slug: "T" },
      { name: Wednesday, slug: "W" },
      { name: Thursday, slug: "H" },
      { name: Friday, slug: "F" },
      { name: Saturday, slug: "A" },
      { name: Sunday, slug: "S" },
    ]);

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champInclude = computed(() => {
      return t("errors.ChampIncludeOnlyNumbers");
    });
    const formatMustBeLikeAdresseIP = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const zeroNumber = computed(() => {
      return t("zeroNumber");
    });

    const format = computed(() => {
      return t("errors.format_address");
    });

    const rules = computed(() => {
      return {
        formData: {
          ruleName: {
            required: helpers.withMessage(
              error,
              requiredIf(() => modalModeRule.value === "create")
            ),
          },

          value: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageType.slug === "subnet"
              )
            ),
            isValidValue: helpers.withMessage(
              formatMustBeLikeAdresseIP,

              helpers.regex(
                /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
              )
            ),
          },

          value2: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  (modalModeRule.value === "create" ||
                    modalModeRule.value === "edit") &&
                  state.formData.routageType.slug === "domain" &&
                  !state.formData.time
              )
            ),
            isValidName: helpers.withMessage(
              format,

              helpers.regex(
                /^([a-zA-Z]+\d*|\d+[a-zA-Z]*|\d+|[a-zA-Z]+)\.[a-zA-Z0-9]{2,}$/
              )
            ),
            // isNotZero: helpers.withMessage(zeroNumber, (value) => {
            //   const numericValue = Number(value);
            //   return numericValue !== 0;
            // }),
          },

          valueIp: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageType.slug === "ip"
              )
            ),
            isValidValueIp: helpers.withMessage(
              formatMustBeLikeAdresseIP,

              helpers.regex(/^[0-9.]+$/)
            ),
          },
          valueDomainTime: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageTypeDomain.slug === "domain" &&
                  state.formData.time
              )
            ),
            isValidName: helpers.withMessage(
              format,

              helpers.regex(
                /^([a-zA-Z]+\d*|\d+[a-zA-Z]*|\d+|[a-zA-Z]+)\.[a-zA-Z0-9]{2,}$/
              )
            ),
          },
          routageType: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () => modalModeRule.value === "create" && !state.formData.time
              )
            ),
          },
          routageTypeDomain: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () => modalModeRule.value === "create" && state.formData.time
              )
            ),
          },
          prefix: {
            required: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  modalModeRule.value === "create" &&
                  state.formData.routageType.slug === "subnet"
              )
            ),
            isValidPrefix: helpers.withMessage(
              champInclude,

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
      return state.formData.routageType.slug === "ip";
    });
    const isDomains = computed(() => {
      return state.formData.routageType.slug === "domain";
    });
    const isTimeAndDomains = computed(() => {
      return state.formData.routageTypeDomain.slug === "domain";
    });

    const isValidTime = computed(() => {
      if (!state.formData.from || !state.formData.to) {
        return false;
      }

      let from = state.formData.from;
      let to = state.formData.to;

      return from === to || from > to;
    });

    watch(
      () => state.formData.time,
      (newTime) => {
        if (newTime) {
          if (state.formData.value2) {
            state.formData.valueDomainTime = state.formData.value2;
          }
          v$.value.$reset();
          state.formData.routageTypeDomain = {
            name: "domains",
            slug: "domain",
          };
          state.formData.routageType = "";
          state.formData.status = false;
          state.formData.value = "";
          state.formData.value2 = "";
          state.formData.valueIp = "";
          state.formData.prefix = "";
        } else {
          v$.value.$reset();
          state.formData.routageType = { name: "domains", slug: "domain" };
          if (state.formData.valueDomainTime) {
            state.formData.value2 = state.formData.valueDomainTime;
          }

          state.formData.valueDomainTime = "";
          state.formData.days = [];
          state.formData.from = "";
          state.formData.to = "";
        }
      },
      { immediate: true }
    );

    // watch(
    //   state,
    //   () => {
    //     if (state.formData.time) {
    //       v$.value.$reset();
    //       state.formData.routageTypeDomain = {
    //         name: "domains",
    //         slug: "domain",
    //       };
    //       state.formData.routageType = "";
    //       state.formData.status = false;
    //       state.formData.value = "";
    //       state.formData.value2 = "";
    //       state.formData.valueIp = "";
    //       state.formData.prefix = "";
    //     } else {
    //       v$.value.$reset();
    //       state.formData.valueDomainTime = "";
    //       state.formData.days = [];
    //       state.formData.from = "";
    //       state.formData.to = "";
    //     }
    //   },
    //   { immediate: true }
    // );

    watch(
      () => isDomains.value,
      (val) => {
        if (val) {
          state.formData.value = "";
          state.formData.prefix = "";
          state.formData.valueIp = "";
        }
        v$.value.$reset();
      }
    );
    watch(
      () => isSubnet.value,
      (val) => {
        if (val) {
          state.formData.value2 = "";
          state.formData.valueIp = "";
        }
        v$.value.$reset();
      }
    );
    watch(
      () => isIps.value,
      (val) => {
        if (val) {
          state.formData.value2 = "";
          state.formData.prefix = "";
          state.formData.value = "";
        }
        v$.value.$reset();
      }
    );
    watch(
      () => isOpenModal.value,
      (val) => {
        state.openModalRule = val;
        v$.value.$reset();
      }
    );
    watch(
      () => editRowRule.value,
      (val) => {
        populate(val);
      }
    );
    watch(
      () => modalModeRule.value,
      (val) => {
        if (val === "create") {
          state.formData.allodwedAuth = false;
          state.formData.status = false;
          state.formData.days = [];
          state.formData.time = false;
          state.formData.from = "";
          state.formData.to = "";
          state.formData.routageType = "";
          state.formData.routageTypeDomain = "";
          state.formData.value = "";
          state.formData.value2 = "";
          state.formData.valueIp = "";
          state.formData.prefix = "";
          state.formData.valueDomainTime = "";
          state.formData.ruleName = null;
        }
      }
    );

    const populate = (val) => {
      if (modalModeRule.value === "edit") {
        state.rowEdit = val;
        state.formData.status = val.status === "Disable" ? false : true;
        state.formData.allodwedAuth =
          val.allow_by_auth === "Disable" ? false : true;
        state.formData.ruleName = val?.rule_name;

        let filtredRoutage = routagType.value.filter(
          (i) => i.slug === val?.type
        );

        state.formData.routageType = filtredRoutage[0];

        if (val?.type === "subnet") {
          let addr = val?.value?.split("/");
          if (addr) {
            state.formData.value = addr[0];
            state.formData.prefix = +addr[1];
          }
        } else if (val?.type === "ip") {
          state.formData.valueIp = val?.value;
        } else if (val?.type === "domain" && val?.time_from === "--") {
          state.formData.value2 = val?.value;
        } else if (val?.type === "domain" && val?.time_from != "--") {
          let filtredR = routagTypeDomain.value.filter(
            (i) => i.slug === val?.type
          );

          state.formData.routageTypeDomain = filtredR[0];
          state.formData.valueDomainTime = val?.value;
          state.formData.time = val?.time_from ? true : false;
          state.formData.from = val?.time_from.substring(0, 5);
          state.formData.to = val?.time_to.substring(0, 5);

          let letters = val?.days?.split("");

          if (letters) {
            let array = [];

            letters.forEach((i) => {
              array = [
                ...array,
                ...daysArray.value.filter((e) => e.slug === i),
              ];
            });

            state.formData.days = array;
          }
        }
      }
    };

    const closeModal = () => {
      emitter.emit("closeAddRuleModal");
      v$.value.$reset();

      // if (modalModeRule.value === "create") {
      state.formData.days = [];
      state.formData.time = false;
      state.formData.from = null;
      state.formData.to = null;
      state.formData.routageType = "";
      state.formData.routageTypeDomain = "";
      state.formData.value = "";
      state.formData.value2 = "";
      state.formData.valueIp = "";
      state.formData.ruleName = null;
      state.formData.prefix = "";
      // }
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
        // if (isValidTime) return;
        let payload = {};
        if (state.formData.routageType.slug == "subnet") {
          payload = {
            rule_name: state.formData.ruleName,
            type: state.formData.routageType.slug,
            value: `${state.formData.value}/${state.formData.prefix}`,
            status: state.formData.status,
            allow_by_auth: state.formData.allodwedAuth,
          };
        }
        if (state.formData.routageType.slug == "ip") {
          payload = {
            rule_name: state.formData.ruleName,
            type: state.formData.routageType.slug,
            value: state.formData.valueIp,
            status: state.formData.status,
            allow_by_auth: state.formData.allodwedAuth,
          };
        }
        if (state.formData.routageType.slug == "domain") {
          payload = {
            rule_name: state.formData.ruleName,
            type: state.formData.routageType?.slug,
            value: state.formData.value2,
            status: state.formData.status,
            allow_by_auth: state.formData.allodwedAuth,
            days: "",
            time_from: "",
            time_to: "",
          };
        }

        if (state.formData.routageTypeDomain.slug == "domain") {
          let from = state.formData.from;
          let to = state.formData.to;

          // let from = dayjs(state.formData.from).format("HH:mm");
          // let to = dayjs(state.formData.to).format("HH:mm");

          let mappedDays = state.formData.days.map((e) => e.slug);
          let resultString = mappedDays.join("");

          payload = {
            rule_name: state.formData.ruleName,
            type: state.formData.routageTypeDomain.slug,
            value: state.formData.valueDomainTime,
            status: true,
            allow_by_auth: state.formData.allodwedAuth,
            days: resultString,
            time_from: from,
            time_to: to,
          };
        }

        payload = { ...payload, user_id: id };
        if (modalModeRule.value === "edit") {
          // let payload = {
          //   status: state.formData.status,
          //   allow_by_auth: state.formData.allodwedAuth,
          // };

          axios
            .put(`/proxy/updateRuleSquid/${state.rowEdit.id}`, payload)
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
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

                if (i.response.data?.error) {
                  state.textAlert = i.response.data.error;
                } else {
                  const errorData = i.response.data;
                  const allErrors = [];

                  for (const key in errorData) {
                    if (Array.isArray(errorData[key])) {
                      allErrors.push(`${errorData[key].join(", ")}`);
                    }
                  }

                  state.textAlert = allErrors.join(" | ");
                }
              }
            });
        } else {
          axios
            .post("/proxy/addRuleSquid", payload)
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
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

                // if (i.response?.data?.days) {
                //   const daysError = i.response.data.days.join(", ");
                //   state.textAlert = daysError;
                // } else {
                // state.textAlert = i.response.data.error;
                // }
                if (i.response.data?.error) {
                  state.textAlert = i.response.data.error;
                } else {
                  const errorData = i.response.data;
                  const allErrors = [];

                  for (const key in errorData) {
                    if (Array.isArray(errorData[key])) {
                      allErrors.push(`${errorData[key].join(", ")}`);
                    }
                  }

                  state.textAlert = allErrors.join(" | ");
                }
              }
            });
        }
      } else {
        console.log("error :", v$.value);
      }
    };

    return {
      state,
      numberList,
      v$,
      isDomains,
      isTimeAndDomains,
      isSubnet,
      isIps,
      routagType,
      routagTypeDomain,
      emitter,
      isValidTime,
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
