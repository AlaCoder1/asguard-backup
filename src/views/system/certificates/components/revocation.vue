<template>
        <div class="certificats-management" style="display: flex; flex-direction: column; height: 100%">
        <h4>Révocation</h4>
        <v-divider></v-divider>  
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" :columnDefs="columnRevocation"
          :rowData="rowDataRevocation" :gridOptions="gridOptions" style="width: 100%; height: 100%;"
          @grid-size-changed="onGridSizeChanged" /> 
              <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
        <v-btn color="dms_blue_dark" :rounded="true" class="mt-3 add-btn-user">
          <span class="text-white" style="text-transform: lowercase;">Ajouter révocation</span>
        </v-btn>
      </div>
      </div>

</template>
<script>
import { AgGridVue } from "ag-grid-vue3";
export default {
  components: {
    AgGridVue,
  },
  data() {
    return {
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
}
  },
};
</script>
