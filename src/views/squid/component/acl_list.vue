<template>
  <div
    class="mt-6 ml-5"
    style="display: flex; flex-direction: column; margin-bottom: 5%"
  >
    <v-row>
      <v-col cols="12">
        <h4>ACL List</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-5">
          <v-col cols="12" md="6">
            <v-text-field
              id="filter-text-box-acl"
              density="compact"
              class="w-25"
              variant="solo"
              rounded
              label="Search"
              append-inner-icon="mdi-magnify"
              single-line
              hide-details
              @input="onFilterAclChanged"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <div style="overflow: hidden; flex-grow: 1">
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
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidBlackList from "@/components/modals/ModalSquidBlackList.vue";
import CertStatusRenderVue from "../agGridCustomRender/CertStatusRenderVue.vue";
import CertAclStatus from "../agGridCustomRender/CertAclStatus.vue";
export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidBlackList,
    CertStatusRenderVue,
    CertAclStatus
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      snackbar: false,
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

    const rowDataAclList = reactive({});
    const gridColumnApi = ref(null);
    const gridApi = ref(null);
    const defaultColDef = ref({
      flex: 1,
      cellDataType: false,
    });
    const columnAclList = [
      {
        headerName: "List name",
        field: "name",
        autoHeight: true,
      },
      {
        headerName: "Status",
        field: "status",
        cellRendererSelector: function (params) {
          const status = {
            component: "CertAclStatus",
            params: params.data.status,
          };
          return status;
        },
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
      },
    ];

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

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
        if (params.data.name === "adult") {
          eGui.innerHTML = `No Adult For Instance`;
        } else {
          if (params.data.status === "Blocked") {
            eGui.innerHTML = `
            <button
              class="action-button edit"
              data-action="edit" >
                <i class="far fa-edit" style="color: #086eae;"></i>
              </button>
            <button
              class="action-button enable"
              data-action="enable" title="Change Group Status">
                <i class="mdi mdi-lock-open-outline fa-lg"" style="color: #086eae; font-size:24px;"></i>
              </button>

            

    `;
          } else {
            eGui.innerHTML = `
          
            <button
              class="action-button enable"
              data-action="enable" title="Change Group Status">
                <i class="mdi mdi-lock fa-lg"" style="color: #086eae; font-size:24px;"></i>
              </button>

    `;
          }
        }
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }

    const handleAction = (action, rowData) => {
      switch (action) {
        case "edit":
          console.log("rowData", rowData);

          state.modalData = {};
          state.editRow = rowData;
          state.modalMode = "edit";
          state.isModalOpen = true;

          break;
        case "enable":
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
      emitter,
      columnAclList,
      gridColumnApi,
      rowDataAclList,
      onGridReady,
      actionCellRenderer,
      defaultColDef,
      handleAction,
      onFilterAclChanged,
    };
  },
};
</script>
