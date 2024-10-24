<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
        <v-card-text>
          You do not have the required permissions to perform any
          actions.<br />
          Please contact the administrator if you believe this is an
          error.
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" label="Close" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mr-3">
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>{{ $t('tabs.OneToOne') }}</h4>
      <v-divider></v-divider>
      <v-row>
        <v-col cols="12">
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
              @grid-ready="onGridReady" :columnDefs="columnOneTowOne" :rowData="rowDataOneTowOne.value"
              :overlayNoRowsTemplate="overlayTemplate" :gridOptions="gridOptions" :rowDragManaged="true"
              :rowDragEntireRow="true" @row-drag-end="onRowDragEnd" :localeText="paginationLocalization" />
          </div>
          <div class="d-flex justify-end mt-3">
            <VButton rounded outlined color="#213E9F" label-color="#ffffff" :label="$t('firewall.add')" :isLarge="true"
              type="submit" class="ml-2" @click="openModalAdd" />
          </div>
        </v-col>
      </v-row>
      <OneToOneModal :isOpen="state.isModalAreaOpen" :editRow="state.editRow" :modalMode="state.modalMode" />
    </div>
    <v-dialog v-model="state.deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">{{ $t("firewall.delete_confirm") }}</v-card-title>
        <v-card-text>{{ $t("nat.msg_confirm_delete") }}</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">{{ $t("firewall.cancel") }}</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete">{{ $t("firewall.delete") }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from "axios";
import { reactive, ref, onMounted, inject, computed } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import OneToOneModal from "@/components/modals/OneToOneModal.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "Sdwan",
  components: {
    OneToOneModal,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const emitter = inject("emitter");
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({
      deleteDialog: false,
      isviewModal: false,
      viewModal: false,
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

    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });
    const interface_row = computed(() => {
      return t("nat.interface");
    });

    const saddr = computed(() => {
      return t("nat.saddr");
    });
    const trans_addr = computed(() => {
      return t("nat.trans_addr");
    });
    const daddr = computed(() => {
      return t("nat.daddr");
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

    const columnOneTowOne = ref([
      {
        headerName: interface_row,
        field: "interface_name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: saddr,
        field: "source_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: trans_addr,
        field: "translation_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: daddr,
        field: "destination_address",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: description,
        field: "description",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: status,
        cellRenderer: checkboxRender,
        autoHeight: true,
        width: 90,
        minWidth: 50,
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

    function checkboxRender(params) {
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

      input.addEventListener("click", function (event) {
        params.value = !params.value;
        params.data.rule_status = params.value;

        if (params.value) {
          axios
            .put(`/nat/startOneToOneNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        } else {
          axios
            .put(`/nat/stopOneToOneNat/${params.data.id}`)
            .then((response) => {
              if (response.status == "201") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
            });
        }
      });
      return input;
    }

    const onRowDragEnd = (event) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const id = event.node.data.id;
      let payload = {
        new_position: event.overIndex + 1,
      };

      axios
        .put(`/nat/changeOneToOneNatPosition/${id}`, payload)
        .then((response) => {
          if (response.status == "201") {
            state.snackbar = true;
            state.color = "success";
            state.textAlert = response.data.msg;
            setTimeout(() => {
              location.reload();
            }, 1000);
          }
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.msg;
        });
    };
    const rowDataOneTowOne = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      // gridApi.value.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     gridApi.value.sizeColumnsToFit();
      //   });
      // });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataOneTowOne.value);
      } else {
        console.error("Grid API.");
      }
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
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
                class="action-button show "  
                data-action="show">
                <i class="mdi mdi-eye" style="color: #086eae;font-size: 20px;"></i>
                </button>
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
        case "show":

          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            console.log("show", rowData);
          }
          break;
        case "edit":
          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            console.log("edit", rowData);
            state.modalMode = "edit";
            state.isModalAreaOpen = true;
            state.editRow = rowData;
          }

          break;
        case "delete":
          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            console.log("delete", rowData);
            state.deleteDialog = true;
            state.deletedRow = rowData;
          }

          break;
        default:
          break;
      }
    };

    const openModalAdd = () => {
      const user = user_privilege();
      if (user === "viewer") {
        console.log("View Mode");
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        state.modalData = {};
        state.modalMode = "create";
        state.isModalAreaOpen = true;
      }

    };

    onMounted(() => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      emitter.on("closeOneModal", () => {
        state.isModalAreaOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });

      let listOneToOne =
        document.getElementById("app").attributes["listOneToOne"].value;

      const validJsonString = listOneToOne
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);
      console.log("parsedArrayOne", parsedArray);

      rowDataOneTowOne.value = parsedArray;
    });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/nat/deleteOneToOneNat/${state.deletedRow.id}`)
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.msg;

          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });
    };
    return {
      state,
      gridOptions,
      columnOneTowOne,
      emitter,
      rowDataOneTowOne,
      defaultColDef,
      actionCellRendererArea,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
      onRowDragEnd,
      overlayTemplate,
      close,
      paginationLocalization
    };
  },
};
</script>

<style></style>
