<template>
  <v-row justify="center">
    <v-dialog v-model="openModal" persistent width="600">
      <form ref="myForm" @submit.prevent="submitForm">
        <v-card>
          <v-card-title>
            <span class="text-h5">Test</span>
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
                    :rowData="rowDataCertificats"
                    :alwaysShowHorizontalScroll="false"
                    :alwaysShowVarticalScroll="false"
                    :gridOptions="gridOptions"
                    style="width: 100%; height: 100%"
                    @grid-size-changed="onGridSizeChanged"
                  />
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
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>
  </v-row>
</template>

<script>
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
      modalMode: "",
      rowEdit: {},
      isModalOpenRevoce: false,
      modalData: {},
      isModalOpen: false,
      columnCertificats: [
        { headerName: "certificat", field: "certif", minWidth: 150 },
        { headerName: "raison", field: "raison", minWidth: 150 },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRenderer,
          minWidth: 150,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataCertificats: [{ id: 1, certif: "certif", raison: "raison" }],
    };
  },
  watch: {
    isOpen(val) {
      this.openModal = val;
    },
  },
  methods: {
    closeModal() {
      this.$emit("closeModal");
    },
    openModalRevoce() {
      console.log("ok");
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
    handleAction(action, rowData) {
      switch (action) {
        case "lock":
          console.log("revoce row:", rowData);
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
<style lang="scss">
@import "font-awesome/css/font-awesome.css";
@import "~@mdi/font/css/materialdesignicons.min.css";
</style>
