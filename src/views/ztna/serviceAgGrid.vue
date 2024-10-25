<template>
<v-overlay v-model="state.viewModal">
            <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
              <v-card color="#193286" class="alert-box">
                <v-card-title class="img-containter">
                  <img
                    src="../../assets/images/view.png"
                    alt="logo"
                    class="img-view"
                    width="100"
                    height="100"
                /></v-card-title>
                <v-card-text>
                  {{  $t("profil.NoPermission") }}
                  <br />
                  {{  $t("profil.ContactAdmin") }} 
                </v-card-text>

                <div class="mr-3 mb-5 d-flex justify-end">
                  <VButton
                    rounded
                    outlined
                    color="#ffffff"
                    label-color="#213E9F"
                   :label="$t('buttons.close')"
                    :isLarge="true"
                    @click="close"
                  />
                </div>
              </v-card>
            </v-dialog>
          </v-overlay>
  <div class="mt-3" style="display: flex; flex-direction: column">
    <h4>{{ $t("ztna.servicesPolicies") }}</h4>
    <v-divider></v-divider>
  </div>

  <div style="overflow: hidden; flex-grow: 1">
    <ag-grid-vue
      id="grid-wrapperService"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      style="width: 100%"
      @grid-ready="ServiceGRID"
      :columnDefs="columnService"
      :rowData="rowDataService.value"
      :gridOptions="gridOptions"
      :overlayNoRowsTemplate="overlayTemplate"
      :localeText="paginationLocalization"
    />
  </div>
  <div class="d-flex justify-end mt-3">
    <v-btn
      class="add-button"
      :rounded="true"
      color="indigo-darken-3"
      @click="openModalAdd"
      :disabled="!tokenStatus"
    >
      {{ $t("ztna.addServicesPolicy") }}
    </v-btn>
  </div>
  <modal-service-policy
    :isOpen="state.isModalOpen"
    :selectedId="state.selectedId"
    :editRow="state.editRow"
    :modalMode="state.modalMode"
  />
  <!-- <ModalUpdateServiceP
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
import ModalServicePolicy from "@/components/modals/ModalServicePolicy.vue";
import ModalUpdateServiceP from "@/components/modals/ModalUpdateServiceP.vue";
import { useI18n } from "vue-i18n";
import { ref, onMounted, reactive, inject, computed } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    VButton,
    ModalUpdateServiceP,
    ModalServicePolicy,
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const tokenStatus = ref('')

    const state = reactive({
      modalData: {},
      isviewModal: false,
      viewModal: false,
      modalMode: "create",
      isModalOpen: false,
      isModalUpdateOpen: false,
      deleteDialog: false,
      selectedId: null,
      isOpen: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    const rowDataService = reactive([]);
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

    const serviceRole = computed(() => {
      return t("ztna.serviceRole");
    });
    const identityRole = computed(() => {
      return t("ztna.identityRole");
    });
    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });

    const columnService = ref([
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
        headerName: identityRole,
        field: "identity_attribute",
        cellRenderer: formatedidentityRoles,
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

    const gridService = ref(null);

    const ServiceGRID = (params) => {
      gridService.value = params.api;
      if (gridService.value) {
        gridService.value.setRowData(rowDataService.value);
      } else {
        console.error("Grid API is not available.");
      }
    };

    function formatedidentityRoles(data) {
      const resultMessage = data.data.identity_attribute;
      let eGui = document.createElement("div");
      eGui.innerHTML = `${resultMessage}`;
      return eGui;
    }

    function formatedserviceRoles(data) {
      const resultMessage = data.data.service_attribute;
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
      if(!tokenStatus.value){
        eGui.innerHTML = `
        <button class="action-button edit" disabled>
          <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button class="action-button delete" disabled>
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
      `;
      }else{
      eGui.innerHTML = `
        <button class="action-button edit" data-action="edit">
          <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button class="action-button delete" data-action="delete">
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
      `;}
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionClient(action, params.node.data);
        });
      });
      return eGui;
    }
    const handleActionClient = (action, rowData) => {
      const user = user_privilege('Ztna');

      switch (action) {
        case "edit":
        if (user && user !=='viewer') {
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;

          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
  
          break;
        case "delete":
        if (user && user !=='viewer') {
          OpenDelete(rowData.id);

          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
          break;
        default:
          break;
      }
    };
    async function OpenDelete(itemId) {
        state.selectedId = itemId;
        state.deleteDialog = true;
    }
    
    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = async (itemId) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      axios
        .delete(`/ztna/delete_services_policies/${itemId}`, {
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
      let token = document.getElementById("app").getAttribute("token");
      if (token && token !== "null") {
        tokenStatus.value = true
      } 
      else {
        tokenStatus.value = false
    }
      let service_policiesString = document
        .getElementById("app")
        .getAttribute("service_policies");

      let service_policiesObject = JSON.parse(service_policiesString);
      rowDataService.value = service_policiesObject
        ? service_policiesObject
        : [];

      if (gridService.value) {
        gridService.value.setRowData(rowDataService.value);
      }


      emitter.on("closeServicesModal", () => {
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
      const user = user_privilege('Ztna');

      if (user && user !=='viewer') {
        state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
    };
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    return {
      t,
      close,
      emitter,
      state,
      openModalAdd,
      gridOptions,
      ServiceGRID,
      // openModalUpdate,
      overlayTemplate,
      confirmDelete,
      cancelDelete,
      paginationLocalization,
      columnService,
      rowDataService,
      tokenStatus

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
