<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5" v-if="modalMode === 'create'">
              {{ $t("squid.createNewProxyUser") }}</span
            >
            <span class="text-h5" v-if="modalMode === 'edit'">
              {{ $t("squid.editUserProxy") }}
            </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Email *"
                    v-model="state.formData.email"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.email.$error"
                  >
                    {{ v$.formData.email.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="`${$t('form.username')} *`"
                    v-model="state.formData.userName"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.userName.$error"
                  >
                    {{ v$.formData.userName.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    :label="`${$t('form.password')} *`"
                    type="password"
                    v-model="state.formData.password"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.password.$error"
                  >
                    {{ v$.formData.password.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    :label="`${$t('form.confirmPassword')} *`"
                    type="password"
                    v-model="state.formData.confirm_password"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.confirm_password.$error"
                  >
                    {{ v$.formData.confirm_password.$errors[0].$message }}
                  </p>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="mt-3 actionBtn">
            <div class="text-start ml-6 mt-3">
              <span class="text-sm">
                <span class="text-red text-lg">*</span>
                {{ $t("errors.oblig") }}</span
              >
            </div>
            <v-spacer></v-spacer>
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
      :timeout="3000"
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
import {
  sameAs,
  helpers,
  requiredIf,
  email,
  required,
} from "@vuelidate/validators";
import { reactive, computed, toRefs, watch, inject } from "vue";
import VButton from "@/components/VButton.vue";
import { id } from "@/mixins/storage_language.js";

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
    const { t } = useI18n();
    const { isOpen, editRow, modalMode } = toRefs(props);
    const emitter = inject("emitter");
    const state = reactive({
      formData: {
        email: "",
        password: "",
        confirm_password: "",
        userName: null,
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champInclude = computed(() => {
      return t("champs.indication");
    });
    const validAddress = computed(() => {
      return t("champs.validAddress");
    });
    const confirmation = computed(() => {
      return t("errors.passwordConfirmation");
    });

    const rules = computed(() => {
      return {
        formData: {
          password: {
            required: helpers.withMessage(
              error,
              requiredIf(() => modalMode.value === "create")
            ),
          },
          confirm_password: {
            sameAsPassword: helpers.withMessage(
              confirmation,

              sameAs(state.formData.password)
            ), // can be a reference to a field or computed property
            required: helpers.withMessage(
              error,
              requiredIf(() => modalMode.value === "create")
            ),
          },
          userName: {
            required: helpers.withMessage(
              error,
              requiredIf(() => modalMode.value === "create")
            ),
            isValiduserName: helpers.withMessage(
              champInclude,
              helpers.regex(/^[^A-Z\s]+$/)
            ),
          },
          email: {
            required: helpers.withMessage(
              error,
              requiredIf(() => modalMode.value === "create")
            ),
            email: helpers.withMessage(validAddress, email),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(
      () => isOpen.value,
      (val) => {
        state.openModal = val;
        v$.value.$reset();
      }
    );
    watch(
      () => editRow.value,
      (val) => {}
    );
    watch(
      () => modalMode.value,
      (val) => {}
    );
    const closeModal = () => {
      emitter.emit("closeSquidUserModal");
      reset();
    };
    const reset = () => {
      state.formData.email = "";
      state.formData.password = "";
      state.formData.confirm_password = "";
      state.formData.userName = null;
      state.openModal = false;
      state.textAlert = "";
      state.color = "";
      state.snackbar = false;
      v$.value.$reset();
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

        let payload = {
          email: state.formData.email,
          username: state.formData.userName,
          password: state.formData.password,
          user_id: id,
        };

        axios
          .post("/proxy/add_user_squid", payload)
          .then((response) => {
            if (response.status == "200") {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                reset();
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
              state.textAlert = i.response.data.error;
            }
          });
      } else {
        console.log("error :", v$.value);
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
