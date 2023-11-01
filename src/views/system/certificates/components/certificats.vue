<template>
   <div class="certificats-management" style="display: flex; flex-direction: column; height: 100%">
        <h4>certificats</h4>
        <v-divider></v-divider>  
        
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnCertificats"
          :rowData="rowDataCertificats" :gridOptions="gridOptions" style="width: 100%; height: 100%;"
          @grid-size-changed="onGridSizeChanged" /> 
   
        <div style="display: flex; justify-content: flex-end ; margin-bottom: 10px;">
      <v-btn
        type="submit"
        color="asguard_primary_light"
        :rounded="true"
        class="mt-3 btn-add"
        @click="openModalAdd"
      >
        <span class="text-white " style="text-transform: lowercase"
          >Ajouter certificats</span
        >
      </v-btn>
    </div>
    <ModalAddEditCertif
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
import { AgGridVue } from "ag-grid-vue3";
import ModalAddEditCertif from "@/components/modals/ModalAddEditCertif.vue";
export default {
  components: {
    AgGridVue,
    ModalAddEditCertif
  },
  data() {
    return {
      modalMode: "",
      rowEdit:{},
      modalData: {},
      isModalOpen: false,
      columnCertificats: [
        { headerName: "nom", field: "nom", minWidth: 150 },
        { headerName: "emetteur", field: "emetteur", minWidth: 150 },
        { headerName: "nom unique", field: "nom_unique", minWidth: 450 },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer, minWidth: 150, editable: false, sortable: false, filter: false },
      ],
      rowDataCertificats: [
        { id: 1, nom: "root", emetteur: "oui", nom_unique: "oui" },
        { id: 2, nom: "admin", emetteur: "oui", nom_unique: "oui" },
        { id: 3, nom: "user", emetteur: "oui", nom_unique: "oui" },
        { id: 4, nom: "client", emetteur: "oui", nom_unique: "oui" },
        { id: 5, nom: "none", emetteur: "oui", nom_unique: "oui" },
        { id: 6, nom: "test", emetteur: "oui", nom_unique: "oui" },
      ],
}
  },
  methods: {
    openModalAdd() {
      console.log("ok");
      this.modalData = {};
      this.modalMode = "create"; // Assuming you want to open the modal in create mode
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
          class="action-button edit"  
          data-action="edit">
             <i class="far fa-edit" style="color: #086eae;"></i> 
          </button>
        <button 
          class="action-button download"
          data-action="export">
             <i class="fas fa-download" style="color: #086eae;"></i> 
          </button>
        <button 
          class="action-button delete"
          data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
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
        handleAction(action, rowData) {
      switch (action) {
        case 'edit':
          this.rowEdit = rowData;
          this.openModalAdd();
          this.modalMode = "update";
          console.log('Edit clicked for row:', rowData);
          break;
        case 'export':
          console.log('Download clicked for row:', rowData);
         
          break;
        case 'delete':
          console.log('Delete clicked for row:', rowData);
          const index = this.rowData.findIndex(item => item.id === rowData.id);
          if (index !== -1) {
            this.rowData.splice(index, 1);
          }
          break;
        case 'update':
          console.log('Update clicked for row:', rowData);
          break;
        case 'cancel':
          console.log('Cancel clicked for row:', rowData);
          break;
        default:
          break;
      }
    },
  },
};
</script>
