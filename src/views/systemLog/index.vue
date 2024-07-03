<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.systemLog')" active-menu="Key_Pair">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>{{ $t("subtitle.systemLog") }}</h4>
            <v-divider></v-divider>
            <v-row>
              <v-col cols="12">
                <div style="overflow: hidden; flex-grow: 1">
                  <ag-grid-vue
                    id="grid-wrapper"
                    domLayout="autoHeight"
                    class="ag-theme-alpine mt-3"
                    style="width: 100%"
                    @grid-ready="onGridReady"
                    :columnDefs="columnKeys"
                    :rowData="rowDataKeys.value"
                    :overlayNoRowsTemplate="overlayTemplate"
                    :pagination="true"
                    :paginationPageSize="4"
                    :localeText="paginationLocalization"
                  />
                </div>
             
              </v-col>
            </v-row>
          </div>
          <!-- <v-dialog v-model="state.deleteDialog" max-width="500px">
            <v-card>
              <v-card-title class="headline">{{
                $t("delete.DeleteConfirmation")
              }}</v-card-title>
              <v-card-text>{{ $t("delete.questionkey") }}</v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="cancelDelete">{{
                  $t("PageGeneral.form.Cancel")
                }}</v-btn>
                <v-btn color="blue darken-1" text @click="confirmDelete">{{
                  $t("PageGeneral.form.Delete")
                }}</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog> -->
          <!-- <v-snackbar
            :timeout="2000"
            v-model="state.snackbar"
            location="bottom right"
            :color="state.color"
          >
            {{ state.textAlert }}
          </v-snackbar> -->
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject, computed } from "vue";
import VButton from "@/components/VButton.vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
export default {
  name: "KeyPair",
  components: {
    BaseLayout,
    AgGridVue
  },
  setup() {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const state = reactive({
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
    });

    onMounted(() => {
     overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
     
    });
    const KeyName = computed(() => {
      return t("KeyPair.KeyName");
    });

    const columnKeys = ref([
      {
        headerName: 'Date',
        field: "name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: 'Process',
        field: "utility",
        width: 90,
        minWidth: 50,
        flex: 1,
        sortable: true,
        filter: true,
      },
      {
        headerName: 'Line',
        autoHeight: true,
        field: "key_size",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Action",
        width:150,
        cellRenderer: actionCellRendererKeys,
        field: "action",
      },
    ]);

    const rowDataKeys = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataKeys.value);
      } else {
        console.error("Grid API.");
      }
    };

    const defaultColDef = {
      sortable: true,
      filter: true,
      // flex: 1,
    };

    const getCookie = (name) => {
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
    };

    function actionCellRendererKeys(params) {
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
        if (params.data.utility === "Public") {
          eGui.innerHTML = `
          <button
           class="action-button copy"
           data-action="copy"  title=${t('titleAgGrid.publicKey')}>
              <i class="mdi mdi-content-copy" style="color: #086eae;font-size: 20px;"></i>
           </button>
          <button
           class="action-button download"
           data-action="export"  title=${t('titleAgGrid.pK')}>
              <i class="mdi mdi-download-circle" style="color: #086eae;font-size: 20px;"></i>
           </button>
           <button
          class="action-button delete"
          data-action="delete">
            <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>`;
        } else {
          eGui.innerHTML = `
          <button
          class="action-button delete"
          data-action="delete">
            <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>

          `;
        }
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
      switch (action) {
        case "delete":
          state.deleteDialog = true;
          state.deletedRow = rowData;

          break;
        case "copy":
          let text = rowData.public_key_value;
          copyContent(text);
          break;
        case "export":
          if (rowData.public_key_value) {
            const text = rowData.public_key_value;
            const blob = new Blob([text], {
              type: "application/x-x509-ca-cert",
            });

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = `${rowData.name}.pem`;

            document.body.appendChild(a);
            a.click();

            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          }

          break;
        default:
          break;
      }
    };



    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      if (state.deletedRow?.utility === "Private") {
        axios
          .delete(`/key_pairs/deletePrivateKey/${state.deletedRow.id}`)
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
      } else if (state.deletedRow?.utility === "Public") {
        axios
          .delete(`/key_pairs/deletePublicKey/${state.deletedRow.id}`)
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
      }
    };
    return {
      state,
      columnKeys,
      rowDataKeys,
      overlayTemplate,
      defaultColDef,
      emitter,
      paginationLocalization,
      actionCellRendererKeys,
      onGridReady,
      getCookie,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
