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
              <h4 class="mb-3">Available Range : {{ initialRanges }}</h4>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('dhcpV4.rangeFrom')"
                    v-model="state.rangeFrom"
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
                    v-model="state.rangeTo"
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

            <v-btn
              large
              rounded
              outlined
              :disabled="!computedTestRange"
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
import axios from "axios";
import useValidate from "@vuelidate/core";
import { toRefs, ref, watch, onMounted, reactive, computed, inject } from "vue";
import { required, helpers, requiredIf } from "@vuelidate/validators";
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
      emitter.on("id-range", (id) => {
        console.log("id", id);
        state.confId = id;
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
        state.rangeFrom = data.range_from;
        state.rangeTo = data.range_to;
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
        console.log("Both ranges are valid.");
        isValidRange = true;
      } else {
        console.log("Invalid range input.");
        isValidRange = false;
      }
      return isValidRange;
    });

    const submitForm = async () => {
      const result = await v$.value.$validate();
      if (result) {
        let payload = {
          idConf: state.confId,
          uuid: modalMode.value === "create" ? uuidv4() : state.editValue,
          range_from: state.rangeFrom,
          range_to: state.rangeTo,
        };

        if (modalMode.value === "create") {
          emitter.emit("add-range", payload);
        }

        if (modalMode.value === "edit") {
          emitter.emit("edit-range", payload);
        }

        closeModal();
        v$.value.$reset();
      } else {
        console.log("v$", v$.value);
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
    const formatMustBeLikeAdresseIP = computed(() => {
      return t("errors.formatMustBeLikeAdresseIP");
    });
    const rules = computed(() => {
      return {
        rangeFrom: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => modalMode.value === "create")
          ),
          isValidlRangeFrom: helpers.withMessage(
            formatMustBeLikeAdresseIP,

            helpers.regex(
              /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            )
          ),
        },
        rangeTo: {
          requiredIfFuction: helpers.withMessage(
            error,
            requiredIf(() => modalMode.value === "create")
          ),
          isValidlRangeTo: helpers.withMessage(
            formatMustBeLikeAdresseIP,

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
