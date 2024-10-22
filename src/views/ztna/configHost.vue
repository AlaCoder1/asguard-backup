<template>
   <v-overlay v-model="state.viewModal">
            <v-dialog v-model="state.isviewModal" :scrim="false" width="auto">
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
                  You do not have the required permissions to perform any
                  actions.<br />
                  Please contact the administrator if you believe this is an
                  error.
                </v-card-text>

                <div class="mr-3 mb-5 d-flex justify-end">
                  <VButton
                    rounded
                    outlined
                    color="#ffffff"
                    label-color="#213E9F"
                    label="Close"
                    :isLarge="true"
                    @click="close"
                  />
                </div>
              </v-card>
            </v-dialog>
          </v-overlay>
  <div class="mt-6" style="display: flex; flex-direction: column">
    <h4>{{ $t("ztna.listofHostConfigs") }}</h4>
    <v-divider></v-divider>
  </div>
  <div style="overflow: hidden; flex-grow: 1">
    <ag-grid-vue id="grid-wrapperHost" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
      @grid-ready="onGridReadyHost" :columnDefs="columnHost" :rowData="configsHost" :gridOptions="gridOptions"
      :overlayNoRowsTemplate="overlayTemplate" :rowDragManaged="true" :rowDragEntireRow="true"
      @row-drag-end="onRowDragEnd" :localeText="paginationLocalization" />
  </div>
  <div class="d-flex justify-end mt-3 mb-15">
    <v-btn class="add-button" :rounded="true" color="indigo-darken-3"  :disabled="!tokenStatus"  @click="openModalHostAdd">
      {{ $t("ztna.addHostConfig")}}
    </v-btn>
  </div>

  <ModalAddHost :isOpen="state.isModalHostOpen" :editRow="state.editRow" :selectedId="state.selectedId"
    :modalMode="state.modalMode" />
  <!-- <ModalUpdateHost
    :isOpen="state.isModalUpdateHostOpen"
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
        <v-btn color="blue darken-1" text @click="confirmDelete(state.selectedId)">{{ $t("buttons.delete") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
    {{ state.textAlert }}
  </v-snackbar>
</template>

<script>
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { ref, onMounted, reactive, inject, computed } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import ModalAddHost from "@/components/modals/ModalAddHost.vue";
import ModalUpdateHost from "@/components/modals/ModalUpdateHost.vue";
import { AgGridVue } from "ag-grid-vue3";
import axios from "axios";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "configsComponent",
  components: {
    BaseLayout,
    ModalAddHost,
    ModalUpdateHost,
    AgGridVue,
    VButton,
  },

  setup() {
    const { t } = useI18n();
    const configsHost = ref([]);
    const emitter = inject("emitter");
    const tokenStatus = ref('')

    const gridApiHost = ref(null);

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      deleteDialog: false,
      deletedItemId: null,
      modalData: {},
      modalMode: "create",
      isModalHostOpen: false,
      isModalUpdateHostOpen: false,
      selectedId: null,
      isOpen: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    const overlayTemplate = ref(
      `
          <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
          <path
            d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
            style="fill: #E8EAF6"
            data-name="Unbox"
          />
         </svg></span>`
    );
    const paginationLocalization = reactive({
      of: "/",
    });
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });
    const name = computed(() => {
      return t("ztna.name");
    });
    const address = computed(() => {
      return t("ztna.address");
    });

    const columnHost = ref([
      {
        headerName: name,
        field: "name",
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: address,
        field: "address",
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "date_creation",
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
        valueFormatter: (params) => formatDateTime(params.value),
      },
      {
        headerName: "Actions",
        field: "actions",
        cellRenderer: actionCellRenderer,
        width: 150,
      },
    ]);

    const fetchConfigs = () => {
      let token = document.getElementById("app").getAttribute("token");
      let configsString = document
        .getElementById("app")
        .getAttribute("hostconfigs");
      let configsObject;
      if (token && token !== "null") {
        tokenStatus.value = true
      } 
      else {
        tokenStatus.value = false
    }
      try {
        configsObject = JSON.parse(configsString);
        console.log('configsObjecthost', configsObject)
        
      } catch (error) {
        console.error("Failed to parse configs string:", error);
        configsObject = { data: [] }; // Default to an empty array if parsing fails
      }
      // let filterHost = configsObject.filter((i) => i.addressId === "NH5p4FpGR")
      configsHost.value = configsObject
      console.log('host conf',configsHost.value)


    };

    const onGridReadyHost = (params) => {
      gridApiHost.value = params.api;
      if (gridApiHost.value) {
        gridApiHost.value.setRowData(configsHost.value);
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

    const confirmDelete = async (deletedItemId) => {

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      let token = document.getElementById("app").getAttribute("token");

      axios
        .delete(`/ztna/delete_host_config/${deletedItemId}`, {
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

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const formatDateTime = (dateTimeStr) => {
      const [datePart, timePart] = dateTimeStr.split("T");
      const formattedDate = `${datePart.slice(0, 10)} ${timePart.slice(0, 5)}`;
      return formattedDate;
    };

    const openModalHostAdd = () => {
      const user = user_privilege('Ztna');
      if (user && user !=='viewer') {
        state.modalData = {};
      state.modalMode = "create";
      state.isModalHostOpen = true;
              } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
    };


    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });
      if (isCurrentRowEditing) {
        eGui.innerHTML = `
                <button
                  class="action-button edit"
                  data-action="edit">
                       edit
                </button>
                <button
                  class="action-button cancel"
                  data-action="cancel">
                       cancel
                </button>
                `;
      } else if(!tokenStatus.value) {
        eGui.innerHTML = `
                <button
                  class="action-button edit"
                  disabled title="Edit Server">
                     <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                  </button>
                  <button
                  class="action-button delete"
                  disabled title="Delete ">
                    <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
                  </button>
        
                  `;
      }
      else {
        eGui.innerHTML = `
                <button
                  class="action-button edit"
                  data-action="edit" title="Edit Server">
                     <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                  </button>
                  <button
                  class="action-button delete"
                  data-action="delete" title="Delete ">
                    <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
                  </button>
        
                  `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionClient(action, params.node.data);
        });
      });
      return eGui;
    }
    const handleActionClient = (action, rowData, index) => {
      const user = user_privilege('Ztna');
      switch (action) {
        case "edit":
        if (user && user !=='viewer') {
          state.modalMode = "edit";
          state.isModalHostOpen = true;
          state.selectedId = rowData.id;
          state.editRow = rowData;
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

    onMounted(() => {
      emitter.on("closeInterceptModal", () => {
        state.isModalInterceptOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeHostModal", () => {
        state.isModalHostOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeUpdateHostModal", () => {
        state.isModalUpdateHostOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeUpdateInterceptModal", () => {
        state.isModalUpdateInterceptOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      fetchConfigs();
    });

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    return {
      t,
      close,
      state,
      columnHost,
      gridOptions,
      overlayTemplate,
      paginationLocalization,
      openModalHostAdd,
      OpenDelete,
      confirmDelete,
      cancelDelete,
      formatDateTime,
      onGridReadyHost,
      tokenStatus,
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
