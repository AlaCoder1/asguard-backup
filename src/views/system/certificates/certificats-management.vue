<template>
  <div class="ml-3">
  
 <authorites />
 <certificats/>
 <revocation/>
 
</div>

</template>

<script>
import axios from "axios";
import { AgGridVue } from 'ag-grid-vue3';
import authorites from './components/authorites.vue'
import certificats from './components/certificats.vue'
import revocation from './components/revocation.vue'
export default {
  name: 'CertificatsManagement',
  components: {
    AgGridVue,
    authorites,
    certificats,
    revocation
  },
  props: {
  },
  data() {
    return {
   
     
    
      // gridOptions: {
      //   pagination: true,
      //   paginationPageSize: 5,
      //   rowSelection: 'single',
      //   onRowEditingStarted: (params) => {
      //     params.api.refreshCells({
      //       columns: ['action'],
      //       rowNodes: [params.node],
      //       force: true,
      //     });
      //   },
      //   onRowEditingStopped: (params) => {
      //     params.api.refreshCells({
      //       columns: ['action'],
      //       rowNodes: [params.node],
      //       force: true,
      //     });
      //   },
      // },
    };
  },
  beforeMount: async function () {
  
    this.getCertif()
  },
  methods: {
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
    getCertif(){
      const csrfToken = this.getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        
    axios.get("/certificates/getAllCertAuth").then(
        (response) => {
        console.log('res',response)
        },
        (error) => {
          console.log(error);
        }
      );
    },

    // actionCellRenderer(params) {
    //   let eGui = document.createElement('div');
    //   let editingCells = params.api.getEditingCells();
    //   let isCurrentRowEditing = editingCells.some((cell) => {
    //     return cell.rowIndex === params.node.rowIndex;
    //   });
    //   if (isCurrentRowEditing) {
    //     eGui.innerHTML = `
    //     <button  
    //       class="action-button update"
    //       data-action="update">
    //            update  
    //     </button>
    //     <button  
    //       class="action-button cancel"
    //       data-action="cancel">
    //            cancel
    //     </button>
    //     `;
    //   }
    //   else {
    //     eGui.innerHTML = `
    //     <button 
    //       class="action-button edit"  
    //       data-action="edit">
    //          <i class="far fa-edit" style="color: #086eae;"></i> 
    //       </button>
    //     <button 
    //       class="action-button download"
    //       data-action="export">
    //          <i class="fas fa-download" style="color: #086eae;"></i> 
    //       </button>
    //     <button 
    //       class="action-button delete"
    //       data-action="delete">
    //         <i class="fas fa-times" style="color: #086eae;"></i>
    //     </button>
    //     `;
    //   }
    //   eGui.querySelectorAll('.action-button').forEach((button) => {
    //     button.addEventListener('click', () => {
    //       const action = button.getAttribute('data-action');
    //       this.handleAction(action, params.node.data);
    //     });
    //   });

    //   return eGui;
    // },

    // exportGridDataAsCsv() {
    //   const params = {
    //     fileName: 'export',
    //   };
    //   this.gridOptions.api.exportDataAsCsv(params);
    // },
    // onFirstDataRendered(params) {
    //   params.api.sizeColumnsToFit();
    // },
    // onGridSizeChanged(params) {
    //   // get the current grids width
    //   var gridWidth = document.getElementById('grid-wrapper').offsetWidth;
    //   // keep track of which columns to hide/show
    //   var columnsToShow = [];
    //   var columnsToHide = [];
    //   // iterate over all columns (visible or not) and work out
    //   // now many columns can fit (based on their minWidth)
    //   var totalColsWidth = 0;
    //   var allColumns = params.columnApi.getAllColumns();
    //   if (allColumns && allColumns.length > 0) {
    //     for (var i = 0; i < allColumns.length; i++) {
    //       var column = allColumns[i];
    //       totalColsWidth += column.getMinWidth() || 0;
    //       if (totalColsWidth > gridWidth) {
    //         columnsToHide.push(column.getColId());
    //       } else {
    //         columnsToShow.push(column.getColId());
    //       }
    //     }
    //   }
    //   // show/hide columns based on current grid width
    //   params.columnApi.setColumnsVisible(columnsToShow, true);
    //   params.columnApi.setColumnsVisible(columnsToHide, false);
    //   // fill out any available space to ensure there are no gaps
    //   params.api.sizeColumnsToFit();
    // },
  },
};

</script>
<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
