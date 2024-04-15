<template>
  <v-row justify="center">
    <!-- <v-dialog v-model="isOpen" persistent width="600">
       -->
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create" ? $t("modal.create") : $t("modal.update")
              }}
              {{ $t("agGrid.user") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- User Modal -->

                <v-col cols="12" class="mb-n5">
                  <v-text-field
                    :label="$t('form.username')"
                    v-model="state.formData.username"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.username.$error"
                    >{{ v$.formData.username.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="6" v-if="mode == 'create'" class="mb-n5">
                  <v-text-field
                    :label="$t('form.password')"
                    type="password"
                    v-model="state.formData.password"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.password.$error"
                    >{{ v$.formData.password.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="6" v-if="mode == 'create'" class="mb-n5">
                  <v-text-field
                    :label="$t('form.confirmPassword')"
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

                <v-col cols="12" class="mb-n5">
                  <v-text-field
                    :label="$t('form.fullname')"
                    v-model="state.formData.fullname"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.fullname.$error"
                    >{{ v$.formData.fullname.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" class="mb-n5">
                  <v-text-field
                    :label="$t('form.emailForLdapAuth')"
                    v-model="state.formData.email"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.email.$error"
                    >{{ v$.formData.email.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" class="mt-5">
                  <label for="Activate" class="mr-3">{{$t("ldap.ActivateLdap")}}</label>
                  <input
                    type="checkbox"
                    id="Activate"
                    v-model="state.formData.activateStatus"
                  />
                </v-col>
                <template v-if="state.formData.activateStatus">
                  <v-col cols="12" class="mb-n5">
                    <v-select
                      v-model="state.formData.dnValue"
                      :label="$t('form.server')"
                      item-title="name"
                      item-value="id"
                      return-object
                      :items="state.formData.mapedServer"
                    ></v-select>
                    <span
                      class="error-feedback"
                      v-if="v$.formData.dnValue.$error"
                      >{{ v$.formData.dnValue.$errors[0].$message }}</span
                    >
                  </v-col>
                  <v-col cols="12" class="mb-n5">
                    <v-text-field
                      :label="$t('form.password')"
                      v-model="state.formData.passwordDN"
                      :append-inner-icon="
                        state.show1 ? 'mdi-eye' : 'mdi-eye-off'
                      "
                      prepend-inner-icon="mdi-lock-outline"
                      :type="state.show1 ? 'text' : 'password'"
                      @click:append-inner="state.show1 = !state.show1"
                    ></v-text-field>
                    <span
                      class="error-feedback"
                      v-if="v$.formData.passwordDN.$error"
                      >{{ v$.formData.passwordDN.$errors[0].$message }}</span
                    >
                  </v-col>
                </template>

                <v-col cols="12" class="mb-n5">
                  <v-autocomplete
                    :items="['root', 'admin', 'user']"
                    :label="$t('form.roleUser')"
                    v-model="state.formData.role"
                  ></v-autocomplete>
                  <span class="error-feedback" v-if="v$.formData.role.$error">{{
                    v$.formData.role.$errors[0].$message
                  }}</span>
                </v-col>

                <v-col cols="12" class="mb-n5">
                  <v-autocomplete
                    :items="groups"
                    :label="$t('form.assignToGroup')"
                    multiple
                    item-title="groupname"
                    item-value="id"
                    v-model="state.formData.groups"
                    @change="handleGroupChange"
                    return-object
                  ></v-autocomplete>
                </v-col>

                <v-col cols="12" class="mt-5">
                  <label for="Deactivate User" class="mr-3">{{
                    $t("form.desactivateUser")
                  }}</label>
                  <input
                    type="checkbox"
                    id="Deactivate User"
                    v-model="state.formData.deactivateUser"
                  />
                </v-col>
                <!-- User Modal -->
              </v-row>
            </v-container>
            <!-- <small>*indicates required field</small> -->
          </v-card-text>
          <v-card-actions>
            <span></span>
            <v-spacer></v-spacer>
            <v-btn
              type="submit"
              color="asguard_primary_light"
              :rounded="true"
              class="mt-3 btn-add"
            >
              <span class="text-white">{{ $t("buttons.save") }}</span>
            </v-btn>

            <v-btn
              color="asguard_primary_light"
              :rounded="true"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="text-white">{{ $t("buttons.close") }}</span>
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
import axios from "axios";
import useValidate from "@vuelidate/core";
import {
  required,
  email,
  sameAs,
  helpers,
  requiredIf,
} from "@vuelidate/validators";
import { reactive, computed, onMounted, watch } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";
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
    const state = reactive({
      formData: {
        mapedServer: [],
        activateStatus: false,
        dnValue: "",
        passwordDN: "",
        username: "",
        password: "",
        confirm_password: "",
        fullname: "",
        email: "",
        role: null,
        groups: null,
        deactivateUser: true,
      },
      show1: "",
      userRole: null,
      userId: null,
      ModalMode: null,
    });

    const { t } = useI18n();
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const invalidPassword = computed(() => {
      return t("errors.invalidPassword");
    });
    const passwordConfirmation = computed(() => {
      return t("errors.passwordConfirmation");
    });

    onMounted(() => {
      getAdList();
    });
    watch(
      () => state.formData.activateStatus,
      (val) => {
        if (!val) {
          state.formData.dnValue = "";
          state.formData.passwordDN = "";
        }
      }
    );
    const getAdList = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/ldap/getAllldap_Servers").then(
        (response) => {
          const parsedArray = JSON.parse(response.data);

          let serverAd = parsedArray.map((i) => {
            return {
              id: i.id,
              name: i.server_name,
            };
          });

          state.formData.mapedServer = serverAd;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const rules = computed(() => {
      return {
        formData: {
          username: { required: helpers.withMessage(error, required) },
          password: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.ModalMode == "create")
            ),
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
            ),
            requiredIf: helpers.withMessage(
              error,
              requiredIf(() => state.ModalMode == "create")
            ),

            isValidPassword: helpers.withMessage(
              invalidPassword,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
              )
            ),
          },

          email: { required: helpers.withMessage(error, required), email },
          fullname: { required: helpers.withMessage(error, required) },
          role: { required: helpers.withMessage(error, required) },

          dnValue: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.activateStatus)
            ),
          },
          passwordDN: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.activateStatus)
            ),
          },
        },
      };
    });

    const v$ = useValidate(rules, state);
    return {
      t,
      state,
      v$,
    };
  },

  data() {
    return {
      openModal: false,
      textAlert: "",
      color: "",
      snackbar: false,
      userId: null,
    };
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
        this.state.ModalMode = "create";
      }
    },
  },

  methods: {
    populate(data) {
      if (this.mode == "update") {
        console.log("data", data);
        this.state.formData.username = data.username;
        this.state.formData.fullname = data.fullname;
        this.state.formData.email = data.email;
        this.state.formData.role = data.role;
        let groupsIds = data.group.map((i) => {
          return {
            id: i.id,
            groupname: i.name,
          };
        });
        this.state.formData.groups = groupsIds;

        this.state.formData.deactivateUser = data.is_active;
        this.userId = data.id;
        this.state.userId = data.id;

        let filtredAD = this.state.formData.mapedServer.filter(
          (i) => i.id === data?.id_server
        );
        this.state.formData.dnValue = filtredAD[0];

        this.state.formData.activateStatus = filtredAD[0] ? true : false;
        // this.state.formData.passwordDN = data.password_ad;

        console.log(
          "state.formData.mapedServer",
          this.state.formData.mapedServer
        );
      }
    },
    handleGroupChange(selectedItems) {
      console.log("Selected Groups:", JSON.stringify(selectedItems));
      console.log(
        "formData Groups:",
        JSON.stringify(this.state.formData.groups)
      );
    },

    closeModal() {
      this.$emit("closeModal");
    },
    resetForm() {
      (this.state.formData.username = ""),
        (this.state.formData.password = ""),
        (this.state.formData.fullname = ""),
        (this.state.formData.email = ""),
        (this.state.formData.role = null),
        (this.state.formData.groups = null),
        (this.state.formData.deactivateUser = true);
    },
    getCookie(name) {
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
    },
    submitForm() {
      this.v$.$validate();
      if (!this.v$.$error) {
        let groupsIds = this.state.formData?.groups?.map((i) => {
          return i.id;
        });
        console.log({ "this.state.formData": this.state.formData });
        const payload = {
          username: this.state.formData.username,
          password: this.state.formData.password,
          fullname: this.state.formData.fullname,
          email: this.state.formData.email,
          role: this.state.formData.role,
          group: groupsIds ?? [],
          is_active: this.state.formData.deactivateUser,
          password_ad: this.state.formData.passwordDN,
          id_server: this.state.formData.dnValue?.id,
          // username: "testtest1525dzada4",
          // password: "azerty",
          // fullname: "sousqdqshail",
          // email: "souhail@gmail.com",
          // role: "admin",
          // group: [67],
          // is_active: true
        };
        console.log({ payload });

        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        if (this.mode == "create") {
          axios
            .post("/users/createUser", payload)
            .then((response) => {
              if (response.status == "201") {
                this.closeModal();

                this.snackbar = true;
                this.color = "success";
                this.textAlert = response.data.msg;

                setTimeout(() => {
                  location.reload();
                }, 1000);

                // this.textAlert = "user Created Successfully";
                // setTimeout(() => {
                //   this.closeModal();
                //   location.reload();
                // }, 2000);
              }
            })
            .catch((i) => {
              console.log("i.response.data", i.response);
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.msg;
            });
        } else {
          let groupsIds = this.state.formData?.groups?.map((i) => {
            return i.id;
          });
          let payload2 = {
            username: this.state.formData.username,
            password: this.state.formData.password,
            fullname: this.state.formData.fullname,
            email: this.state.formData.email,
            role: this.state.formData.role,
            group: groupsIds ?? [],
            is_active: this.state.formData.deactivateUser,
            password_ad: this.state.formData.passwordDN ?? "",
            id_server: this.state.formData.dnValue?.id ?? "",
          };
          console.log("payload2", payload2);
          axios
            .put(`/users/modifyUser/${this.userId}`, payload2)
            .then((response) => {
              console.log("resUpdate", response);
              if (response.status == 200) {
                this.closeModal();

                this.snackbar = true;
                this.color = "success";
                this.textAlert = response.data.msg;

                setTimeout(() => {
                  location.reload();
                }, 1000);
                // this.textAlert = "User updated succesfully";
                // setTimeout(() => {
                //   this.closeModal();
                //   location.reload();
                // }, 2000);
              }
            })
            .catch((i) => {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.error;
            });
        }
      }
    },
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
  display: flex;
}
.scroller {
  overflow: auto;
}
</style>
