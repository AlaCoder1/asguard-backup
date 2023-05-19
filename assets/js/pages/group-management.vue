<template>
        <div> 
            <h4>Networks groups</h4>
            <ag-grid-vue
                domLayout="autoHeight"
                class="ag-theme-alpine mt-3 m-w-80"
                :columnDefs="columnDefs"
                :rowData="rowData"
                :gridOptions="gridOptions"
            />        
            <v-btn
                color="dms_blue_dark"
                :rounded="true"
                class="mt-3 add-btn-user"
            >
                <span class="text-white" >Add Group</span>
            </v-btn>       
         </div>
        
</template>
<script>
import { AgGridVue } from 'ag-grid-vue';
export default {
    name: 'GroupManagement',
    components: {
        AgGridVue,
    },
    props: {
        users: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            columnDefs: [
                { headerName: "Group", field: "group" },
                { headerName: "Description", field: "description" },
                { headerName: "Actions", cellRenderer: this.actionCellRenderer },
            ],
            rowData: [
                { id:1, group:"Support", description: "Super Root"  },
                { id:2, group: "Sudoers", description: "Sudoers"  },
                { id:3, group: "Observateurs", description: "Observateurs"  },
                { id:4, group: "Admins", description: "Admins"  },
                { id:5, group: "Users", description: "Users"  },
                { id:6, group: "tests", description: "tests"  },
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
