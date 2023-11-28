<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create" ? "Create new Authority" : "Update Authority"
              }}
              Certificat</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" class="mb-n6">
                  <v-text-field
                    label="Certificat Name "
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
                    label="Method"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[
                      {
                        name: 'Import an existing Certificate Authority',
                        slug: 'import',
                        id: '1',
                      },
                      { name: 'Create Certificate Authority', slug: 'create', id: '2' },
                    ]"
                  ></v-select>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.method.$error"
                  >
                    {{ v$.formData.method.$errors[0].$message }}
                  </p>
                </v-col>

                <v-col cols="12" v-if="isImportCetif" class="mb-n6">
                  <label for=""> Certificate Existant</label>
                  <v-divider></v-divider>

                  <v-textarea
                    class="mt-3"
                    v-model="state.formData.certificatData"
                    label="Certificat data"
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
                    label="Private key certificate (facultatif)"
                    variant="outlined"
                  ></v-textarea>
                  <p
                    class="error-feedback mb-5"
                    v-if="v$.formData.privateKey.$error"
                  >
                    {{ v$.formData.privateKey.$errors[0].$message }}
                  </p>

                  <v-text-field
                    label="Serial number certificate"
                    v-model="state.formData.serialNumber"
                  ></v-text-field>
                </v-col>

                <v-col v-if="isCreateCetif" cols="12" class="mb-n6">
                  <label for=""> Certification autority</label>
                  <v-divider></v-divider>
                  <!--  -->
                  <v-select
                    v-model="state.formData.keyType"
                    label="Key type"
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
                    label="Key length"
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
                    label="Hash algo"
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
                    label="Lifetime"
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
                        label="Country"
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
                        label="State province"
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
                        label="place"
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
                        label="Organisation"
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
                        label="Commun name"
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
              <span class="text-white pr-3 pl-3">Close</span>
            </v-btn>
            <v-btn
              type="submit"
              color="asguard_primary_light"
              :rounded="true"
              class="mt-3 btn-add"
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
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, requiredIf, helpers, email } from "@vuelidate/validators";
import { reactive, computed, watch } from "vue";
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
    const state = reactive({
      formData: {
        certifName: "",
        method: "",
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

    const rules = computed(() => {
      return {
        formData: {
          certifName: {
            required,
            isValidCertifName: helpers.withMessage(
              `champs can include only letters & Numbers & underscores & hyphens without space.`,

              helpers.regex(/^[A-Za-z0-9_\-]+$/)
            ),
          },
          method: { required },
          certificatData: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  state.formData.method.name ===
                  "Import an existing Certificate Authority"
              )
            ),
          },
          privateKey: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () =>
                  state.formData.method.name ===
                  "Import an existing Certificate Authority"
              )
            ),
          },

          keyLength: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
          },
          hashAlgo: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
          },
          keyType: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
          },
          lifeTime: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
            isValidlifeTime: helpers.withMessage(
              `champs lifeTime can include only Numbers.`,

              helpers.regex(/^[0-9]+$/)
            ),
          },
          country: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
          },
          state: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
            isValidState: helpers.withMessage(
              `champs state can include only letters.`,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          place: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
            isValidPlace: helpers.withMessage(
              `champs place can include only letters.`,

              helpers.regex(/^[a-zA-Z]+$/)
            ),
          },
          organisation: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
          },
          mail: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
            email,
          },
          communName: {
            requiredIfFuction: helpers.withMessage(
              "Value is required",
              requiredIf(
                () => state.formData.method.name === "Create Certificate Authority"
              )
            ),
            isValidCommne: helpers.withMessage(
              `champs can include only letters & Numbers & underscores & hyphens without space.`,

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
    };
  },
  data() {
    return {
      countriesList: null,
      color: "",
      snackbar: false,
      openModal: false,
      textAlert: "",
    };
  },
  mounted() {
    this.getAllcountry();
  },
  computed: {
    isImportCetif() {
      return (
        this.state.formData.method.name ===
        "Import an existing Certificate Authority"
      );
    },
    isCreateCetif() {
      return this.state.formData.method.name === "Create Certificate Authority";
    },
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
    getAllcountry() {
      axios.get("https://restcountries.com/v3.1/all").then(
        (response) => {
          let countryList = response.data.map((element) => {
            return {
              countryName: element.name.common,
              countryCode: element.cca2,
              countryID: element.ccn3,
            };
          });
          this.countriesList = countryList;
        },
        (error) => {
          console.log(error);
        }
      );
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
        if (this.state.formData.method.name == "Create Certificate Authority") {
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

        axios
          .post("/certificates/createCertAuth", payload)
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
