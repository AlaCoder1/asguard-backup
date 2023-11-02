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
      getRowId: null,
      dataAuth: null,
      modalData: {},
      modalMode: "",
      rowEdit: {},
      isModalOpen: false,
      columnAuthority: [
        { headerName: "nom", field: "nom", minWidth: 150 },
        { headerName: "certificats", field: "certificats", minWidth: 150 },
        { headerName: "nom unique", field: "nom_unique", minWidth: 150 },
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
          console.log("eeleme,t", element);
          return {
            nom: element.name ?? "",
            certificats: element.certificates,
            nom_unique: element.common_name ?? "",
            id: element.id,
          };
        });
        this.rowDataAuthority = infoAuth;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataAuthority);
        }, 2000);
      }
    },
  },
  methods: {
    // async forceFileDownload(response) {
    //   try {
    //     const blob = new Blob([response]);
    //     const url = window.URL.createObjectURL(blob);
    //     const link = document.createElement('a');
    //     link.href = url;
    //     link.setAttribute('download', 'file.crt'); // or any other extension
    //     document.body.appendChild(link);
    //     link.click();
    //     window.URL.revokeObjectURL(url); // Clean up the URL after download
    //   } catch (error) {
    //     console.error('Error during file download:', error);
    //   }
    // },

    onGridReady(params) {
      this.gridApi = params.api;
      this.gridColumnApi = params.columnApi;
      // this.gridApi.setRowData(this.rowDataAuthority);

      params.api.sizeColumnsToFit();
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
          data-action="export">
             <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i> 
          </button>
          <button 
          class="action-button download"
          data-action="exportKey">
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

    download(id,type,fileExtention) {
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        type: type,
      };
      axios.post(`/certificates/exportCertAuth/${id}`, payload).then(
        (response) => {
          console.log("res", response.data.cert);

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
        },
        (error) => {
          console.log(error);
        }
      );
    },
    handleAction(action, rowData) {
      switch (action) {
        case "edit":

          this.rowEdit = rowData;
          this.openModalAdd();
          this.modalMode = "update";
          console.log("Edit clicked for row:", rowData);
          break;
        case "export":
          console.log("Download clicked for row:", rowData);
          console.log("rowData.name", rowData.id);
          let id = rowData.id
          let type ='certificate'
         let fileExtention = "certificate.crt"
          this.download(id,type,fileExtention);

          break;
        case "delete":
          console.log("Delete clicked for row:", rowData);
          const index = this.rowData.findIndex(
            (item) => item.id === rowData.id
          );
          if (index !== -1) {
            this.rowData.splice(index, 1);
          }
          break;
        case "exportKey":
          console.log("Update clicked for row:", rowData);
          let rowId = rowData.id
          let typeName ='private_key'
          let fileExt = "private_Key.key"
          this.download(rowId,typeName,fileExt);
          
          break;
        case "cancel":
          console.log("Cancel clicked for row:", rowData);
          break;
        default:
          break;
      }
    },
  },
};
</script>
