<template>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-row>
      <v-col cols="12">
        <h4>List</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-5">
          <v-col cols="12" md="6">
            <v-text-field
              id="filter-text-box"
              density="compact"
              class="w-25"
              variant="solo"
              rounded
              label="Search"
              append-inner-icon="mdi-magnify"
              single-line
              hide-details
              @input="onFilterTextBoxChanged"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine"
              :columnDefs="columnRules"
              :rowData="rowDataRules.value"
              @grid-ready="onGridReady"
              :rowDrag="true"
              :defaultColDef="defaultColDef"
              style="width: 100%"
              :pagination="true"
              :paginationPageSize="10"
            >
            </ag-grid-vue>
          </div>
        </v-row>
        <div class="error-feedback mt-5">{{ textAlert }}</div>
      </v-col>
    </v-row>
    <v-row class="d-flex justify-end mt-5">
      <div>
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          label="Add"
          :isLarge="true"
          class="ml-2"
          @click="openModalRule"
        />
      </div>
    </v-row>
    <v-dialog v-model="state.deleteDialogRule" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this rule ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete"
            >Delete</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <ModalAddRule
      :isOpenModal="state.isModalOpenRule"
      :editRowRule="state.editRowRule"
      :modalModeRule="state.modalModeRule"
    />
    
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
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalAddRule from "@/components/modals/ModalAddRule.vue";

export default {
  components: {
    AgGridVue,
    VButton,
    ModalAddRule,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      deleteDialogRule: false,
      deletedRow: null,
      modalDataRule: {},
      isOpenModal: null,
      modalModeRule: "",
      isModalOpenRule: false,
      editRowRule: {},
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rowDataRules = reactive({});
    const gridColumnApi = ref(null);
    const textAlert = ref(null);
    const gridApi = ref(null);
    const defaultColDef = ref({
      flex: 1,
      cellDataType: false,
    });
    const columnRules = [
      {
        headerName: "Rule name",
        field: "rule_name",
      },

      {
        headerName: "Routage Type",
        field: "type",
      },
      {
        headerName: "Value",
        field: "value",
      },

      {
        headerName: "Allowed by auth",
        field: "allow_by_auth",
      },
      {
        headerName: "Start",
        field: "time_from",
      },
      {
        headerName: "End",
        field: "time_to",
      },
      {
        headerName: "Status",
        field: "status",
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
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("Grid API.");
      }
    };

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      if (params.data.time_from === "--") {
        eGui.innerHTML = `
        <button
      class="action-button edit"
      data-action="edit">
         <i class="far fa-edit" style="color: #086eae;"></i>
      </button>
  
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;
      } else {
        eGui.innerHTML = `
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;
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

          state.modalDataRule = {};
          state.modalModeRule = "edit";
          state.isModalOpenRule = true;
          state.editRowRule = rowData;

          break;
        case "delete":
          console.log("delete", rowData);
          state.deleteDialogRule = true;
          state.deletedRow = rowData;
          break;
        default:
          break;
      }
    };

    const openModalRule = () => {
      state.modalDataRule = {};
      state.modalModeRule = "create";
      state.isModalOpenRule = true;
    };

    onMounted(() => {
      emitter.on("closeAddRuleModal", () => {
        state.isModalOpenRule = false;
      });

      const proxyRuleAttribute =
        document.getElementById("app").attributes["proxyRule"].value;
      const proxyRule = JSON.parse(proxyRuleAttribute);
      console.log("proxyRule", proxyRule);

      let mapedRule = proxyRule.map((i) => {
        return {
          id: i.id,
          rule_name: i.rule_name,
          days: i.days,
          status: i.status === false ? "Disable" : "Enable",
          allow_by_auth: i.allow_by_auth === false ? "Denied" : "Allow",
          time_from: i.time_from ?? "--",
          time_to: i.time_to ?? "--",
          type: i.type,
          value: i.value,
        };
      });
      console.log("mapedRule", mapedRule);

      if (!rowDataRules.value) {
        rowDataRules.value = [];
      }
      rowDataRules.value = mapedRule;
    });
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
    const cancelDelete = () => {
      state.deleteDialogRule = false;
    };
    const confirmDelete = () => {
      const csrfTok = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfTok;

      axios
        .delete(`/proxy/deleteRuleSquid/${state.deletedRow.id}`)
        .then((response) => {
          if (response.status == 200) {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };
    return {
      state,
      cancelDelete,
      confirmDelete,
      textAlert,
      columnRules,
      gridColumnApi,
      rowDataRules,
      onGridReady,
      emitter,
      openModalRule,
      actionCellRenderer,
      defaultColDef,
      onFilterTextBoxChanged,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
</style>
