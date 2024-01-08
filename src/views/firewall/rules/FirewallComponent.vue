<template>
  <div>
    <div class="container">
      <h4>Inbound rules</h4>
      <v-divider></v-divider>
      <v-dialog v-model="deleteDialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">Delete Confirmation</v-card-title>
          <v-card-text>Are you sure you want to delete this rule from the
            Firewall?</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
            <v-btn color="blue darken-1" text @click="confirmDelete">Delete</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <!-- Modal -->
      <v-dialog v-model="showAddModal" persistent max-width="600px">
        <v-card>
          <v-card-title>
            <span class="headline">{{
              mode === "create" ? "Add new" : "Update"
            }} Rule</span>
          </v-card-title>
          <v-card-text>
            <v-select :items="['accept', 'drop', 'reject']" label="Policy" v-model="policy"></v-select>
            <v-textarea variant="filled" auto-grow rows="2" row-height="20" label="Rule Description"
              v-model="rule_description" outlined></v-textarea>
            <v-select :items="['tcp', 'udp', 'icmp', 'icmp type echo-request', 'icmp type echo-reply', 'all']"
              v-model="protocol" label="Protocol" outlined></v-select>
            <v-row>
              <v-col cols="6">
                <v-text-field label="Src Address" v-model="saddr" outlined></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field label="Src Port" v-model="sport" outlined></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <v-text-field label="Dst Address" v-model="daddr" outlined></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field label="Dst Port" v-model="dport" outlined></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
          <div class="container">
            <div class="row justify-content-center">
              <br />
              <div class="col-12 d-flex justify-center">
                <VButton rounded outlined border-color="'#213E9F'" color="#ffffff" label-color="#213E9F" label="cancel"
                  :isLarge="true" @click="cancel" />
                <VButton rounded outlined color="#213E9F" label-color="#ffffff" label="save" :isLarge="true" class="ml-2"
                  @click="handleSave" />
              </div>
            </div>
          </div>
          <br />
        </v-card>
      </v-dialog>
      <v-card class="mt-3">
        <v-card-title>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field id="filter-text-box" v-model="filterText" placeholder="Search" clearable hide-details dense
                prepend-inner-icon="mdi-magnify" variant="outlined" @input="onFilterTextBoxChanged"></v-text-field>
            </v-col>
            <v-col cols="12" md="6" class="d-flex justify-end">
              <v-btn class="ml-3 mt-2" @click="showAddModal = true">
                <i class="fas fa-plus" style="color: #086eae"></i>
                <span class="ml-2" style="color: #086eae">Add</span>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-title>
        <v-card-text>
          <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine" :columnDefs="columnDefs"
            :rowData="rowData.value" @grid-ready="onGridReady" :rowDrag="true" :defaultColDef="defaultColDef"
            style="width: 100%" :animateRows="true" @column-row-group-changed="onColumnRowGroupChanged"
            @column-row-drag-end="onColumnRowDragEnd" @firstDataRendered="onFirstDataRendered"
            @row-drag-end="onRowDragEnd" :pagination="true" :paginationPageSize="10" :rowSelection="'multiple'">
          </ag-grid-vue>
        </v-card-text>
      </v-card>
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

export default defineComponent({
  name: "FirewallComponent",
  components: {
    AgGridVue,
    VButton,
  },
  props: {
    id: String,
    activeTab: String,
  },
  setup(props) {
    const alert = ref(false);
    const mode = ref("create");
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
      },
      {
        field: "rule_description",
        headerName: "Rule Description",
        headerName: "Rule Description",
        sortable: true,
        filter: true,
      },
      {
        field: "protocol",
        headerName: "Protocol",
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: [
            "tcp",
            "udp",
            "icmp type echo-request",
            "icmp type echo-reply",
            "all"
          ],
        },
        sortable: true,
        filter: true,
      },

      {
        field: "saddr",
        headerName: "Src Address",
        sortable: true,
        filter: true,
      },
      {
        field: "sport",
        headerName: "Src Port",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Dst Address",
        field: "daddr",
        sortable: true,
        filter: true,
      },
      {
        field: "dport",
        headerName: "Dst Port",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Action",
        field: "action",
        cellRenderer: actionCellRenderer,
      },
    ];
    const gridApi = ref(null);
    const gridColumnApi = ref(null);
    const defaultColDef = ref({
      flex: 1,
      editable: false,
      cellDataType: false,
    });
    const rowData = reactive([]);
    const rules = reactive([]);
    const filterText = ref(null);
    const columnOrder = ref([]);

    const deleteDialog = ref(false);
    const showAddModal = ref(false);
    const rowDataToDelete = ref(null);

    const policy = ref(null);
    const rule_description = ref(null);
    const protocol = ref(null);
    const saddr = ref(null);
    const sport = ref(null);
    const daddr = ref(null);
    const dport = ref(null);


    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      if (rowData.value && rowData.value.length > 0) {
        gridApi.value.forEachNode((node) =>
          node.setSelected(node.rowIndex === 0)
        );
      }
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
          class="action-button update"
          data-action="update"
          >
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
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
          class="action-button update"
          data-action="update"
          >
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
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
        case "update":
          mode.value = "update";
          showAddModal.value = true;
          policy.value = rowData.policy;
          rule_description.value = rowData.rule_description;
          protocol.value = rowData.protocol;
          saddr.value = rowData.saddr;
          sport.value = rowData.sport;
          daddr.value = rowData.daddr;
          dport.value = rowData.dport;
          break;
        default:
          break;
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
    const handleRemove = () => {
      alert.value = false;
    };
    const showDeleteModal = () => {
      deleteDialog.value = true;
    };

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
    };
    const cancelDelete = () => {
      rowDataToDelete.value = null;
      deleteDialog.value = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete("/rules/deleteRule/" + rowDataToDelete.value.id)
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

    };
    const saveModal = () => {
      showAddModal.value = false;
    };
    const cancel = () => {
      showAddModal.value = false;
    };
    const handleSave = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      const dataToSend = {
        type_rule: "inbound",
        policy: policy.value,
        rule_description: rule_description.value,
        protocol: [protocol.value],
        saddr: saddr.value,
        sport: sport.value,
        daddr: daddr.value,
        dport: dport.value,
      };

      try {
        const response = await axios.post(
          "/rules/saveRules/" + props.activeTab,
          dataToSend
        );
        if (response.status === 200 && response.data.msg === "success") {
          alert.value = true;
          setTimeout(() => {
            alert.value = false;
          }, 3000);
        }
      } catch (error) {
        console.error(error);
      }
    };
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
      { immediate: true },

      (newValue, oldValue) => {
        if (newValue) {
          if (mode.value === "create") {
            rowData.value.push(newValue);
            gridApi.value.forEachNode((node) =>
              node.setSelected(node.rowIndex === rowData.value.length - 1)
            );
          } else {
            const selectedNode = gridApi.value.getSelectedNodes()[0];
            if (selectedNode) {
              selectedNode.setData(newValue);
            }
          }
        }
      }
    );

    return {
      columnDefs,
      gridApi,
      gridColumnApi,
      defaultColDef,
      rowData,
      filterText,
      columnOrder,
      rules,
      deleteDialog,
      rowDataToDelete,
      showAddModal,
      alert,
      mode,
      policy,
      rule_description,
      protocol,
      saddr,
      sport,
      daddr,
      dport,
      onGridReady,
      setGridApi,
      onFirstDataRendered,
      actionCellRenderer,
      onFilterTextBoxChanged,
      arrayMove,
      onRowDragEnd,
      onColumnRowGroupChanged,
      onColumnRowDragEnd,
      handleRemove,
      showDeleteModal,
      handleAction,
      cancelDelete,
      confirmDelete,
      saveModal,
      cancel,
      handleSave,
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

.actionBtn {
  justify-content: center;
}

.button-bg-color {
  background-color: #213E9F;
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
