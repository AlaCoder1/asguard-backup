<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
        <v-card-text>
          {{  $t("profil.NoPermission") }}
                  <br />
                  {{  $t("profil.ContactAdmin") }} 
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <v-app id="inspire">
    <base-layout :title="$t('keyPair')" active-menu="Key_Pair">
      <template #content>
        <helpModal help="key-pair"/>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>{{ $t("KeyPair.ListofKeys") }}</h4>
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
                    :localeText="paginationLocalization"
                  />
                </div>
                <div class="d-flex justify-end mt-3">
                  <VButton
                    rounded
                    outlined
                    color="#213E9F"
                    label-color="#ffffff"
                    :label="$t('KeyPair.addkey')"
                    :isLarge="true"
                    type="submit"
                    class="ml-2"
                    @click="openModalAdd"
                  />
                </div>
              </v-col>
            </v-row>
            <ModalKeys :isOpen="state.isModalOpen" />
          </div>
          <v-dialog v-model="state.deleteDialog" max-width="500px">
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
import ModalKeys from "@/components/modals/ModalKeys.vue";
import { user_privilege } from "@/mixins/user_privilege.js";
import helpModal from "@/components/modals/help.vue";

export default {
  name: "KeyPair",
  components: {
    ModalKeys,
    BaseLayout,
    AgGridVue,
    VButton,
    helpModal
  },
  setup() {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const state = reactive({
      isviewModal: false,
      viewModal: false,
      deleteDialog: false,
      deletedRow: null,
      snackbar: false,
      color: null,
      textAlert: "",
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isOpen: null,
    });

    onMounted(() => {
      emitter.on("closeKeyPairModal", () => {
        state.isModalOpen = false;
      });

      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
      let privateKeyAttribute =
        document.getElementById("app").attributes["privateKey"].value;

      const validJsonString = privateKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);

      let publicKeyAttribute =
        document.getElementById("app").attributes["publicKey"].value;

      const validJsonString2 = publicKeyAttribute
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray2 = JSON.parse(validJsonString2);

      let mapedPrivateKey = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.name,
          utility: "Private",
          key_size: i.key_size,
          fingerPrint: i.finger_print ?? "--",
        };
      });
      let mapedPublicKey = parsedArray2.map((i) => {
        return {
          id: i.id,
          name: i.name,
          utility: "Public",
          key_size: i.key_size,
          fingerPrint: i.finger_print ?? "--",
          public_key_value: i.public_key_value,
        };
      });
      var combinedArray = [...mapedPrivateKey, ...mapedPublicKey];
      rowDataKeys.value = combinedArray;
    });
    const KeyName = computed(() => {
      return t("KeyPair.KeyName");
    });
    const Utility = computed(() => {
      return t("KeyPair.Utility");
    });
    const KeySize = computed(() => {
      return t("KeyPair.KeySize");
    });

    const FingerPrint = computed(() => {
      return t("KeyPair.FingerPrint");
    });

    const columnKeys = ref([
      {
        headerName: KeyName,
        field: "name",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: Utility,
        field: "utility",
        width: 90,
        minWidth: 50,
        flex: 1,
        sortable: true,
        filter: true,
      },
      {
        headerName: KeySize,
        autoHeight: true,
        field: "key_size",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: FingerPrint,
        field: "fingerPrint",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Action",
        width: 150,
        cellRenderer: actionCellRendererKeys,
        field: "action",
      },
    ]);

    const rowDataKeys = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
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
           data-action="copy"  title=${t("titleAgGrid.publicKey")}>
              <i class="mdi mdi-content-copy" style="color: #086eae;font-size: 20px;"></i>
           </button>
          <button
           class="action-button download"
           data-action="export"  title=${t("titleAgGrid.pK")}>
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

    const copyContent = async (text) => {
      try {
        await navigator.clipboard.writeText(text);
        state.snackbar = true;
        state.color = "success";
        state.textAlert = "Public Key copied Successfully";
      } catch (err) {
        state.snackbar = true;
        state.color = "red";
        state.textAlert = "Failed to Copy";
      }
    };
    const handleActionClient = (action, rowData, index) => {
      const user = user_privilege();
      switch (action) {
        case "delete":
        if (user !== 'viewer') {
          state.deleteDialog = true;
          state.deletedRow = rowData;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "copy":
        if (user !== 'viewer') {
          let text = rowData.public_key_value;
          copyContent(text);
    } else {
            state.isviewModal = true;
            state.viewModal = true;
          };

          break;
        case "export":
        if (user !== 'viewer') {
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

    } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          
          break;
        default:
          break;
      }
    };

    const openModalAdd = () => {
      const user = user_privilege();
      if (user !== 'viewer') {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
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
    };
    return {
      close,
      state,
      columnKeys,
      rowDataKeys,
      overlayTemplate,
      defaultColDef,
      emitter,
      paginationLocalization,
      actionCellRendererKeys,
      openModalAdd,
      onGridReady,
      getCookie,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
<style lang="scss">
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}
.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>
