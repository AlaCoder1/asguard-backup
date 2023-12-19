<template>
    <div class="mt-3 ml-3 mr-3">
      <v-row>
        <v-col cols="12">
          <h4>List of alerts</h4>
          <v-divider></v-divider>
          
         
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  id="filter-text-box"
                  v-model="filterText"
                  placeholder="Search"
                  clearable
                  hide-details
                  dense
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  @input="onFilterTextBoxChanged"
                ></v-text-field>
              </v-col>
            </v-row>
      
          <div style="display: flex; flex-direction: column">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              :columnDefs="columnRules"
              :rowData="rowDataAlerts.value"
              :defaultColDef="defaultColDef"
              :autoGroupColumnDef="autoGroupColumnDef"
              :rowGroupPanelShow="rowGroupPanelShow"
              @cell-clicked="cellWasClicked"
              @grid-ready="onGridReady"
              :pagination="true"
              :paginationPageSize="10"
            />
            
          </div>
        </v-col>
      </v-row>
    </div>
  </template>
  
  <script>
  import VButton from "@/components/VButton.vue";
  import { AgGridVue } from "ag-grid-vue3";
  import { onMounted, reactive, ref } from "vue";
  import { inject } from "vue";
  
  import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
  import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS
  
  export default {
    name: "AlertsComponent",
    components: {
      AgGridVue,
      VButton,
    },
    setup() {
      const emitter = inject("emitter");
      const columnRules = [
        {
          headerName: "Timestamp",
          field: "timestamp",
          sortable: true,
          filter: true,
          checkboxSelection: true,
        },
        {
          headerName: "sid",
          field: "sid",
          sortable: true,
          filter: true,
        },
        {
          headerName: "priority",
          field: "priority",
          sortable: true,
          filter: true,
        },
        {
          headerName: "protocol",
          field: "protocol",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Source address",
          field: "src_addr",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Source port",
          field: "src_port",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Destination address",
          field: "dst_addr",
          sortable: true,
          filter: true,
        },
        {
          headerName: "alert",
          field: "alert",
          sortable: true,
          filter: true,
        },
      
      ];
      const onFilterTextBoxChanged = () => {
        gridApi.value.setQuickFilter(
          document.getElementById("filter-text-box").value
        );
      };
      
      const rowDataAlerts = reactive({});
  
      const gridApi = ref(null); // Optional - for accessing Grid's API
  
      // Obtain API from grid's onGridReady event
      const onGridReady = (params) => {
        gridApi.value = params.api;
      };
  
      // DefaultColDef sets props common to all Columns
      const defaultColDef = {
        sortable: true,
        filter: true,
        flex: 1,
      };
  
      const autoGroupColumnDef = {
        headerName: "Server Name",
        field: "serverNname",
        minWidth: 300,
        cellRenderer: "agGroupCellRenderer",
        cellRendererParams: {
          checkbox: true,
        },
      };
      const rowGroupPanelShow = ref("always");
  
      function actionCellRenderer(params) {
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
            class="action-button play"
            data-action="play" title="Start Server">
               <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
            </button>
            <button
            class="action-button stop"
            data-action="stop" title="Stop Server">
               <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
            </button>
            <button
            class="action-button edit"
            data-action="edit" title="Edit Server">
               <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
            </button>
            <button
            class="action-button delete"
            data-action="delete" title="Delete Server">
               <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
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
      }
  
      function actionCellRendererClient(params) {
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
            class="action-button download"
            data-action="download" title="download">
               <i class="mdi mdi-download-circle" style="color: #086EAE; font-size: 20px;"></i>
            </button>
            <button
            class="action-button edit"
            data-action="edit" title="Edit Server">
               <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
            </button>
            <button
            class="action-button delete"
            data-action="delete" title="Delete Server">
               <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
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
      }
  
      const publishServer = () => {
        console.log("publishServer");
      };
  
      const saveAlertSuricata = () => {
        emitter.emit("add-alert");
      };
  
      const publishClient = () => {
        console.log("publishClient");
      };
  
      
  
      onMounted(async () => {
        try {
          rowDataAlerts.value=document.getElementById("app").attributes["alerts_suricata"].value;
          let validJsonString3 =  rowDataAlerts.value
            .replace(/True/g, "true")
            .replace(/False/g, "false")
            .replace(/None/g, "null");
          let parsedArray3 = JSON.parse(validJsonString3);
          rowDataAlerts.value = parsedArray3;
        } catch (error) {
          console.error("Error setting rowDataAlerts:", error);
        }
      });
  
      return {
        columnRules,
        rowDataAlerts,
        defaultColDef,
        autoGroupColumnDef,
        rowGroupPanelShow,
        emitter,
        actionCellRendererClient,
        cellWasClicked: (event) => {
          // Example of consuming Grid Event
          console.log("cell was clicked", event);
        },
        deselectRows: () => {
          gridApi.value.deselectAll();
        },
        actionCellRenderer,
        onGridReady,
        publishServer,
        saveAlertSuricata,
        publishClient,
        onFilterTextBoxChanged
      };
    },
  };
  </script>
  
  <style lang="scss"></style>