<template>
  <v-app id="inspire">
    <base-layout title="Routing" active-menu="Key_Pair">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>Static Routing</h4>
            <v-divider></v-divider>
            <v-row>
              <v-col cols="12">
                <div style="overflow: hidden; flex-grow: 1">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    style="width: 100%"
                    @grid-ready="onGridReady"
                    :columnDefs="columnRoute"
                    :rowData="rowDataRoute.value"
                  />
                </div>
                <div class="d-flex justify-end mt-3">
                  <VButton
                    rounded
                    outlined
                    color="#213E9F"
                    label-color="#ffffff"
                    label="Add"
                    :isLarge="true"
                    type="submit"
                    class="ml-2"
                    @click="openModalAdd"
                  />
                </div>
              </v-col>
            </v-row>
            <RoutingModal :isOpen="state.isModalOpen" />
          </div>
          <v-dialog v-model="state.deleteDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">Delete Confirmation</v-card-title>
              <v-card-text
                >Are you sure you want to delete this Row ?</v-card-text
              >
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="cancelDelete"
                  >Cancel</v-btn
                >
                <v-btn color="blue darken-1" text @click="confirmDelete"
                  >Delete</v-btn
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
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import RoutingModal from "@/components/modals/RoutingModal.vue";
export default {
  name: "Routing",
  components: {
    RoutingModal,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isOpen: null,
    });

    onMounted(() => {
      emitter.on("closeRoutingModal", () => {
        state.isModalOpen = false;
      });
    });

    const columnRoute = [
      {
        headerName: "Network",
        field: "Network",
        sortable: true,
        autoHeight: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Gateway",
        field: "Gateway",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        autoHeight: true,
        field: "Description",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Status",
        field: "Status",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRendererKeys,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];

    const rowDataRoute = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRoute.value);
      } else {
        console.error("Grid API.");
      }
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
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

    function actionCellRendererKeys(params) {
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
                data-action="edit" title="Edit Server">
                   <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>
                <button
                class="action-button delete"
                data-action="delete" title="Delete ">
                  <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>`;
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
      switch (action) {
        case "delete":
          state.deleteDialog = true;
          state.deletedRow = rowData;

          break;
        case "edit":
          console.log("rowData", rowData);
          break;

        default:
          break;
      }
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (state.deletedRow?.utility === "Private") {
        axios
          .delete(`/key_pairs/deletePrivateKey/${state.deletedRow.id}`)
          .then((response) => {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      } else if (state.deletedRow?.utility === "Public") {
        axios
          .delete(`/key_pairs/deletePublicKey/${state.deletedRow.id}`)
          .then((response) => {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          });
      }
    };
    return {
      state,
      columnRoute,
      rowDataRoute,
      defaultColDef,
      emitter,
      actionCellRendererKeys,
      openModalAdd,
      onGridReady,
      getCookie,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
