<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5"
              >{{ mode === "create" ? "Create" : "Update" }} group</span
            >
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <!-- Group Modal -->
                <v-col cols="12">
                  <v-text-field
                    label="Group name*"
                    v-model="formData.groupname"
                  ></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-text-field
                    label="Description"
                    v-model="formData.description"
                  ></v-text-field>
                </v-col>

                <!-- <v-col cols="12">
                  <label for="Deactivate User">add group in sudoers</label>
                  <input type="checkbox" id="Deactivate User" v-model="formData.sudoers" />
                </v-col> -->
                <!-- Group Modal -->
              </v-row>
            </v-container>

            <small>*indicates required field</small>
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
import axios from "axios";
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
  data() {
    return {
      formData: {
        groupname: "",
        description: "",
        sudoers: "",
      },
      groupId: null,
      textAlert: "",
    };
  },
  watch: {
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
        (this.formData.groupname = data.groupname), (this.groupId = data.id);
        this.formData.description = data.description;
      }
    },

    closeModal() {
      // this.resetForm();
      this.$emit("closeModal");
    },
    resetForm() {
      this.formData = {
        firstname: "",
        // Reset other form fields as needed
      };
      this.$refs.myForm.reset();
    },
    submitForm() {
      // Perform form submission actions here

      // Emit an event to send form data to the parent component
      // this.$emit('updateModalData', this.formData);
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
        groupname: this.formData.groupname,
        description: this.formData.description,
        // sudoers: this.formData.sudoers
      };

      if (this.mode == "create") {
        console.log("params are : " + JSON.stringify(params));

        axios.post("/groups/createGroup", params).then(
          (response) => {
            this.textAlert = "Group Created Successfully";
            setTimeout(() => {
              this.closeModal();
              location.reload();
            }, 2000);
            console.log(response);
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
        );
      } else {
        const payload = {
          Newgroupname: this.formData.groupname,
          description: this.formData.description,
          // sudoers: this.formData.sudoers
        };
        axios
          .put(`/groups/groupChangeGroupname/${this.groupId}`, payload)
          .then((response) => {
            this.textAlert = "Group Updated Successfully";
            setTimeout(() => {
              this.closeModal();
              location.reload();
            }, 2000);

            // Handle the successful response
            console.log("Resource updated:", response.data);
          })
          .catch((error) => {
            // Handle any errors that occur during the request
            console.error("Error updating resource:", error);
          });
      }

      console.log("submitForm :", this.formData);
    },
  },
  // components: {
  //   VTextField: Vue.extend(VTextField),
  // },
};
</script>
