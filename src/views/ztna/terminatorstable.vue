<template>
  <v-container class="axe-media-print-hide" fluid>
    <div class="mt-6" style="display: flex; flex-direction: column">
      <h4>{{ $t("ztna.listOfTerminators") }}</h4>
      <v-divider></v-divider>
    </div>
    <div style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-3"
        style="width: 100%"
        @grid-ready="onGridReady"
        :columnDefs="columnTerminator"
        :rowData="terminators.value"
        :gridOptions="gridOptions"
        :overlayNoRowsTemplate="overlayTemplate"
        :rowDragManaged="true"
        :rowDragEntireRow="true"
        @row-drag-end="onRowDragEnd"
        :localeText="paginationLocalization"
      />
    </div>
    <div class="d-flex justify-end mt-3">
      <v-btn
        class="add-button"
        :rounded="true"
        color="indigo-darken-3"
        @click="openModalAdd"
      >
        {{ $t("ztna.addTerminator") }}
      </v-btn>
    </div>
    <ModalTerminators
      :isOpen="state.isModalOpen"
      :selectedId="state.selectedId"
      :editRow="state.editRow"
      :modalMode="state.modalMode"
    />
    <!-- <ModalUpdateTerminators
      :isOpen="state.isModalUpdateOpen"
      :selectedId="state.selectedId"
    /> -->
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
          <v-btn
            color="blue darken-1"
            text
            @click="confirmDelete(state.selectedId)"
            >{{ $t("buttons.delete") }}</v-btn
          >
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
  </v-container>
</template>

<script>
import ModalTerminators from "@/components/modals/ModalTerminators.vue";
import ModalUpdateTerminators from "@/components/modals/ModalUpdateTerminators.vue";
import { useI18n } from "vue-i18n";
import { ref, onMounted, reactive, inject, computed } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    ModalUpdateTerminators,
    ModalTerminators,
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const terminators = reactive([]);
    const state = reactive({
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isModalUpdateOpen: false,
      isOpen: null,
      deleteDialog: false,
      selectedId: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    const overlayTemplate = ref(`
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`);
    const paginationLocalization = reactive({
      of: "/",
    });
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const address = computed(() => {
      return t("ztna.address");
    });
    const services = computed(() => {
      return t("ztna.services");
    });
    const relays = computed(() => {
      return t("ztna.relays");
    });
    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });
    const binding = computed(() => {
      return t("ztna.binding");
    });

    const columnTerminator = ref([
      {
        headerName: address,
        field: "address",  
        autoHeight: true,
        resizable: true,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: services,
        field: "service",
        // cellRenderer: formatedservice,
        autoHeight: true,
        resizable: true,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: relays,
        field: "router",
        // cellRenderer: formatedrouter,
        autoHeight: true,
        resizable: true,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: binding,
        field: "binding",
        autoHeight: true,
        resizable: true,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "createdAt",
        // cellRenderer: formatedcreatedAt,
        autoHeight: true,
        resizable: true,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Action",
        field: "actions",
        cellRenderer: actionCellRenderer,
        autoHeight: true,
        resizable: true,
        width: 150,
        sortable: false,
      },
    ]);

    const rowDataDnat = reactive([]);

    const gridApi = ref(null);
    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(terminators.value);
      }
    };

    function formatedservice(data) {
      let eGui = document.createElement("div");
      eGui.innerHTML = `${data.data.service.name}`;
      return eGui;
    }

    function formatedrouter(data) {
      const resultMessage = Array.isArray(data.data.router.name)
        ? data.data.router.map((e) => e + "<br>").join("")
        : data.data.router.name || "";
      let eGui = document.createElement("div");
      eGui.innerHTML = `${resultMessage}`;
      return eGui;
    }

    function formatedcreatedAt(data) {
      const resultMessage = formatDateTime(data.data.createdAt);
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "";
      return eGui;
    }

    const formatDateTime = (dateTimeStr) => {
      const [datePart, timePart] = dateTimeStr.split("T");
      const formattedDate = `${datePart.slice(0, 10)} ${timePart.slice(0, 5)}`;
      return formattedDate;
    };
    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      eGui.innerHTML = `
        <button class="action-button edit" data-action="edit">
          <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button class="action-button delete" data-action="delete">
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
      `;
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionClient(action, params.node.data);
        });
      });
      return eGui;
    }
    const handleActionClient = (action, rowData) => {
      switch (action) {
        case "edit":
          // openModalUpdate(rowData.id);
          // console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;
          break;
        case "delete":
          OpenDelete(rowData.id);
          break;
        default:
          break;
      }
    };
    async function OpenDelete(itemId) {
      state.selectedId = itemId;
      state.deleteDialog = true;
    }
    // const openModalUpdate = (id) => {
    //   state.modalData = {};
    //   state.modalMode = "create";
    //   state.isModalUpdateOpen = true;
    //   state.selectedId = id;
    // };
    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = async (itemId) => {
      try {
        let token = document.getElementById("app").getAttribute("token");
        const proxyUrl = "https://asguard:3000";
        const apiUrl = `/edge/management/v1/terminators/${itemId}`;
        await axios.delete(proxyUrl + apiUrl, {
          headers: { "zt-session": token, "Content-Type": "application/json" },
        });
        state.snackbar = true;
        state.color = "success";
        state.textAlert = "Terminator deleted successfully";
        setTimeout(() => {
          location.reload();
        }, 1000);
      } catch (error) {
        state.snackbar = true;
        state.color = "red";
        state.textAlert = "Delete failure";
        console.error("Failed to delete item:", error);
      }
    };

    async function fetchterminators() {
      let terminatorsString = document
        .getElementById("app")
        .getAttribute("terminators");
      let terminatorsObject;
      try {
        terminatorsObject = JSON.parse(terminatorsString);
      } catch (error) {
        console.error("Failed to parse terminators string:", error);
      }
      // terminators.value = terminatorsObject.data;

      let test = [
        {
          address: "address",
          service: "service",
          router: "router",
          createdAt: "createdAt",
          binding: "binding",
        },
      ];
      terminators.value = test
      // terminators.value = terminatorsObject?.data ? terminatorsObject.data : [];

      if (gridApi.value) {
        gridApi.value.setRowData(terminators.value);
      }
      console.log("terms", terminators.value);
    }

    onMounted(() => {
      fetchterminators();
      emitter.on("closeTerminatorsModal", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeUpdateModal", () => {
        state.isModalUpdateOpen = false;
      });
    });

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    return {
      t,
      emitter,
      state,
      terminators,
      openModalAdd,
      fetchterminators,
      gridOptions,
      // openModalUpdate,
      rowDataDnat,
      overlayTemplate,
      paginationLocalization,
      columnTerminator,
      confirmDelete,
      cancelDelete,
      onGridReady,
      formatDateTime,
    };
  },
};
</script>

<style>
.table {
  width: 100%;
  border-collapse: collapse;
  border: 0.5px solid #000;
}
.table thead tr:first-child {
  border-bottom: 0.5px solid #000;
  background-color: ghostwhite;
}
.table tbody tr:last-child {
  border-bottom: 0.5px solid #000;
}
</style>
