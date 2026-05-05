<template>
  <v-row justify="center">
    <!-- <v-dialog v-model="isOpen" persistent width="600">
       -->
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
                    :label="`${$t('form.username')} *`"
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
                    :label="`${$t('form.password')} *`"
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
                    :label="`${$t('form.confirmPassword')} *`"
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
                    :label="`${$t('form.fullname')} *`"
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
                    :label="`${$t('form.emailForLdapAuth')} *`"
                    v-model="state.formData.email"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.email.$error"
                    >{{ v$.formData.email.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" class="mt-5">
                  <label for="Activate" class="mr-3">{{
                    $t("ldap.ActivateLdap")
                  }}</label>
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
                      :label="`${$t('form.server')} *`"
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
                      :label="`${$t('form.password')} *`"
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
                    :label="`${$t('form.roleUser')} *`"
                    v-model="state.formData.role"
                    item-title="name"
                    item-value="id"
                    :items="state.userRoles"
                    return-object
                  ></v-autocomplete>
                  <span class="error-feedback" v-if="v$.formData.role.$error">{{
                    v$.formData.role.$errors[0].$message
                  }}</span>
                </v-col>

                <v-col cols="12" class="mb-n5">
                  <v-autocomplete
                    v-model="state.formData.groups"
                    :items="groups"
                    :label="$t('form.assignToGroup')"
                    multiple
                    item-title="groupname"
                    item-value="id"
                    clearable
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
            <div class="text-start ml-6 mt-3">
              <span class="text-sm">
                <span class="text-red text-lg">*</span>
                {{ $t("errors.oblig") }}</span
              >
            </div>
            <v-spacer></v-spacer>

            <v-btn
              color="asguard_primary_light"
              :rounded="true"
              @click="closeModal"
              class="mt-3 btn-add"
            >
              <span class="pr-3 pl-3 text-white" style="color: #213e9f">{{
                $t("buttons.close")
              }}</span>
            </v-btn>
            <v-btn
              type="submit"
              color="asguard_primary_light"
              :rounded="true"
              class="mt-3 btn-add"
            >
              <span class="text-white pr-3 pl-3">{{
                mode === "create" ? $t("buttons.create") : $t("buttons.update")
              }}</span>
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
import { reactive, computed, onMounted, watch, ref } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { get_params } from "@/mixins/params.js";

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
      loading: false,
      isLoadingDialogue: false,
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
      userRoles: [],
    });
    const length = ref(0);
    const { t } = useI18n();
    const error = computed(() => {
      return t("errors.valueRequired");
    });

    const passwordConfirmation = computed(() => {
      return t("errors.passwordConfirmation");
    });

    onMounted(async () => {
      const params = await get_params();
      length.value = params?.password_length || 16;

      getAdList();

      let allLisRoles =
        document.getElementById("app").attributes["roles"].value;

      const parsedArray = JSON.parse(allLisRoles);

      state.userRoles = parsedArray;
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

      axios.get("/ldap/getAllldap_Servers").then((response) => {
        const parsedArray = JSON.parse(response.data);

        let serverAd = parsedArray.map((i) => {
          return {
            id: i.id,
            name: i.server_name,
          };
        });

        state.formData.mapedServer = serverAd;
      });
    };
    const champNoInclude = computed(() => {
      return t("errors.ChampNoInclude");
    });

    const invalidPassword = computed(() => {
      return `${t("errors.invalidPassword1")} ${length.value} ${t(
        "errors.invalidPassword"
      )}`;
    });

    const passwordRegex = computed(() => {
      if (!length.value) return /.*/;
      const pattern = `^(?=.*[A-Z])(?=.*[a-z])(?=.*\\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\\]^_\\{|}~])[A-Za-z\\d!"#$%&'()*+,-./:;<=>?@[\\]^_\\{|}~]{${length.value},}$`;
      return new RegExp(pattern);
    });
    const rules = computed(() => {
      return {
        formData: {
          username: {
            required: helpers.withMessage(error, required),
            isValidName: helpers.withMessage(
              champNoInclude,

              helpers.regex(
                /^(?=.*[a-zA-Z])[a-zA-Z0-9-]{1,63}(\.[a-zA-Z0-9-]{1,63})*$/
              )
            ),
          },
          password: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.ModalMode == "create")
            ),
            isValidPassword: helpers.withMessage(
              invalidPassword,

              (value) => passwordRegex.value.test(value)
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

              (value) => passwordRegex.value.test(value)
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
            isValidPassword: helpers.withMessage(
              invalidPassword,

              (value) => {
                if (!value) return true;
                return passwordRegex.value.test(value);
              }
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
        this.state.formData.username = data.username;
        this.state.formData.fullname = data.fullname;
        this.state.formData.email = data.email;

        let filtredRole = this.state.userRoles.filter(
          (i) => i.name === data?.role
        );
        this.state.formData.role = filtredRole[0];

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
      }
    },
    handleGroupChange(selectedItems) {},

    closeModal() {
      this.v$.$reset();
      this.resetForm();
      this.$emit("closeModal");
    },
    resetForm() {
      this.state.formData.username = "";
      this.state.formData.password = "";
      this.state.formData.confirm_password = "";
      this.state.formData.fullname = "";
      this.state.formData.email = "";
      this.state.formData.role = null;
      this.state.formData.groups = null;
      this.state.formData.deactivateUser = true;
      (this.state.formData.activateStatus = false),
        (this.state.formData.dnValue = "");
      this.state.formData.passwordDN = "";
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
        const payload = {
          username: this.state.formData.username,
          password: this.state.formData.password,
          fullname: this.state.formData.fullname,
          email: this.state.formData.email,
          role: this.state.formData.role.id,
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

        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        this.state.loading = true;
        this.state.isLoadingDialogue = true;

        if (this.mode == "create") {
          axios
            .post("/users/createUser", payload)
            .then((response) => {
              if (response.status == "201") {
                this.closeModal();

                this.snackbar = true;
                this.color = "success";
                this.textAlert = response.data.msg;

                this.state.loading = false;
                this.state.isLoadingDialogue = false;

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
              this.state.loading = false;
              this.state.isLoadingDialogue = false;
              if (i.response.status === 500) {
                this.snackbar = true;
                this.color = "red";
                this.textAlert = this.$t("errors.errorServer");
              } else {
                this.snackbar = true;
                this.color = "red";
                this.textAlert = i.response.data.msg;
              }
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
            role: this.state.formData.role.id,
            group: groupsIds ?? [],
            is_active: this.state.formData.deactivateUser,
            password_ad: this.state.formData.passwordDN ?? "",
            id_server: this.state.formData.dnValue?.id ?? "",
          };
          axios
            .put(`/users/modifyUser/${this.userId}`, payload2)
            .then((response) => {
              if (response.status == 200) {
                this.closeModal();

                this.snackbar = true;
                this.color = "success";
                this.textAlert = response.data.msg;

                this.state.loading = false;
                this.state.isLoadingDialogue = false;

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
              this.state.loading = false;
              this.state.isLoadingDialogue = false;

              if (i.response.status === 500) {
                this.snackbar = true;
                this.color = "red";
                this.textAlert = this.$t("errors.errorServer");
              } else {
                this.snackbar = true;
                this.color = "red";
                this.textAlert = i.response.data.msg;
              }
            });
        }
      } else {
        console.log("error : ", this.v$.$errors);
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
