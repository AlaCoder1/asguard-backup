<template>
  <v-overlay v-model="state.isExec"> </v-overlay>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text>
          {{ $t("profil.NoPermission") }}
          <br />
          {{ $t("profil.ContactAdmin") }}
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>

  <v-dialog v-model="deleteDialog" max-width="500px">
    <v-card>
      <v-card-title class="headline">{{
        $t("firewall.delete_confirm")
      }}</v-card-title>
      <v-card-text>{{ $t("firewall.msg_confirm_delete") }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelDeleteRow">{{
          $t("firewall.cancel")
        }}</v-btn>
        <v-btn color="blue darken-1" text @click="confirmDeleteRow">{{
          $t("firewall.delete")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <div>
    <div class="mt-6" style="display: flex; flex-direction: column">
      <h4>{{ $t("tabs.SNAT") }}</h4>
      <v-divider></v-divider>
      <v-row>
        <v-col cols="12" class="mt-2">
          <v-alert
            v-model="state.snackbarAlert"
            v-for="(error, index) in state.textAlertRow"
            :key="index"
            :type="error.status === 400 ? 'error' : 'success'"
            :color="error.status === 400 ? 'error' : 'success'"
            style="margin-bottom: 10px"
          >
            {{ error.msg }}
          </v-alert>
        </v-col>
        <v-col cols="12" class="d-flex justify-end mt-2">
          <v-btn
            class="ml-3"
            @click.prevent="deleteSelectedRows"
            v-if="hasSelection"
          >
            <i class="fas fa-trash" style="color: #086eae"></i>
          </v-btn>
        </v-col>

        <v-col cols="12">
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnSnat"
              :rowData="rowDataSnat.value"
              :gridOptions="gridOptions"
              :overlayNoRowsTemplate="overlayTemplate"
              :rowDragManaged="state.user === 'viewer' ? false : true"
              :rowDragEntireRow="state.user === 'viewer' ? false : true"
              @row-drag-enter="onRowDragStart"
              @row-drag-end="onRowDragEnd"
              :localeText="paginationLocalization"
              :rowSelection="'multiple'"
              @selection-changed="onSelectionChanged"
              :rowMultiSelectWithClick="true"
              rowClick="multiple"
            />
          </div>
          <div class="d-flex justify-end mt-3 mb-14">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              :label="$t('firewall.add')"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="openModalAdd"
            />
          </div>
        </v-col>
      </v-row>
      <SnatModal
        :isOpen="state.isModalAreaOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
    </div>
    <v-dialog v-model="state.deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{
          $t("firewall.delete_confirm")
        }}</v-card-title>
        <v-card-text>{{ $t("nat.msg_confirm_delete") }}</v-card-text>
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
    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import { reactive, ref, onMounted, inject, onBeforeMount, computed } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import SnatModal from "@/components/modals/SnatModal.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "SNAT",
  components: {
    SnatModal,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const hasSelection = ref(false);
    const deleteDialog = ref(false);
    const id_list_selection = ref([]);
    const array = ref([]);
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const state = reactive({
      textAlertRow: [],
      snackbarAlert: false,
      user: null,
      initialRowIndex: null,
      isExec: false,
      mapedInterface: [],
      isviewModal: false,
      viewModal: false,
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      modalData: {},
      modalMode: "create",
      isModalAreaOpen: false,
      isOpen: null,
      editRow: {},
    });
    const interface_row = computed(() => {
      return t("nat.interface");
    });
    const protocol = computed(() => {
      return t("nat.protocol");
    });
    const saddr = computed(() => {
      return t("nat.saddr");
    });
    const sport = computed(() => {
      return t("nat.sport");
    });
    const daddr = computed(() => {
      return t("nat.daddr");
    });
    const dport = computed(() => {
      return t("firewall.dport");
    });
    const trans_addr = computed(() => {
      return t("nat.trans_addr");
    });
    const trans_port = computed(() => {
      return t("nat.trans_port");
    });
    const description = computed(() => {
      return t("nat.description");
    });
    const status = computed(() => {
      return t("nat.status");
    });
    const action = computed(() => {
      return t("nat.action");
    });

    const gridOptions = ref({
      // pagination: true,
      // paginationPageSize: 5,
      rowSelection: "single",
    });

    const columnSnat = ref([
      {
        headerName: "",
        checkboxSelection: true,
        headerCheckboxSelection: true,
        width: 50,
      },
      {
        headerName: interface_row,
        field: "interface_name",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: protocol,
        field: "protocol",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: saddr,
        field: "source_address",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: sport,
        field: "source_port",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: daddr,
        field: "destination_address",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 210,
        flex: 1,
      },
      {
        headerName: dport,
        field: "destination_port",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 210,
        flex: 1,
      },
      {
        headerName: trans_addr,
        field: "tcp_ip",
        autoHeight: true,
        // resizable: true,
        width: 100,
        minWidth: 210,
        flex: 1,
      },
      {
        headerName: trans_port,
        field: "translation_port",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 210,
        flex: 1,
      },
      {
        headerName: description,
        field: "description",
        autoHeight: true,
        // resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: status,
        // field: "rule_status",
        cellRenderer: checkboxRender,
        autoHeight: true,
        // resizable: true,
        // editable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: action,
        width: 150,
        minWidth: 50,
        cellRenderer: actionCellRendererArea,
        field: "action",
      },
    ]);
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    const onRowDragStart = (event) => {
      state.initialRowIndex = event.overIndex;
    };
    const onRowDragEnd = (event) => {
      const user = user_privilege();
      if (user !== "viewer") {
        if (event.overIndex === state.initialRowIndex) {
          state.initialRowIndex = null;
          return;
        }
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        const id = event.node.data.id;
        let payload = {
          new_position: event.overIndex + 1,
        };

        axios
          .put(`/nat/changeSNatPosition/${id}`, payload)
          .then((response) => {
            if (response.status == "201") {
              state.snackbar = true;
              state.isExec = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              setTimeout(() => {
                location.reload();
              }, 1000);
            }
          })
          .catch((i) => {
            if (i.response.status === 500) {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = t("errors.errorServer");
            } else {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.msg;
            }
          });
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const rowDataSnat = reactive({});

    const gridApi = ref(null);

    function checkboxRender(params) {
      const user = user_privilege();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      var input = document.createElement("input");
      input.type = "checkbox";
      params.value = params.data.rule_status;
      input.checked = params.value;

      input.style.margin = "10px";
      input.style.width = "20px";
      input.style.height = "18px";
      input.style.cursor = "pointer";
      input.disabled = user === "viewer";

      input.addEventListener("click", function (event) {
        params.value = !params.value;
        params.data.rule_status = params.value;

        if (params.value) {
          axios
            .put(`/nat/startSNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.isExec = true;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        } else {
          axios
            .put(`/nat/stopSNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.isExec = true;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              if (i.response.status === 500) {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = t("errors.errorServer");
              } else {
                state.snackbar = true;
                state.color = "red";
                state.textAlert = i.response.data.error;
              }
            });
        }
      });
      return input;
    }
    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataSnat.value);
      } else {
        console.error("Grid API.");
      }
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };

    function actionCellRendererArea(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
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
              data-action="edit" title="Edit Server">
                 <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
              </button>
              <button
              class="action-button delete"
              data-action="delete" title="Delete ">
                <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
              </button>

              `;
      }
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionClient(action, params.node.data);
        });
      });
      return eGui;
    }

    const handleActionClient = (action, rowData, index) => {
      const user = user_privilege();
      switch (action) {
        case "edit":
          if (user !== "viewer") {
            console.log("edit", rowData);
            state.modalMode = "edit";
            state.isModalAreaOpen = true;
            state.editRow = rowData;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        case "delete":
          if (user !== "viewer") {
            console.log("delete", rowData);
            state.deleteDialog = true;
            state.deletedRow = rowData;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        default:
          break;
      }
    };

    const getInterface = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/network/AllInterfaces").then(
        (response) => {
          let filtredInterface = response.data.filter(
            (i) => !i.ifname.startsWith("tun_") && !i.ifname.startsWith("tap_")
          );

          let interfaces = filtredInterface.map((i) => {
            return {
              id: i.id,
              name: i.name_interface,
            };
          });

          state.mapedInterface = interfaces;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    const openModalAdd = () => {
      const user = user_privilege();

      if (user !== "viewer") {
        state.modalData = {};
        state.modalMode = "create";
        state.isModalAreaOpen = true;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };
    onBeforeMount(() => {
      getInterface();
    }),
      onMounted(() => {
        state.user = user_privilege();
        overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
        emitter.on("closeSnatModal", () => {
          state.isModalAreaOpen = false;
          state.isOpen = false;
          state.modalMode = "";
          state.editRow = {};
        });

        let allListNat =
          document.getElementById("app").attributes["listNat"].value;
        const validJsonString = allListNat
          .replace(/'/g, '"')
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        const parsedArray = JSON.parse(validJsonString);

        let mapedNatRow = parsedArray.map((i) => {
          return {
            id: i.id,
            description: i.description,
            destination_address: i.destination_address,
            destination_port: i.destination_port,
            interface: i.interface,
            interface_name: i.interface_name,
            protocol: i.protocol,
            rule_number: i.rule_number,
            rule_status: i.rule_status,
            snat_type: i.snat_type,
            source_address: i.source_address,
            source_port: i.source_port,
            tcp_ip: i.tcp_ip,
            translation_address_from: i.translation_address_from,
            translation_address_to: i.translation_address_to,
            translation_port: i.translation_port,
          };
        });
        rowDataSnat.value = mapedNatRow;
      });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/nat/deleteSNat/${state.deletedRow.id}`)
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          if (i.response.status === 500) {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = t("errors.errorServer");
          } else {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.error;
          }
        });
    };

    const onSelectionChanged = () => {
      const selected = gridApi.value.getSelectedRows();
      hasSelection.value = selected.length > 0;
    };

    const deleteSelectedRows = () => {
      const user = user_privilege();

      if (user !== "viewer") {
        deleteDialog.value = true;
        const selectedRows = gridApi.value.getSelectedRows();
        id_list_selection.value = selectedRows.map((i) => i.id);
        array.value = [...id_list_selection.value];
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const cancelDeleteRow = () => {
      deleteDialog.value = false;
    };
    const confirmDeleteRow = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        list_rules: array.value,
      };

      axios
        .post(`/nat/deleteSNat`, payload)
        .then((response) => {
          const results = response.data;
          console.log("results9", results);
          state.snackbarAlert = true;
          state.textAlertRow = results;
          deleteDialog.value = false;

          setTimeout(() => {
            state.textAlertRow = [];
            location.reload();
          }, 3000);
        })
        .catch((i) => {
          if (i.response.status === 500) {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = t("errors.errorServer");
          } else {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = i.response.data.response;
          }
        });
    };

    return {
      confirmDeleteRow,
      cancelDeleteRow,
      deleteSelectedRows,
      onSelectionChanged,
      hasSelection,
      deleteDialog,
      state,
      close,
      gridOptions,
      columnSnat,
      emitter,
      onRowDragEnd,
      onRowDragStart,
      rowDataSnat,
      defaultColDef,
      actionCellRendererArea,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
      overlayTemplate,
      paginationLocalization,
    };
  },
};
</script>
