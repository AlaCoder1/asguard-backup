<template>
  <div class="mt-5 mb-10">
    <div class="container">
      <h4>{{ $t("firewall.outbound") }}</h4>
      <v-divider></v-divider>
      <v-dialog v-model="deleteDialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">{{
            $t("firewall.delete_confirm")
          }}</v-card-title>
          <v-card-text>{{ $t("firewall.msg_confirm_delete") }}</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="cancelDelete">{{
              $t("firewall.cancel")
            }}</v-btn>
            <v-btn color="blue darken-1" text @click="confirmDelete">{{
              $t("firewall.delete")
            }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <!-- Modal -->
      <ModalFirewallRuleOutbound
        :isOpen="state.isModalOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
      <!-- <v-card class="mt-10">
          <v-card-title> -->
      <v-row class="mt-8 mb-6">
        <v-col cols="12" md="6">
          <v-text-field
            id="filter-text-box"
            v-model="filterText"
            :placeholder="$t('firewall.search')"
            density="compact"
            rounded
            variant="solo"
            hide-details
            dense
            prepend-inner-icon="mdi-magnify"
            @input="onFilterTextBoxChanged"
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="6" class="d-flex justify-end">
          <v-btn class="ml-3 mt-2" @click="openModalAdd">
            <i class="fas fa-plus" style="color: #086eae"></i>
            <span class="ml-2" style="color: #086eae">{{
              $t("firewall.add")
            }}</span>
          </v-btn>
        </v-col>
      </v-row>
      <v-alert
        v-model="state.snackbar"
        v-for="(error, index) in state.textAlert"
        :key="index"
        :type="error.status === 400 ? 'error' : 'success'"
        :color="state.color"
        style="margin-bottom: 10px"
      >
        {{ error.msg }}
      </v-alert>
      <!-- </v-card-title> -->
      <!-- <v-card-text> -->
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine"
        :columnDefs="columnDefs"
        :rowData="rowData.value"
        @grid-ready="onGridReady"
        :defaultColDef="defaultColDef"
        :gridOptions="gridOptions"
        style="width: 100%"
        :pagination="true"
        :paginationPageSize="4"
        :localeText="paginationLocalization"
      >
        <!-- @column-row-group-changed="onColumnRowGroupChanged"
             @firstDataRendered="onFirstDataRendered"
        @column-row-drag-end="onColumnRowDragEnd" -->
        <!-- @row-drag-end="onRowDragEnd" -->
      </ag-grid-vue>

      <v-card v-if="changes" class="mt-3">
        <v-card-title>Changes</v-card-title>
        <v-card-text>
          <v-row
            :class="[
              oldRow.length !== 0
                ? 'mt-5'
                : 'justify-start mt-5 ml-2',
            ]"
          >
            <v-col
              :cols="oldRow.length !== 0 ? 6 : 1"
              v-if="oldRow.length"
              style=""
            >
              <!-- <span v-if="oldRow.length === 0"
                >-----------------------------</span
              > -->
              <v-row v-for="rule in sortedrray" :key="rule.id">
                <span
                  v-if="
                    (rule.id && rule.status === 'initial') ||
                    (rule.id && rule.status === 'old')
                  "
                  style="
                    color: #ef233c;
                    display: flex;
                    left: 1%;
                    position: relative;
                    font-size: 16px;
                    font-weight: bold;
                  "
                >
                  <span>--</span>
                  {{
                    ` ${rule.type_rule} ${rule.policy} ${rule.protocol} ${
                      rule.saddr
                    } ${rule.sport === undefined ? "" : rule.sport} ${
                      rule.daddr
                    } ${rule.dport === undefined ? "" : rule.dport}   `
                  }}
                </span>
                <del
                  v-if="rule.id && rule.status === 'deleted'"
                  style="
                    color: #ef233c;
                    display: flex;
                    left: 1%;
                    position: relative;
                    font-size: 16px;
                    font-weight: bold;
                  "
                >
                  <span>--</span>
                  {{
                    ` ${rule.type_rule} ${rule.policy} ${rule.protocol} ${
                      rule.saddr
                    } ${rule.sport === undefined ? "" : rule.sport} ${
                      rule.daddr
                    } ${rule.dport === undefined ? "" : rule.dport}   `
                  }}
                </del>
              </v-row>
            </v-col>
            <v-col cols="6">
              <v-row v-for="rule in rowData.value" :key="rule.uuid">
                <span
                  v-if="rule.status === 'new' || rule.status === 'old'"
                  :style="{
                    color: rule?.status === 'new' ? ' #4CCD99' : '  #4CCD99',
                  }"
                  style="
                    display: flex;
                    /* left: 15%; */
                    position: relative;
                    font-size: 16px;
                    font-weight: bold;
                  "
                >
                  <span> {{ `${rule?.status === "new" ? "+++" : "+-"}` }}</span>
                  {{
                    ` ${rule.type_rule} ${rule.policy} ${rule.protocol} ${
                      rule.saddr
                    } ${rule.sport === undefined ? "" : rule.sport} ${
                      rule.daddr
                    } ${rule.dport === undefined ? "" : rule.dport}   `
                  }}</span
                >
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      <div class="d-flex justify-end ml-3 mt-3 mb-10">
        <v-btn
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          :isLarge="false"
          :disabled="!rowDataLength"
          @click="saveRules"
        >
          <span class="text-white pr-3 pl-3">{{ $t("buttons.save") }}</span>
        </v-btn>
      </div>

      <v-snackbar
        :timeout="2000"
        v-model="state.snackbarDelete"
        location="bottom right"
        :color="state.color"
      >
        {{ state.textAlertDelete }}
      </v-snackbar>
    </div>
  </div>
</template>
<script>
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { AgGridVue } from "ag-grid-vue3";
import axios from "axios";
import {
  onMounted,
  reactive,
  ref,
  watch,
  defineComponent,
  inject,
  computed,
} from "vue";
import VButton from "../../../components/VButton.vue";
import ModalFirewallRuleOutbound from "../../../components/modals/ModalFirewallRuleOutbound.vue";
import { useI18n } from "vue-i18n";
import { v4 as uuidv4 } from "uuid";

export default defineComponent({
  name: "Outbound",
  components: {
    AgGridVue,
    VButton,
    ModalFirewallRuleOutbound,
  },
  props: {
    id: String,
    uuid: String,
    activeTab: String,
  },
  setup(props) {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    //const overlayTemplate = ref("");
    const emitter = inject("emitter");
    const state = reactive({
      // deleteDialogSquid: false,
      // deletedRow: null,
      snackbar: false,
      color: "",
      textAlert: [],
      textAlertDelete: "",
      snackbarDelete: false,
      enable: false,
      modalData: {},
      isOpen: null,
      modalMode: "",
      isModalOpen: false,
      editRow: {},
      rowDataId: null,
    });

    const gridOptions = {
      overlayNoRowsTemplate: `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`,
    };

    const changes = ref(false);

    const rowDataLength = computed(() => {
      return !rowData.value || rowData.value.length == 0 ? false : true;
    });

    const policy = computed(() => {
      return t("firewall.policy");
    });
    const description = computed(() => {
      return t("firewall.description");
    });
    const protocol = computed(() => {
      return t("firewall.protocol");
    });
    const saddr = computed(() => {
      return t("firewall.saddr");
    });
    const sport = computed(() => {
      return t("firewall.sport");
    });
    const daddr = computed(() => {
      return t("firewall.daddr");
    });
    const dport = computed(() => {
      return t("firewall.dport");
    });
    const action = computed(() => {
      return t("firewall.action");
    });

    const sortedrray = computed(() => {
      return oldRow.value.slice().sort((a, b) => a.id - b.id);
    });

    const alert = ref(false);
    const mode = ref("create");
    const last_Subscription = ref([]);
    const columnDefs = ref([
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
      // },
      {
        field: "policy",
        headerName: policy,
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: ["accept", "drop"],
        },
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        field: "rule_description",
        headerName: description,
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        field: "protocol",
        headerName: protocol,
        cellEditor: "agSelectCellEditor",
        cellEditorParams: {
          values: [
            "tcp",
            "udp",
            "icmp type echo-request",
            "icmp type echo-reply",
            "all",
          ],
        },
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },

      {
        field: "saddr",
        autoHeight: true,
        headerName: saddr,
        cellRenderer: formatedLineSadd,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        field: "sport",
        headerName: sport,
        cellRenderer: formatedLineSport,
        autoHeight: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: daddr,
        field: "daddr",
        cellRenderer: formatedLineDaddr,
        autoHeight: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        field: "dport",
        headerName: dport,
        cellRenderer: formatedLineDport,
        autoHeight: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: action,
        field: "action",
        width: 150, minWidth: 50,
        cellRenderer: actionCellRenderer,
      },
    ]);

    function formatedLineSport(data) {
      const rslt = data.data.sport ? data.data.sport : "--";
      let eGui = document.createElement("div");
      eGui.innerHTML = `${rslt}
        `;
      eGui.style.lineHeight = "-4";
      return eGui;
    }
    function formatedLineSadd(data) {
      const rslt = data.data.saddr ? data.data.saddr : "--";
      let eGui = document.createElement("div");
      eGui.innerHTML = `${rslt}
        `;
      eGui.style.lineHeight = "-4";
      return eGui;
    }
    function formatedLineDaddr(data) {
      const rslt = data.data.daddr ? data.data.daddr : "--";
      let eGui = document.createElement("div");
      eGui.innerHTML = `${rslt}
        `;
      eGui.style.lineHeight = "-4";
      return eGui;
    }
    function formatedLineDport(data) {
      const rslt = data.data.dport ? data.data.dport : "--";
      let eGui = document.createElement("div");
      eGui.innerHTML = `${rslt}
        `;
      eGui.style.lineHeight = "-4";
      return eGui;
    }

    const gridApi = ref(null);
    const gridColumnApi = ref(null);
    const defaultColDef = ref({
      // flex: 1,
      // editable: false,
      // cellDataType: false,
    });
    const rowData = reactive([]);
    const oldRow = ref([]);
    const rules = reactive([]);
    const filterText = ref(null);
    const columnOrder = ref([]);

    const deleteDialog = ref(false);
    const showAddModal = ref(false);
    const rowDataToDelete = ref(null);

    const openModalAdd = () => {
      if (last_Subscription.value.includes("Firewall L4")) {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
      emitter.emit("inter-Outbound-uuid", props.uuid);
      }
       else {
        emitter.emit("firewal-subscription");
        window.scrollTo(0, 0);
      }
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;

      // if (rowData.value && rowData.value.length > 0) {
      //   gridApi.value.forEachNode((node) =>
      //     node.setSelected(node.rowIndex === 0)
      //   );
      // }
    };

    // const setGridApi = (api) => {
    //   gridApi.value = api;
    // };
    // const onFirstDataRendered = (params) => {
    //   params.api.sizeColumnsToFit();
    // };
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
          state.rowDataId = rowData.uuid;
          break;
        case "update":
          mode.value = "update";
          state.modalData = {};
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          break;
        default:
          break;
      }
    };

    // const arrayMove = (arr, fromIndex, toIndex) => {
    //   const element = arr[fromIndex];
    //   arr.splice(fromIndex, 1);
    //   arr.splice(toIndex, 0, element);
    //   return arr.slice();
    // };
    // const onRowDragEnd = (event) => {
    //   const updatedRows =
    //     event.overIndex !== undefined
    //       ? arrayMove(rowData.value, event.node.rowIndex, event.overIndex)
    //       : rowData.value;

    //   rowData.value = updatedRows;
    // };
    // const onColumnRowGroupChanged = (event) => {
    //   const newColumnOrder = event.columns.map((column) => column.colId);
    //   gridApi.value.setColumnDefs(columnDefs.value);
    //   gridApi.value.setColumnOrder(newColumnOrder);
    // };
    // const onColumnRowDragEnd = (event) => {
    //   if (event && event.columns) {
    //     columnOrder.value = event.columns.map((column) => column.colId);

    //     gridApi.value.setColumnDefs(columnDefs.value);
    //     gridApi.value.setColumnOrder(columnOrder.value);
    //   } else {
    //     console.log("event.columns is undefined or null");
    //   }
    // };
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
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const cancelDelete = () => {
      rowDataToDelete.value = null;
      deleteDialog.value = false;
    };
    // const confirmDelete = () => {
    //   if (oldRow.value.length === 0 && rowDataToDelete.value.id) {
    //     const index = rowData.value.findIndex(
    //       (item) => item.id === rowDataToDelete.value.id
    //     );
    //     if (index !== -1) {
    //       rowData.value.splice(index, 1);
    //       if (rowData.value.length === 0) changes.value = false;
    //       console.log("no00");
    //       deleteDialog.value = false;
    //       oldRow.value.push({ ...rowDataToDelete.value, status: "deleted" });
    //       // if (rowData.value.length === 0) changes.value = false;

    //       if (gridApi.value) {
    //         gridApi.value.setRowData(rowData.value);
    //       } else {
    //         console.error("Grid API.");
    //       }
    //     }
    //   } else {
    //     const index = oldRow.value.findIndex(
    //       (obj) => obj.id === rowDataToDelete.value.id
    //     );
    //     if (index !== -1) {
    //       oldRow.value[index].status = "deleted";
    //     }
    //   }
    //   if (rowDataToDelete.value.id) {
    //     console.log("rowDataToDelete.value", rowDataToDelete.value);
    //     const index = rowData.value.findIndex(
    //       (item) => item.id === rowDataToDelete.value.id
    //     );

    //     if (index !== -1) {
    //       rowData.value.splice(index, 1);

    //       deleteDialog.value = false;
    //       if (gridApi.value) {
    //         gridApi.value.setRowData(rowData.value);
    //       } else {
    //         console.error("Grid API.");
    //       }
    //     }

    //     const csrfToken = getCookie("csrftoken");
    //     axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

    //     axios
    //       .delete(`/rules/deleteRule/${rowDataToDelete.value.id}`)
    //       .then((response) => {
    //         if (response.status == "200") {
    //           // state.snackbar = true;
    //           // state.color = "success";
    //           // state.textAlert = response.data.msg;
    //           // setTimeout(() => {
    //           //   location.reload();
    //           // }, 1000);
    //         }
    //       })
    //       .catch((i) => {
    //         state.snackbar = true;
    //         state.color = "red";
    //         state.textAlert = i.response.data.response;
    //       });
    //   } else {
    //     const index = rowData.value.findIndex(
    //       (item) => item.uuid === state.rowDataId
    //     );

    //     if (index !== -1) {
    //       rowData.value.splice(index, 1);

    //       if (rowData.value.length === 0) changes.value = false;

    //       deleteDialog;
    //       deleteDialog.value = false;
    //       if (gridApi.value) {
    //         gridApi.value.setRowData(rowData.value);
    //       } else {
    //         console.error("Grid API.");
    //       }
    //     }
    //   }
    // };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (oldRow.value.length === 0 && rowDataToDelete.value.id) {
        const index = rowData.value.findIndex(
          (item) => item.id === rowDataToDelete.value.id
        );
        if (index !== -1) {
          rowData.value.splice(index, 1);

          axios
            .delete(`/rules/deleteRule/${rowDataToDelete.value.id}`)
            .then((response) => {
              if (response.status == "200") {
                // state.snackbar = true;
                state.color = "success";
                // state.textAlert = response.data.msg;
                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
                state.snackbarDelete = true;
                state.textAlertDelete = response.data.msg;
                // setTimeout(() => {
                //   location.reload();
                // }, 1000);
              }
            })
            .catch((i) => {
              state.snackbarDelete = true;
              state.color = "red";
              state.textAlertDelete = i.response.data.response;
              setTimeout(() => {
                state.snackbar = false;
              }, 1000);
            });

          if (rowData.value.length === 0) changes.value = true;
          deleteDialog.value = false;
          oldRow.value.push({ ...rowDataToDelete.value, status: "deleted" });

          if (gridApi.value) {
            gridApi.value.setRowData(rowData.value);
          } else {
            console.error("Grid API.");
          }
        }
      } else if (oldRow.value.length != 0 && rowDataToDelete.value.id) {
        const index = oldRow.value.findIndex(
          (obj) => obj.id === rowDataToDelete.value.id
        );
        if (index !== -1) {
          oldRow.value[index].status = "deleted";
        } else {
          oldRow.value.push({ ...rowDataToDelete.value, status: "deleted" });
        }
        const index2 = rowData.value.findIndex(
          (item) => item.id === rowDataToDelete.value.id
        );

        if (index2 !== -1) {
          rowData.value.splice(index, 1);

          deleteDialog.value = false;
          if (gridApi.value) {
            axios
              .delete(`/rules/deleteRule/${rowDataToDelete.value.id}`)
              .then((response) => {
                if (response.status == "200") {
                  // state.snackbar = true;
                  // state.color = "success";
                  // state.textAlert = response.data.msg;
                  // setTimeout(() => {
                  //   location.reload();
                  // }, 1000);
                  state.color = "success";
                  state.snackbarDelete = true;
                  state.textAlertDelete = response.data.msg;
                  // setTimeout(() => {
                  //   location.reload();
                  // }, 1000);
                }
              })
              .catch((i) => {
                state.snackbarDelete = true;
                state.color = "red";
                state.textAlertDelete = i.response.data.response;
                setTimeout(() => {
                  state.snackbar = false;
                }, 1000);
              });
            gridApi.value.setRowData(rowData.value);
          } else {
            console.error("Grid API.");
          }
        }
      }

      if (!rowDataToDelete.value.id) {
        const index = rowData.value.findIndex(
          (item) => item.uuid === state.rowDataId
        );

        if (index !== -1) {
          rowData.value.splice(index, 1);

          if (rowData.value.length === 0) changes.value = false;

          deleteDialog;
          deleteDialog.value = false;
          if (gridApi.value) {
            gridApi.value.setRowData(rowData.value);
          } else {
            console.error("Grid API.");
          }
        }
      }
    };
    const saveModal = () => {
      showAddModal.value = false;
    };
    const saveRules = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = rowData.value.map((e) => {
        return {
          id: e.id ?? null,
          policy: e.policy,
          saddr: e.saddr,
          daddr: e.daddr,
          sport: e.sport,
          dport: e.dport,
          protocol: e.protocol,
          type_rule: e.type_rule,
          rule_description: e.rule_description,
        };
      });

      axios
        .post(`/rules/saveRules/${props.activeTab}`, payload)
        .then((response) => {
          if (response.status == "200") {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.response;
            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.response;

          setTimeout(() => {
            state.snackbar = false;
          }, 1000);
        });
    };
    const cancel = () => {
      showAddModal.value = false;
    };

    function updateObjectById(uuid, updatedObject) {
      const index = rowData.value.findIndex((obj) => obj.uuid === uuid);
      if (index !== -1) {
        rowData.value[index] = {
          ...rowData.value[index],
          ...updatedObject,
        };
        changes.value = true;
      }
    }

    onMounted(() => {
      //   overlayTemplate.value = `
      //   <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      //   <path
      //     d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
      //     style="fill: #E8EAF6"
      //     data-name="Unbox"
      //   />
      //  </svg></span>`;
      // console.log(overlayTemplate.valye)
      emitter.on("closeOutboundRule", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
        if (gridApi.value) {
          gridApi.value.setRowData(rowData.value);
        } else {
          console.error("Grid API.");
        }
      });

      const rulesAttribute =
        document.getElementById("app").attributes["rules"].value;

      let parsedArray = JSON.parse(rulesAttribute);

      rules.value = parsedArray;

      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription.value", last_Subscription.value);

      emitter.on("addFirewallRuleOutbound", (data) => {
        if (data.interUuid === props.uuid) {
          if (!rowData.value) {
            rowData.value = [];
          }

          let ruleInbound = {
            uuid: data.uuid,
            daddr: data.daddr,
            policy: data.policy,
            protocol: data.protocol,
            rule_description: data.rule_description,
            saddr: data.saddr,
            sport: data.sport ?? "ALL",
            dport: data.dport ?? "ALL",
            type_rule: data.type_rule,
            status: data.status,
          };
          rowData.value.push(ruleInbound);
          changes.value = true;
          if (gridApi.value) {
            gridApi.value.setRowData(rowData.value);
          } else {
            console.error("Grid API.");
          }
        }
      });

      emitter.on("oldOutbound", (oldObject) => {
        const array1AsArray = [oldObject];
        function testObjectEquality() {
          for (const obj1 of array1AsArray) {
            const obj2 = rowData.value.find((item) => item.id === obj1.id);

            if (obj2) {
              let equal = true;
              for (const key in obj1) {
                if (obj1.hasOwnProperty(key) && obj1[key] !== obj2[key]) {
                  equal = false;
                  break;
                }
              }
              if (!equal) {
                const index = oldRow.value.findIndex(
                  (item) => item.id === obj1.id
                );
                if (index !== -1) {
                  oldRow.value.splice(index, 1);
                  oldRow.value.push(obj1);
                } else {
                  if (oldObject.id) oldRow.value.push(obj1);
                }
              }
            }
            // else {
            //   oldRow.value.push(obj1);
            // }
          }
        }
        testObjectEquality();
      });

      emitter.on("firewallRuleOutboundEdit", (data) => {
        let ruleInbound = {
          uuid: data.uuid,
          daddr: data.daddr,
          policy: data.policy,
          protocol: data.protocol,
          rule_description: data.rule_description,
          saddr: data.saddr,
          sport: data.sport,
          dport: data.dport,
          type_rule: data.type_rule,
          status: data.status,
        };

        updateObjectById(data.uuid, ruleInbound);

        if (!rowData.value) {
          rowData.value = [];
        }

        if (gridApi.value) {
          gridApi.value.setRowData(rowData.value);
        } else {
          console.error("Grid API.");
        }
      });
    });

    watch(
      () => rules.value,
      (newValue, oldValue) => {
        if (newValue) {
          rowData.value = rules.value[props.activeTab]["outbound"]?.map((e) => {
            return {
              uuid: uuidv4(),
              id: e.id,
              policy: e.policy,
              saddr: e.saddr ?? "ALL",
              daddr: e.daddr ?? "ALL",
              sport: e.sport ?? "ALL",
              dport: e.dport ?? "ALL",
              protocol: e.protocol[0],
              type_rule: e.type_rule,
              rule_description: e.rule_description,
              status: "initial",
            };
          });
        } else {
          rowData.value = [];
        }
      },
      { immediate: true }

      // (newValue, oldValue) => {
      //   if (newValue) {
      //     if (mode.value === "create") {
      //       rowData.value.push(newValue);
      //       gridApi.value.forEachNode((node) =>
      //         node.setSelected(node.rowIndex === rowData.value.length - 1)
      //       );
      //     } else {
      //       const selectedNode = gridApi.value.getSelectedNodes()[0];
      //       if (selectedNode) {
      //         selectedNode.setData(newValue);
      //       }
      //     }
      //   }
      // }
    );
    // watch(
    //   () => rowData.value,
    //   (newValue, oldValue) => {
    //     if (rowData.value.length) {
    //       console.log("oldValue10", oldValue);
    //       console.log("newValue10", newValue);
    //     }
    //   },
    //   { immediate: true }
    // );
    // watch(
    //   () => rowData.value?.slice(),
    //   (newArray, oldArray) => {
    //     // console.log("oldValue", oldArray);
    //     // console.log("newValue", newArray);
    //     // oldRow.value = oldArray
    //   },
    //   { deep: true }
    // );

    return {
      changes,
      openModalAdd,
      saveRules,
      oldRow,
      emitter,
      rowDataLength,
      columnDefs,
      state,
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
      paginationLocalization,
      alert,
      mode,
      last_Subscription,
      sortedrray,
      onGridReady,
      // setGridApi,
      // onFirstDataRendered,
      actionCellRenderer,
      onFilterTextBoxChanged,
      // arrayMove,
      // onRowDragEnd,
      // onColumnRowGroupChanged,
      // onColumnRowDragEnd,
      handleRemove,
      showDeleteModal,
      handleAction,
      cancelDelete,
      confirmDelete,
      saveModal,
      cancel,
      gridOptions,
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
  background-color: #213e9f;
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
