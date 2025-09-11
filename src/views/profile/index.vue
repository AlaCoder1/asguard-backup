<template>
  <v-app id="inspire">
    <base-layout :title="$t('profil.Personalinformations')">
      <template #content>
        <helpModal />

        <div>
          <div>
            <div class="d-flex justify-center mt-5">
              <v-badge
                location="bottom right"
                color="#205dc2"
                offsetX="20"
                offsetY="30"
                @click="launchFilePicker()"
                style="cursor: pointer"
              >
                <template v-slot:badge>
                  <span class="mdi mdi-pencil" v-if="imageURL"></span>
                  <span class="mdi mdi-camera-outline" v-else></span>
                </template>

                <v-avatar
                  size="150px"
                  v-ripple
                  v-if="!imageURL"
                  class="grey lighten-3 mb-3 bg-grey"
                  style="cursor: pointer"
                >
                  <!-- border: 1px solid rgb(33, 62, 159) -->
                  <span>
                    <svg
                      width="500px"
                      height="200px"
                      viewBox="0 0 24 24"
                      fill="white"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        opacity="0.4"
                        d="M12 22.01C17.5228 22.01 22 17.5329 22 12.01C22 6.48716 17.5228 2.01001 12 2.01001C6.47715 2.01001 2 6.48716 2 12.01C2 17.5329 6.47715 22.01 12 22.01Z"
                      />
                      <path
                        d="M12 6.93994C9.93 6.93994 8.25 8.61994 8.25 10.6899C8.25 12.7199 9.84 14.3699 11.95 14.4299C11.98 14.4299 12.02 14.4299 12.04 14.4299C12.06 14.4299 12.09 14.4299 12.11 14.4299C12.12 14.4299 12.13 14.4299 12.13 14.4299C14.15 14.3599 15.74 12.7199 15.75 10.6899C15.75 8.61994 14.07 6.93994 12 6.93994Z"
                        fill="white"
                      />
                      <path
                        d="M18.7807 19.36C17.0007 21 14.6207 22.01 12.0007 22.01C9.3807 22.01 7.0007 21 5.2207 19.36C5.4607 18.45 6.1107 17.62 7.0607 16.98C9.7907 15.16 14.2307 15.16 16.9407 16.98C17.9007 17.62 18.5407 18.45 18.7807 19.36Z"
                        fill="white"
                      />
                    </svg>
                  </span>
                </v-avatar>

                <v-avatar
                  size="150px"
                  v-ripple
                  v-else
                  class="mb-3"
                  style="cursor: pointer; overflow: hidden; border-radius: 50%"
                >
                  <img
                    :src="imageURL"
                    alt="avatar"
                    style="width: 100%; height: 100%; object-fit: cover"
                  />
                </v-avatar>
              </v-badge>
            </div>
            <!-- <div
              v-if="imageURL && saved == false"
              class="d-flex justify-center"
            >
              <v-btn class="primary" @click="uploadImage" :loading="saving"
                >Save Avatar</v-btn
              >
            </div> -->

            <input
              type="file"
              ref="file"
              :name="uploadFieldName"
              @change="onFileChange($event.target.name, $event.target.files)"
              style="display: none"
            />
            <v-dialog v-model="errorDialog" max-width="300">
              <v-card>
                <v-card-text class="subheading">{{ errorText }}</v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="errorDialog = false" flat>{{
                    $t("profil.GotIt")
                  }}</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </div>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Username')"
                v-model="username"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Address')"
                v-model="address"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Firstname')"
                v-model="firstname"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Region')"
                v-model="region"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Phonenumber')"
                v-model="phone_number"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Country')"
                v-model="country"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Email')"
                v-model="state.formData.email"
              ></v-text-field>
              <p
                class="error-feedback mb-2"
                v-if="vEmail$.formData.email.$error"
              >
                {{ vEmail$.formData.email.$errors[0].$message }}
              </p>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Postalcode')"
                v-model="code_postal"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="d-flex justify-center align-center mt-5">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Lastname')"
                v-model="lastname"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-row>
                <v-col cols="8">
                  <label>{{ $t("profil.2FA") }} </label>
                </v-col>
                <v-spacer></v-spacer>
                <v-col cols="4" class="mb-n6">
                  <input type="checkbox" hide-details v-model="is_enable_2FA" />
                  <label class="ml-1">{{ $t("profil.ActivateOTP") }} </label>
                </v-col>
              </v-row>
            </v-col>
          </v-row>

          <v-row class="flex py-8">
            <v-col>
              <div class="d-flex justify-center align-center">
                <VButton
                  rounded
                  outlined
                  color="#213E9F"
                  label-color="#ffffff"
                  :label="$t('profil.Update')"
                  :isLarge="true"
                  @click="submitForm"
                />
              </div>
            </v-col>
          </v-row>

          <v-row class="d-flex justify-center align-center mt-0 mb-3">
            <v-col cols="8" class="mb-n6">
              <v-text-field
                :label="$t('profil.Oldpassword')"
                v-model="state.formData.olPassword"
                :append-inner-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
                prepend-inner-icon="mdi-lock-outline"
                :type="show1 ? 'text' : 'password'"
                @click:append-inner="show1 = !show1"
              ></v-text-field>

              <p class="error-feedback" v-if="v$.formData.olPassword.$error">
                {{ v$.formData.olPassword.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>

          <v-row class="d-flex justify-center align-center">
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('profil.Newpassowrd')"
                v-model="state.formData.newPassword"
                :append-inner-icon="show2 ? 'mdi-eye' : 'mdi-eye-off'"
                prepend-inner-icon="mdi-lock-outline"
                :type="show2 ? 'text' : 'password'"
                @click:append-inner="show2 = !show2"
              ></v-text-field>
              <p class="error-feedback" v-if="v$.formData.newPassword.$error">
                {{ v$.formData.newPassword.$errors[0].$message }}
              </p>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :append-inner-icon="show3 ? 'mdi-eye' : 'mdi-eye-off'"
                prepend-inner-icon="mdi-lock-outline"
                :type="show3 ? 'text' : 'password'"
                @click:append-inner="show3 = !show3"
                :label="$t('profil.ConfirmNewpassowrd')"
                v-model="state.formData.confirmPassword"
              ></v-text-field>
              <p
                class="error-feedback"
                v-if="v$.formData.confirmPassword.$error"
              >
                {{ v$.formData.confirmPassword.$errors[0].$message }}
              </p>
            </v-col>
          </v-row>
          <v-row class="flex py-8 mb-10">
            <v-col>
              <div class="d-flex justify-center align-center">
                <VButton
                  rounded
                  outlined
                  color="#213E9F"
                  label-color="#ffffff"
                  :label="$t('profil.ChangePassword')"
                  :isLarge="true"
                  @click="changePass"
                />
              </div>
            </v-col>
          </v-row>
          <v-snackbar
            :timeout="2000"
            v-model="snackbar"
            location="bottom right"
            :color="color"
          >
            {{ textAlert }}
          </v-snackbar>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { useI18n } from "vue-i18n";
import { reactive, computed, ref, onMounted } from "vue";
import useValidate from "@vuelidate/core";
import { required, sameAs, helpers, email } from "@vuelidate/validators";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import helpModal from "@/components/modals/help.vue";
import { get_params } from "@/mixins/params.js";

export default {
  name: "Profile",
  components: {
    BaseLayout,
    VButton,
    helpModal,
  },

  mounted() {
    let retriveInfo = localStorage.getItem("user-info");
    let userInfo = JSON.parse(retriveInfo);
    let userId = userInfo?.currentUser?.id;
    this.id = userId;
    this.getUserById(userId);
  },

  setup() {
    const length = ref(0);
    const { t } = useI18n();

    onMounted(async () => {
      const params = await get_params();
      length.value = params?.password_length || 16;
    });

    const state = reactive({
      formData: {
        confirmPassword: "",
        newPassword: "",
        olPassword: "",
        email: "",
      },
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });

    const passwordConfirmation = computed(() => {
      return t("errors.passwordConfirmation");
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
          olPassword: {
            required: helpers.withMessage(error, required),
            // isValidPassword: helpers.withMessage(
            //   invalidPassword,

            //   helpers.regex(
            //     /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            //   )
            // ),
          },
          newPassword: {
            required: helpers.withMessage(error, required),
            isValidPassword: helpers.withMessage(
              invalidPassword,

              (value) => {
                if (!value) return true;
                return passwordRegex.value.test(value);
              }
            ),
          },
          confirmPassword: {
            sameAsPassword: helpers.withMessage(
              passwordConfirmation,

              sameAs(state.formData.newPassword)
            ), // can be a reference to a field or computed property
            required: helpers.withMessage(error, required),

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
    const ruleEmail = computed(() => {
      return {
        formData: {
          email: { required: helpers.withMessage(error, required), email },
        },
      };
    });

    const vEmail$ = useValidate(ruleEmail, state);
    return {
      state,
      v$,
      vEmail$,
    };
  },
  data: () => ({
    id: null,
    show1: false,
    show2: false,
    show3: false,
    errorDialog: false,
    errorText: "",
    uploadFieldName: "file",
    maxSize: 1024,
    avatar: null,
    saving: false,
    saved: false,
    imageURL: null,
    //
    snackbar: false,
    color: "",
    textAlert: "",
    //
    username: "",
    firstname: "",
    lastname: "",
    code_postal: "",
    // email: "",
    region: "",
    phone_number: "",
    is_enable_2FA: "",
    address: "",
    country: "",
    fileImg: null,
    //
  }),

  methods: {
    getUserById(userId) {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .get(`/users/getUser/${userId}`)
        .then((response) => {
          this.username =
            response.data.username === "null" ? "" : response.data.username;
          this.firstname =
            response.data.fullname === "null" ? "" : response.data.fullname;
          this.lastname =
            response.data.fullname === "null" ? "" : response.data.fullname;
          this.code_postal =
            response.data.profile.code_postal === "null"
              ? ""
              : response.data.profile.code_postal;
          this.state.formData.email =
            response.data.email === "null" ? "" : response.data.email;
          this.region =
            response.data.profile.region === "null"
              ? ""
              : response.data.profile.region;
          this.phone_number =
            response.data.profile.phone_number === "null"
              ? ""
              : response.data.profile.phone_number;
          this.is_enable_2FA = response.data.profile.is_enable_2FA;
          this.address =
            response.data.profile.address === "null"
              ? ""
              : response.data.profile.address;
          this.country =
            response.data.profile.country === "null"
              ? ""
              : response.data.profile.country;
          this.imageURL = response.data.profile.photo_url;
        })
        .catch((e) => {});
    },

    uploadImage() {
      this.saving = true;
      setTimeout(() => this.savedAvatar(), 1000);
    },
    savedAvatar() {
      this.saving = false;
      this.saved = true;
    },
    launchFilePicker() {
      this.$refs.file.click();
    },
    onFileChange(fieldName, file) {
      const { maxSize } = this;
      let imageFile = file[0];
      if (file.length > 0) {
        let size = imageFile.size / maxSize / maxSize;
        if (!imageFile.type.match("image.*")) {
          this.errorDialog = true;
          this.errorText = this.$t("profil.pleaseChoose");
        } else if (size > 1) {
          this.errorDialog = true;
          this.errorText = this.$t("profil.fileBig");
        } else {
          this.imageURL = URL.createObjectURL(imageFile);
          this.fileImg = file[0];
        }
      }
    },

    submitForm() {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      this.vEmail$.$validate();
      if (!this.vEmail$.$error) {
        let formData = new FormData();
        formData.append("photo", this.fileImg ? this.fileImg : this.imageURL);
        formData.append("username", this.username);
        formData.append("fullname", this.firstname);
        formData.append("code_postal", this.code_postal);
        formData.append("email", this.state.formData.email);
        formData.append("region", this.region);
        formData.append("phone_number", this.phone_number);
        formData.append(" is_enable_2FA", this.is_enable_2FA);
        formData.append("address", this.address);
        formData.append("country", this.country);

        axios
          .put(`/users/update_profile/${this.id}`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          })
          .then((response) => {
            if (response.status == "200") {
              this.snackbar = true;
              this.color = "success";
              this.textAlert = response.data.message;
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
              this.textAlert = i.response.data.msg;
            }
          });
      }
    },
    changePass() {
      this.v$.$validate();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (!this.v$.$error) {
        let payload = {
          current_password: this.state.formData.olPassword,
          new_password: this.state.formData.newPassword,
          confirm_password: this.state.formData.confirmPassword,
        };

        axios
          .put(`/users/userChangePW`, payload)
          .then((response) => {
            if (response.status == "200") {
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
              this.textAlert = i.response.data.response;
            }
          });
      } else {
        console.log("error :", this.v$);
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
