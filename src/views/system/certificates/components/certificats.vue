<template>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>certificats</h4>
    <v-divider></v-divider>

    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      :columnDefs="columnCertificats"
      :rowData="rowDataCertificats"
      :gridOptions="gridOptions"
      style="width: 100%; height: 100%"
      @grid-size-changed="onGridSizeChanged"
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
          >Ajouter certificats</span
        >
      </v-btn>
    </div>
    <ModalAddEditCertif
      :allCertifAuth="allCertifAuth"
      :isOpen="isModalOpen"
      :editRow="rowEdit"
      v-model="isModalOpen"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
    <ModalRevocation
      :isOpen="isModalOpenRevoce"
      :editRow="rowEdit"
      v-model="isModalOpenRevoce"
      :mode="modalMode"
      @closeModal="closeModal"
      :initialData="modalData"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";
import ModalAddEditCertif from "@/components/modals/ModalAddEditCertif.vue";
import ModalRevocation from "@/components/modals/ModalRevocation.vue";
export default {
  props: {
    certifData: {
      type: Array,
      required: true,
    },
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalAddEditCertif,
    ModalRevocation,
  },
  data() {
    return {
      allCertifAuth:null,
      modalMode: "",
      rowEdit: {},
      isModalOpenRevoce: false,
      modalData: {},
      isModalOpen: false,
      columnCertificats: [
        { headerName: "nom", field: "nom" },
        { headerName: "nom unique", field: "nom_unique" },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataCertificats: [

      ],
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
        this.allCertifAuth = infoAuth;
      }
    },
    certifData(newValue) {
      console.log('newval',newValue)
      
      // if (newValue) {
      //   let infoCertif = newValue.map((element) => {
      //     console.log("eeleme,t", element);
      //     return {
      //       nom: element.name ?? "",
      //       certificats: element.certificats ?? 0,
      //       nom_unique: element.common_name ?? "",
      //       id: element.id,
      //     };
      //   });
      //   this.rowDataCertificats = infoCertif;
      //   setTimeout(() => {
      //     this.gridApi.setRowData(this.rowDataCertificats);
      //   }, 2000);
      // }
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
    openModalAdd() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
      this.isModalOpen = true;
    },
    openModalRevoce() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "revoce"; // Assuming you want to open the modal in create mode
      this.isModalOpenRevoce = true;
    },
    closeModal() {
      this.isModalOpen = false;
      this.isModalOpenRevoce = false;
      // location.reload()
    },
    actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      eGui.innerHTML = `
       

      <button 
          class="action-button revoce"
          data-action="revoce">
          <i class="mdi mdi-skull-outline" style="color: #086eae;font-size: 20px;"></i>
          </button>
      <button 
        class="action-button lock"
        data-action="lock">
     
        <i class="fa fa-unlock-alt" aria-hidden="true" style="color: #086eae;font-size: 20px;"></i>
        </button>
   
          <button 
          class="action-button download"
          data-action="export">
             <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i> 
          </button>
        <button 
          class="action-button download"
          data-action="download">
          <i class="mdi mdi-download-circle-outline" style="color: #086eae;font-size: 20px;"></i> 
        </button>
        
     
        
      
        `;

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
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
        case "update":
          console.log("Update clicked for row:", rowData);
          break;
        case "revoce":
          console.log("revoce row:", rowData);
          this.rowEdit = rowData;
          this.openModalRevoce();
          this.modalMode = "revoce";
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
