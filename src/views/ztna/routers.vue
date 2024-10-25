<template>
<v-overlay v-model="state.viewModal">
            <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
              <v-card color="#193286" class="alert-box">
                <v-card-title class="img-containter">
                  <img
                    src="../../assets/images/view.png"
                    alt="logo"
                    class="img-view"
                    width="100"
                    height="100"
                /></v-card-title>
                <v-card-text>
                  {{  $t("profil.NoPermission") }}
                  <br />
                  {{  $t("profil.ContactAdmin") }} 
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
  <v-overlay v-model="state.loading">
    <v-dialog v-model="state.isLoadingDialogue" :scrim="false" persistent width="auto">
      <v-card color="#193286">
        <v-card-text>
          {{ $t("sdwan.pleaseWait") }}
          <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-overlay>
  <v-container class="axe-media-print-hide" fluid>
    <div class="mt-6" style="display: flex; flex-direction: column">
      <h4>{{ $t("ztna.listOfRelays") }}</h4>
      <v-divider></v-divider>
    </div>
    <div style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
        @grid-ready="onGridReady" :columnDefs="columnRouters" :rowData="routers" :gridOptions="gridOptions"
        :overlayNoRowsTemplate="overlayTemplate" :rowDragManaged="true" :rowDragEntireRow="true"
        @row-drag-end="onRowDragEnd" :localeText="paginationLocalization" />
    </div>
    <div class="d-flex justify-end mt-3">
      <v-btn class="add-button" :rounded="true" color="indigo-darken-3"   :disabled="!tokenStatus"  @click="openModalAdd">
        {{ $t("ztna.addRelay") }}
      </v-btn>
    </div>
    <ModalAddRouter :isOpen="state.isModalOpen" :selectedId="state.selectedId" :editRow="state.editRow"
      :modalMode="state.modalMode" />
    <!-- <ModalUpdateRouter
      :isOpen="state.isModalUpdateOpen"
      :selectedId="state.selectedId"
    /> -->

    <v-dialog v-model="state.deleteDialog" max-width="500px">
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
          <v-btn color="blue darken-1" text @click="confirmDelete(state.selectedId)">{{ $t("buttons.delete") }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar :timeout="2000" v-model="state.snackbar" location="bottom right" :color="state.color">
      {{ state.textAlert }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { getCookie } from "@/mixins/csrftoken.js";
import ModalAddRouter from "@/components/modals/ModalAddRouter.vue";
import ModalUpdateRouter from "@/components/modals/ModalUpdateRouter.vue";
import { useI18n } from "vue-i18n";
import { ref, onMounted, reactive, inject, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "RoutersComponent",
  components: {
    ModalAddRouter,
    VButton,
    ModalUpdateRouter,
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const routers = ref([]);
    const tokenStatus = ref('')

    const overlayTemplate = ref(
      `
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`
    );
    const paginationLocalization = reactive({
      of: "/",
    });
    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    const name = computed(() => {
      return t("ztna.name");
    });

    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });
    const online = computed(() => {
      return t("ztna.online");
    });
    const verified = computed(() => {
      return t("ztna.verified");
    });

    const columnRouters = ref([
      // { headerName: "ID", field: "id", sortable: true,  flex: 1 },
      {
        headerName: name,
        field: "name",
        sortable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: verified,
        field: "verified",
        cellRenderer: enrollmentCellRendrer,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: online,
        field: "online",
        cellRenderer: IsOnlineCellRendrer,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "date_creation",
        cellRenderer: formatedcreatedAt,

        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Actions",
        field: "actions",
        cellRenderer: actionCellRenderer,
        width: 150,
      },
    ]);

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      loading: false,
      isLoadingDialogue: false,
      deleteDialog: false,
      deletedItemId: null,
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isModalUpdateOpen: false,
      selectedId: null,
      isOpen: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    function tokenCellRendrer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (params.node.data?.enrollmentJwt) {
        eGui.innerHTML = `
          <button
           class="action-button download"
           data-action="download">
              <i class="mdi mdi-download-circle" style="color: #086eae; font-size: 20px;"></i>
           </button>
    `;

        eGui.querySelectorAll(".action-button").forEach((button) => {
          button.addEventListener("click", () => {
            const action = button.getAttribute("data-action");
            handleActionClient(action, params.node.data);
          });
        });
      } else {
        eGui.innerHTML = `--`;
      }

      return eGui;
    }

    function enrollmentCellRendrer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (params.node.data.verified === true) {
        eGui.innerHTML = `<i class="mdi mdi-check-circle" style="color: green; font-size: 20px;"></i>`;
      } else {
        eGui.innerHTML = `
        <i class="mdi mdi-alert-circle" style="color: red; font-size: 20px;"></i>
    `;

        eGui.querySelectorAll(".action-button").forEach((button) => {
          button.addEventListener("click", () => {
            const action = button.getAttribute("data-action");
            handleActionClient(action, params.node.data);
          });
        });
      }

      return eGui;
    }

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });
      if (isCurrentRowEditing) {
        eGui.innerHTML = `
              <button
                class="action-button edit"
                data-action="edit">
                     edit
              </button>
              <button
                class="action-button cancel"
                data-action="cancel">
                     cancel
              </button>
              `;
      } else {
        if (!params.data.online) {
          if(!tokenStatus.value) {
          eGui.innerHTML = `
         <button
          id="play"
          class="action-button play"
          disabled>
             <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
          </button>
              <button
                class="action-button edit"
                disabled title="Edit Server">
                   <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>
                <button
                class="action-button delete"
                disabled title="Delete ">
                  <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button> 
                `;}
              else{
                 eGui.innerHTML = `
                <button
          id="play"
          class="action-button play"
          data-action="play">
             <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
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
        }
        else {
          if(!tokenStatus.value) {
            eGui.innerHTML = `
             <button
          id="stop"
          class="action-button stop"
          disabled>
             <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
          </button>
              <button
                class="action-button edit"
               disabled title="Edit Server">
                   <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>
                <button
                class="action-button delete"
                disabled title="Delete ">
                  <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
                </button>
      
                `;}
                else {
                  eGui.innerHTML = `
             <button
          id="stop"
          class="action-button stop"
          data-action="stop">
             <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
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
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const user = user_privilege('Ztna');

      switch (action) {
        case "edit":
        if (user && user !=='viewer') {
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };

          break;
        case "download":
        if (user && user !=='viewer') {
          let text = rowData.enrollmentJwt;
          // copyContent(text);
          const blob = new Blob([text], {
            type: "application/x-x509-ca-cert",
          });

          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.style.display = "none";
          a.href = url;
          a.download = `${rowData.name}.txt`;

          document.body.appendChild(a);
          a.click();

          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
          
          break;
        case "delete":
        if (user && user !=='viewer') {
          opendelete(rowData.id);
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };

          break;
        case "play":
        if (user && user !=='viewer') {
          let payloadStart = {
            name: rowData.name,
            token: rowData.enrollmentJwt
          };

          let tokenStart = document.getElementById("app").getAttribute("token");
          state.loading = true;
          state.isLoadingDialogue = true;

          axios
            .post(`/ztna/start_routers/${rowData.id}`, payloadStart, {
              headers: {
                "zt-session": tokenStart,
                "Content-Type": "application/json",
              },
            })
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.message;
                state.loading = false;
                state.isLoadingDialogue = false;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
              state.loading = false;
              state.isLoadingDialogue = false;
            });

          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
          
          break;
        case "stop":
        if (user && user !=='viewer') {
          let payload = {
            name: rowData.name,
            token: rowData.enrollmentJwt
          };

          let token = document.getElementById("app").getAttribute("token");
          state.loading = true;
          state.isLoadingDialogue = true;

          axios
            .post(`/ztna/stop_routers/${rowData.id}`, payload, {
              headers: {
                "zt-session": token,
                "Content-Type": "application/json",
              },
            })
            .then((response) => {
              if (response.status == "200") {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.message;
                state.loading = false;
                state.isLoadingDialogue = false;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              }
            })
            .catch((i) => {
              state.snackbar = true;
              state.color = "red";
              state.textAlert = i.response.data.error;
              state.loading = false;
              state.isLoadingDialogue = false;
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };

 
          break;
        default:
          break;
      }
    };

    const copyContent = async (text) => {
      try {
        await navigator.clipboard.writeText(text);
        state.snackbar = true;
        state.color = "success";
        state.textAlert = "JWT copied Successfully";
      } catch (err) {
        state.snackbar = true;
        state.color = "red";
        state.textAlert = "Failed to Copy";
      }
    };

    const fetchRouters = () => {
      let token = document.getElementById("app").getAttribute("token");
      let routersString = document
        .getElementById("app")
        .getAttribute("routers");
      let routersObject;
      if (token && token !== "null") {
        tokenStatus.value = true
      } 
      else {
        tokenStatus.value = false
    }
      try {
        routersObject = JSON.parse(routersString);
        console.log("routersObject", routersObject);
        console.log(routersObject);
      } catch (error) {
        console.error("Failed to parse routers string:", error);
        routersObject = { data: [] };
      }

      routers.value = routersObject ? routersObject : [];

      console.log(routers.value);
    };

    const onGridReady = (params) => {
      // params.api.sizeColumnsToFit();
    };

    onMounted(() => {
      emitter.on("closeRouterModal", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeUpdateModal", () => {
        state.isModalUpdateOpen = false;
      });
      fetchRouters();
    });

    const openModalAdd = () => {
      const user = user_privilege('Ztna');
      if (user && user !=='viewer') {
        state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
    };

    const opendelete = (itemId) => {
  state.selectedId = itemId;
  state.deleteDialog = true;
 
    };

    const confirmDelete = async (deletedItemId) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      let token = document.getElementById("app").getAttribute("token");
      state.loading = true;
          state.isLoadingDialogue = true;
      axios
        .delete(`/ztna/delete_routers/${deletedItemId}`, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.message;
          state.loading = false;
          state.isLoadingDialogue = false;
          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
          state.loading = false;
          state.isLoadingDialogue = false;
        });
    };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    function IsOnlineCellRendrer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (params.node.data.online === true) {
        eGui.innerHTML = `<i class="mdi mdi-check-circle" style="color: green; font-size: 20px;"></i>`;
      } else {
        eGui.innerHTML = `
        <i class="mdi mdi-alert-circle" style="color: red; font-size: 20px;"></i>
    `;

        eGui.querySelectorAll(".action-button").forEach((button) => {
          button.addEventListener("click", () => {
            const action = button.getAttribute("data-action");
            handleActionClient(action, params.node.data);
          });
        });
      }

      return eGui;
    }

    const formatDateTime = (params) => {
      const dateTimeStr = params;
      const [datePart, timePart] = dateTimeStr.split("T");
      const formattedDate = `${datePart.slice(0, 10)} ${timePart.slice(0, 5)}`;
      return formattedDate;
    };

    function formatedcreatedAt(data) {
      const resultMessage = formatDateTime(data.data.date_creation);
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "--";
      return eGui;
    }
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    return {
      close,
      t,
      emitter,
      state,
      openModalAdd,
      routers,
      gridOptions,
      columnRouters,
      overlayTemplate,
      paginationLocalization,
      fetchRouters,
      onGridReady,
      opendelete,
      confirmDelete,
      cancelDelete,
      tokenStatus,
    };
  },
};
</script>

<style>
.table {
  width: 100%;
  border-collapse: collapse;
  border: 0.5px solid #000;
}

.table thead tr:first-child {
  border-bottom: 0.5px solid #000;
  background-color: ghostwhite;
}

.table tbody tr:last-child {
  border-bottom: 0.5px solid #000;
}
</style>
