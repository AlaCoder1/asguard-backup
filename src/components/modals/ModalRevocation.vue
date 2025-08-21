<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">Revoke certificat</span>
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
                      'Affiliation changed',
                      'Supersed',
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
import axios from "axios";
import { reactive } from "vue";
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
        reason: "Unspecified",
      },
    });

    return {
      state,
    };
  },
  data() {
    return {
      editRevocRow: null,
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
    editRow(newVal) {
      this.editRevocRow = newVal;
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
      // this.v$.$validate();
      // if (!this.v$.$error) {

      // }

      let id = this.editRevocRow.id;
      let payload = {
        reason: this.state.formData.reason,
      };
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .put(`/certificates/revokeCertificate/${id}`, payload)
        .then((response) => {

          this.closeModal();

          this.snackbar = true;
          this.color = "success";
          this.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          if (i.response.status === 500) {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = this.$t("errors.errorServer");
          } else {
            this.snackbar = true;
            this.color = "red";
            this.textAlert = i.response.data.error;
          }
        });
    },
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
