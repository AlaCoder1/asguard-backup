<template>
  <v-row justify="center">
    <!-- <v-dialog v-model="isOpen" persistent width="600"> -->
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ mode }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    label="Password"
                    type="password"
                    v-model="state.formData.password"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.password.$error"
                    >{{ v$.formData.password.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="6">
                  <v-text-field
                    label="Confirm password"
                    type="password"
                    v-model="state.formData.confirm_password"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.confirm_password.$error"
                    >{{
                      v$.formData.confirm_password.$errors[0].$message
                    }}</span
                  >
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <span style="color: green; margin-top: 10px">{{ textAlert }}</span>
            <v-spacer></v-spacer>
            <v-btn
              :rounded="true"
              class="mt-3 btn-add text-white"
              color="blue-darken-1"
              variant="text"
              @click="closeModal"
            >
              <span class="pr-3 pl-3 text-white" style="color: #213e9f">{{
                $t("buttons.close")
              }}</span>
            </v-btn>
            <v-btn
              :rounded="true"
              class="mt-3 btn-add text-white"
              color="blue-darken-1"
              variant="text"
              type="submit"
            >
              <span class="text-white pr-3 pl-3">Save</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
    <v-snackbar
      :timeout="2000"
      v-model="snackbar"
      location="bottom right"
      :color="color"
    >
      {{ textAlert }}
    </v-snackbar>
  </v-row>
</template>

<script>
import { useI18n } from "vue-i18n";
import { mapState } from "pinia";
import { useAuthStore } from "@/store/modules/auth.js";
const storeAuth = useAuthStore();
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, sameAs, helpers } from "@vuelidate/validators";
import { reactive, computed } from "vue";
export default {
  name: "Modal_User",
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    initialData: {
      type: Object,
      required: true,
    },
    editRow: {
      type: Object,
      required: true,
    },
    mode: {
      type: String,
      required: true,
    },
    groups: {
      type: Array,
      required: true,
    },
  },
  setup() {
    const { t } = useI18n();
    //data
    const state = reactive({
      formData: {
        password: "",
        confirm_password: "",
      },
      userRole: null,
      userName: null,
    });

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const invalidPassword = computed(() => {
      return t("errors.invalidPassword");
    });
    const passwordConfirmation = computed(() => {
      return t("errors.passwordConfirmation");
    });

    const rules = computed(() => {
      return {
        formData: {
          password: {
            required: helpers.withMessage(error, required),
            isValidPassword: helpers.withMessage(
              invalidPassword,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
              )
            ),
          },
          confirm_password: {
            sameAsPassword: helpers.withMessage(
              passwordConfirmation,

              sameAs(state.formData.password)
            ), // can be a reference to a field or computed property
            required: helpers.withMessage(error, required),

            isValidPassword: helpers.withMessage(
              invalidPassword,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
              )
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);
    return {
      state,
      v$,
    };
  },
  data() {
    return {
      userId: null,
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
    };
  },
  mounted() {
    // this.state.userRole = this.user.currentUser.role;
  },

  watch: {
    isOpen(val) {
      this.openModal = val;
    },
    editRow(newValue) {
      this.populate(newValue);
    },
    mode(val) {
      if (val == "create") {
        this.resetForm();
      }
    },
  },
  computed: {
    // ...mapState(storeAuth, ["user"]),
  },
  methods: {
    populate(data) {
      if (this.mode == "Reset Password") {
        this.state.formData.password = data.password;
        this.state.userName = data.username;

        this.userId = data.id;
      }
    },

    closeModal() {
      this.$emit("closeModal");
    },
    resetForm() {
      this.state.formData.password = "";
    },
    submitForm() {
      this.v$.$validate();
      if (!this.v$.$error) {
        function getCookie(name) {
          let cookieValue = null;
          if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                  cookie.substring(name.length + 1)
                );
                break;
              }
            }
          }
          return cookieValue;
        }
        const params = {
          new_password: this.state.formData.password,
          confirm_password: this.state.formData.confirm_password,
        };

        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        axios
          .put(`/users/userChangePW/${this.userId}`, params)
          .then((response) => {
            if (response.status == 200) {
              this.closeModal();

              this.snackbar = true;
              this.color = "success";
              this.textAlert = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            if (i.response.status === 500) {
               this.snackbar = true;
               this.color = "red";
               this.textAlert = this.$t("errors.errorServer");
            } else {
               this.snackbar = true;
               this.color = "red";
               this.textAlert = i.response.data.error;
            }
          });
      }
    },
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
