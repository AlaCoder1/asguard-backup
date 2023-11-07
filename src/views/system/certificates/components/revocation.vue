<template>
  <div
    class="certificats-management"
    style="display: flex; flex-direction: column; height: 100%"
  >
    <h4>List Revocation per authority</h4>
    <v-divider></v-divider>

    <div style="height: 100%">
      <div style="display: flex; flex-direction: row; height: 100%">
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            :columnDefs="columnRevocation"
           
            style="width: 100%; height: 100%"
          
            @grid-ready="onGridReady"
          />
        </div>
      </div>
    </div>

    <div style="display: flex; justify-content: flex-end; margin-top: 20px">
      <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
        <span class="text-white" style="text-transform: lowercase"
          >Ajouter révocation</span
        >
      </v-btn>
    </div>
    <ModalCertifRevocation
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
import ModalCertifRevocation from "@/components/modals/ModalCertifRevocation.vue";
export default {
  props: {
    authoritesData: {
      type: Array,
      required: true,
    },
  },
  components: {
    AgGridVue,
    ModalCertifRevocation,
  },

  data() {
    return {
      listAuthRevoc: null,
      modalMode: "",
      rowEdit: {},
      modalData: {},
      isModalOpen: false,

      columnRevocation: [
        { headerName: "nom", field: "nom" },
        {
          headerName: "list of authority certificate",
          field: "list_revoc",
        },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataRevocation: null,
    };
  },
  watch: {
    authoritesData(newValue) {
      this.listAuthRevoc = newValue;

      if (newValue) {
        let infoRevocCertif = newValue.map((element) => {
          return {
            id: element.id,
            nom: element.name,
            list_revokation: element.list_revokation,
            list_revoc: element.list_revokation.map((i) => {
              return i.name;
            }),
          };
        });
        this.rowDataRevocation = infoRevocCertif;
        setTimeout(() => {
          this.gridApi.setRowData(this.rowDataRevocation);
        }, 5);
      }
    },
  },
  methods: {
    openModal() {
      console.log("ok");
      this.modalData = {};
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
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
          class="action-button show"  
          data-action="show">
          <span class="mdi mdi-eye  fa-lg" style="color: #086eae;font-size: 24px;"></span>
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
        case "show":
          this.rowEdit = rowData;
          this.openModal();
          this.modalMode = "update";
          console.log("Edit clicked for row:", rowData);
          break;
        default:
          break;
      }
    },
  },
};
</script>
