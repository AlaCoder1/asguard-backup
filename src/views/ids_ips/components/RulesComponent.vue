<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
          <v-card-text v-html="overlayMessage">
          </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
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
            {{ $t("sdwan.pleaseWait") }}
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
        <h4>{{ $t("suricata.servicesIntrusion") }}</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column" class="mt-3">
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
              <span class="ml-16" style="margin-top: 20px !important">
                <i
                  class="fas fa-times justify-end cursor"
                  @click="handleRemove(index)"
                ></i>
              </span>
            </v-alert>
          </div>
          <v-dialog v-model="deleteDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">{{
                $t("delete.DeleteConfirmation")
              }}</v-card-title>
              <v-card-text>{{ $t("delete.deleteRow") }} ?</v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="cancelDelete">{{
                  $t("buttons.cancel")
                }}</v-btn>
                <v-btn color="blue darken-1" text @click="confirmDelete">{{
                  $t("buttons.delete")
                }}</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-card class="mt-3">
            <v-card-title>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    id="filter-text-box"
                    class="mb-3"
                    v-model="filterText"
                    :placeholder="$t('squid.search')"
                    density="compact"
                    rounded
                    variant="solo"
                    hide-details
                    dense
                    prepend-inner-icon="mdi-magnify"
                    @input="onFilterTextBoxChanged"
                  ></v-text-field>
                </v-col>

                <!-- <v-col cols="12" md="6" class="d-flex justify-end">
                  <v-btn class="ml-3 mt-2" @click="addRow">
                    <i class="fas fa-plus" style="color: #086eae;"></i>
                    <span class="ml-2" style="color: #086eae;">Add</span>
                  </v-btn>
                </v-col> -->
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
                style="width: 100%"
                :animateRows="true"
                @cell-value-changed="onCellValueChanged"
                @column-row-group-changed="onColumnRowGroupChanged"
                @column-row-drag-end="onColumnRowDragEnd"
                @firstDataRendered="onFirstDataRendered"
                @row-drag-end="onRowDragEnd"
                :rowSelection="'multiple'"
                :overlayNoRowsTemplate="overlayTemplate"
              >
              </ag-grid-vue>
              <v-pagination
                class="mt-5"
                v-model="state.page"
                :length="state.nombrePageRules"
                @update:model-value="getData"
              ></v-pagination>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-end mt-5 mb-10">
            <div class="mr-3 flex center">
              <!-- <VButton
                rounded
                outlined
                color="#ffffff"
                label-color="#213E9F"
                :label="$t('buttons.cancel')"
                :isLarge="true"
                @click="cancel"
              /> -->
              <VButton
                rounded
                outlined
                color="#213E9F"
                label-color="#ffffff"
                :label="$t('buttons.save')"
                :isLarge="true"
                class="ml-2"
                @click="save"
              />
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref, computed } from "vue";
import { inject } from "vue";
import { user_privilege } from "@/mixins/user_privilege.js";

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
    const current_user = ref();
    const last_Subscription = ref([]);
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const state = reactive({
      nombrePageRules: null,
      isviewModal: false,
      viewModal: false,
      page: 1,
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
      messages: [],
    });

    const protocol = computed(() => {
      return t("suricata.protocol");
    });
    const revision = computed(() => {
      return t("suricata.revision");
    });
    const status = computed(() => {
      return t("squid.status");
    });
    const overlayMessage = computed(() => {
current_user.value= user_privilege('Suricata') 
console.log('current_user',current_user.value)
  if (current_user.value === "viewer" || current_user.value === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("IDS/IPS")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
});

    const columnRules = ref([
      // {
      //   width: 50,
      //   minWidth: 50,
      //   maxWidth: 50,
      //   rowDrag: true,
      //   editable: false,
      // },
      // {
      //   headerCheckboxSelection: false,
      //   checkboxSelection: true,
      //   editable: false,
      //   width: 50,
      //   minWidth: 50,
      //   maxWidth: 50,
      //   sortable: false,
      // },
      {
        headerName: "id",
        field: "id",
        sortable: true,
        hide: true,
        sort: "asc",
      },
      {
        headerName: "Sid",
        field: "sid",
        // editable: true,
        minWidth: 100,
        sortable: false,
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
        minWidth: 120,
        sortable: false,
      },
      {
        headerName: "Message",
        field: "msg",
        editable: true,
        minWidth: 400,
        autoHeight: true,
        cellStyle: { whiteSpace: "pre-wrap", lineHeight: "2" },
        sortable: false,
      },
      {
        headerName: protocol,
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
        // editable: true,
        minWidth: 120,
        sortable: false,
      },
      {
        headerName: "Source",
        field: "source_ip",
        // editable: true,
        minWidth: 150,
        autoHeight: true,
        cellStyle: { whiteSpace: "pre-wrap", lineHeight: "2" },
        sortable: false,
      },
      {
        headerName: "Direction",
        field: "direction",
        // editable: true,
        minWidth: 125,
        sortable: false,
      },
      {
        headerName: "Destination",
        field: "destination_ip",
        // editable: true,
        minWidth: 150,
        autoHeight: true,
        cellStyle: { whiteSpace: "pre-wrap", lineHeight: "2" },
        sortable: false,
      },

      {
        headerName: revision,
        field: "rev",
        // editable: true,
        minWidth: 125,
        sortable: false,
      },

      {
        headerName: status,
        field: "activate_rule",
        editable: true,
        minWidth: 100,
        sortable: false,
      },

      // {
      //   headerName: "Actions",
      //   cellRenderer: actionCellRenderer,
      //   minWidth: 100,
      //   field: "action",
      //   filter: true,
      //   sortable: false,

      // },
    ]);

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

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };
    const handleAction = (action, rowData) => {
      const user = user_privilege('Suricata');
      if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("IDS/IPS")) {
        rowDataToDelete.value = rowData;
        deleteDialog.value = true;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    const addRow = () => {
      const newRow = {
        isSelected: false,
        isRowSelected: false,
        isModified: false,
        sid: 0,
        action: "alert",
        msg: "",
        protocol: "",
        source_ip: "",
        direction: "",
        destination_ip: "",
        rev: 0,
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
          "sid",
          "action",
          "msg",
          "protocol",
          "source_ip",
          "direction",
          "destination_ip",
          "rev",
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
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const reloadData = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      state.loading = true;
      state.isLoadingDialogue = true;
      try {
        const response = await axios.post(
          "activerSuricataUpdate/" + props.configInfo
        );
        if (response.status === 200) {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          // state.messages=response.data.message
          showMessage({
            color: "success",
            text: t("suricata.allRulesSaved"),
          });
        } else {
          state.loading = false;
          state.isLoadingDialogue = false;
          state.snackbar = true;
          showMessage({
            color: "error",
            text: t("suricata.failedToUpdate"),
          });
        }
      } catch (i) {
        state.loading = false;
        state.isLoadingDialogue = false;

        if (i.response.status === 500) {
          state.snackbar = true;
          showMessage({
            color: "error",
            text: t("errors.errorServer"),
          });
        } else {
          state.snackbar = true;
          showMessage({
            color: "error",
            text: i,
          });
        }
      }
    };

    const save = async () => {
      const user = user_privilege('Suricata');
      if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("IDS/IPS")) {
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
                  text: t("suricata.rulesavedSuccessfully"),
                });
              } else {
                showMessage({
                  color: "error",
                  text: t("suricata.failed"),
                });
              }
            });
          }
        } catch (i) {
          if (i.response.status === 500) {
            state.snackbar = true;
            showMessage({
              color: "error",
              text: t("errors.errorServer"),
            });
          } else {
            state.snackbar = true;
            showMessage({
              color: "error",
              text: t("suricata.failed"),
            });
          }
        }
      } else {
        state.isviewModal = true;
        state.viewModal = true;
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
          // location.reload();
        }, 3000);
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
                  text: t("suricata.deleteRuleSuccessfully"),
                });
              } else {
                showMessage({
                  color: "error",
                  text: t("suricata.failedToDeleteRule"),
                });
              }
            })
            .catch((i) => {
              if (i.response.status === 500) {
                state.snackbar = true;
                showMessage({
                  color: "error",
                  text: t("errors.errorServer"),
                });
              } else {
                state.snackbar = true;
                showMessage({
                  color: "error",
                  text: t("suricata.failedToDeleteRule"),
                });
              }
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
          data-action="delete">
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
    const getData = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .get(`/ids-ips/getRulesFromDatabase/${state.page}`)
        .then((response) => {
          console.log("response", response);
          rowDataRules.value = response.data.rules;
          state.nombrePageRules = response.data.nombrePageRules;
        })
        .catch((e) => {
          console.log("e", e.response);
        });
    };
    onMounted(() => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)
      getData();

      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;

      // try {
      //   rowDataRules.value = document.getElementById("app").attributes[
      //     "rules_suricata"
      //   ].value;

      //   let validJsonString2 = rowDataRules.value
      //     .replace(/True/g, "true")
      //     .replace(/False/g, "false")
      //     .replace(/None/g, "null");
      //   let parsedArray2 = JSON.parse(validJsonString2);
      //   rowDataRules.value = parsedArray2;
      // } catch (error) {
      //   console.error("Error setting rowDataRules:", error);
      // }
    });

    return {
      state,
      overlayTemplate,
      columnRules,
      rowDataRules,
      defaultColDef,
      close,
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
      overlayMessage,
      updateIndex,
      reloadData,
      getData,
    };
  },
};
</script>

<style lang="scss">
.white-link {
  color: white;
  text-decoration: underline;
}
</style>
