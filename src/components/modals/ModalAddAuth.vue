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
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create"
                  ? $t("buttons.createauth")
                  : $t("buttons.updateauth")
              }}
              {{ $t("agGrid.certificat") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="`${$t('certificat.certificatName')} *`"
                    v-model="state.formData.certifName"
                  ></v-text-field>

                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.certifName.$error"
                  >
                    {{ v$.formData.certifName.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.formData.method"
                    :label="`${$t('certificat.method')} *`"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="selectcetifoptions"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.method.$error"
                  >
                    {{ v$.formData.method.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" v-if="isImportCetif" class="mb-n6">
                  <label for="">{{
                    $t("certificat.certificat_existant")
                  }}</label>
                  <v-divider></v-divider>

                  <v-textarea
                    class="mt-3"
                    v-model="state.formData.certificatData"
                    :label="`${$t('certificat.certificatdata')} *`"
                    variant="outlined"
                  ></v-textarea>

                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.certificatData.$error"
                  >
                    {{ v$.formData.certificatData.$errors[0].$message }}
                  </p>

                  <v-textarea
                    class="mt-3"
                    v-model="state.formData.privateKey"
                    :label="$t('certificat.privatekey')"
                    variant="outlined"
                  ></v-textarea>

                  <v-text-field
                    :label="$t('certificat.serialnumber')"
                    v-model="state.formData.serialNumber"
                  ></v-text-field>
                </v-col>

                <v-col v-if="isCreateCetif" cols="12" class="mb-n6">
                  <label for="">{{ $t("certificat.certificat_auth") }}</label>
                  <v-divider></v-divider>
                  <!--  -->
                  <v-select
                    v-model="state.formData.keyType"
                    :label="`${$t('certificat.keytype')} *`"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[{ name: 'RSA', id: '1', slug: 'rsa' }]"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.keyType.$error"
                  >
                    {{ v$.formData.keyType.$errors[0].$message }}
                  </p>

                  <v-select
                    v-model="state.formData.keyLength"
                    :label="`${$t('certificat.keylength')} *`"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[
                      {
                        name: '2048',
                        slug: '2048',
                        id: '1',
                      },
                      {
                        name: '3072',
                        slug: '3072',
                        id: '2',
                      },
                      {
                        name: '4096',
                        slug: '4096',
                        id: '3',
                      },
                      {
                        name: '8192',
                        slug: '8192',
                        id: '4',
                      },
                    ]"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.keyLength.$error"
                  >
                    {{ v$.formData.keyLength.$errors[0].$message }}
                  </p>
                  <v-select
                    v-model="state.formData.hashAlgo"
                    :label="`${$t('certificat.Hashalgo')} *`"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[
                      {
                        name: 'SHA256',
                        slug: 'sha256',
                        id: '1',
                      },
                      {
                        name: 'SHA384',
                        slug: 'sha384',
                        id: '2',
                      },
                      {
                        name: 'SHA512',
                        slug: 'sha512',
                        id: '3',
                      },
                    ]"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.hashAlgo.$error"
                  >
                    {{ v$.formData.hashAlgo.$errors[0].$message }}
                  </p>

                  <v-text-field
                    :label="`${$t('certificat.lifetime')} *`"
                    v-model="state.formData.lifeTime"
                  ></v-text-field>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.lifeTime.$error"
                  >
                    {{ v$.formData.lifeTime.$errors[0].$message }}
                  </p>
                  <v-row>
                    <v-col cols="6" class="mb-n6">
                      <v-autocomplete
                        v-model="state.formData.country"
                        :label="`${$t('certificat.country')} *`"
                        item-title="countryName"
                        item-value="countryCode"
                        return-object
                        :items="countriesList"
                      ></v-autocomplete>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.country.$error"
                      >
                        {{ v$.formData.country.$errors[0].$message }}
                      </p>
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        :label="`${$t('certificat.state')} *`"
                        v-model="state.formData.state"
                      ></v-text-field>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.state.$error"
                      >
                        {{ v$.formData.state.$errors[0].$message }}
                      </p>
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        :label="`${$t('certificat.place')} *`"
                        v-model="state.formData.place"
                      ></v-text-field>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.place.$error"
                      >
                        {{ v$.formData.place.$errors[0].$message }}
                      </p>
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        :label="`${$t('certificat.organisation')} *`"
                        v-model="state.formData.organisation"
                      ></v-text-field>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.organisation.$error"
                      >
                        {{ v$.formData.organisation.$errors[0].$message }}
                      </p>
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="E-Mail *"
                        v-model="state.formData.mail"
                      ></v-text-field>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.mail.$error"
                      >
                        {{ v$.formData.mail.$errors[0].$message }}
                      </p>
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        :label="`${$t('certificat.communName')} *`"
                        v-model="state.formData.communName"
                      ></v-text-field>
                      <p
                        class="error-feedback mb-5"
                        v-if="v$.formData.communName.$error"
                      >
                        {{ v$.formData.communName.$errors[0].$message }}
                      </p>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-container>
            <!-- <small>*indicates required field</small> -->
          </v-card-text>

          <v-card-actions class="mt-10 actionBtn">
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
              <span class="text-white pr-3 pl-3">{{
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
                $t("buttons.create")
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
import countryList from "country-list";
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, requiredIf, helpers, email } from "@vuelidate/validators";
import { reactive, computed, watch, ref } from "vue";
export default {
  name: "Modal_User",
  props: {
    isOpen: {
      type: Boolean,
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
  },
  setup() {
    const { t } = useI18n();
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      formData: {
        certifName: "",
        method: null,
        certificatData: "",
        privateKey: "",
        serialNumber: "",
        keyType: "",
        keyLength: "",
        hashAlgo: "",
        lifeTime: "",
        country: "",
        state: "",
        place: "",
        organisation: "",
        communName: "",
        mail: "",
      },
      ModalMode: null,
    });
    const certifexist = computed(() => {
      return t("certificat.exist_certif");
    });
    const certifnew = computed(() => {
      return t("certificat.certif_new");
    });
    const selectcetifoptions = ref([
      {
        name: certifexist,
        slug: "import",
        id: "1",
      },
      {
        name: certifnew,
        slug: "create",
        id: "2",
      },
    ]);

    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const champ = computed(() => {
      return t("champs.indication");
    });
    const champNumber = computed(() => {
      return t("champs.champNumber");
    });
    const champletter = computed(() => {
      return t("champs.champletter");
    });

    const champplaceletter = computed(() => {
      return t("champs.champplaceletter");
    });
    const champNumberAndMax = computed(() => {
      return t("champs.champNumberAndMax");
    });
    const rules = computed(() => {
      return {
        formData: {
          certifName: {
            required: helpers.withMessage(error, required),
            isValidCertifName: helpers.withMessage(
              champ,
              helpers.regex(/^[A-Za-z0-9_\-]+$/)
            ),
          },
          method: { required: helpers.withMessage(error, required) },
          certificatData: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "import")
            ),
          },

          keyLength: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
          },
          hashAlgo: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
          },
          keyType: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
          },
          lifeTime: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
            isValidlifeTime: helpers.withMessage(
              champNumberAndMax,
              helpers.regex(/^(?:[0-9]{1,2}|[1-7][0-9]{2}|8[0-1][0-9]|82[0-5])$/)
            ),
          },
          country: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
          },
          state: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
            isValidState: helpers.withMessage(
              champletter,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          place: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
            isValidPlace: helpers.withMessage(
              champplaceletter,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          organisation: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
          },
          mail: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
            email,
          },
          communName: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(() => state.formData.method?.slug === "create")
            ),
            isValidCommne: helpers.withMessage(
              champ,

              helpers.regex(/^[A-Za-z0-9_\-]+$/)
            ),
          },
        },
      };
    });
    const v$ = useValidate(rules, state);
    return {
      state,
      v$,
      selectcetifoptions,
    };
  },
  data() {
    return {
      countriesList: [],
      color: "",
      snackbar: false,
      openModal: false,
      textAlert: "",
    };
  },
  mounted() {
    let countries = countryList.getData();
    this.getAllcountry(countries);
  },
  computed: {
    isImportCetif() {
      return this.state.formData.method?.slug === "import";
    },
    isCreateCetif() {
      return this.state.formData.method?.slug === "create";
    },
  },

  watch: {
    isImportCetif() {
      this.v$.$reset();
      this.state.formData.lifeTime = "";
      console.log("this.state.formData.lifeTime", this.state.formData.lifeTime);
    },
    isCreateCetif(test) {
      this.v$.$reset();
    },
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
    async getAllcountry(countries) {
      // await axios.get("https://countriesnow.space/api/v0.1/countries/iso").then(
      //   (response) => {
      //     let countryList = response.data.data.map((element) => {
      //       return {
      //         countryName: element.name,
      //         countryCode: element.Iso2,
      //       };
      //     });
      //     countryList.sort((a, b) =>
      //       a.countryName.localeCompare(b.countryName)
      //     );
      //     this.countriesList = countryList;
      //   },
      //   (error) => {
      //     console.log(error);
      //   }
      // );
      let countryList = countries.map((element) => {
        return {
          countryName: element.name,
          countryCode: element.code,
        };
      });
      countryList.sort((a, b) => a.countryName.localeCompare(b.countryName));
      this.countriesList = countryList;
    },

    closeModal() {
      this.v$.$reset();
      this.$emit("closeModal");
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
    resetForm() {},
    submitForm() {
      this.v$.$validate();
      if (!this.v$.$error) {
        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = {};
        if (this.state.formData.method?.slug === "create") {
          payload = {
            name: this.state.formData?.certifName,
            method: {
              name_method: this.state.formData?.method?.slug,
              key_type: this.state.formData?.keyType?.slug,
              key_length: +this.state.formData?.keyLength?.slug,
              digest_algorithm: this.state.formData?.hashAlgo?.slug,
              lifetime: +this.state.formData?.lifeTime,
              country_code: this.state.formData?.country?.countryCode,
              state: this.state.formData?.state,
              city: this.state.formData?.place,
              organization: this.state.formData?.organisation,
              email: this.state.formData?.mail,
              common_name: this.state.formData?.communName,
            },
          };
        } else {
          payload = {
            name: this.state.formData?.certifName,
            method: {
              name_method: this.state.formData?.method?.slug,
              certificate_data: this.state.formData?.certificatData,
              certificate_key: this.state.formData?.privateKey,
              serial: this.state.formData?.serialNumber,
            },
          };
        }

        this.state.loading = true;
        this.state.isLoadingDialogue = true;

        axios
          .post("/certificates/createCertAuth", payload)
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
              this.textAlert = i.response.data.error;
              setTimeout(() => {
                this.textAlert = "";
              }, 2000);
            }
          });
      } else {
        console.log("this.v$.$error", this.v$);
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
.scroller {
  overflow-y: scroll;
}
.actionBtn {
  justify-content: center;
}
</style>
