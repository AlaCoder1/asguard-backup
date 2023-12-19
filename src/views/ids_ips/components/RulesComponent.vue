<template>
  <div class="mt-3 ml-3 mr-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="12">
        <h4>Services Intrusion Detection</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column;">
          <div v-for="(message, index) in state.messages" :key="index">
            <v-alert
              v-model="message.snackbar"
              :type="message.color"
              class="d-flex mt-3"
              :style="{
                position: 'fixed',
                marginTop: '10 px',
                top: `${100 + index * 80}px`,
                right: '10px',
                zIndex: 9999,
              }"
            >
              <!-- style="position: fixed; top: 80px; right: 10px;"> -->
              <span class="c-o ml-3">
                <strong>{{ message.color }} </strong> {{ message.text }}
              </span>
              <span class="ml-16" style="margin-top: 20px !important;">
                <i
                  class="fas fa-times justify-end cursor"
                  @click="handleRemove(index)"
                ></i>
              </span>
            </v-alert>
          </div>
          <v-dialog v-model="deleteDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">Delete Confirmation</v-card-title>
              <v-card-text
                >Are you sure you want to delete this rule from
                suricata?</v-card-text
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
                    <i class="fas fa-plus" style="color: #086eae;"></i>
                    <span class="ml-2" style="color: #086eae;">Add</span>
                  </v-btn>
                  <v-btn @click="reloadData" icon>
                <v-icon class="small-refresh-icon">mdi-refresh</v-icon>
              </v-btn>
                </v-col>
              </v-row>
            </v-card-title>
            <v-card-text>
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
                style="width: 100%;"
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
          <div class="d-flex justify-end mt-3">
            <div class="mr-3 flex center">
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
                @click="save" />
  
    
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";
import { inject } from "vue";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS
import axios from "axios";
export default {
  name: "RulesComponent",
  components: {
    AgGridVue,
    VButton,
  },
  props: {
    id: String,
    activeTab: String,
    configInfo: String,
  },
  setup(props) {
    const emitter = inject("emitter");
    const state = reactive({
      loading: false,
      isLoadingDialogue: false,

      snackbar: false,
      color: "",
      textAlert: "",
      messages: [],
    });
    const columnRules = [
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
        sortable: false,
      },
      {
        headerName: "id",
        field: "id",
        sortable: true,
        hide: true,
        sort: "asc",
      },
      {
        headerName: "Action",
        field: "action",
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: [
            "alert",
            "pass",
            "drop",
            "reject",
            "rejectsrc",
            "rejectdst",
            "rejectnoth",
          ],
        },
        editable: true,
        minWidth: 150,
      },
      {
        headerName: "Protocol",
        field: "protocol",
        editable: true,
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: [
            "tcp",
            "udp",
            "icmp",
            "ip",
            "http",
            "smtp",
            "krb5",
            "sip",
            "ftp",
            "imap",
            "ntp",
            "http2",
            "tls(ssl)",
            "modbus(*)",
            "dhcp",
            "smb",
            "dnp3(*)",
            "rfb",
            "dns",
            "enip(*)",
            "rdp",
            "dcerpc",
            "nfs",
            "snmp",
            "ssh",
            "ikev2",
            "tftp",
            "pkthdr",
          ],
        },
        editable: true,
        minWidth: 150,
      },
      {
        headerName: "Source address",
        field: "source_ip",
        editable: true,
        minWidth: 150,
      },
      {
        headerName: "Direction",
        field: "direction",
        editable: true,
        minWidth: 150,
      },
      {
        headerName: "Destination address",
        field: "destination_ip",
        editable: true,
        minWidth: 200,
      },
      {
        headerName: "Message",
        field: "msg",
        editable: true,
        minWidth: 400,
      },
      {
        headerName: "Revision",
        field: "rev",
        editable: true,
        minWidth: 125,
      },
      {
        headerName: "Sid",
        field: "sid",
        editable: true,
        minWidth: 100,
      },
      {
        headerName: "Status",
        field: "activate_rule",
        editable: true,
        minWidth: 100,
      },

      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];

    const currentIndex = ref(0);
    const deleteDialog = ref(false);
    const rowDataToDelete = ref(null);
    const rowDataRules = reactive({});
    const gridColumnApi = ref(null);
    const gridApi = ref(null); // Optional - for accessing Grid's API
    // Methods
    const onCellValueChanged = (event) => {
      const row = event.data;
      row.isModified = true;
    };
    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      if (rowDataRules.value && rowDataRules.value.length > 0) {
        gridApi.value.forEachNode((node) =>
          node.setSelected(node.rowIndex === 0)
        );
      }
    };
    // DefaultColDef sets props common to all Columns
    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
      suppressMovable: true,
    };
    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };
    const handleAction = (action, rowData) => {
      rowDataToDelete.value = rowData;
      deleteDialog.value = true;
    };
    const addRow = () => {
      const newRow = {
        isSelected: false,
        isRowSelected: false,
        isModified: false,
        action: "alert",
        protocol: "",
        source_ip: "",
        direction: "",
        destination_ip: "",
        msg: "",
        rev: 0,
        sid: 0,
        activate_rule: false,
      };

      if (!rowDataRules.value) {
        rowDataRules.value = [];
      }

      // rowDataRules.value.push(newRow);
      // Add the new row at the beginning of the array
      rowDataRules.value.unshift(newRow);
      // Check if gridApi is available before using it
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
        // If pagination is enabled, navigate to the first page
        if (gridApi.value.paginationGetCurrentPage() > 1) {
          gridApi.value.paginationGoToFirstPage();
        }

        // Focus on the newly added row to make it editable
        const newRowNode = gridApi.value.getRenderedNodes()[0];
        if (newRowNode) {
          newRowNode.setSelected(true);
          // newRowNode.setEditing(true);
        }
      } else {
        console.error("gridApi is not available");
      }
    };
    const onSelectionChanged = () => {
      const selectedNodes = gridApi.value.getSelectedNodes();
      rowDataRules.value.forEach((row) => {
        row.isSelected = selectedNodes.some((node) => node.data === row);
        row.isRowSelected = row.isSelected;
      });
      gridApi.value.refreshCells({
        columns: [
          "id",
          "action",
          "protocol",
          "source_ip",
          "direction",
          "destination_ip",
          "msg",
          "rev",
          "sid",
          "activate_rule",
        ],
      });
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
      }
      const reloadData = async() => {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken; 
        state.loading = true;
        state.isLoadingDialogue = true;
        try {
        const response = await axios.post(
          "addDefaultRulesToDatabase/" + props.configInfo
        );
        if (response.status === 200 ) {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          // state.messages=response.data.message
          showMessage({
                color: "success",
                text: "All rules saved successfully!!",
              });
            } else {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
              showMessage({
                color: "error",
                text: "Failed to save rule!",
              });
            }
      } catch (error) {
        showMessage({
          color: "error",
          text: "Failed to consomme api!".concat(error),
        });
      }
    };
  
    const save = async () => {
      let modifiedRows = rowDataRules.value.filter((row) => row.isModified);
      const dataToSend = modifiedRows.map((row) => {
        return {
          action: row.action,
          protocol: row.protocol,
          source_ip: row.source_ip,
          direction: row.direction,
          destination_ip: row.destination_ip,
          msg: row.msg,
          rev: row.rev,
          sid: row.sid,
          activate_rule: row.activate_rule,
          id: row.id,
        };
      });
    
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      try {
        const response = await axios.post(
          "/ids-ips/saveRulesSuricata/" + props.configInfo,
          dataToSend
        );
        if (
          response.status === 200 &&
          modifiedRows.length > 0 &&
          response.data.message.length > 0
        ) {
          // state.messages=response.data.message
          modifiedRows.forEach((row) => (row.isModified = false));
          response.data.message.forEach(async (rule) => {
            if (rule.status === 200) {
              showMessage({
                color: "success",
                text: "Rule saved successfully!",
              });
            } else {
              showMessage({
                color: "error",
                text: "Failed to save rule!",
              });
            }
          });
        }
      } catch (error) {
        showMessage({
          color: "error",
          text: "Failed to save rule!",
        });
      }
    };
    

    const cancel = () => {
      rowDataRules.value = rowDataRules.value.filter((row) => row.id);
      // cancel the changes of modfied rows
      rowDataRules.value.forEach((row) => {
        if (row.isModified) {
          row.isModified = false;
        }
      });
    };
    const handleRemove = (index) => {
      state.messages[index].snackbar = false;
    };
    const showMessage = (message) => {
      // Show a new message in the alert
      state.messages.push({ 
        color: message.color,
        text: message.text,
        snackbar: true,
      });
      // Automatically close the alert after a specified delay
      const lastIndex = state.messages.length - 1;
      setTimeout(() => {
        state.messages[lastIndex].snackbar = false;
        state.messages[lastIndex].read = true; // Mark the message as read
        updateIndex(); // Update the index after setting a message as read
      }, 2000 * (lastIndex + 1));
    };
    const updateIndex = () => {
      // Check if all messages are read
      const allRead = state.messages.every((message) => message.read);
      // If all messages are read, reset the index to 0
      if (allRead) {
        state.messages = [];
        currentIndex.value = 0;
        setTimeout(() => {
          location.reload();
        },3000)
       
      } else {
        // Increment the index if not all messages are read
        currentIndex.value += 1;
      }
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
        if (rowData.sid) {
          const index = rowDataRules.value.findIndex(
            (item) => item.id === rowData.id
          );
          if (index !== -1) {
            rowDataRules.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataRules.value);
            } else {
              console.error("Grid API.");
            }
          }
          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
          axios
            .delete("/ids-ips/deleteRule/" + rowData.sid)
            .then((response) => {
              if (response.status === 200) {
                showMessage({
                  color: "success",
                  text: "Delete rule Successfully!",
                });
               
              } else {
                showMessage({
                  color: "error",
                  text: "Failed to delete rule!",
                });
              }
            })
            .catch((error) => {
              showMessage({
                color: "error",
                text: "Failed to delete rule!",
              });
            });
        } else {
          const index = rowDataRules.value.indexOf(rowData);
          if (index > -1) {
            rowDataRules.value.splice(index, 1);
            if (gridApi.value) {
              gridApi.value.setRowData(rowDataRules.value);
            } else {
              console.error("Grid API.");
            }
          }
        }
        rowDataToDelete.value = null;
        deleteDialog.value = false;
      }
    };

    const rowGroupPanelShow = ref("always");

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });
      eGui.innerHTML = `
        <button
          class="action-button delete"
          data-action="delete" title="Delete Rule">
             <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>

        `;
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data);
        });
      });
      return eGui;
    }

    onMounted(async () => {
      try {
        rowDataRules.value = document.getElementById("app").attributes[
          "rules_suricata"
        ].value;
        
        let validJsonString2 = rowDataRules.value
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        let parsedArray2 = JSON.parse(validJsonString2);
        rowDataRules.value = parsedArray2;
      } catch (error) {
        console.error("Error setting rowDataRules:", error);
      }
    });

    return {
      state,
      columnRules,
      rowDataRules,
      defaultColDef,
      rowGroupPanelShow,
      emitter,
      currentIndex,
      deleteDialog,
      cellWasClicked: (event) => {
        // Example of consuming Grid Event
        console.log("cell was clicked", event);
      },
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      actionCellRenderer,
      onGridReady,
      addRow,
      onFilterTextBoxChanged,
      handleAction,
      onCellValueChanged,
      onSelectionChanged,
      cancel,
      save,
      handleRemove,
      showDeleteModal,
      cancelDelete,
      confirmDelete,
      showMessage,
      updateIndex,
      reloadData,
    };
  },
};
</script>

<style lang="scss"></style>
