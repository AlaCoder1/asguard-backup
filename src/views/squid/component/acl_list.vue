<template>
    <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
        <v-card-text>
          {{  $t("profil.NoPermission") }}
                  <br />
                  {{  $t("profil.ContactAdmin") }} 
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div
    class="mt-6 ml-5"
    style="display: flex; flex-direction: column; margin-bottom: 5%"
  >
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("squid.aclList") }}</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-5">
          <v-col cols="12" md="6">
            <v-text-field
              id="filter-text-box-acl"
              density="compact"
              class="w-75"
              variant="solo"
              rounded
              :label="$t('squid.search')"
              append-inner-icon="mdi-magnify"
              single-line
              hide-details
              @input="onFilterAclChanged"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <div class="mb-10" style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine"
              :columnDefs="columnAclList"
              :rowData="rowDataAclList.value"
              @grid-ready="onGridReady"
              :defaultColDef="defaultColDef"
              style="width: 100%"
              :pagination="true"
              :paginationPageSize="10"
              :localeText="paginationLocalization"
              :overlayNoRowsTemplate="overlayTemplate"
            >
            </ag-grid-vue>
          </div>
        </v-row>
        <v-snackbar
          :timeout="2000"
          v-model="state.snackbar"
          location="bottom right"
          :color="state.color"
        >
          {{ state.textAlert }}

          <template v-slot:actions> </template>
        </v-snackbar>

        <ModalSquidBlackList
          :isOpen="state.isModalOpen"
          :editRow="state.editRow"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidBlackList from "@/components/modals/ModalSquidBlackList.vue";
import CertStatusRenderVue from "../agGridCustomRender/CertStatusRenderVue.vue";
import CertAclStatus from "../agGridCustomRender/CertAclStatus.vue";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidBlackList,
    CertStatusRenderVue,
    CertAclStatus,
  },
  setup() {
    const emitter = inject("emitter");
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const state = reactive({
      snackbar: false,
      isviewModal: false,
      viewModal: false,
      color: "",
      textAlert: "",
      off: false,
      on: false,
      proxyPort: "",
      enable: false,
      filterText: "",

      modalData: {},
      editRow: null,
      modalMode: "",
      isModalOpen: false,
    });
    const paginationLocalization = reactive({
      of: "/",
    });
    const rowDataAclList = reactive({});
    const gridColumnApi = ref(null);
    const gridApi = ref(null);
    const defaultColDef = ref({
      // flex: 1,
      cellDataType: false,
    });

    const listName = computed(() => {
      return t("squid.listName");
    });
    const status = computed(() => {
      return t("squid.status");
    });

    const columnAclList = ref([
      {
        headerName: listName,
        field: "name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: status,
        field: "status",
        cellRendererSelector: function (params) {
          const status = {
            component: "CertAclStatus",
            params: params.data.status,
          };
          return status;
        },
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
      },
    ]);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAclList.value);
      } else {
        console.error("Grid API.");
      }
    };

    const onFilterAclChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box-acl").value
      );
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
        // if (params.data.name === "adult") {
        //   eGui.innerHTML = `${t("squid.noAdult")}`;
        // }

        // else {
        if (params.data.status === "Blocked") {
          eGui.innerHTML = `
            <button
              class="action-button edit"
              data-action="edit" >
                <i class="mdi mdi-square-edit-outline fa-lg" style="color: #086eae; font-size:24px;"></i>
              </button>
            <button
              class="action-button enable"
              data-action="enable" title=${t("squid.changeGroup")}>
                <i class="mdi mdi-lock-open-outline fa-lg"" style="color: #086eae; font-size:24px;"></i>
              </button>

            

    `;
        } else {
          eGui.innerHTML = `
          
            <button
              class="action-button enable"
              data-action="enable" title=${t("squid.changeGroup")}>
                <i class="mdi mdi-lock fa-lg"" style="color: #086eae; font-size:24px;"></i>
              </button>

    `;
        }
        // }
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const handleAction = (action, rowData) => {
      const user = user_privilege('Proxy');
      switch (action) {
        case "edit":
      if (user && user !== 'viewer' && user !=='default') {
          console.log("rowData", rowData);

          state.modalData = {};
          state.editRow = rowData;
          state.modalMode = "edit";
          state.isModalOpen = true;
        } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
          break;
        case "enable":
        if (user && user !== 'viewer' && user !=='default') {
          console.log("rowData", rowData);
          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          let payload = {
            group: rowData.name,
            status: rowData.status === "Blocked" ? true : false,
          };

          axios
            .post("/proxy/changeStausGroup", payload)
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.loading = false;
                state.isLoadingDialogue = false;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.loading = false;
              state.isLoadingDialogue = false;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
          break;
        default:
          break;
      }
    };
    const getCookie = (name) => {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    };

    onMounted(() => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;

      emitter.on("closeAclListModal", () => {
        state.isModalOpen = false;
      });

      const proxyGroupsAttribute =
        document.getElementById("app").attributes["proxyGroups"].value;
      const proxyGroups = JSON.parse(proxyGroupsAttribute);

      let mapedGroups = proxyGroups.map((i) => {
        return {
          name: i.name,
          status: i.status === true ? "Blocked" : "Unblocked",
        };
      });

      if (!rowDataAclList.value) {
        rowDataAclList.value = [];
      }

      rowDataAclList.value = mapedGroups;
    });

    return {
      state,
      close,
      emitter,
      columnAclList,
      gridColumnApi,
      rowDataAclList,
      paginationLocalization,
      overlayTemplate,
      onGridReady,
      actionCellRenderer,
      defaultColDef,
      handleAction,
      onFilterAclChanged,
    };
  },
};
</script>
