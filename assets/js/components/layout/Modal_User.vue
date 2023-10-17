<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{ mode === "create" ? "Create" : "Update" }} user</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- User Modal -->

                <v-col cols="12">
                  <v-text-field
                    label="Username "
                    v-model="state.formData.username"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.username.$error"
                    >{{ v$.formData.username.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="6" v-if="mode == 'create'">
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

                <v-col cols="6" v-if="mode == 'create'">
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

                <v-col cols="12">
                  <v-text-field
                    label="Fullname "
                    v-model="state.formData.fullname"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.fullname.$error"
                    >{{ v$.formData.fullname.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12">
                  <v-text-field
                    label="Email for Ldap auth "
                    v-model="state.formData.email"
                  ></v-text-field>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.email.$error"
                    >{{ v$.formData.email.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12">
                  <v-autocomplete
                    :items="['root', 'admin', 'user']"
                    label="Role user"
                    v-model="state.formData.role"
                  ></v-autocomplete>
                  <span class="error-feedback" v-if="v$.formData.role.$error">{{
                    v$.formData.role.$errors[0].$message
                  }}</span>
                </v-col>

                <v-col cols="12">
                  <v-autocomplete
                    :items="groups"
                    label="Assign to Group"
                    multiple
                    item-text="groupname"
                    item-value="id"
                    v-model="state.formData.groups"
                    @change="handleGroupChange"
                    return-object
                  ></v-autocomplete>
                  <span
                    class="error-feedback"
                    v-if="v$.formData.groups.$error"
                    >{{ v$.formData.groups.$errors[0].$message }}</span
                  >
                </v-col>

                <v-col cols="12">
                  <label for="Deactivate User">Desactivate User</label>
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
            <span style="color: green; margin-top: 10px">{{ textAlert }}</span>
            <v-spacer></v-spacer>
            <v-btn color="blue-darken-1" variant="text" type="submit">
              Save
            </v-btn>
            <v-btn color="blue-darken-1" variant="text" @click="closeModal">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
import { mapState } from "vuex";
import axios from "axios";
import useValidate from "@vuelidate/core";
import {
  required,
  email,
  sameAs,
  helpers,
  requiredIf,
} from "@vuelidate/validators";
import { reactive, computed, watch } from "vue";
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
        username: "",
        password: "",
        confirm_password: "",
        fullname: "",
        email: "",
        role: null,
        groups: null,
        deactivateUser: false,
      },
      userRole: null,
      userId: null,
      ModalMode: null,
    });

    const rules = computed(() => {
      return {
        formData: {
          username: { required },
          password: {
            requiredIfFuction: helpers.withMessage(
              "This field must be indicated",
              requiredIf(() => state.ModalMode == "create")
            ),
            isValidPassword: helpers.withMessage(
              `There must be at least 8 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}$/
              )
            ),
          },
          confirm_password: {
            sameAsPassword: helpers.withMessage(
              "Your password does not match",

              sameAs(state.formData.password)
            ), 
            requiredIf: helpers.withMessage(
              "This field must be indicated",
              requiredIf(() => state.ModalMode == "create")
            ),

            isValidPassword: helpers.withMessage(
              `There must be at least 8 characters, including at least one uppercase, one number, and one special character.`,

              helpers.regex(
                /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}$/
              )
            ),
          },

          email: { required, email },
          fullname: { required },
          role: { required },
          groups: { required },
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
      textAlert: "",
      userId: null,
    };
  },
  mounted() {
    this.state.userRole = this.user.currentUser.role;
  },

  watch: {
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
  computed: {
    ...mapState("auth", ["user"]),
  },
  methods: {
    populate(data) {
      if (this.mode == "update") {
        this.state.formData.username = data.username;
        this.state.formData.fullname = data.fullname;
        this.state.formData.email = data.email;
        this.state.formData.role = data.role;
        this.state.formData.groups = data.group;
        this.state.formData.deactivateUser = data.is_active;
        this.userId = data.id;
        this.state.userId = data.id;
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
        (this.state.formData.deactivateUser = false);
    },
    submitForm() {
      this.v$.$validate();
      if (!this.v$.$error) {
        let groupsIds = this.state.formData.groups.map((i) => {
          return i.id;
        });
        const payload = {
          username: this.state.formData.username,
          password: this.state.formData.username,
          fullname: this.state.formData.fullname,
          email: this.state.formData.email,
          role: this.state.formData.role,
          group: groupsIds,
          is_active: this.state.formData.deactivateUser,
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
        if (this.mode == "create") {
          axios.post("/users/createUser", payload).then(
            (response) => {
              if (response.status == "201") {
                this.textAlert = "user Created Successfully";
                setTimeout(() => {
                  this.closeModal();
                  location.reload();
                }, 2000);
              } else {
                console.log("error");
              }
            },
            (error) => {
              console.log(error);
            }
          );
        } else {
          let groupsIds = this.state.formData.groups.map((i) => {
            return i.id;
          });

          axios
            .put(`/users/modifyUser/${this.userId}`, {
              username: this.state.formData.username,
              password: this.state.formData.password,
              fullname: this.state.formData.fullname,
              email: this.state.formData.email,
              role: this.state.formData.role,
              group: groupsIds,
              is_active: this.state.formData.deactivateUser,
            })
            .then((response) => {
              if (response.status == 200) {
                this.textAlert = "User updated succesfully";
                setTimeout(() => {
                  this.closeModal();
                  location.reload();
                }, 2000);
              } else {
                console.log("error");
              }
            })
            .catch((error) => {
              console.error("Error updating resource:", error);
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
}
</style>
