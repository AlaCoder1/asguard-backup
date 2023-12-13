<template>
  <div style="overflow: hidden; flex-grow: 1">
    <v-row>
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

    <ag-grid-vue
      id="grid-wrapper"
      domLayout="autoHeight"
      class="ag-theme-alpine mt-3"
      style="width: 100%"
      @grid-ready="onGridReady"
      :columnDefs="columnUpdate"
      :rowData="rowDataUpdate.value"
    />
  </div>
</template>

<script>
import { ref, reactive } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  components: {
    AgGridVue,
  },

  setup() {
    const gridApi = ref(null);
    const rowDataUpdate = reactive({});

    const columnUpdate = [
      {
        headerName: "Date",
        field: "date",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Process",
        field: "Process",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Line",
        autoHeight: true,
        field: "Line",
        sortable: true,
        filter: true,
      },
    ];

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };


    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataUpdate.value);
      } else {
        console.error("Grid API.");
      }
    };
    return {
      onGridReady,
      onFilterTextBoxChanged,
      columnUpdate,
      rowDataUpdate,
      gridApi,
    };
  },
};
</script>
