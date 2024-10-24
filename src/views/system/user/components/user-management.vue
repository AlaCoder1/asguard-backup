<template>
  <div>
    <h4>{{ $t("networkAdmins") }}</h4>

    <div style="height: 100%">
      <div style="display: flex; flex-direction: row; height: 100%">
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3 m-w-80"
            :columnDefs="columnDefs"
            :rowData="rowData"
            :gridOptions="gridOptions"
            @grid-ready="onGridReady"
            :localeText="paginationLocalization"
            :overlayNoRowsTemplate="overlayTemplate"
          />
        </div>
      </div>
    </div>

    <div class="d-flex justify-end">
      <v-btn
        color="asguard_primary_light"
        :rounded="true"
        class="mt-3 btn-add"
        @click="openModalAdd"
      >
        <span class="text-white">{{ $t("button.addUser") }}</span>
      </v-btn>
    </div>

    <Modal_User
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
      @updateModalData="handleModalUpdate"
      :groups="DataList.groups"
    />
    <Modal_Password
      :editRow="rowEdit"
      :mode="modalMode"
      :isOpen="isModalPasswordOpen"
      @closeModal="closeModalPassword"
      :initialData="modalData"
      @updateModalData="handleModalUpdate"
      :groups="DataList.groups"
    />
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">
          {{ $t("delete.DeleteConfirmation") }}</v-card-title
        >
        <v-card-text>{{ $t("delete.questionuser") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">{{
            $t("PageGeneral.form.Cancel")
          }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete">{{
            $t("PageGeneral.form.Delete")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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

<script>
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import axios from "axios";
import Modal_User from "@/components/modals/ModalUser.vue";
import Modal_Password from "@/components/modals/ModalChangePassword.vue";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

// import {
//   createUser
// } from '../services/users';

export default {
  name: "UserManagement",
  components: {
    AgGridVue,
    Modal_User,
    Modal_Password,
  },
  props: {
    DataList: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      textAlert: "",
      color: "",
      snackbar: false,
      deletedRow: null,
      deleteDialog: false,
      rowEdit: {},
      isModalOpen: false,
      isModalPasswordOpen: false,
      selectedRowIndex: null,
      modalData: {},
      modalMode: "",
      columnDefs: [
        {
          headerName: this.user,
          field: "username",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: this.role,
          field: "role",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        { headerName: "Actions",width: 150, minWidth: 50, cellRenderer: this.actionCellRenderer },
      ],
      rowData: [], // Initialize rowData as an empty array
      gridOptions: {
        pagination: true,
        paginationPageSize: 3,
        rowSelection: "single",
        // Rest of the gridOptions
      },

      paginationLocalization: {
        of: "/",
      },
      overlayTemplate: `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`,
    };
  },

  watch: {
    DataList: {
      handler(newData) {
        this.rowData = newData.users.filter((i) => i.id != 1);
        // Update rowData with the new prop value
      },
      immediate: true,
    },
    user: {
      handler(val) {
        this.columnDefs[0].headerName = val;
      },
      immediate: true,
    },
    role: {
      handler(val) {
        this.columnDefs[1].headerName = val;
      },
      immediate: true,
    },
  },
  computed: {
    user() {
      return this.$t("agGrid.user");
    },
    role() {
      return this.$t("agGrid.role");
    },
  },
  methods: {
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;
    },
    cancelDelete() {
      this.deleteDialog = false;
    },
    confirmDelete() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/users/deleteUser/${this.deletedRow.id}`)
        .then((response) => {
          console.log("Resource deleted:", response.data);
          this.closeModal();

          this.snackbar = true;
          this.color = "success";
          this.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          this.snackbar = true;
          this.color = "red";
          this.textAlert = i.response.data.error;
        });
    },
    actionCellRenderer(params) {
      let eGui = document.createElement("div");

      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (isCurrentRowEditing) {
        eGui.innerHTML = `
          <button class="action-button update" data-action="update">update</button>
          <button class="action-button cancel" data-action="cancel">cancel</button>
        `;
      } else {
        eGui.innerHTML = `
          <button class="action-button edit" data-action="edit">
            <i class="far fa-edit" style="color: #086eae;"></i>
          </button>
          <button class="action-button changePass " data-action="change">
            <span class="mdi mdi-key-alert-outline"style="color: #086eae;"></span>
              </button>
          <button class="action-button delete" data-action="delete">
             <i class="fas fa-times" style="color: #086eae;"></i>
           </button>


          `;
      }

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    },

    handleAction(action, rowData, CurrentIndex) {
      switch (action) {
        case "edit": {
          this.rowEdit = rowData;
          this.openModal();
          this.modalMode = "update";

          // this.selectedRowIndex = CurrentIndex;

          // this.getuser(rowData.id, (data) => {
          //   console.log("Edit clicked for row:", rowData);
          //   console.log("response data local 1:", data);

          //   // this.openModal();

          //   this.modalData = {
          //     id: data.id,
          //     username: data.username,
          //     password: data.password,
          //     fullname: data.fullname,
          //     email: data.email,
          //     role: data.role,
          //     groups: data.group,
          //     // Add more form fields as needed
          //   };
          // });

          break;
        }
        case "change":
          this.isModalPasswordOpen = true;
          this.modalMode = "Reset Password";
          this.rowEdit = rowData;
          break;
        case "delete":
          console.log("Delete clicked for row:", rowData);
          this.deleteDialog = true;
          this.deletedRow = rowData;

          // const index = this.rowData.findIndex(
          //   (item) => item.id === rowData.id
          // );

          // this.delete(rowData.id, () => {
          //   if (index !== -1) {
          //     this.rowData.splice(index, 1);
          //   }
          // });

          break;
        case "update":
          console.log("Update clicked for row:", rowData);
          break;
        case "cancel":
          console.log("Cancel clicked for row:", rowData);
          break;
        default:
          break;
      }
    },

    openModalAdd() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    openModal() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
      // location.reload()
    },
    closeModalPassword() {
      this.isModalPasswordOpen = false;
    },
    handleModalUpdate(formData) {
      //
      this.modalData = formData;
      console.log("formData", formData);
      console.log("this.selectedRowIndex", this.rowData[this.selectedRowIndex]);

      // this.rowData[this.modalData.id - 1] = updatedData;
      if (this.modalMode === "update") {
        console.log("update action ..." + JSON.stringify(this.rowData));
        this.update(formData, () => {
          console.log(
            "old DataList :" +
              JSON.stringify(this.DataList.users[this.selectedRowIndex])
          );

          this.DataList.users[this.selectedRowIndex] = {
            id: formData.id,
            username: formData.username,
            password: formData.password,
            fullname: formData.fullname,
            email: formData.email,
            role: formData.role,
            group: formData.groups,
          };

          console.log("new formData :" + JSON.stringify(formData));
          // this.selectedRowIndex = null;
        });
      } else {
        console.log("create action ...");

        console.log("formData : " + JSON.stringify(formData));
        // Handle the data returned from the modal here
        this.Create(formData, () => {
          this.DataList.users.push(formData);
        });

        // this.$set(this.rowData, this.rowData.length, formData);
      }
      this.closeModal();
    },

    // Fetch APIs
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    async Create(data, callback) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      console.log("token :" + csrfToken);
      console.log("DataList :" + JSON.stringify(this.DataList));

      // {"email":"mohamedkaabi90@gmail.com","role":"root","groups":["Group 2","Group 3"],"deactivateUser":true,"fullname":"name","password":"password","username":"username"}

      const params = {
        username: data.username,
        password: data.password,
        fullname: data.fullname,
        email: data.email,
        role: data.role,
        group: data.groups,
      };

      console.log("params are : " + JSON.stringify(params));

      axios.post("/users/createUser", params).then(
        (response) => {
          callback();
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
    },
    async delete(id, callback) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      console.log("token :" + csrfToken);
      console.log("user id :" + id);

      axios
        .delete(`/users/deleteUser/${id}`)

        .then((response) => {
          callback();
          // Handle the successful response
          console.log("Resource deleted:", response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error("Error deleting resource:", error);
        });
    },
    async update(data, callback) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      console.log("token :" + csrfToken);
      console.log("DataList :" + JSON.stringify(data));

      axios
        .put(`/users/modifyUser/${data.id}`, {
          username: data.username,
          password: data.password,
          fullname: data.fullname,
          email: data.email,
          role: data.role,
          group: data.groups,
        })
        .then((response) => {
          callback();
          // Handle the successful response
          console.log("Resource updated:", response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error("Error updating resource:", error);
        });
    },
    async getuser(id, callback) {
      axios
        .get(`/users/getUser/${id}`)
        .then((response) => {
          callback(response.data);
          // Handle the successful response
          console.log("Data received:", response.data);
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error("Error fetching data:", error);
        });
    },
    // Fetch APIs

    // Rest of the methods
  },
};
</script>

<style lang="scss">
.btn-add {
  background: #213e9f;
}
</style>
