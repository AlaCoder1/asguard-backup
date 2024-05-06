<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create"
                  ? $t("buttons.createcertif")
                  : $t("buttons.updatecertif")
              }}
              {{ $t("agGrid.certificat") }}</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    :label="$t('certificat.certificatName')"
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
                    :label="$t('certificat.method')"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="selectlist"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.method.$error"
                  >
                    {{ v$.formData.method.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" v-if="isImportCetif" class="mb-n6">
                  <label for="">
                    {{ $t("certificat.certificat_existant") }}</label
                  >
                  <v-divider></v-divider>

                  <v-textarea
                    class="mt-3"
                    v-model="state.formData.certificatData"
                    :label="$t('certificat.certificatdata')"
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
                  <label for=""> {{ $t("certificat.certif_intern") }}</label>
                  <v-divider></v-divider>

                  <v-select
                    class="mt-3"
                    v-model="state.formData.autorityCertif"
                    :label="$t('certificat.certificat_auth')"
                    :items="allCertifAuth"
                    item-title="nom"
                    item-value="id"
                    :no-data-text="$t('certificat.certificatlist')"
                    return-object
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.autorityCertif.$error"
                  >
                    {{ v$.formData.autorityCertif.$errors[0].$message }}
                  </p>

                  <v-select
                    v-model="state.formData.type"
                    label="Type"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="selectlisttype"
                  ></v-select>
                  <p class="error-feedback mb-5" v-if="v$.formData.type.$error">
                    {{ v$.formData.type.$errors[0].$message }}
                  </p>
                  <v-select
                    v-model="state.formData.keyType"
                    :label="$t('certificat.keytype')"
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
                    :label="$t('certificat.keylength')"
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
                    :label="$t('certificat.Hashalgo')"
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
                    :label="$t('certificat.lifetime')"
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
                        :label="$t('certificat.country')"
                        item-title="countryName"
                        item-value="countryID"
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
                        :label="$t('certificat.state')"
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
                        :label="$t('certificat.place')"
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
                        :label="$t('certificat.organisation')"
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
                        label="Mail"
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
                        :label="$t('certificat.communName')"
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
                mode === "create"
                  ? $t("buttons.create")
                  : $t("buttons.updatecertif")
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

      <template v-slot:actions> </template>
    </v-snackbar>
  </v-row>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, helpers, email, requiredIf } from "@vuelidate/validators";
import { reactive, computed, ref } from "vue";
export default {
  name: "Modal_User",
  props: {
    allCertifAuth: {
      type: Array,
      required: true,
    },
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
  },
  setup() {
    const { t } = useI18n();
    const state = reactive({
      formData: {
        certifName: "",
        method: "",
        certificatData: "",
        privateKey: "",
        serialNumber: "",
        autorityCertif: "",
        //
        type: "",
        keyType: "",
        keyLength: "",
        hashAlgo: "",
        lifeTime: "",
        country: "",
        state: "",
        place: "",
        organisation: "",
        mail: "",
        communName: "",
      },
      userRole: null,
      userId: null,
      ModalMode: null,
    });

    const certifexist = computed(() => {
      return t("certificat.exist_certificat");
    });
    const createcertif = computed(() => {
      return t("certificat.create_certificat");
    });

    const selectlist = ref([
      {
        name: certifexist,
        slug: "import",
        id: "1",
      },
      { name: createcertif, slug: "create", id: "2" },
    ]);

    const serveur = computed(() => {
      return t("agGrid.server");
    });

    const selectlisttype = ref([
      { name: "Client", id: "1", slug: "client" },
      { name: serveur, id: "2", slug: "server" },
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
          method: {
            required: helpers.withMessage(error, required),
          },

          certificatData: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name ===
                    "Import an existing Certificate" ||
                  state.formData.method.name ===
                    "Importer un certificat existant"
              )
            ),
          },
          autorityCertif: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          keyLength: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          hashAlgo: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          type: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          keyType: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          lifeTime: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
            isValidlifeTime: helpers.withMessage(
              champNumber,

              helpers.regex(/^[0-9]+$/)
            ),
          },

          country: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          state: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
            isValidState: helpers.withMessage(
              champletter,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          place: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
            isValidPlace: helpers.withMessage(
              champplaceletter,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          organisation: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
          },
          mail: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
            ),
            email,
          },
          communName: {
            requiredIfFuction: helpers.withMessage(
              error,
              requiredIf(
                () =>
                  state.formData.method.name === "Create Certificate" ||
                  state.formData.method.name === "Créer un certificat"
              )
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
      selectlist,
      selectlisttype,
    };
  },
  data() {
    return {
      countriesList: null,
      color: "",
      openModal: false,
      textAlert: "",
      userId: null,
    };
  },
  computed: {
    isImportCetif() {
      return (
        this.state.formData.method.name === "Import an existing Certificate" ||
        this.state.formData.method.name === "Importer un certificat existant"
      );
    },
    isCreateCetif() {
      return (
        this.state.formData.method.name === "Create Certificate" ||
        this.state.formData.method.name === "Créer un certificat"
      );
    },
  },
  mounted() {
    this.getAllcountry();
  },

  watch: {
    isImportCetif() {
      this.v$.$reset();
    },
    isCreateCetif(test) {
      this.v$.$reset();
    },
    isOpen(val) {
      this.openModal = val;
    },
    editRow(newValue) {
      // this.populate(newValue);
    },
    mode(val) {
      if (val == "create") {
        this.resetForm();
        this.state.ModalMode = "create";
      }
    },
  },

  methods: {
    getAllcountry() {
      axios
        .get("https://restcountries.com/v3.1/all")
        .then((response) => {
          let countryList = response.data.map((element) => {
            return {
              countryName: element.name.common,
              countryCode: element.cca2,
              countryID: element.ccn3,
            };
          });
          countryList.sort((a, b) =>
            a.countryName.localeCompare(b.countryName)
          );

          this.countriesList = countryList;
        })
        .catch(() => {
          console.log("error");
        });
    },
    closeModal() {
      this.v$.$reset();
      this.$emit("closeModal");
    },
    resetForm() {},
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
        const csrfToken = this.getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let payload = {};
        if (this.state.formData.method.name == "Create Certificate" || this.state.formData.method.name == "Créer un certificat") {
          payload = {
            name: this.state.formData?.certifName,
            activation: "True",
            method: {
              method_name: this.state.formData?.method?.slug,
              certificate_type: this.state.formData?.type?.slug,
              ca: +this.state.formData?.autorityCertif?.id,
              key_type: this.state.formData?.keyType?.slug,
              key_length: +this.state.formData?.keyLength?.slug,
              digest_algorithm: this.state.formData?.hashAlgo?.slug,
              lifetime: +this.state.formData?.lifeTime,
              private_key_location: "Save on this firewall",
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
            activation: "True",
            method: {
              method_name: this.state.formData?.method?.slug,
              certificate_data: this.state.formData?.certificatData,
              certificate_key: this.state.formData?.privateKey,
              serial: this.state.formData?.serialNumber,
            },
          };
        }

        axios
          .post("/certificates/createCertificate", payload)
          .then((response) => {
            if (response.status == "201") {
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
            this.snackbar = true;
            this.color = "red";
            this.textAlert = i.response.data.error;
          });
      } else {
        console.log("rr", this.v$);
      }
    },
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
  /* display: flex; */
}
.scroller {
  overflow-y: scroll;
}
.actionBtn {
  display: flex !important;
  justify-content: center !important;
}
</style>
