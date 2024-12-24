<template>
  <v-overlay v-model="state.loading">
    <v-dialog
      v-model="state.isLoadingDialogue"
      :scrim="false"
      persistent
      width="auto"
    >
      <v-card color="#193286">
        <v-card-text>
          {{ $t("sdwan.pleaseWait") }}
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-overlay>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"> {{ $t("ztna.createNewIdentity") }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="date" label="Date" prepend-icon="mdi-calendar" type="date" :rules="dateRules"

                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field v-model="time" label="Time" prepend-icon="mdi-clock" type="time"  :rules="timeRules"
                    class="ml-1"></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="indigo-darken-3" :rounded="true" large rounded outlined label-color="#213E9F" variant="flat"
              class="mt-3 btn-add" text @click="cancel"><span class="text-white pr-3 pl-3">
                {{ $t("buttons.close") }}</span
              ></v-btn>
            <VBtn large rounded outlined label-color="#213E9F" color="indigo-darken-3" :rounded="true" variant="flat"
              class="mt-3 ml-2 btn-add" type="submit">
              {{ $t("buttons.create") }}
            </VBtn>
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
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { toRefs, ref, watch, reactive, inject } from "vue";
import { useI18n } from "vue-i18n";


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
    const { t } = useI18n();
    const date = ref(null);
    const time = ref(null);
    const selectedTitle = ref("ott");
    const jwtToken = ref("");
    const showJwtToken = ref(false);
    const EnrollementId = ref("");
    const items = [{ title: "ott" }, { title: "updb" }, { title: "ottca" }];
    const rules = [(value) => !!value || t("ztna.enterValue")];

    const emitter = inject("emitter");

    const { isOpen, selectedId } = toRefs(props);

    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      openModal: false,
      itemId: null,
      snackbar: false,
      color: null,
      textAlert: ""
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
        console.log('valeur',val);
        state.itemId = val;
      }
    );

    const timeRules = [
  (value) => !!value || t("ztna.enterTime"),
  (value) => {
    if (!value) return true;

    const currentDate = new Date();
    const enteredDate = new Date(date.value);

    const enteredTimeParts = value.split(":");
    if (enteredTimeParts.length !== 2 || isNaN(enteredTimeParts[0]) || isNaN(enteredTimeParts[1])) {
      return t("ztna.timeformat"); // Invalid time format
    }

    const enteredHour = parseInt(enteredTimeParts[0]);
    const enteredMinute = parseInt(enteredTimeParts[1]);

    if (enteredHour < 0 || enteredHour > 23 || enteredMinute < 0 || enteredMinute > 59) {
      return t("ztna.timeformat"); // Ensure valid hour and minute range
    }

    // Compare dates and times
    currentDate.setHours(0, 0, 0, 0);
    enteredDate.setHours(0, 0, 0, 0);

    if (enteredDate > currentDate) {
      return true; // Future date is valid
    }

    if (enteredDate.getTime() === currentDate.getTime()) {
      const currentTime = new Date();
      const enteredTime = new Date();
      enteredTime.setHours(enteredHour, enteredMinute, 0, 0);

      if (enteredTime <= currentTime) {
        return t("ztna.timeCheck"); // Time is in the past for the same day
      }
    }

    return true; // Valid time
  },
];


const dateRules = [
  (value) => !!value || t("ztna.enterDate"),
  (value) => {
    if (!value) return true;

    const currentDate = new Date();
    const enteredDate = new Date(value);

    if (isNaN(enteredDate.getTime())) {
      return t("ztna.dateformat"); // Invalid date format
    }

    currentDate.setHours(0, 0, 0, 0);
    enteredDate.setHours(0, 0, 0, 0);

    if (enteredDate < currentDate) {
      return t("ztna.dateCheck"); // Date is in the past
    }

    return true; // Valid date
  },
];




    const submitForm = async () => {
      const isDateValid = dateRules.every((rule) => rule(date.value) === true);
      const isTimeValid = timeRules.every((rule) => rule(time.value) === true);
      if(isTimeValid && isDateValid){
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      let dateTime = `${date.value}T${time.value}:00Z`;
      state.loading = true;
      state.isLoadingDialogue = true;

      let payload = {
        expiresAt: dateTime,
        method: "ott",
        identityId: state.itemId
      }
      axios
        .post("/ztna/add_enrollments", payload, {
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
            if (i.response.status === 500) {
              state.loading = false;
      state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.loading = false;
      state.isLoadingDialogue = false;
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            }
          });} else {
      state.snackbar = true;
              state.color = "red";
              state.textAlert = t("ztna.missingFields");
      }
    };

    const selectItem = (item) => {
      selectedTitle.value = item.title;
    };

    const cancel = () => {
      emitter.emit("closeEnrollmentModal");
    };

    return {
      state,
      cancel,
      emitter,
      rules,
      submitForm,
      selectedTitle,
      selectItem,
      items,
      date,
      time,
      jwtToken,
      showJwtToken,
      timeRules,
      dateRules,
      EnrollementId,
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

.v-application--is-ltr .v-menu__content {
  display: flex;
  justify-content: center;
  left: 50% !important;
  transform: translateX(-50%) !important;
}
</style>
