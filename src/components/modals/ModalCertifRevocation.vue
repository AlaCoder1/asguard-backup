<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ nameCertif }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row class="mb-5">
                <v-col cols="12" class="mb-n5">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    :columnDefs="columnCertificats"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :gridOptions="gridOptions"
                    :rowData="rowDataCertificats"
                    style="width: 100%; height: 100%"
                    @grid-ready="onGridReady"
                  />
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
import { AgGridVue } from "ag-grid-vue3";

export default {
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
  components: {
    AgGridVue,
  },
  data() {
    return {
      textAlert: "",
      color: "",
      snackbar: false,
      nameCertif: null,
      modalMode: "",
      rowEdit: {},
      isModalOpenRevoce: false,
      modalData: {},
      isModalOpen: false,
      columnCertificats: [
        { headerName: this.$t("agGrid.certificat"), field: "certif", minWidth: 150 },
        { headerName: this.$t("agGrid.raison"), field: "raison", minWidth: 250 },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          minWidth: 150,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataCertificats: null,
    };
  },
  watch: {
    isOpen(val) {
      this.openModal = val;
    },
    editRow(val) {
      this.nameCertif = val.nom;
      if (val) {
        let infoList = val.list_revokation.map((element) => {
          return {
            id: element.id,
            certif: element.name,
            raison: element.reason,
          };
        });
        this.rowDataCertificats = infoList;
        // setTimeout(() => {
        // this.gridApi.setRowData(this.rowDataCertificats);
        // });
      }
    },
  },
  methods: {
    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;

      params.api.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          params.api.sizeColumnsToFit();
        });
      });

      params.api.sizeColumnsToFit();
    },
    closeModal() {
      this.$emit("closeModal");
    },
    openModalRevoce() {
      this.modalData = {};
      this.modalMode = "revoce"; // Assuming you want to open the modal in create mode
      this.isModalOpenRevoce = true;
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
          class="action-button lock"
          data-action="lock">
       
         
          <i class="fa fa-unlock-alt" style="color: #086eae; aria-hidden="true"></i>
          </button>
        <button 
        
   
      
       
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
    handleAction(action, rowData) {
      switch (action) {
        case "lock":
          const csrfToken = this.getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .put(`/certificates/unrevokeCertificate/${rowData.id}`)
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

          break;
        default:
          break;
      }
    },
  },
};
</script>
<style lang="scss">
@import "font-awesome/css/font-awesome.css";
@import "~@mdi/font/css/materialdesignicons.min.css";
</style>
