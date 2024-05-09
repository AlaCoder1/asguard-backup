<template>
  <div class="mr-3">
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>{{ $t("networksServers") }}</h4>
      <!-- <v-divider></v-divider> -->
      <v-row>
        <v-col cols="12">
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnDefs"
              :rowData="rowData.value"
              :gridOptions="gridOptions"
              :localeText="paginationLocalization"
            />
          </div>
          <div class="d-flex justify-end">
            <v-btn
              color="asguard_primary_light"
              :rounded="true"
              class="mt-3 btn-add"
              @click="openModalAdd"
            >
              <span class="text-white"> {{ $t("button.addServer") }}</span>
            </v-btn>
          </div>
        </v-col>
      </v-row>
      <Modal
        :modalMode="state.modalMode"
        :isOpen="state.isModalOpen"
        :editRow="state.editRow"
      />
    </div>
    <v-dialog v-model="state.deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{
          $t("delete.DeleteConfirmation")
        }}</v-card-title>
        <v-card-text>{{ $t("delete.questionserver") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">{{
            $t("PageGeneral.form.Cancel")
          }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete">{{
            $t("PageGeneral.form.Delete")
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
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject, computed } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import Modal from "@/components/modals/Modal.vue";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  name: "Sdwan",
  components: {
    Modal,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const paginationLocalization = reactive({
      of: "/",
    });

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
      editRow: {},
    });

    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const servername = computed(() => {
      return t("PageGeneral.ServerName");
    });
    
    const columnDefs = ref([
      {
        headerName: servername,
        field: "server_name",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Url",
        field: "server_url",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      { headerName: "Actions", cellRenderer: actionCellRenderer },
    ]);

    const rowData = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("Grid API.");
      }
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
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
        eGui.innerHTML = `
         
              <button
                class="action-button edit"
                data-action="edit">
                   <i class="far fa-edit" style="color: #086EAE;"></i>
                </button>
                <button
                class="action-button delete"
                data-action="delete">
                  <i class="fas fa-times" style="color: #086EAE;"></i>
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
      switch (action) {
        case "edit":
          console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          break;
        case "delete":
          console.log("delete", rowData);
          state.deleteDialog = true;
          state.deletedRow = rowData;

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

    onMounted(() => {
      emitter.on("closeServerModal", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      let allLisServers =
        document.getElementById("app").attributes["servers"].value;

      const parsedArray = JSON.parse(allLisServers);

      rowData.value = parsedArray;
    });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/ldap/deleteldap_Server/${state.deletedRow.id}`)
        .then((response) => {
          console.log("response.data", response.data);
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
    };
    return {
      state,
      t,
      paginationLocalization,
      gridOptions,
      columnDefs,
      emitter,
      rowData,
      defaultColDef,
      actionCellRenderer,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>

<style></style>
