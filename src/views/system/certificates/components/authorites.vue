<template>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>Authorités</h4>
    <v-divider></v-divider>
    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      :columnDefs="columnAuthority"
      :gridOptions="gridOptions"
      style="width: 100%; height: 100%"
      @grid-ready="onGridReady"
    />
    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px">
      <v-btn
        type="submit"
        color="asguard_primary_light"
        :rounded="true"
        class="mt-3 btn-add"
        @click="openModalAdd"
      >
        <span class="text-white" style="text-transform: lowercase"
          >Ajouter Authorités</span
        >
      </v-btn>
    </div>
    <ModalAddAuth
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this certif ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete"
            >Delete</v-btn
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
import axios from "axios";
import ModalAddAuth from "@/components/modals/ModalAddAuth.vue";
import { AgGridVue } from "ag-grid-vue3";
export default {
  props: {
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalAddAuth,
  },
  data() {
    return {
      textAlert: "",
      color: "",
      snackbar: false,
      deletedRow: null,
      deleteDialog: false,
      getRowId: null,
      dataAuth: null,
      modalData: {},
      modalMode: "",
      rowEdit: {},
      isModalOpen: false,
      columnAuthority: [
        { headerName: "nom", field: "nom", minWidth: 150 },
        { headerName: "certificats", field: "certificats", minWidth: 150 },
        {
          headerName: "distingushed name",
          cellRenderer: this.formatedDn,
          minWidth: 100,
        },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          minWidth: 150,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataAuthority: null,

      gridOptions: {
        rowHeight: 120,
        pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",
      },
    };
  },

  watch: {
    authoritesData(newValue) {
      this.dataAuth = newValue;
      if (newValue) {
        let infoAuth = newValue.map((element) => {
          return {
            id: element.id,
            nom: element.name,
            certificats: element.certificates,
            nom_unique: element.common_name,
            country_code: element.country_code,
            state: element.state,
            city: element.city,
            organization: element.organization,
            email: element.email,
            valid_from: element.valid_from,
            valid_until: element.valid_until,
          };
        });
        this.rowDataAuthority = infoAuth;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataAuthority);
        }, 5);
      }
    },
  },
  computed: {},
  methods: {
    formatedDn(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
      emailAddress= ${data.data.email},ST=${data.data.state}, O=${data.data.organization}, <br/>
        L=${data.data.city},CN=${data.data.nom_unique},C=${data.data.country_code}<br/>
        Valide à partir du :${data.data.valid_from}<br/>
        Valide jusqu'au :${data.data.valid_until}
        `;
      eGui.style.lineHeight = "2";

      return eGui;
    },

    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;

      window.addEventListener("resize", function () {
        setTimeout(function () {
          params.api.sizeColumnsToFit();
        });
      });

      params.api.sizeColumnsToFit();
    },
    openModalAdd() {
      this.modalData = {};
      this.modalMode = "create";
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
      this.deleteDialog = false;
      // location.reload()
    },
    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
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
          class="action-button download"
          data-action="export" title="download CRT">
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
          <button 
          class="action-button download"
          data-action="exportKey" title="download Private Key">
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae; font-size: 20px;"></i>
        </button>
        `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
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

    download(id, type, fileExtention) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        type: type,
      };
      axios
        .post(`/certificates/exportCertAuth/${id}`, payload)
        .then((response) => {
          console.log("response", response.data.cert);
          const text = response.data.cert;
          const blob = new Blob([text], {
            type: "application/x-x509-ca-cert",
          });

          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.style.display = "none";
          a.href = url;
          a.download = fileExtention;

          document.body.appendChild(a);
          a.click();

          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          if (response.status == "201") {
            console.log("success");
          } else {
            console.log("error");
          }
        })
        .catch((i) => {
          console.log("i", i.response.data.error);
          this.snackbar = true;
          this.color = "red";
          this.textAlert = i.response.data.error;
        });
    },
    cancelDelete() {
      this.deleteDialog = false;
    },
    confirmDelete() {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/certificates/deleteCertAuth/${this.deletedRow.id}`)
        .then((response) => {
          if (response.status == "200") {
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
          console.log("i", i.response);
          this.snackbar = true;
          this.color = "red";
          this.textAlert = i.response.data.error;
        });
    },
    handleAction(action, rowData) {
      switch (action) {
        case "edit":
          this.rowEdit = rowData;
          this.openModalAdd();
          this.modalMode = "update";
          break;
        case "export":
          let id = rowData.id;
          let type = "certificate";
          let fileExtention = `${rowData.nom}.crt`;

          this.download(id, type, fileExtention);

          break;
        case "delete":
          this.deleteDialog = true;
          this.deletedRow = rowData;

          break;
        case "exportKey":
          let rowId = rowData.id;
          let typeName = "private_key";
          let fileExt = `${rowData.nom}.key`;
          this.download(rowId, typeName, fileExt);

          break;
        case "cancel":
          break;
        default:
          break;
      }
    },
  },
};
</script>
