<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">Revoke Certificat</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row class="mb-5">
                <v-col cols="12" class="mb-n5">
                  <v-select
                    class="mt-3"
                    v-model="state.formData.reason"
                    label="Reason"
                    :items="[
                      'No Status',
                      'Unspecified',
                      'key compromise',
                      'CA compromise',
                      'affiliation changed',
                      'supersed/Superseded',
                      'Cessation of Operation/Certificate Hold',
                      'End of Validity Period',
                      'Technical Issues',
                    ]"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions class="actionBtn">
            <span style="color: green; margin-top: 10px">{{ textAlert }}</span>
            <span style="color: rgb(245, 8, 8); margin-top: 10px">{{
              textAlertDanger
            }}</span>

            <v-btn
              :rounded="true"
              class="mt-3 btn-add"
              color="blue-darken-1"
              variant="text"
              @click="closeModal"
            >
              <span class="text-white pr-3 pl-3">Close</span>
            </v-btn>

            <v-btn
              :rounded="true"
              class="mt-3 btn-add"
              color="blue-darken-1"
              variant="text"
              type="submit"
            >
              <span class="text-white pr-3 pl-3">Revoke</span>
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
    const state = reactive({
      formData: {
        reason: "",
      },
    });

    return {
      state,
    };
  },
  data() {
    return {
      openModal: false,
      groupNameCheck: "",
      groupId: null,
      textAlert: "",
      textAlertDanger: "",
    };
  },
  watch: {
    isOpen(val) {
      this.openModal = val;
    },
  },
  methods: {
    // populate(data) {
    //   if (this.mode == "update") {
    //     this.groupNameCheck = data.groupname;
    //     this.state.formData.groupname = data.groupname;
    //     this.groupId = data.id;
    //     this.state.formData.description = data.description;
    //   }
    // },

    closeModal() {
      this.$emit("closeModal");
    },
    resetForm() {
      this.state.formData = {
        firstname: "",
      };
      this.$refs.myForm.reset();
    },
    // submitForm() {
    //   this.v$.$validate();
    //   if (!this.v$.$error) {
    //     function getCookie(name) {
    //       let cookieValue = null;
    //       if (document.cookie && document.cookie !== "") {
    //         const cookies = document.cookie.split(";");
    //         for (let i = 0; i < cookies.length; i++) {
    //           const cookie = cookies[i].trim();
    //           if (cookie.substring(0, name.length + 1) === name + "=") {
    //             cookieValue = decodeURIComponent(
    //               cookie.substring(name.length + 1)
    //             );
    //             break;
    //           }
    //         }
    //       }
    //       return cookieValue;
    //     }
    //     const csrfToken = getCookie("csrftoken");
    //     axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

    //     console.log("token :" + csrfToken);
    //     console.log("DataList :" + JSON.stringify(this.DataList));

    //     // {"email":"mohamedkaabi90@gmail.com","role":"root","groups":["Group 2","Group 3"],"deactivateUser":true,"fullname":"name","password":"password","username":"username"}

    //     const params = {
    //       groupname: this.state.formData.groupname,
    //       description: this.state.formData.description,
    //       // sudoers: this.formData.sudoers
    //     };

    //     if (this.mode == "create") {
    //       console.log("params are : " + JSON.stringify(params));

    //       axios.post("/groups/createGroup", params).then(
    //         (response) => {
    //           console.log("res", response);
    //           if (response.data.msg.includes("exists")) {
    //             this.textAlertDanger = `Group ${this.state.formData.groupname} already exists`;
    //             setTimeout(() => {
    //               this.textAlertDanger = "";
    //             }, 2000);
    //           } else {
    //             this.textAlert = "Group Created Successfully";
    //             setTimeout(() => {
    //               this.closeModal();
    //               this.textAlert = "";
    //               location.reload();
    //             }, 2000);
    //             console.log(response);
    //           }
    //         },
    //         (err) => {
    //           if (err.response && err.response.status === 401) {
    //             const responseData = err.response.data; // Access the response data
    //             console.log("401 Error Response:", responseData);
    //             // this.invalid = true ;
    //             this.message = responseData.message;
    //             // Handle the 401 error here
    //           } else {
    //             console.error("Error occurred:", err);
    //             // Handle other errors
    //           }
    //         }
    //       );
    //     } else {
    //       const payload = {
    //         Newgroupname: this.state.formData.groupname,
    //         description: this.state.formData.description,
    //         // sudoers: this.formData.sudoers
    //       };
    //       axios
    //         .put(`/groups/groupChangeGroupname/${this.groupId}`, payload)
    //         .then((response) => {
    //           // if(this.groupNameCheck == this.formData.groupname){
    //           //   console.log("response", response);
    //           //   this.textAlertDanger = ''
    //           //   this.textAlert = "Group Updated Successfully";
    //           //   setTimeout(() => {
    //           //     this.closeModal();
    //           //     location.reload();
    //           //     this.textAlert = "";
    //           //   }, 2000);
    //           // }
    //           if (response.data.msg.includes("exists")) {
    //             this.textAlertDanger = `Group ${this.state.formData.groupname} already exists`;
    //             setTimeout(() => {
    //               this.textAlertDanger = "";
    //             }, 2000);
    //           } else {
    //             console.log("response", response);
    //             this.textAlert = "Group Updated Successfully";
    //             setTimeout(() => {
    //               this.closeModal();
    //               location.reload();
    //               this.textAlert = "";
    //             }, 2000);
    //           }

    //           // Handle the successful response
    //           console.log("Resource updated:", response.data);
    //         })
    //         .catch((error) => {
    //           // Handle any errors that occur during the request
    //           console.error("Error updating resource:", error);
    //         });
    //     }

    //     console.log("submitForm :", this.state.formData);
    //   }
    // },
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.actionBtn {
  justify-content: center;
}
</style>
