<template>
  <v-overlay v-model="state.loading">
    <v-dialog
      v-model="state.isLoadingDialogue"
      :scrim="false"
      persistent
      width="auto"
    >
      <v-card color="#193286">
        <v-card-text>
          {{ $t("sdwan.pleaseWait") }}
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3 ml-3">
    <h4>{{ $t("tabs.application") }}</h4>
    <v-divider class="mb-2"></v-divider>
    <div style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-3"
        style="width: 100%"
        @grid-ready="onGridReady"
        :columnDefs="columnApplication"
        :rowData="rowDataApplication.value"
        :gridOptions="gridOptions"
        :overlayNoRowsTemplate="overlayTemplate"
        :localeText="paginationLocalization"
      />
    </div>
    <div class="d-flex justify-end mt-3 mb-5">
      <VButton
        rounded
        outlined
        color="#213E9F"
        label-color="#ffffff"
        :label="$t('buttons.Add')"
        :isLarge="true"
        type="submit"
        class="ml-2"
        @click="openModalAdd"
      />
    </div>
  </div>

  <v-dialog v-model="state.deleteDialog" max-width="500px">
    <v-card>
      <v-card-title class="headline">{{
        $t("delete.DeleteConfirmation")
      }}</v-card-title>
      <v-card-text>{{ $t("delete.deleteRow") }} ?</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelDelete">{{
          $t("buttons.cancel")
        }}</v-btn>
        <v-btn color="blue darken-1" text @click="confirmDelete">{{
          $t("buttons.delete")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar
    :timeout="2000"
    v-model="state.snackbar"
    location="bottom right"
    :color="state.color"
  >
    {{ state.textAlert }}
  </v-snackbar>

  <ModalApplicationWaf
    :isOpen="state.isModalOpen"
    :editRow="state.editRow"
    :modalMode="state.modalMode"
  />
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import VButton from "@/components/VButton.vue";
import { reactive, ref, computed, onMounted, inject } from "vue";
import ModalApplicationWaf from "@/components/modals/ModalApplicationWaf.vue";

export default {
  name: "Rules",
  components: {
    VButton,
    AgGridVue,
    ModalApplicationWaf,
  },
  setup() {
    const emitter = inject("emitter");
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      modalData: {},
      isModalOpen: false,
      isOpen: null,
      editRow: {},
      modalMode: "create",
    });

    const appName = computed(() => {
      return t("Waf.applicationName");
    });
    const value = computed(() => {
      return t("squid.value");
    });
    const protocol = computed(() => {
      return t("firewall.protocol");
    });
    const columnApplication = ref([
      {
        headerName: appName,
        field: "name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "protocol",
        field: "application_type",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: protocol,
        field: "application_protocol",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: value,
        field: "application_value",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        field: "action",
      },
    ]);

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
                class="action-button edit"
                data-action="edit">
                   <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>
          <button
          class="action-button delete"
          data-action="delete">
            <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>`;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data);
        });
      });
      return eGui;
    }

    const handleAction = (action, rowData, index) => {
      switch (action) {
        case "delete":
          state.deleteDialog = true;
          state.deletedRow = rowData;

          break;
        case "edit":
          console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          break;

        default:
          break;
      }
    };

    const rowDataApplication = reactive({});
    const gridApi = ref(null);
    const overlayTemplate = ref("");
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 9,
      rowSelection: "single",
    });

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataApplication.value);
      }
    };
    onMounted(() => {
      overlayTemplate.value = `
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`;

      let list_waf_app =
        document.getElementById("app").attributes["list_waf_app"].value;
      let list_rules = JSON.parse(list_waf_app);

      rowDataApplication.value = list_rules;
    });

    emitter.on("closeWafApplicationModal", () => {
      state.isModalOpen = false;
      state.isOpen = false;
      state.modalMode = "";
      state.editRow = {};
    });

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    const restartNginx = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios.post(`/waf/restartNginx`);
    };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/waf/deleteApplicationWaf/${state.deletedRow.id}`)
        .then((response) => {
          restartNginx();
          state.loading = true;
          state.isLoadingDialogue = true;
          setTimeout(() => {
            state.loading = false;
            state.isLoadingDialogue = false;
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;
            state.deleteDialog = false;
          }, 4000);
          setTimeout(() => {
            location.reload();
          }, 4000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };

    return {
      confirmDelete,
      cancelDelete,
      state,
      onGridReady,
      openModalAdd,
      columnApplication,
      rowDataApplication,
      gridOptions,
      overlayTemplate,
      paginationLocalization,
    };
  },
};
</script>
