<template>
  <div class="mt-3 ml-3 mr-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="12">
        <h4>List of alerts</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column;">
          <div v-for="(message, index) in state.messages" :key="index">
            <v-alert
              v-model="message.snackbar"
              :type="message.color"
              class="d-flex mt-3"
              :style="{
                position: 'fixed',
                marginTop: '10 px',
                top: `${100 + index * 80}px`,
                right: '10px',
                zIndex: 9999,
              }"
            >
              <!-- style="position: fixed; top: 80px; right: 10px;"> -->
              <span class="c-o ml-3">
                <strong>{{ message.color }} </strong> {{ message.text }}
              </span>
              <span class="ml-16" style="margin-top: 20px !important;">
                <i
                  class="fas fa-times justify-end cursor"
                  @click="handleRemove(index)"
                ></i>
              </span>
            </v-alert>
          </div>
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
            <v-col cols="12" md="6" class="text-right">
              <v-btn @click="reloadData" icon>
                <v-icon class="small-refresh-icon">mdi-refresh</v-icon>
              </v-btn>
            </v-col>
          </v-row>

          <div>
            <ag-grid-vue
              
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              :columnDefs="columnRules"
              :rowData="rowDataAlerts.value"
              :gridOptions="gridOptions"
              :defaultColDef="defaultColDef"
              :autoGroupColumnDef="autoGroupColumnDef"
              :rowGroupPanelShow="rowGroupPanelShow"
              @cell-clicked="cellWasClicked"
              @grid-ready="onGridReady"
              :pagination="true"
              :paginationPageSize="10"
            />
          
        
    </div>
  </div>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
.grid-container {
  height: 400px;
  max-height: 100%; /* Ajustez cette valeur en fonction de vos besoins */
  overflow-y: auto;
  overflow-x: auto; /* Ajoutez cette ligne pour la défilement horizontal */
}

</style>
<style lang="scss">
.small-refresh-icon {
  font-size: 16px; /* Ajustez la taille selon vos besoins */
}
</style>
<script>
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";
import { inject } from "vue";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS
import axios from "axios";
export default {
  name: "AlertsComponent",
  components: {
    AgGridVue,
    VButton,
  },
  props: {
    configInfo: String,
  },
  setup(props) {
    const emitter = inject("emitter");
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      messages: [],
    });
    const currentIndex = ref(0);
    const columnRules = [
      {
        width: 50,
        minWidth: 50,
        maxWidth: 50,
        rowDrag: true,
        editable: false,
      },
      {
        headerCheckboxSelection: false,
        checkboxSelection: true,
        editable: false,
        width: 50,
        minWidth: 50,
        maxWidth: 50,
        sortable: false,
      },
      {
        headerName: "Horodatage LINUX",
        field: "timestamp",
        sortable: true,
        sort: "desc",
        minWidth: 250,
      },
      {
        headerName: "Sid",
        field: "sid",
        minWidth: 150,
        sortable: false,

      },
      {
        headerName: "Message",
        field: "message",
        minWidth: 420,
        autoHeight: true,
        cellStyle: { whiteSpace: 'pre-wrap' , lineHeight: '2'},
        sortable: false,
      },
      {
        headerName: "Severity",
        field: "priority",
        minWidth: 120,
        sortable: false,

      },
      {
        headerName: "Protocol",
        field: "protocol",
         minWidth: 120,
         sortable: false,

      },
      {
        headerName: "Source",
        field: "src_addr",
        minWidth: 150,
        sortable: false,

      },
      {
    
        headerName: "Port",
        field: "src_port",
        minWidth: 100,
        sortable: false,

      },
      {
        headerName: "Destination",
        field: "dst_addr",
        minWidth: 150,
        sortable: false,

      },
      {
    
    headerName: "Port",
    field: "dst_port",
    minWidth: 100,
    sortable: false,

  },


    ];
    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };
    const rowDataAlerts = reactive({});
    const handleRemove = (index) => {
      state.messages[index].snackbar = false;
    };
    const gridApi = ref(null); // Optional - for accessing Grid's API
    const gridOptions = ref({
      pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",  
    });
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
      cellRenderer: "agGroupCellRenderer",
      cellRendererParams: {
        checkbox: true,
      },
    };
    const rowGroupPanelShow = ref("always");

    

    
    const publishServer = () => {
      console.log("publishServer");
    };

    const saveAlertSuricata = () => {
      emitter.emit("add-alert");
    };
    const showMessage = (message) => {
      // Show a new message in the alert
      state.messages.push({
        color: message.color,
        text: message.text,
        snackbar: true,
      });
      // Automatically close the alert after a specified delay
     const lastIndex = state.messages.length - 1;
      setTimeout(() => {
        state.messages[lastIndex].snackbar = false;
        state.messages[lastIndex].read = true; // Mark the message as read
        updateIndex(); // Update the index after setting a message as read
      }, 2000 * (lastIndex + 1));
    };
     
    const updateIndex = () => {
      // Check if all messages are read
      const allRead = state.messages.every((message) => message.read);
      // If all messages are read, reset the index to 0
      if (allRead) {
        state.messages = [];
        currentIndex.value = 0;
        setTimeout(() => {
          location.reload();
        },1000)
       
      } else {
        // Increment the index if not all messages are read
        currentIndex.value += 1;
      }
    };
    const publishClient = () => {
      console.log("publishClient");
    };
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
    const reloadData = async() => {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken; 
        state.loading = true;
        state.isLoadingDialogue = true;
        try {
        const response = await axios.post(
          "/ids-ips/addalertsToDatabase/" + props.configInfo
        );
        if (response.status === 200 ) {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          // state.messages=response.data.message
          showMessage({
                color: "success",
                text: "All alerts saved successfully!!",
              });
            } else {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
              showMessage({
                color: "error",
                text: "Failed to save rule!",
              });
            }
      } catch (error) {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
        showMessage({
          color: "error",
          text: error,
        });
      }
    };
  

    onMounted(async () => {
      // try {
      //   rowDataAlerts.value=document.getElementById("app").attributes["alerts_suricata"].value;
      //   let validJsonString3 =  rowDataAlerts.value
      //     .replace(/True/g, "true")
      //     .replace(/False/g, "false")
      //     .replace(/None/g, "null");
      //   let parsedArray3 = JSON.parse(validJsonString3);
      //   rowDataAlerts.value = parsedArray3;

      // } catch (error) {
      //   console.error("Error setting rowDataAlerts:", error);
      // }
    });

    return {
      columnRules,
      rowDataAlerts,
      defaultColDef,
      autoGroupColumnDef,
      rowGroupPanelShow,
      emitter,
      gridOptions,
      state,
      
      
      cellWasClicked: (event) => {
        // Example of consuming Grid Event
        console.log("cell was clicked", event);
      },
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      onGridReady,
      publishServer,
      saveAlertSuricata,
      publishClient,
      onFilterTextBoxChanged,
      reloadData,
      showMessage,
      handleRemove,
      updateIndex,
     
    };
  },
};
</script>

<style lang="scss"></style>

