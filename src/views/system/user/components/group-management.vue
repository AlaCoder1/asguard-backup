<template>
  <div>
    <h4>{{ $t('networksGroups') }}</h4>

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
        class="mt-3 add-btn-group"
        @click="openModal"
      >
        <span class="text-white">{{ $t("button.addGroup") }}</span>
      </v-btn>
    </div>
    <Modal_Group
      :editRow="rowEdit"
      :mode="modalMode"
      :isOpen="isModalOpen"
      @closeModal="closeModal"
      :initialData="modalData"
      @updateModalData="handleModalUpdate"
    />
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{ $t("delete.DeleteConfirmation") }}</v-card-title>
        <v-card-text>{{ $t("delete.questiongroup") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">{{ $t("PageGeneral.form.Cancel") }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete"
            >{{ $t("PageGeneral.form.Delete") }}</v-btn
          >
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
import { AgGridVue } from "ag-grid-vue3";
import Modal_Group from "@/components/modals/ModalGroup.vue";
import axios from "axios";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "GroupManagement",
  components: {
    AgGridVue,
    Modal_Group,
  },
  props: {
    DataList: {
      type: Array,
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
      modalMode: "",
      isModalOpen: false,
      modalData: {},
      selectedRowIndex: null,
      columnDefs: [
        {
          headerName: this.testGroupe,
          field: "groupname",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        {
          headerName: "Description",
          field: "description",
          width: 90,
          minWidth: 50,
          flex: 1,
        },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer },
      ],
      rowData: [],
      gridOptions: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",
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
  computed: {
    testGroupe() {
      return this.$t("agGrid.group");
    },
  },

  watch: {
    DataList: {
      handler(newData) {
        this.rowData = newData; // Update rowData with the new prop value
      },
      immediate: true, // This will trigger the watcher when the component is created to initialize rowData
    },
    testGroupe: {
      handler(val) {
        this.columnDefs[0].headerName = val;
      },
      immediate: true,
    },
  },

  methods: {
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;

      // params.api.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     params.api.sizeColumnsToFit();
      //   });
      // });

      // params.api.sizeColumnsToFit();
    },
    cancelDelete() {
      this.deleteDialog = false;
    },
    confirmDelete() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      console.log("token :" + csrfToken);
      console.log("group id :" + this.deletedRow.id);

      axios
        .delete(`/groups/deleteGroup/${this.deletedRow.id}`)

        .then((response) => {
          // Handle the successful response
          this.deleteDialog = false;
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
    openModal() {
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
      location.reload();
    },

    handleModalUpdate(formData) {
      console.log("formDataformDataformDataformData", formData);
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
              JSON.stringify(this.DataList[this.selectedRowIndex])
          );

          this.$set(this.DataList, this.selectedRowIndex, {
            groupname: formData.groupname,
            description: formData.description,
            sudoers: formData.sudoers,
          });

          // this.DataList[this.selectedRowIndex] =
          // {
          //   groupname: formData.groupname,
          //   description: formData.description,
          //   sudoers: formData.sudoers,
          // };

          console.log("new formData :" + JSON.stringify(formData));
          // this.selectedRowIndex = null;
        });
      } else {
        console.log("create action ...");

        console.log("formData : " + JSON.stringify(formData));
        // Handle the data returned from the modal here
        this.Create(formData, () => {
          this.DataList.push(formData);
        });

        // this.$set(this.rowData, this.rowData.length, formData);
      }
      this.closeModal();
    },

    actionCellRenderer(params) {
      let eGui = document.createElement("div");

      let editingCells = params.api.getEditingCells();
      // checks if the rowIndex matches in at least one of the editing cells
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (isCurrentRowEditing) {
        eGui.innerHTML = `
        <button  
          class="action-button update"
          data-action="update">
               update  
        </button>
        <button  
          class="action-button cancel"
          data-action="cancel">
               cancel
        </button>
        `;
      } else {
        eGui.innerHTML = `
        <button 
          class="action-button edit"  
          data-action="edit">
             <i class="far fa-edit" style="color: #086eae;"></i> 
          </button>
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
        </button>
        `;
      }

      // Add event listeners to handle button clicks
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    },
    handleAction(action, rowData, CurrentIndex) {
      // Perform the desired action based on the action type
      switch (action) {
        case "edit": {
          this.selectedRowIndex = CurrentIndex;
          this.openModal();
          this.modalMode = "update";
          this.rowEdit = rowData;

          this.getgroup(rowData.id, (data) => {
            console.log("Edit clicked for row Group:", rowData);
            console.log("response data local 1:", data);

            // this.modalData = {
            //   id: data?.id,
            //   gid: data?.gid,
            //   groupname: data?.groupname,
            //   description: data?.description,
            //   sudoers: data?.sudoers,
            //   // Add more form fields as needed
            // }
          });

          break;
          // Perform edit action
        }
        case "delete":
          console.log("Delete clicked for row:", rowData);
          this.deleteDialog = true;
          this.deletedRow = rowData;

          // const index = this.rowData.findIndex(item => item.id === rowData.id);

          // this.delete(rowData.id, () => {
          //   if (index !== -1) {
          //     this.rowData.splice(index, 1);
          //   }
          // })

          break;
        case "update":
          console.log("Update clicked for row:", rowData);
          // Perform update action
          break;
        case "cancel":
          console.log("Cancel clicked for row:", rowData);
          // Perform cancel action
          break;
        default:
          break;
      }
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
        groupname: data.groupname,
        description: data.description,
        sudoers: data.sudoers,
      };

      console.log("params are : " + JSON.stringify(params));

      axios.post("/groups/createGroup", params).then(
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
      console.log("group id :" + id);

      axios
        .delete(`/groups/deleteGroup/${id}`)

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
        .put(`/groups/groupChangeGroupname/${data.id}`, {
          Newgroupname: data.groupname,
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
    async getgroup(id, callback) {
      axios
        .get(`/groups/getGroup/${id}`)
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
  },
};
</script>
<style lang="scss">
.add-btn-group {
  background: #213e9f;
}
</style>
