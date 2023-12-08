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
              :columnDefs="columnAclList"
              :rowData="rowDataAclList.value"
              @grid-ready="onGridReady"
              :defaultColDef="defaultColDef"
              style="width: 100%"
              :animateRows="true"
              :pagination="true"
              :paginationPageSize="10"
              :rowSelection="'multiple'"
            >
            </ag-grid-vue>
          </div>
        </v-row>

        <ModalSquidBlackList
          :isOpen="state.isModalOpen"
          :editRow="state.editRow"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { reactive, ref, onMounted, inject } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidBlackList from "@/components/modals/ModalSquidBlackList.vue";
export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidBlackList,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
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
      editable: true,
      cellDataType: false,
    });
    const columnAclList = [
      {
        headerName: "List name",
        field: "list_name",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Category",
        field: "category",
        sortable: true,
        filter: true,
      },
      {
        headerName: "List Count",
        field: "list_count",
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

      if (rowDataAclList.value && rowDataAclList.value.length > 0) {
        gridApi.value.forEachNode((node) =>
          node.setSelected(node.rowIndex === 0)
        );
      }
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAclList.value);
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

      let editingCells = params.api.getEditingCells();
      // checks if the rowIndex matches in at least one of the editing cells
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
         <i class="far fa-edit" style="color: #086eae;"></i> 
      </button>
    <button 
      class="action-button delete"
      data-action="delete">
        <i class="fas fa-times" style="color: #086eae;"></i>
    </button>
    `;
      }

      // Add event listeners to handle button clicks
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
        default:
          break;
      }
    };

    onMounted(() => {
      emitter.on("closeAclListModal", () => {
        state.isModalOpen = false;
      });
      if (!rowDataAclList.value) {
        rowDataAclList.value = [];
      }
      const newRow = {
        list_name: "souhail",
        category: "category",
        list_count: "list_count",
      };
      rowDataAclList.value.push(newRow);
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
      onFilterTextBoxChanged,
      handleAction,
    };
  },
};
</script>
