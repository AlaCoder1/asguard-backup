<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" style="overflow: auto">
        <v-card>
          <v-card-title>
            <span class="headline" v-if="modalMode === 'create'">
              {{ $t("dhcpV4.addRange") }}
            </span>
            <span class="headline" v-if="modalMode === 'edit'">
              {{ $t("dhcpV4.editRange") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <h4 class="mb-3">
                {{ $t("availableRange") }} : {{ initialRanges }}
              </h4>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('dhcpV4.rangeFrom')"
                    v-model.trim="state.rangeFrom"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.rangeFrom.$errors.length"
                  >
                    {{ v$.rangeFrom.$errors?.[0].$message }}
                  </p>
                  <p
                    class="error-feedback mb-5"
                    v-if="state.messageRangeFrom && state.rangeFrom"
                  >
                    {{ state.messageRangeFrom }}
                  </p>
                </v-col>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('dhcpV4.rangeTo')"
                    v-model.trim="state.rangeTo"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.rangeTo.$errors.length"
                  >
                    {{ v$.rangeTo.$errors?.[0].$message }}
                  </p>
                  <p
                    class="error-feedback mb-5"
                    v-if="state.messageRangeTo && state.rangeTo"
                  >
                    {{ state.messageRangeTo }}
                  </p>
                  <p
                    class="error-feedback mb-5"
                    v-if="state.rangeFrom && state.rangeTo && egoRange"
                  >
                    {{ $t("plageAddresse") }}
                  </p>
                  <p class="error-feedback mb-5" v-if="state.error">
                    {{ state.error }}
                  </p>
                  <p class="error-feedback mb-5" v-if="state.exist_plage_from">
                    {{ state.exist_plage_from }}
                  </p>
                  <p class="error-feedback mb-5" v-if="state.exist_plage_to">
                    {{ state.exist_plage_to }}
                  </p>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <v-btn
              color="indigo-darken-3"
              :rounded="true"
              large
              rounded
              outlined
              label-color="#213E9F"
              variant="outlined"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3">{{ $t("buttons.close") }}</span>
            </v-btn>
            <!-- :disabled="!computedTestRange || egoRange || same_edit" -->

            <v-btn
              large
              rounded
              outlined
              :disabled="!computedTestRange || egoRange || same_edit"
              label-color="#213E9F"
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
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
import useValidate from "@vuelidate/core";
import { toRefs, watch, onMounted, reactive, computed, inject } from "vue";
import { helpers, requiredIf } from "@vuelidate/validators";
import { v4 as uuidv4 } from "uuid";

export default {
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    editRow: {
      type: Object,
      Array,
      required: false,
    },
    modalMode: {
      type: String,
      required: true,
    },
    initialRanges: {
      type: String,
      required: true,
    },
  },

  setup(props) {
    const emitter = inject("emitter");
    const { t } = useI18n();
    onMounted(() => {
      emitter.on("id-range", (data) => {
        state.confId = data.id;
        state.ranges = data.range;
      });

      let ranges = initialRanges.value.split("-").map((part) => part.trim());

      state.initialFrom = ranges[0];
      state.initialTo = ranges[1];
    });

    const { isOpen, editRow, modalMode, initialRanges } = toRefs(props);

    const state = reactive({
      rangeTo: "",
      rangeFrom: "",
      editValue: null,
      confId: null,
      initialFrom: null,
      initialTo: null,
      messageRangeFrom: null,
      messageRangeTo: null,
      error: null,
      ranges: [],
      is_same: false,
      exist_plage_from: "",
      exist_plage_to: "",
      currentRow: null,
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

    const populate = (data) => {
      if (modalMode.value === "edit") {
        state.editValue = data.uuid;
        state.rangeFrom = data.range_from.trim();
        state.rangeTo = data.range_to.trim();
        state.currentRow = data;
      }
    };

    watch(
      () => modalMode.value,
      (val) => {
        if (val === "create") {
          v$.value.$reset();
          state.rangeTo = "";
          state.rangeFrom = "";
        }
      }
    );

    function ipToNumber(ip) {
      return ip
        .split(".")
        .reduce((acc, octet) => (acc << 8) | parseInt(octet, 10), 0);
    }

    function isIpInRange(ip, start, end) {
      const ipNum = ipToNumber(ip);
      const startNum = ipToNumber(start);
      const endNum = ipToNumber(end);
      return ipNum >= startNum && ipNum <= endNum;
    }

    function validateRange(inputFrom, inputTo) {
      const isFromValid = isIpInRange(
        inputFrom,
        state.initialFrom,
        state.initialTo
      );
      const isToValid = isIpInRange(
        inputTo,
        state.initialFrom,
        state.initialTo
      );

      if (!isFromValid) {
        state.messageRangeFrom = `${t("rangeFrom")} ${inputFrom} ${t(
          "outBounds"
        )}`;
      } else {
        state.messageRangeFrom = null;
      }
      if (!isToValid) {
        state.messageRangeTo = `${t("rangeFrom")} ${inputTo} ${t("outBounds")}`;
      } else {
        state.messageRangeTo = null;
      }

      return isFromValid && isToValid;
    }

    const computedTestRange = computed(() => {
      let isValidRange = false;
      if (validateRange(state.rangeFrom, state.rangeTo)) {
        isValidRange = true;
      } else {
        isValidRange = false;
      }
      return isValidRange;
    });

    const egoRange = computed(() => {
      let is_egoRange = false;
      if (state.rangeFrom === state.rangeTo) is_egoRange = true;
      else is_egoRange = false;

      return is_egoRange;
    });

    const same_edit = computed(() => {
      if (modalMode.value === "edit") {
        // const matching = state.ranges.find((a) => a.uuid === state.editValue);
        if (
          state.currentRow.range_from.trim() === state.rangeFrom &&
          state.currentRow.range_to.trim() === state.rangeTo
        ) {
          return true;
        } else return false;
      }
    });

    const verifierPlageExistante = (new_plage, ranges) => {
      const { rangeFrom, rangeTo } = new_plage;

      const matchingRange = ranges.find(
        (plage) =>
          plage.range_from.trim() === rangeFrom ||
          plage.range_to.trim() === rangeTo
      );

      if (matchingRange) {
        if (matchingRange.range_from.trim() === rangeFrom) {
          state.exist_plage_from = `${t("dhcpV4.range")} '${rangeFrom}' ${t(
            "dhcpV4.exist"
          )}`;
          setTimeout(() => {
            state.exist_plage_from = "";
          }, 2000);
          return true;
        } else if (matchingRange.range_to.trim() === rangeTo) {
          state.exist_plage_to = `${t("dhcpV4.range")} '${rangeTo}' ${t(
            "dhcpV4.exist"
          )}`;
          setTimeout(() => {
            state.exist_plage_to = "";
          }, 2000);
          return true;
        } else {
          return false;
        }
      }

      // const existe = ranges.some(
      //   (plage) => plage.range_from === rangeFrom || plage.range_to === rangeTo
      // );
      // if (existe) {
      //   return true;
      // } else {
      //   return false;
      // }
    };

    // const verifierPlageExistante = computed(() => {
    //   // const { rangeFrom, rangeTo } = new_plage;
    //   let matchingRange = null;

    //   if (state.ranges && state.rangeTo) {
    //     matchingRange = state.ranges.find(
    //       (plage) =>
    //         plage.rangeFrom === state.rangeFrom ||
    //         plage.range_to === state.rangeTo
    //     );
    //   }

    //   if (matchingRange) {
    //     if (matchingRange.range_from === state.rangeFrom) {
    //       state.exist_plage_from = `${t("dhcpV4.range")} '${
    //         state.rangeFrom
    //       }' ${t("dhcpV4.exist")}`;
    //       // setTimeout(() => {
    //       //   state.exist_plage_from = "";
    //       // }, 2000);
    //       // return true;
    //     } else if (matchingRange.range_to === state.rangeTo) {
    //       state.exist_plage_to = `${t("dhcpV4.range")} '${state.rangeTo}' ${t(
    //         "dhcpV4.exist"
    //       )}`;
    //       // setTimeout(() => {
    //       //   state.exist_plage_to = "";
    //       // }, 2000);
    //       return true;
    //     } else {
    //       return false;
    //     }
    //   }
    // });
    const submitForm = async () => {
      const result = await v$.value.$validate();
      if (result) {
        const numeroOne = ipToNumber(state.rangeFrom);
        const numeroTwo = ipToNumber(state.rangeTo);

        if (numeroOne > numeroTwo) {
          state.error = t("mustBe");

          setTimeout(() => {
            state.error = "";
          }, 2000);
          return;
        }

        //

        const nouvellePlage = {
          rangeFrom: state.rangeFrom,
          rangeTo: state.rangeTo,
        };

        let payload = {
          idConf: state.confId,
          uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
          range_from: state.rangeFrom,
          range_to: state.rangeTo,
        };

        if (modalMode.value === "create") {
          const verification = verifierPlageExistante(
            nouvellePlage,
            state.ranges
          );
          if (verification) return;

          emitter.emit("add-range", payload);
        }

        if (modalMode.value === "edit") {
          let filtredList = state.ranges.filter(
            (e) => e.uuid !== state.editValue
          );
          const verification = verifierPlageExistante(
            nouvellePlage,
            filtredList
          );
          if (verification) return;

          emitter.emit("edit-range", payload);
        }

        closeModal();
        v$.value.$reset();
      } else {
        console.log("error :", v$.value);
      }
    };

    const closeModal = () => {
      emitter.emit("closeModalAddRange");
      state.rangeTo = "";
      state.rangeFrom = "";
    };
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const formatRange = computed(() => {
      return t("errors.formatRange");
    });
    const rules = computed(() => {
      return {
        rangeFrom: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => modalMode.value === "create" || modalMode.value === "edit"
            )
          ),
          isValidlRangeFrom: helpers.withMessage(
            formatRange,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        rangeTo: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(
              () => modalMode.value === "create" || modalMode.value === "edit"
            )
          ),
          isValidlRangeTo: helpers.withMessage(
            formatRange,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
      };
    });

    const v$ = useValidate(rules, state);

    return {
      state,
      emitter,
      v$,
      closeModal,
      submitForm,
      computedTestRange,
      egoRange,
      same_edit,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red !important;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
</style>
