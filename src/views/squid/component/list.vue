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
          <v-col cols="12" md="6" class="d-flex justify-end">
            <v-btn class="ml-3 mt-2" @click="addRow">
              <i class="fa fa-plus-circle" style="color: #086eae"></i>
              <span class="ml-2" style="color: #086eae">Add New</span>
            </v-btn>
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
              :editType="editType"
              style="width: 100%"
              :animateRows="true"
              @cell-value-changed="onCellValueChanged"
              @column-row-group-changed="onColumnRowGroupChanged"
              :pagination="true"
              :paginationPageSize="10"
              :rowSelection="'multiple'"
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
          color="#ffffff"
          label-color="#213E9F"
          label="cancel"
          :isLarge="true"
          @click="cancel"
        />
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          label="save"
          :isLarge="true"
          class="ml-2"
          @click="save"
        />
      </div>
    </v-row>
  </div>
</template>

<script>
import { reactive, ref } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import MultiSelectRenderVue from "../agGridCustomRender/MultiSelectRenderVuer.vue";
import StartDateFieldRenderVue from "../agGridCustomRender/StartDateFieldRenderVue.vue";
import EndDateFieldRenderVue from "../agGridCustomRender/EndDateFieldRenderVue.vue";
export default {
  components: {
    AgGridVue,
    MultiSelectRenderVue,
    StartDateFieldRenderVue,
    EndDateFieldRenderVue,
    VButton,
  },
  setup() {
    const state = reactive({
      off: false,
      on: false,
      proxyPort: "",
      enable: false,
      filterText: "",
      published: "",
    });

    const rowDataRules = reactive({});
    const gridColumnApi = ref(null);
    const textAlert = ref(null);
    const editType = ref("fullRow");
    const gridApi = ref(null);
    const defaultColDef = ref({
      flex: 1,
      editable: true,
      cellDataType: false,
    });
    const columnRules = [
      {
        headerName: "Rule name",
        field: "rule_name",
        sortable: true,
        filter: true,
        editable: true,
      },

      {
        field: "routage_type",
        headerName: "Routage Type",
        editable: true,
        cellEditor: "MultiSelectRenderVue",
        cellEditorParams: {
          values: ["subnet", "ips", "domains"],
          formatValue: (value) => value.toUpperCase(),
          cellRenderer: (params) => params.value.toUpperCase(),

          onProtocolsSelected: (event) => {
            params.setValue(event);
          },
        },
      },
      {
        headerName: "Value",
        field: "value",
        sortable: true,
        filter: true,
        editable: true,
      },
      {
        headerName: "Start Time",
        field: "start_time",
        sortable: true,
        filter: true,
        editable: true,
        cellEditor: "StartDateFieldRenderVue",
      },
      {
        headerName: "End Time",
        field: "end_time",
        sortable: true,
        filter: true,
        editable: true,
        cellEditor: "EndDateFieldRenderVue",
      },
      {
        headerName: "Status",
        field: "status",
        cellRenderer: checkboxRender,
        sortable: true,
        filter: true,
        editable: false,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        editable: false,
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

      if (rowDataRules.value && rowDataRules.value.length > 0) {
        gridApi.value.forEachNode((node) =>
          node.setSelected(node.rowIndex === 0)
        );
      }
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("Grid API.");
      }
    };
    const onCellValueChanged = (event) => {
      //   const row = event.data;
      //   row.isModified = true;
    };

    const onColumnRowGroupChanged = (event) => {
      //   const newColumnOrder = event.columns.map((column) => column.colId);
      //   gridApi.value.setColumnDefs(columnDefs.value);
      //   gridApi.value.setColumnOrder(newColumnOrder);
    };

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };

    const addRow = () => {
      const newRow = {
        rule_name: "",
        routage_type: "",
        value: "",
        start_time: "",
        end_time: "",
        status: "",
      };

      if (!rowDataRules.value) {
        rowDataRules.value = [];
      }

      rowDataRules.value.push(newRow);
      // Check if gridApi is available before using it
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("gridApi is not available");
      }
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

          break;
        default:
          break;
      }
    };

    const hasEmptyProperty = (obj) => {
      console.log("object", obj);

      const emptyProperties = [];
      if (obj.rule_name === "") {
        emptyProperties.push("Rule Name");
      }

      if (obj.routage_type === "") {
        emptyProperties.push("Routage Type");
      }
      if (obj.start_time === "") {
        emptyProperties.push("Start Time");
      }

      if (obj.end_time === "") {
        emptyProperties.push("End Time");
      }

      if (obj.value === "") {
        emptyProperties.push("Value");
      } else if (
        obj.routage_type === "subnet" &&
        !isValidSubnetFormat(obj.value)
      ) {
        emptyProperties.push("Value Format must be XX.XX.XX.XX/XX");
      }

      return emptyProperties;
    };
    const isValidSubnetFormat = (value) => {
      const subnetRegex = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;
      return subnetRegex.test(value);
    };

    const save = () => {
      if (!rowDataRules.value) rowDataRules.value = [];

      var emptyPropertiesList = rowDataRules.value
        .map(hasEmptyProperty)
        .filter((properties) => properties.length > 0);

      const concatenatedArray = emptyPropertiesList.reduce(
        (acc, curr) => acc.concat(curr),
        []
      );

      const uniqueArray = [...new Set(concatenatedArray)];

      if (emptyPropertiesList.length > 0) {
        textAlert.value = "The following properties are empty: " + uniqueArray;
      } else {
        textAlert.value = "";
      }
    };
    function checkboxRender(params) {
      var input = document.createElement("input");
      input.type = "checkbox";
      // params.value = params.data.server_status;
      input.checked = params.value;

      input.style.margin = "10px";
      input.style.width = "20px";
      input.style.height = "18px";
      input.style.cursor = "pointer";

      input.addEventListener("click", function (event) {
        params.value = !params.value;
        // params.data.server_status = params.value;
      });
      return input;
    }

    return {
      state,
      textAlert,
      columnRules,
      gridColumnApi,
      rowDataRules,
      onGridReady,
      save,
      actionCellRenderer,
      defaultColDef,
      onCellValueChanged,
      onColumnRowGroupChanged,
      onFilterTextBoxChanged,
      addRow,
      checkboxRender,
      editType,
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
