<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{
                mode === "create" ? $t("modal.create") : $t("modal.update")
              }}
              group</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row class="mb-5">
                <v-col cols="12" class="mb-n5">
                  <v-text-field
                    :label="$t('form.goupname')"
                    v-model="state.formData.groupname"
                  ></v-text-field>
                  <span
                    class="error-feedback mb-1"
                    v-if="v$.formData.groupname.$error"
                    >{{ v$.formData.groupname.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12" class="mb-n5">
                  <v-text-field
                    :label="$t('form.description')"
                    v-model="state.formData.description"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.description.$error"
                    >{{ v$.formData.description.$errors[0].$message }}</span
                  >
                </v-col>

                <!-- <v-col cols="12">
                  <label for="Deactivate User">add group in sudoers</label>
                  <input type="checkbox" id="Deactivate User" v-model="formData.sudoers" />
                </v-col> -->
                <!-- Group Modal -->
              </v-row>
            </v-container>

            <small class="mt-10 ml-5"
              >*{{ $t("requiredfield.indicatesrequiredfield") }}</small
            >
          </v-card-text>
          <v-card-actions>
            <!-- <span style="color: green; margin-top: 10px">{{ textAlert }}</span>
            <span style="color: rgb(245, 8, 8); margin-top: 10px">{{
              textAlertDanger
            }}</span> -->
            <v-spacer></v-spacer>

            <v-btn
              :rounded="true"
              class="mt-3 btn-add"
              color="asguard_primary_light"
              variant="text"
              @click="closeModal"
            >
              <span class="pr-3 pl-3 text-white" style="color: #213e9f">{{
                $t("buttons.close")
              }}</span>
            </v-btn>
            <v-btn
              :rounded="true"
              class="mt-3 btn-add"
              color="asguard_primary_light"
              variant="text"
              type="submit"
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
import axios from "axios";
import { useI18n } from "vue-i18n";
import useValidate from "@vuelidate/core";
import { required, helpers } from "@vuelidate/validators";
import { reactive, computed } from "vue";
export default {
  name: "Modal_Group",
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
  },
  setup() {
    const { t } = useI18n();
    const state = reactive({
      formData: {
        groupname: "",
        description: "",
      },
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const startwithletter = computed(() => {
      return t("errors.startwithletter");
    });
    const rules = computed(() => {
      return {
        formData: {
          groupname: {
            required: helpers.withMessage(error, required),
            isValidName: helpers.withMessage(
              startwithletter,

              helpers.regex(/^[a-zA-Z][a-zA-Z0-9_\-]{0,31}$/)
            ),
          },
          description: {
            required: helpers.withMessage(error, required),
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
      openModal: false,
      groupNameCheck: "",
      groupId: null,
      textAlert: "",
      color: "",
      snackbar: false,
      textAlertDanger: "",
    };
  },
  watch: {
    isOpen(val) {
      this.openModal = val;
    },
    initialData(newValue) {
      // React to prop changes
      this.formData = newValue;
      console.log("Prop changed:", newValue);
    },
    editRow(newValue) {
      this.populate(newValue);
    },
  },
  methods: {
    populate(data) {
      if (this.mode == "update") {
        this.groupNameCheck = data.groupname;
        this.state.formData.groupname = data.groupname;
        this.groupId = data.id;
        this.state.formData.description = data.description;
      }
    },

    closeModal() {
      this.$emit("closeModal");
    },
    resetForm() {
      this.state.formData = {
        firstname: "",
      };
      this.$refs.myForm.reset();
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

        console.log("token :" + csrfToken);
        console.log("DataList :" + JSON.stringify(this.DataList));

        // {"email":"mohamedkaabi90@gmail.com","role":"root","groups":["Group 2","Group 3"],"deactivateUser":true,"fullname":"name","password":"password","username":"username"}

        const params = {
          groupname: this.state.formData.groupname,
          description: this.state.formData.description,
          // sudoers: this.formData.sudoers
        };

        if (this.mode == "create") {
          console.log("params are : " + JSON.stringify(params));

          axios
            .post("/groups/createGroup", params)
            .then(
              (response) => {
                if (response.data.msg.includes("exists")) {
                  let textAlertDanger = `Group ${this.state.formData.groupname} already exists`;
                  setTimeout(() => {
                    this.snackbar = true;
                    this.color = "red";
                    this.textAlert = textAlertDanger;
                  }, 1000);
                } else {
                  this.closeModal();

                  this.snackbar = true;
                  this.color = "success";
                  this.textAlert = response.data.msg;

                  setTimeout(() => {
                    location.reload();
                  }, 2000);
                  console.log(response);
                }
              },
              (err) => {
                if (err.response && err.response.status === 401) {
                  const responseData = err.response.data; // Access the response data
                  console.log("401 Error Response:", responseData);
                  // this.invalid = true ;
                  this.message = responseData.message;
                  // Handle the 401 error here
                } else {
                  console.error("Error occurred:", err);
                  // Handle other errors
                }
              }
            )
            .catch((i) => {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.error;
            });
        } else {
          const payload = {
            Newgroupname: this.state.formData.groupname,
            description: this.state.formData.description,
            // sudoers: this.formData.sudoers
          };
          axios
            .put(`/groups/groupChangeGroupname/${this.groupId}`, payload)
            .then((response) => {
              // if(this.groupNameCheck == this.formData.groupname){
              //   console.log("response", response);
              //   this.textAlertDanger = ''
              //   this.textAlert = "Group Updated Successfully";
              //   setTimeout(() => {
              //     this.closeModal();
              //     location.reload();
              //     this.textAlert = "";
              //   }, 2000);
              // }
              if (response.data.msg.includes("exists")) {
                let textAlertDanger = `Group ${this.state.formData.groupname} already exists`;
                setTimeout(() => {
                  this.snackbar = true;
                  this.color = "red";
                  this.textAlert = textAlertDanger;
                }, 1000);
              } else {
                this.closeModal();

                this.snackbar = true;
                this.color = "success";
                this.textAlert = response.data.msg;

                setTimeout(() => {
                  location.reload();
                }, 2000);
              }

              // Handle the successful response
              console.log("Resource updated:", response.data);
            })
            .catch((i) => {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.error;
            });
        }

        console.log("submitForm :", this.state.formData);
      }
    },
  },
  // components: {
  //   VTextField: Vue.extend(VTextField),
  // },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
