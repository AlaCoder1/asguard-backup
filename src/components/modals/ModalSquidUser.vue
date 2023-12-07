<template>
  <v-row justify="center">
    <v-dialog v-model="state.openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                modalMode === "create"
                  ? "Create New Proxy User"
                  : "Edit User Proxy "
              }}
            </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Username"
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
                    label="Password"
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
                    label="Confirm password"
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
              type="submit"
              color="indigo-darken-3"
              :rounded="true"
              variant="flat"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                modalMode === "create" ? "Create" : "Edit"
              }}</span>
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
import useValidate from "@vuelidate/core";
import { required, sameAs, helpers } from "@vuelidate/validators";
import { reactive, computed, toRefs, watch } from "vue";
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
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
        userName: null,
      },
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rules = computed(() => {
      return {
        formData: {
          password: {
            required: helpers.withMessage("Value is required", required),
            isValidPassword: helpers.withMessage(
              `There must be at least 20 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
              )
            ),
          },
          confirm_password: {
            sameAsPassword: helpers.withMessage(
              "Your password does not match",

              sameAs(state.formData.password)
            ), // can be a reference to a field or computed property
            required: helpers.withMessage("Value is required", required),

            isValidPassword: helpers.withMessage(
              `There must be at least 20 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
              )
            ),
          },
          userName: { required },
        },
      };
    });

    const v$ = useValidate(rules, state);

    watch(
      () => isOpen.value,
      () => {
        state.openModal = true;
      }
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
    const closeModal = () => {
      state.openModal = false;
      setTimeout(() => {
        location.reload();
      }, 1000);
    };

    return {
      state,
      v$,
      closeModal,
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
