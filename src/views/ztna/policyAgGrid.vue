<template>
  <div class="mt-3" style="display: flex; flex-direction: column">
    <h4>{{ $t("ztna.servicesEdgeRelaysPolicies") }}</h4>
    <v-divider></v-divider>
  </div>

  <div style="overflow: hidden; flex-grow: 1">
    <ag-grid-vue
      id="grid-wrapperService"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      style="width: 100%"
      @grid-ready="PolicyGrid"
      :columnDefs="columnPolicy"
      :rowData="rowDataPolicy.value"
      :gridOptions="gridOptions"
      :overlayNoRowsTemplate="overlayTemplate"
      :localeText="paginationLocalization"
    />
  </div>
  <div class="d-flex justify-end mt-3 mb-14">
    <v-btn
      class="add-button"
      :rounded="true"
      color="indigo-darken-3"
      @click="openModalAdd"
    >
      {{ $t("ztna.addService") }}
    </v-btn>
  </div>
  <ModalServiceRouterPolicy
    :isOpen="state.isModalOpen"
    :selectedId="state.selectedId"
    :editRow="state.editRow"
    :modalMode="state.modalMode"
  />
  <!-- <ModalUpdateServiceRouterP
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
</template>

<script>
import { getCookie } from "@/mixins/csrftoken.js";
import ModalServiceRouterPolicy from "@/components/modals/ModalServiceRouterPolicy.vue";
import ModalUpdateServiceRouterP from "@/components/modals/ModalUpdateServiceRouterP.vue";
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
    ModalServiceRouterPolicy,
    ModalUpdateServiceRouterP,
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const state = reactive({
      modalData: {},
      modalMode: "create",
      deleteDialog: false,
      selectedId: null,
      isModalOpen: false,
      isOpen: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    const rowDataPolicy = reactive([]);
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

    const name = computed(() => {
      return t("ztna.name");
    });
    const semantic = computed(() => {
      return t("ztna.semantic");
    });

    const edgeRelaysRole = computed(() => {
      return t("ztna.edgeRelaysRole");
    });
    const serviceRole = computed(() => {
      return t("ztna.serviceRole");
    });
    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });

    const columnPolicy = ref([
      {
        headerName: name,
        field: "name",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: serviceRole,
        field: "service_attribute",
        cellRenderer: formatedserviceRoles,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: edgeRelaysRole,
        field: "relay_attribute",
        cellRenderer: formatededgeRouterRoles,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: semantic,
        field: "semantique",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "date_creation",
        cellRenderer: formatedcreatedAt,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Actions",
        field: "actions",
        cellRenderer: actionCellRenderer,
        autoHeight: true,
        resizable: true,
        width: 150,
        sortable: false,
      },
    ]);

    const gridPolicy = ref(null);

    const PolicyGrid = (params) => {
      gridPolicy.value = params.api;
      if (gridPolicy.value) {
        gridPolicy.value.setRowData(rowDataPolicy.value);
      } else {
        console.error("Grid API is not available.");
      }
    };

    function formatedserviceRoles(data) {
      const resultMessage = data.data.service_attribute;
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "";
      return eGui;
    }
    function formatededgeRouterRoles(data) {
      const resultMessage = data.data.relay_attribute;
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "";
      return eGui;
    }
    function formatedcreatedAt(data) {
      const resultMessage = formatDateTime(data.data.date_creation);
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
      let token = document.getElementById("app").getAttribute("token");

      switch (action) {
        case "edit":
        if (token && token !== "null") {
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;

} 
else {
  state.snackbar = true;
  state.color = "red";
  state.textAlert = "ZTNA is not running";

}

          break;
        case "delete":
          OpenDelete(rowData.id);
          break;
        default:
          break;
      }
    };
    async function OpenDelete(itemId) {
      let token = document.getElementById("app").getAttribute("token");
      if (token && token !== "null") {
        state.selectedId = itemId;
        state.deleteDialog = true;

} 
else {
  state.snackbar = true;
  state.color = "red";
  state.textAlert = "ZTNA is not running";

}
      
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

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      axios
        .delete(`/ztna/delete_services_edge_routers_policies/${itemId}`, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.message;
          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };

    onMounted(() => {
      let service_edge_router_policiesString = document
        .getElementById("app")
        .getAttribute("service_edge_router_policies");
      let service_edge_router_policiesObject = JSON.parse(
        service_edge_router_policiesString
      );
     

      rowDataPolicy.value = service_edge_router_policiesObject
        ? service_edge_router_policiesObject
        : [];
    

      if (gridPolicy.value) {
        gridPolicy.value.setRowData(rowDataPolicy.value);
      }

      console.log(
        "rowDataservice_edge_router_policies*: ",
        rowDataPolicy.value
      );

      emitter.on("closeServiceRouterPolicyModal", () => {
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
      let token = document.getElementById("app").getAttribute("token");
      if (token && token !== "null") {
        state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;

} 
else {
  state.snackbar = true;
  state.color = "red";
  state.textAlert = "ZTNA is not running";
}
    };

    return {
      t,
      emitter,
      state,
      openModalAdd,
      confirmDelete,
      cancelDelete,
      gridOptions,
      PolicyGrid,
      overlayTemplate,
      paginationLocalization,
      columnPolicy,
      rowDataPolicy,
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
