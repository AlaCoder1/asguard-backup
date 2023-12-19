<template>
  <div>
    <div class="container">
      <h4>Inbound rules</h4>
      <v-divider></v-divider>
      <v-alert type="success" class="d-flex mt-3 alert-style" v-if="alert">
        <span class="ml-3">
          <strong>Success!</strong> Rules saved successfully.
        </span>
      </v-alert>
      <v-dialog v-model="deleteDialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">Delete Confirmation</v-card-title>
          <v-card-text
            >Are you sure you want to delete this rule from the
            Firewall?</v-card-text
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
      <v-card class="mt-3">
        <v-card-title>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                id="filter-text-box"
                v-model="filterText"
                placeholder="Search"
                clearable
                hide-details
                dense
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                @input="onFilterTextBoxChanged"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end">
              <v-btn class="ml-3 mt-2" @click="addRow">
                <i class="fas fa-plus" style="color: #086eae"></i>
                <span class="ml-2" style="color: #086eae">Add</span>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-title>
        <v-card-text>
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine"
            :columnDefs="columnDefs"
            :rowData="rowData.value"
            @grid-ready="onGridReady"
            :rowDrag="true"
            :defaultColDef="defaultColDef"
            :editType="editType"
            style="width: 100%"
            :animateRows="true"
            @cell-value-changed="onCellValueChanged"
            @column-row-group-changed="onColumnRowGroupChanged"
            @column-row-drag-end="onColumnRowDragEnd"
            @firstDataRendered="onFirstDataRendered"
            @row-drag-end="onRowDragEnd"
            :pagination="true"
            :paginationPageSize="10"
            :rowSelection="'multiple'"
          >
          </ag-grid-vue>
        </v-card-text>
      </v-card>
    </div>
    <div class="container">
      <div class="row justify-content-center">
        <br />
        <div class="col-12 d-flex justify-end">
          <VButton
            rounded
            outlined
            border-color="'#213E9F'"
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
      </div>
    </div>
  </div>
</template>

<script>
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import axios from "axios";
import { onMounted, reactive, ref, watch, defineComponent } from "vue";
import VButton from "../../../components/VButton.vue";
import MultiSelectRenderVue from "../../firewall/rules/agGridCustomRender/MultiSelectRenderVuer.vue";

export default defineComponent({
  name: "FirewallComponent",
  components: {
    AgGridVue,
    MultiSelectRenderVue,
    VButton,
  },
  props: {
    id: String,
    activeTab: String,
  },
  setup(props) {
    // Variables
    const columnDefs = [
      {
        width: 50,
        minWidth: 50,
        maxWidth: 50,
        rowDrag: true,
        editable: false,
      },
      {
        headerCheckboxSelection: false,
        checkboxSelection: true,
        editable: false,
        width: 50,
        minWidth: 50,
        maxWidth: 50,
      },
      {
        field: "policy",
        headerName: "Policy",
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: ["accept", "drop"],
        },
        editable: (params) => params.node.data.isRowSelected,
      },
      {
        field: "rule_description",
        headerName: "Rule Description",
        editable: true,
        headerName: "Rule Description",
      },
      {
        field: "protocol",
        headerName: "Protocol",
        editable: true,
        cellEditor: "MultiSelectRenderVue",
        cellEditorParams: {
          values: [
            "tcp",
            "udp",
            "icmp type echo-request",
            "icmp type echo-reply",
          ],
          cellEditor: "CustomRichSelect",
          cellHeight: 20,
          formatValue: (value) => value.toUpperCase(),
          cellRenderer: (params) => params.value.toUpperCase(),
          searchDebounceDelay: 200,
          // Add a custom event listener to the cell editor
          onProtocolsSelected: (event) => {
            // Update the cell value with the selected values
            params.setValue(event);
          },
        },
        cellRenderer: "CustomRichSelect",
      },

      {
        field: "saddr",
        headerName: "Src Address",
        editable: true,
      },
      {
        field: "sport",
        headerName: "Src Port",
        editable: true,
        cellStyle: (params) => {
          if (
            params.data.protocol === "icmp request" ||
            params.data.protocol === "icmp reply"
          ) {
            return {
              "pointer-events": "none",
              "background-color": "#eee",
              opacity: "0.6",
            };
          }
          return null;
        },
      },
      {
        headerName: "Dst Address",
        field: "daddr",
        editable: true,
      },
      {
        field: "dport",
        headerName: "Dst Port",
        editable: true,
        cellStyle: (params) => {
          if (
            params.data.protocol === "icmp request" ||
            params.data.protocol === "icmp reply"
          ) {
            return {
              "pointer-events": "none",
              "background-color": "#eee",
              opacity: "0.6",
            };
          }
          return null;
        },
      },
      {
        headerName: "Action",
        field: "action",
        cellRenderer: actionCellRenderer,
        editable: false,
      },
    ];
    const gridApi = ref(null);
    const gridColumnApi = ref(null);
    const defaultColDef = ref({
      flex: 1,
      editable: false,
      cellDataType: false,
    });
    const editType = ref("fullRow");
    const rowData = reactive([]);
    const filterText = ref(null);
    const columnOrder = ref([]);
    const rules = reactive([]);
    const alert = ref(false);
    const isSaveDisabled = ref(true);
    const deleteDialog = ref(false);
    const rowDataToDelete = ref(null);

    // Methods
    const onCellValueChanged = (event) => {
      const row = event.data;
      row.isModified = true;
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      if (rowData.value && rowData.value.length > 0) {
        gridApi.value.forEachNode((node) =>
          node.setSelected(node.rowIndex === 0)
        );
      }
    };
    const onSelectionChanged = () => {
      const selectedNodes = gridApi.value.getSelectedNodes();
      rowData.value.forEach((row) => {
        row.isSelected = selectedNodes.some((node) => node.data === row);
        row.isRowSelected = row.isSelected;
      });

      gridApi.value.refreshCells({
        columns: [
          "Policy",
          "rule_description",
          "protocol",
          "saddr",
          "sport",
          "daddr",
          "dport",
          "Action",
        ],
      });
    };

    const setGridApi = (api) => {
      gridApi.value = api;
    };
    const onFirstDataRendered = (params) => {
      params.api.sizeColumnsToFit();
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
          class="action-button delete"
          data-action="delete"
          >
             <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        `;
      } else {
        eGui.innerHTML = `
        <button 
          class="action-button delete"
          data-action="delete">
                       <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data);
        });
      });
      return eGui;
    }
    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };
    const handleAction = (action, rowData) => {
      switch (action) {
        case "delete":
          rowDataToDelete.value = rowData;
          deleteDialog.value = true;
          break;
        default:
          break;
      }
    };
    const addRow = () => {
      const newRow = {
        isSelected: false,
        isRowSelected: false,
        isModified: false,
        policy: "accept",
        rule_description: "",
        protocol: [],
        saddr: "",
        sport: "",
        daddr: "",
        dport: "",
        Action: "",
      };

      if (!rowData.value) {
        rowData.value = [];
      }

      rowData.value.push(newRow);
      // Check if gridApi is available before using it
      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("gridApi is not available");
      }
    };

    const arrayMove = (arr, fromIndex, toIndex) => {
      const element = arr[fromIndex];
      arr.splice(fromIndex, 1);
      arr.splice(toIndex, 0, element);
      return arr.slice();
    };
    const onRowDragEnd = (event) => {
      const updatedRows =
        event.overIndex !== undefined
          ? arrayMove(rowData.value, event.node.rowIndex, event.overIndex)
          : rowData.value;

      rowData.value = updatedRows;
    };
    const onColumnRowGroupChanged = (event) => {
      const newColumnOrder = event.columns.map((column) => column.colId);
      gridApi.value.setColumnDefs(columnDefs.value);
      gridApi.value.setColumnOrder(newColumnOrder);
    };
    const onColumnRowDragEnd = (event) => {
      if (event && event.columns) {
        columnOrder.value = event.columns.map((column) => column.colId);

        gridApi.value.setColumnDefs(columnDefs.value);
        gridApi.value.setColumnOrder(columnOrder.value);
      } else {
        console.log("event.columns is undefined or null");
      }
    };
    const cancel = () => {
      rowData.value = rules.value[props.activeTab]["inbound"].filter(
        (row) => row.id
      );
      // cancel the changes of modfied rows
      rowData.value.forEach((row) => {
        if (row.isModified) {
          row.isModified = false;
        }
      });
    };
    const save = async () => {
      let modifiedRows = rowData.value.filter((row) => row.isModified);
      console.log("Modified rows:", modifiedRows);
      modifiedRows?.map((row) => {
        if (
          row.protocol.includes("icmp type echo-request") ||
          row.protocol.includes("icmp type echo-reply")
        ) {
          const newRowProtocol = row.protocol.filter(
            (item) =>
              item !== "icmp type echo-request" &&
              item !== "icmp type echo-reply"
          );
          row.protocol = newRowProtocol;
        }
      });
      const dataToSend = modifiedRows.map((row) => {
        return {
          policy: row.policy,
          rule_description: row.rule_description,
          protocol: row.protocol,
          saddr: row.saddr,
          daddr: row.daddr,
          sport: row.sport,
          dport: row.dport,
          type_rule: "inbound",
          id: row.id,
        };
      });
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      try {
        const response = await axios.post(
          "/rules/saveRules/" + props.activeTab,
          dataToSend
        );
        if (response.status === 200 && modifiedRows.length > 0) {
          modifiedRows.forEach((row) => (row.isModified = false));
          alert.value = true;
          setTimeout(() => {
            alert.value = false;
          }, 5000);
        } else {
          console.error("Failed to save data");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };
    const handleRemove = () => {
      alert.value = false;
    };
    const showDeleteModal = () => {
      deleteDialog.value = true;
    };
    const cancelDelete = () => {
      rowDataToDelete.value = null;
      deleteDialog.value = false;
    };
    const confirmDelete = () => {
      if (rowDataToDelete.value) {
        const rowData = rowDataToDelete.value;
        if (rowData.id) {
          function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
              const cookies = document.cookie.split(";");
              for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                  cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                  );
                  break;
                }
              }
            }
            return cookieValue;
          }
          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
          axios
            .delete("/rules/deleteRule/" + rowData.id)
            .then((response) => {
              const responseData = response.data;
              if (responseData.msg === "delete rule Successfully!!") {
                const index = rowData.value.indexOf(rowData);
                if (index > -1) {
                  rowData.value.splice(index, 1);
                }
              } else {
                console.error("Failed to delete row");
              }
            })
            .catch((error) => {
              console.error(error);
            });
        } else {
          const index = rowData.value.indexOf(rowData);
          if (index > -1) {
            rowData.value.splice(index, 1);
          }
        }
        rowDataToDelete.value = null;
        deleteDialog.value = false;
      }
    };

    // Lifecycle hooks
    onMounted(() => {
      const rulesAttribute =
        document.getElementById("app").attributes["rules"].value;
      let validJsonString = rulesAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      let parsedArray = JSON.parse(validJsonString);
      rules.value = parsedArray;
    });

    watch(
      () => rules.value,
      (newValue, oldValue) => {
        if (newValue) {
          rowData.value = rules.value[props.activeTab]["inbound"];
        } else {
          rowData.value = [];
        }
      },
      { immediate: true }
    );

    // Return values/methods to be used in the template
    return {
      columnDefs,
      gridApi,
      gridColumnApi,
      defaultColDef,
      editType,
      rowData,
      filterText,
      columnOrder,
      rules,
      alert,
      isSaveDisabled,
      deleteDialog,
      rowDataToDelete,
      onGridReady,
      onCellValueChanged,
      onSelectionChanged,
      setGridApi,
      onFirstDataRendered,
      actionCellRenderer,
      onFilterTextBoxChanged,
      addRow,
      arrayMove,
      onRowDragEnd,
      onColumnRowGroupChanged,
      onColumnRowDragEnd,
      cancel,
      save,
      handleRemove,
      showDeleteModal,
      handleAction,
      cancelDelete,
      confirmDelete,
    };
  },
});
</script>

<style lang="scss">
.action-button:hover {
  color: #086eae;
}

.action-button.update {
  color: #00b300;
}

.action-button.cancel {
  color: #ff0000;
}

.action-button.edit {
  color: #086eae;
}

.action-button.delete {
  color: #086eae;
}

.ag-theme-alpine .ag-header {
  background-color: #f5f5f5;
}

.v-alert.v-theme--light.bg-success.v-alert--density-default.v-alert--variant-flat.d-flex.mt-3.alert-style {
  width: 350px;
  right: -78%;
  /* Default value for small and medium screens */

  /* Media query for large screens */
  @media screen and (min-width: 1080px) {
    right: -70%;
    /* Value for larger screens */
  }
}
</style>
