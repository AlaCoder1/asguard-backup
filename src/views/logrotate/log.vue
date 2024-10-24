<template>
  <div class="mt-5">
    <div class="container">
      <h4>{{ $t("subtitle.archivedLog") }}</h4>
      <v-divider></v-divider>

      <v-dialog v-model="state.deleteDialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">{{
            $t("firewall.delete_confirm")
          }}</v-card-title>
          <v-card-text>{{ $t("nat.msg_confirm_delete") }}</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="cancelDelete">{{
              $t("firewall.cancel")
            }}</v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="confirmDelete(state.deletedRow)"
              >{{ $t("firewall.delete") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-row class="mb-15">
        <v-col cols="9" md="6" class="mt-5">
          <v-text-field
            id="filter-text-box"
            v-model="state.filterText"
            :placeholder="$t('firewall.search')"
            density="compact"
            rounded
            variant="solo"
            hide-details
            dense
            prepend-inner-icon="mdi-magnify"
            @input="onFilterTextBoxChanged"
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <div style="overflow: hidden; flex-grow: 1">
            <!-- :rowData="getRowDataByService(tab.service)" -->
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnKeys"
              :overlayNoRowsTemplate="overlayTemplate"
              :rowData="rowData.value"
              :pagination="true"
              :paginationPageSize="30"
              :localeText="paginationLocalization"
            />
          </div>
        </v-col>
      </v-row>
    </div>
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>
<script>
import { AgGridVue } from "ag-grid-vue3";
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import {
  onMounted,
  reactive,
  ref,
  watch,
  defineComponent,
  inject,
  computed,
} from "vue";
import { useI18n } from "vue-i18n";

export default defineComponent({
  name: "Component",
  components: {
    AgGridVue,
  },
  props: {
    id: String,
    uuid: String,
    activeTab: String,
  },
  setup(props) {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const state = reactive({
      filterText: "",
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      textAlert: [],
      socket: null,
      deletedRow: null,
      color: null,
      modalData: {},
      isModalOpen: false,
      isOpen: null,
      editRow: {},
      logsManagement: [],
    });
    onMounted(() => {
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;

      let services =
        document.getElementById("app").attributes["logrotate"].value;
      let validJsonString = services
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      let logData = JSON.parse(validJsonString);
      state.logsManagement = [logData][0];
    });

    const columnKeys = ref([
      {
        headerName: t("logrotate.id"),
        field: "id",
        autoHeight: true,

        flex: 1,
        width: 150,
        minWidth: 150,
      },
      {
        headerName: t("logrotate.filename"),
        field: "filename",
        flex: 1,
        width: 350,
        minWidth: 50,
      },
      {
        headerName: t("logrotate.original_path"),
        field: "original_path",
        autoHeight: true,
        flex: 1,
        width: 350,
        minWidth: 50,
      },
      {
        headerName: t("logrotate.backup_path"),
        field: "backup_path",
        autoHeight: true,
        flex: 1,
        width: 350,
        minWidth: 50,
      },
      {
        headerName: t("logrotate.date"),
        field: "date",
        autoHeight: true,
        flex: 1,
        width: 150,
        minWidth: 50,
      },
      {
        headerName: t("firewall.action"),
        field: "action",
        width: 150,
        minWidth: 50,
        cellRenderer: actionCellRenderer,
      },
    ]);
    const rowData = reactive([]);
    watch(
      () => state.logsManagement,
      (newValue, oldValue) => {
        if (newValue) {
          if (state.logsManagement[props.activeTab]) {
            rowData.value = state.logsManagement[props.activeTab].map((e) => {
              return {
                id: e.id,
                backup_path: e.backup_path,
                date: e.date,
                filename: e.filename,
                original_path: e.original_path,
                service: e.service,
              };
            });
          }
        } else {
          rowData.value = [];
        }
      },
      { immediate: true }
    );

    // const getRowDataByService = (service) => {
    //   return logData.value.filter((log) => log.service === service);
    // };

    const gridApi = ref(null);
    const overlayTemplate = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        // console.log(logData.value);
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("Grid API is not available.");
      }
    };
    // const groupedTabs = computed(() => {
    //   // Group tabs by service
    //   const grouped = {};
    //   logData.value.forEach((log) => {
    //     if (!grouped[log.service]) {
    //       grouped[log.service] = [];
    //     }
    //     grouped[log.service].push(log);
    //   });
    //   return Object.keys(grouped).map((service) => ({
    //     service,
    //     logs: grouped[service],
    //   }));
    // });

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
          state.deletedRow = rowData; // Set the row to be deleted
          state.deleteDialog = true; // Open the delete confirmation dialog
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

      axios
        .post(
          `/system_log/downloadLogrotate`,
          {
            file_path: filePath,
          },
          {
            responseType: "blob",
          }
        )
        .then((response) => {
          const blob = new Blob([response.data], { type: "application/zip" });
          const url = window.URL.createObjectURL(blob);

          const a = document.createElement("a");
          a.style.display = "none";
          a.href = url;

          let filename = rowData.filename;
          if (filename.endsWith(".gz")) {
            filename = filename.slice(0, -3) + ".zip";
          }

          a.download = filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          state.textAlert = t("logrotate.download_succes");
          state.snackbar = true;
          state.color = "green";
        })
        .catch((error) => {
          console.error("Error downloading file:", error);
          state.textAlert = t("logrotate.download_fail");
          state.snackbar = true;
          state.color = "red";
        });
    };

    const confirmDelete = (rowData) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/system_log/deleteLogrotate/${rowData.id}`)
        .then((response) => {
          state.textAlert = t("logrotate.delete_succes");
          state.snackbar = true;
          state.color = "green";
          setTimeout(() => location.reload(), 1000);
        })
        .catch((error) => {
          state.textAlert = t("logrotate.delete_fail");
          state.snackbar = true;
          state.color = "red";
          setTimeout(() => location.reload(), 1000);
        });

      state.deleteDialog = false;
    };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    return {
      t,
      columnKeys,
      rowData,
      state,
      // tabs,
      // groupedTabs,
      // activeTab,
      paginationLocalization,
      overlayTemplate,
      // getRowDataByService,
      onGridReady,
      onFilterTextBoxChanged,
      cancelDelete,
      confirmDelete,
    };
  },
});
</script>

<style lang="scss">
.action-button:hover {
  color: #086eae;
}

.action-button.update {
  color: #00b300;
}

.action-button.cancel {
  color: #ff0000;
}

.action-button.edit {
  color: #086eae;
}

.action-button.delete {
  color: #086eae;
}

.ag-theme-alpine .ag-header {
  background-color: #f5f5f5;
}

.actionBtn {
  justify-content: center;
}

.button-bg-color {
  background-color: #213e9f;
}

.v-alert.v-theme--light.bg-success.v-alert--density-default.v-alert--variant-flat.d-flex.mt-3.alert-style {
  width: 350px;
  right: -78%;
  /* Default value for small and medium screens */

  /* Media query for large screens */
  @media screen and (min-width: 1080px) {
    right: -70%;
    /* Value for larger screens */
  }
}
</style>
