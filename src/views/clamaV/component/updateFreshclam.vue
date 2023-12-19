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
import { ref, toRefs, reactive, watch } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  components: {
    AgGridVue,
  },

  props: {
    freshclam: {
      type: Array,
    },
  },

  setup(props) {
    const { freshclam } = toRefs(props);
    const gridApi = ref(null);
    const rowDataUpdate = reactive({});

    const columnUpdate = [
      {
        headerName: "Date",
        field: "date",
        width: 150,
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Process",
        field: "process_type",
        sortable: true,
        autoHeight: true,
        width: 150,
        filter: true,
      },
      {
        headerName: "Line",
        autoHeight: true,
        cellRenderer: formatedLine,
        sortable: true,
        filter: true,
        width: 350,
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
    watch(
      () => freshclam.value,
      (val) => {
        if (!rowDataUpdate.value) rowDataUpdate.value = [];
        rowDataUpdate.value = val;
      }
    );

    function formatedLine(data) {
      const longString = data.data.line;
      const chunks = longString.match(/.{1,100}/g);

      const resultWithBr = chunks.map((chunk) => chunk + "<br>").join("");

      let eGui = document.createElement("div");

      eGui.innerHTML = `${resultWithBr}
        `;
      eGui.style.lineHeight = "2";
      return eGui;
    }

    return {
      onGridReady,
      onFilterTextBoxChanged,
      formatedLine,
      columnUpdate,
      rowDataUpdate,
      gridApi,
    };
  },
};
</script>
