<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm" class="scroller">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create" ? "Create new" : "Update"
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
                  <span
                    class="error-feedback"
                    v-if="v$.formData.certifName.$error"
                    >{{ v$.formData.certifName.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" class="mb-n6">
                  <v-select
                    v-model="state.formData.method"
                    label="Select"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[
                      {
                        name: 'Import an existing Certificate Authority',
                        slug: 'import',
                        id: '1',
                      },
                      { name: 'Create Certificate', slug: 'create', id: '2' },
                    ]"
                  ></v-select>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.method.$error"
                    >{{ v$.formData.method.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" v-if="isImportCetif" class="mb-n6">
                  <label for=""> Certificate Existant</label>
                  <v-divider></v-divider>
                  <v-text-field
                    class="mt-2"
                    label="Certificat data"
                    v-model="state.formData.certificatData"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.certificatData.$error"
                    >{{ v$.formData.certificatData.$errors[0].$message }}</span
                  >

                  <v-text-field
                    label="Private key certificate (facultatif)"
                    v-model="state.formData.privateKey"
                  ></v-text-field>

                  <v-text-field
                    label="Serial number certificate"
                    v-model="state.formData.serialNumber"
                  ></v-text-field>
                </v-col>

                <v-col v-if="isCreateCetif" cols="12" class="mb-n6">
                  <label for=""> Certification intern</label>
                  <v-divider></v-divider>

                  <v-select
                    class="mt-3"
                    v-model="state.formData.autorityCertif"
                    label="autority certification"
                    :items="allCertifAuth"
                    item-title="nom"
                    item-value="id"
                    return-object
                  ></v-select>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.autorityCertif.$error"
                    >{{ v$.formData.autorityCertif.$errors[0].$message }}</span
                  >

                  <v-select
                    v-model="state.formData.type"
                    label="Type"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[
                      { name: 'Client', id: '1', slug: 'client' },
                      { name: 'Server', id: '2', slug: 'server' },
                    ]"
                  ></v-select>
                  <span class="error-feedback" v-if="v$.formData.type.$error">{{
                    v$.formData.type.$errors[0].$message
                  }}</span>
                  <v-select
                    v-model="state.formData.keyType"
                    label="Key type"
                    item-title="name"
                    item-value="id"
                    return-object
                    :items="[{ name: 'RSA', id: '1', slug: 'rsa' }]"
                  ></v-select>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.keyType.$error"
                    >{{ v$.formData.keyType.$errors[0].$message }}</span
                  >

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
                  <span
                    class="error-feedback"
                    v-if="v$.formData.keyLength.$error"
                    >{{ v$.formData.keyLength.$errors[0].$message }}</span
                  >
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
                  <span
                    class="error-feedback"
                    v-if="v$.formData.hashAlgo.$error"
                    >{{ v$.formData.hashAlgo.$errors[0].$message }}</span
                  >

                  <v-text-field
                    label="Lifetime"
                    v-model="state.formData.lifeTime"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.lifeTime.$error"
                    >{{ v$.formData.lifeTime.$errors[0].$message }}</span
                  >

                  <v-row>
                    <v-col cols="6" class="mb-n6">
                      <v-select
                        v-model="state.formData.country"
                        label="Country"
                        item-title="name"
                        item-value="id"
                        return-object
                        :items="[
                          {
                            name: 'California',
                            code: 'CA',
                            id: '1',
                          },
                          {
                            name: 'Colorado',
                            code: 'CO',
                            id: '2',
                          },
                        ]"
                      ></v-select>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.country.$error"
                        >{{ v$.formData.country.$errors[0].$message }}</span
                      >
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="State province"
                        v-model="state.formData.state"
                      ></v-text-field>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.state.$error"
                        >{{ v$.formData.state.$errors[0].$message }}</span
                      >
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="place"
                        v-model="state.formData.place"
                      ></v-text-field>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.place.$error"
                        >{{ v$.formData.place.$errors[0].$message }}</span
                      >
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="Organisation"
                        v-model="state.formData.organisation"
                      ></v-text-field>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.organisation.$error"
                        >{{
                          v$.formData.organisation.$errors[0].$message
                        }}</span
                      >
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="Mail"
                        v-model="state.formData.mail"
                      ></v-text-field>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.mail.$error"
                        >{{ v$.formData.mail.$errors[0].$message }}</span
                      >
                    </v-col>
                    <v-col cols="6" class="mb-n6">
                      <v-text-field
                        label="Commun name"
                        v-model="state.formData.communName"
                      ></v-text-field>
                      <span
                        class="error-feedback"
                        v-if="v$.formData.communName.$error"
                        >{{ v$.formData.communName.$errors[0].$message }}</span
                      >
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-container>
            <!-- <small>*indicates required field</small> -->
          </v-card-text>
          <v-card-actions class="mt-10 actionBtn">
            <span style="color: green; margin-bottom: 10px">{{
              textAlert
            }}</span>

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
              <span class="text-white pr-3 pl-3">{{
                mode === "create" ? "Create" : "Update"
              }}</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import axios from "axios";
import useValidate from "@vuelidate/core";
import { required, helpers, requiredIf } from "@vuelidate/validators";
import { reactive, computed } from "vue";
export default {
  name: "Modal_User",
  props: {
    allCertifAuth: {
      type: Boolean,
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

    const rules = computed(() => {
      return {
        formData: {
          certifName: { required },
          method: { required },

          certificatData: { required },
          autorityCertif: { required },
          keyLength: { required },
          hashAlgo: { required },
          type: { required },
          lifeTime: { required },
          country: { required },
          state: { required },
          place: { required },
          keyType: { required },
          organisation: { required },
          mail: { required },
          communName: { required },
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
      openModal: false,
      textAlert: "",
      userId: null,
    };
  },
  computed: {
    isImportCetif() {
      return (
        this.state.formData.method.name ===
        "Import an existing Certificate Authority"
      );
    },
    isCreateCetif() {
      return this.state.formData.method.name === "Create Certificate";
    },
  },
  mounted() {
    // this.state.userRole = this.user.currentUser.role;
  },

  watch: {
    allCertifAuth(val) {
      console.log("allCertifAuthallCertifAuth", val);
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
    closeModal() {
      this.$emit("closeModal");
    },
    resetForm() {},
    submitForm() {
      //     this.v$.$validate();
      //     if (!this.v$.$error) {
      // }
    
      const payload = {
        name: this.state.formData?.certifName,
        certificate_type: this.state.formData?.type?.slug,
        activation: "True",
        method: {
          method_name: this.state.formData?.method?.slug,
          ca: +this.state.formData?.autorityCertif?.id,
          key_type: this.state.formData?.keyType?.slug,
          key_length: +this.state.formData?.keyLength?.slug,
          digest_algorithm: this.state.formData?.hashAlgo?.slug,
          lifetime: +this.state.formData?.lifeTime,
          private_key_location: "Save on this firewall",
          country_code: this.state.formData?.country?.code,
          state: this.state.formData?.state,
          city:  this.state.formData?.place,
          organization: this.state.formData?.organisation,
          email: this.state.formData?.mail,
          common_name: this.state.formData?.communName,
        },
      };

      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
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

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.post("/certificates/createCertificate", payload).then(
        (response) => {
          console.log("res", response);
          if (response.status == "201") {
            console.log("success");
          } else {
            console.log("error");
          }
        },
        (error) => {
          console.log(error);
        }
      );
      console.log('payload', payload)
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
