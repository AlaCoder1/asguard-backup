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
      updateFresh: {
        type: Array,
      },
    },
  
    setup(props) {
      const { updateFresh } = toRefs(props);
      const gridApi = ref(null);
      const rowDataUpdate = reactive({});
  
      const columnUpdate = [
        {
          headerName: "File Name",
          field: "date",
          sortable: true,
          autoHeight: true,
          filter: true,
        },
        {
          headerName: "File Path",
          field: "process_type",
          sortable: true,
          autoHeight: true,
          filter: true,
        },
        {
          headerName: "Status",
          autoHeight: true,
          field: "status",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Actions",
          autoHeight: true,
          field: "actions",
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
    //   watch(
    //     () => updateFresh.value,
    //     (val) => {
    //       if (!rowDataUpdate.value) rowDataUpdate.value = [];
    //       rowDataUpdate.value = val;
    //     }
    //   );
  

  
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
  