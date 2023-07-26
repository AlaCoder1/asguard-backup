<template>
  <div>
    <h4>Networks admins</h4>
    <ag-grid-vue domLayout="autoHeight" class="ag-theme-alpine mt-3 m-w-80" :columnDefs="columnDefs" :rowData="rowData"
      :gridOptions="gridOptions" />
    <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user" @click="openModal">
      <span class="text-white">Add rr</span>
    </v-btn>
    <Modal_User :mode="modalMode" 
    :isOpen="isModalOpen" 
    @closeModal="closeModal" 
    :initialData="modalData"
      @updateModalData="handleModalUpdate" />
  </div>
</template>
<script>
import { AgGridVue } from 'ag-grid-vue';
import Modal_User from '../components/layout/Modal_User.vue';

export default {
  name: 'UserManagement',
  components: {
    AgGridVue,
    Modal_User,

  },
  props: {
    // users: {
    //   type: Object,
    //   required: true,
    // }
  },
  data() {
    return {
      isModalOpen: false,
      modalData: {}, // Add this line
      modalMode: '', // Mode of the modal ('create' or 'update')

      columnDefs: [
        { headerName: "User", field: "user" },
        { headerName: "Role", field: "role" },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer },
      ],
      rowData: [
        { id: 1, user: "root (root@numeryx.fr)", role: "Super Root" },
        { id: 2, user: "admin (admin@numeryx.fr)", role: "Root" },
        { id: 3, user: "user (admin@numeryx.fr)", role: "Root" },
        { id: 4, user: "client (admin@numeryx.fr)", role: "Root" },
        { id: 5, user: "none (admin@numeryx.fr)", role: "Root" },
        { id: 6, user: "test (admin@numeryx.fr)", role: "Root" },

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
      eGui.querySelectorAll('.action-button').forEach((button) => {
        button.addEventListener('click', () => {
          const action = button.getAttribute('data-action');
          this.handleAction(action, params.node.data);
        });
      });

      return eGui;
    },
    handleAction(action, rowData) {
      // Perform the desired action based on the action type
      switch (action) {
        case 'edit':
          console.log('Edit clicked for row:', rowData);
          // Perform edit action
          break;
        case 'delete':
          console.log('Delete clicked for row:', rowData);
          // Perform delete action
          const index = this.rowData.findIndex(item => item.id === rowData.id);
          console.log(index);
          if (index !== -1) {
            this.rowData.splice(index, 1); // Remove the element from the rowData array
          }
          break;
        case 'update':
          console.log('Update clicked for row:', rowData);
          // Perform update action
          break;
        case 'cancel':
          console.log('Cancel clicked for row:', rowData);
          // Perform cancel action
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
