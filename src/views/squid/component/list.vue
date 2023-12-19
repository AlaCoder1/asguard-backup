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
    <ModalAddRule
      :isOpenModal="state.isModalOpenRule"
      :editRowRule="state.editRowRule"
      :modalModeRule="state.modalModeRule"
    />
  </div>
</template>

<script>
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
      modalDataRule: {},
      isOpenModal: null,
      modalModeRule: "",
      isModalOpenRule: false,
      editRowRule: {},
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
        sortable: true,
        filter: true,
      },

      {
        field: "routage_type",
        headerName: "Routage Type",
      },
      {
        headerName: "Value",
        field: "value",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Allowed by authentification",
        field: "allowed",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Status",
        field: "status",
        sortable: true,
        filter: true,
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

      if (!rowDataRules.value) {
        rowDataRules.value = [];
      }
      let obj = {
        rule_name: "rule name",
        value: "test",
        routage_type: "test",
        allowed: "test",
        status: "test",
      };
      rowDataRules.value.push(obj);
    });

    return {
      state,
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
