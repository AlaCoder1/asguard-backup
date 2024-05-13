<template>
  <div class="mt-3">
    <h4>General information</h4>
    <v-divider class="mb-2"></v-divider>
    <div style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-3"
        style="width: 100%"
        @grid-ready="onGridReady"
        :columnDefs="columnRules"
        :rowData="rowDataRules.value"
        :gridOptions="gridOptions"
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
  </div>

  <v-snackbar
    :timeout="2000"
    v-model="state.snackbar"
    location="bottom right"
    :color="state.color"
  >
    {{ state.textAlert }}
  </v-snackbar>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import VButton from "@/components/VButton.vue";
import { reactive, ref } from "vue";

export default {
  name: "Rules",
  components: {
    VButton,
    AgGridVue,
  },
  setup() {
    const state = reactive({
      snackbar: false,
      color: "",
      textAlert: "",
    });

    const columnRules = [
      {
        headerName: "ID",
        field: "ID",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Request Action",
        field: "request_action",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: "Rule",
        field: "Rule",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Status",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        field: "action",
      },
    ];
    const rowDataRules = reactive({});
    const gridApi = ref(null);
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("Grid API.");
      }
    };

    return {
      state,
      onGridReady,
      columnRules,
      rowDataRules,
      gridOptions,
    };
  },
};
</script>
