<template>
  <div>
    <h4>Networks servers</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 " :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-server" @click="openModal">
      <span>addd Server </span>
    </v-btn>
    <Modal 
    :mode="modalMode"
    :isOpen="isModalOpen"
    @closeModal="closeModal"
    :initialData="modalData" 
    @updateModalData="handleModalUpdate" />
  </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue';
import Modal from '../components/layout/Modal.vue';

export default {
  name: 'NetworkServerManagement',
  components: {
    AgGridVue,
    Modal,
  },
  data() {
    return {
      isModalOpen: false,
      modalData: {}, // Add this line
      modalMode: '', // Mode of the modal ('create' or 'update')

      columnDefs: [
        { headerName: "Server name", field: "servername" },
        { headerName: "Type", field: "type" },
        { headerName: "Host Name", field: "hostname" },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer },
      ],
      rowData: [
        { id: 1, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 2, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 3, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 4, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 5, servername: "mfa", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
        { id: 6, servername: "mfa2", type: "Local + Mot de Passe à Usage Unique Temporel (TOTP)	", hostname: "DMS sdwan" },
      ],
      gridOptions: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: 'single',
        onRowEditingStarted: (params) => {
          params.api.refreshCells({
            columns: ['action'],
            rowNodes: [params.node],
            force: true,
          });
        },
        onRowEditingStopped: (params) => {
          params.api.refreshCells({
            columns: ['action'],
            rowNodes: [params.node],
            force: true,
          });
        },
      }
    };
  },

  methods: {
    handleModalUpdate(updatedData) {
      // Do something with the updated data
      this.modalData = updatedData;
      console.log("updatedData" , updatedData)
      console.log("this.rowData[this.modalData.id]" , this.rowData[this.modalData.id])

      // this.rowData[this.modalData.id - 1] = updatedData;
      if ( this.modalMode === "update")
      {
        this.$set(this.rowData, this.modalData.id - 1, updatedData);
      }
      else
      {
        this.$set(this.rowData, this.rowData.length, updatedData);
      }
      
      // Additional actions if needed
    },
    openModal() {

      this.modalMode = 'create';

      this.modalData = {
        servername: '',
        type: '',
        hostname: '',
        transport: [],
        protocolVersion: [],
        bindingIdentities: '',
        password: '',
        searchScope: [],
        baseDN: '',
        // Add more form fields as needed
      }

      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    actionCellRenderer(params) {
      let eGui = document.createElement('div');

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
          <button class="action-button delete" data-action="delete">
            <i class="fas fa-times" style="color: #086eae;"></i>
          </button>
        `;
      }

      eGui.querySelectorAll('.action-button').forEach((button) => {
        button.addEventListener('click', () => {
          const action = button.getAttribute('data-action');
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
    },
    handleAction(action, rowData) {
      switch (action) {
        case 'edit':
          {
            console.log('Edit clicked for row:', rowData);

            this.openModal()

            this.modalMode = 'update';

            this.modalData = {
              id : rowData.id ,
              servername: rowData.servername,
              type: rowData.type,
              hostname: rowData.hostname,
              transport: [],
              protocolVersion: [],
              bindingIdentities: '',
              password: '',
              searchScope: [],
              baseDN: '',
              // Add more form fields as needed
            }

            break;
          }
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
  }
};
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
