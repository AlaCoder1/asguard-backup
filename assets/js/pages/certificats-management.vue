<template>
  <div class="ml-3">
    <div>
      <div class="certificats-management" style="display: flex; flex-direction: column; height: 100%">
        <h4>Authorités</h4>
        <v-divider></v-divider>
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnAuthority"
          :rowData="rowDataAuthority" :gridOptions="gridOptions" style="width: 100%; height: 100%;"
          @first-data-rendered="onFirstDataRendered" @grid-size-changed="onGridSizeChanged" />
      </div>
      <div style="margin-left: 400px !important;">
        <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
          <span class="text-white" style="text-transform: lowercase;">Ajouter Authorités</span>
        </v-btn>
      </div>
    </div>
    <div>
      <div class="certificats-management" style="display: flex; flex-direction: column; height: 100%">
        <h4>certificats</h4>
        <v-divider></v-divider>
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnCertificats"
          :rowData="rowDataCertificats" :gridOptions="gridOptions" style="width: 100%; height: 100%;"
          @first-data-rendered="onFirstDataRendered" @grid-size-changed="onGridSizeChanged" />
      </div>
      <div style="margin-left: 400px !important;">
        <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
          <span class="text-white" style="text-transform: lowercase;">Ajouter certificats</span>
        </v-btn>
      </div>
    </div>
    <div>
      <div class="certificats-management" style="display: flex; flex-direction: column; height: 100%">
        <h4>Révocation</h4>
        <v-divider></v-divider>
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnRevocation"
          :rowData="rowDataRevocation" :gridOptions="gridOptions" style="width: 100%; height: 100%;"
          @first-data-rendered="onFirstDataRendered" @grid-size-changed="onGridSizeChanged" />
      </div>
      <div style="margin-left: 400px !important;">
        <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
          <span class="text-white" style="text-transform: lowercase;">Ajouter révocation</span>
        </v-btn>
      </div>
    </div>
  </div>
</template>
<script>
import { AgGridVue } from 'ag-grid-vue';
export default {
  name: 'CertificatsManagement',
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
      columnAuthority: [
        { headerName: "nom", field: "nom", minWidth: 150 },
        { headerName: "interne", field: "interne", minWidth: 150 },
        { headerName: "emetteur", field: "emetteur", minWidth: 150 },
        { headerName: "certificats", field: "certificats", minWidth: 150 },
        { headerName: "nom unique", field: "nom_unique", minWidth: 150 },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer, minWidth: 150, editable: false, sortable: false, filter: false },
      ],
      rowDataAuthority: [
        { id: 1, nom: "root", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
        { id: 2, nom: "admin", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
        { id: 3, nom: "user", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
        { id: 4, nom: "client", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
        { id: 5, nom: "none", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
        { id: 6, nom: "test", interne: "oui", emetteur: "oui", certificats: "oui", nom_unique: "oui" },
      ],
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
      columnRevocation: [
        { headerName: "nom", field: "nom", minWidth: 150 },
        { headerName: "emetteur", field: "emetteur", minWidth: 150 },
        { headerName: "nom unique", field: "nom_unique", minWidth: 450 },
        { headerName: "Actions", cellRenderer: this.actionCellRenderer, minWidth: 150, editable: false, sortable: false, filter: false },
      ],
      rowDataRevocation: [
        { id: 1, nom: "root", emetteur: "oui", nom_unique: "oui" },
        { id: 2, nom: "admin", emetteur: "oui", nom_unique: "oui" },
        { id: 3, nom: "user", emetteur: "oui", nom_unique: "oui" },
        { id: 4, nom: "client", emetteur: "oui", nom_unique: "oui" },
        { id: 5, nom: "none", emetteur: "oui", nom_unique: "oui" },
        { id: 6, nom: "test", emetteur: "oui", nom_unique: "oui" },
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
      },
    };
  },
  methods: {
    actionCellRenderer(params) {
      let eGui = document.createElement('div');
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
      }
      else {
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
          console.log('Edit clicked for row:', rowData);
          break;
        case 'export':
          console.log('Download clicked for row:', rowData);
          this.exportGridDataAsCsv();
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
    exportGridDataAsCsv() {
      const params = {
        fileName: 'export',
      };
      this.gridOptions.api.exportDataAsCsv(params);
    },
    onFirstDataRendered(params) {
      params.api.sizeColumnsToFit();
    },
    onGridSizeChanged(params) {
      // get the current grids width
      var gridWidth = document.getElementById('grid-wrapper').offsetWidth;
      // keep track of which columns to hide/show
      var columnsToShow = [];
      var columnsToHide = [];
      // iterate over all columns (visible or not) and work out
      // now many columns can fit (based on their minWidth)
      var totalColsWidth = 0;
      var allColumns = params.columnApi.getAllColumns();
      if (allColumns && allColumns.length > 0) {
        for (var i = 0; i < allColumns.length; i++) {
          var column = allColumns[i];
          totalColsWidth += column.getMinWidth() || 0;
          if (totalColsWidth > gridWidth) {
            columnsToHide.push(column.getColId());
          } else {
            columnsToShow.push(column.getColId());
          }
        }
      }
      // show/hide columns based on current grid width
      params.columnApi.setColumnsVisible(columnsToShow, true);
      params.columnApi.setColumnsVisible(columnsToHide, false);
      // fill out any available space to ensure there are no gaps
      params.api.sizeColumnsToFit();
    },
  },
};

</script>
<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
