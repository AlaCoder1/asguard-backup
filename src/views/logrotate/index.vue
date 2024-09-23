<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.logManagement')" active-menu="Key_Pair">
      <template #content>
        <div class="mr-3">
          <v-tabs v-model="activeTab" background-color="#f5f5f5" color="black" :class="{ 'elevation-0': true }"
            :slider-color="'#FFC300'">
            <v-tab v-for="tab in tabs" :key="tab.service" :value="tab.service">
              <span style="color: #020202">{{ tab.service }}</span>
            </v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <v-window-item v-for="tab in tabs" :key="tab.service" :value="tab.service">
              <v-card>
                <v-card-text>
                  <h4>{{ $t('subtitle.archivedLog') }} </h4>
                  <v-divider></v-divider>
                  <v-row class="mb-15">
                    <v-col cols="9" md="6" class="mt-5">
                      <v-text-field id="filter-text-box" v-model="state.filterText" :placeholder="$t('firewall.search')"
                        density="compact" rounded variant="solo" hide-details dense prepend-inner-icon="mdi-magnify"
                        @input="onFilterTextBoxChanged"></v-text-field>
                    </v-col>

                    <v-col cols="12">
                      <div style="overflow: hidden; flex-grow: 1">
                        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3"
                          style="width: 100%" @grid-ready="onGridReady" :columnDefs="columnKeys"
                          :rowData="getRowDataByService(tab.service)" :overlayNoRowsTemplate="overlayTemplate"
                          :pagination="true" :paginationPageSize="30" :localeText="paginationLocalization" />
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import { getCookie } from "@/mixins/csrftoken.js";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "KeyPair",
  components: {
    BaseLayout,
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const paginationLocalization = reactive({ of: "/" });
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const activeTab = ref("");  // Use ref for activeTab

    const state = reactive({
      filterText: "",
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      socket: null,
    });

    const tabs = ref([]);
    const logData = ref([]);

    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width="50px">
          <!-- SVG content -->
        </svg>
      </span>`;

      let services = document.getElementById("app").attributes["logrotate"].value;
      let validJsonString = services
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      logData.value = JSON.parse(validJsonString);

      tabs.value = logData.value.map((element) => ({
        service: element.service,
      }));

      activeTab.value = tabs.value[0]?.service || '';
    });

    const columnKeys = ref([
      { headerName: t("logrotate.id"), field: "id", autoHeight: true, width: 150, minWidth: 150 },
      { headerName: t("logrotate.filename"), field: "filename", width: 350, minWidth: 50 },
      { headerName: t("logrotate.original_path"), field: "original_path", autoHeight: true, width: 350, minWidth: 50 },
      { headerName: t("logrotate.backup_path"), field: "backup_path", autoHeight: true, width: 350, minWidth: 50 },
      { headerName: t("logrotate.date"), field: "date", autoHeight: true, width: 250, minWidth: 50 },
      { headerName: t("firewall.action"), field: "action", cellRenderer: actionCellRenderer },
    ]);

    const getRowDataByService = (service) => {
      return logData.value.filter((log) => log.service === service);
    };

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataKeys.value);
      } else {
        console.error("Grid API is not available.");
      }
    };

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(state.filterText);
    };

    

    function actionCellRenderer(params) {
    const eGui = document.createElement("div");

    eGui.innerHTML = `
      <button class="action-button delete" data-action="delete">
        <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
      </button>
      <button class="action-button download" data-action="download">
        <i class="mdi mdi-download-circle" style="color: #086EAE; font-size: 20px;"></i>
      </button>
    `;
    
    eGui.querySelectorAll(".action-button").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.getAttribute("data-action");
        handleActionLog(action, params.node.data);
      });
    });

    return eGui;
  }

    const handleActionLog = (action, rowData) => {
      switch (action) {
        case "delete":
          confirmDelete(rowData);
          state.deleteDialog = true;
          state.deletedRow = rowData;
          break;
        case "download":
          downloadLogsForRow(rowData);
          break;
        default:
          break;
      }
    };

  const downloadLogsForRow = (rowData) => {
  console.log("Downloading logs for row:", rowData);
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  const filePath = `${rowData.backup_path}${rowData.filename}`;

  axios.get(`/system_log/downloadLogrotate`, {
    params: {
      file_path: filePath 
    },
    responseType: "blob",  
  })
    .then((response) => {
      const blob = new Blob([response.data], { type: "application/gzip" });  

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `${rowData.filename}`; 
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    })
    .catch((error) => {
      console.error("Error downloading file:", error);
    });
};

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = (rowdata) => {
    const csrfToken = getCookie("csrftoken");
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

   
    axios.delete(`/system_log/deleteLogrotate/${rowData.id}`)
      .then(response => {
        state.snackbar = true;
        state.color = "success";
        state.textAlert = response.data; 
        setTimeout(() => location.reload(), 1000);  
      })
      .catch(error => {
        state.snackbar = true;
        state.color = "red";
        state.textAlert = error.response.data;  
      });
  };

    return {
      state,
      tabs,
      activeTab,
      columnKeys,
      getRowDataByService,
      overlayTemplate,
      paginationLocalization,
      onFilterTextBoxChanged,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>


