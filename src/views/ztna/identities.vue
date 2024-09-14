<template>
  <div class="mr-3">
    <div class="certificats-management mt-6 ml-4" style="display: flex; flex-direction: column">
      <h4>{{ $t("ztna.listofIdentities") }}</h4>
      <v-divider></v-divider>
      <div style="overflow: hidden; flex-grow: 1">
        <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
          @grid-ready="onGridReady" :columnDefs="columnIdentities" :rowData="Identities" :gridOptions="gridOptions"
          :overlayNoRowsTemplate="overlayTemplate" :rowDragManaged="true" :rowDragEntireRow="true"
          :localeText="paginationLocalization" />
      </div>
    </div>
  </div>
  <br />
  <ModalAddIdentity :isOpen="state.isModalOpen" :selectedId="state.selectedId" :editRow="state.editRow"
    :modalMode="state.modalMode" />
  <ModalAddEnrollment :isOpen="state.isModalEnrollmentOpen" :selectedId="state.selectedId" />
  <!-- <ModalUpdateIdentity
    :isOpen="state.isModalUpdateOpen"
    :selectedId="state.selectedId"
    :editRow="state.editRow"
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
  <div class="d-flex justify-end mt-5 mr-2">
    <v-btn class="add-button" :rounded="true" color="indigo-darken-3" @click="openModalAdd">
      {{ $t("ztna.addIdentity") }}
    </v-btn>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import { reactive, onMounted, inject, ref, computed } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import ModalAddIdentity from "@/components/modals/ModalAddIdentity.vue";
import ModalAddEnrollment from "@/components/modals/ModalAddEnrollment.vue";
import ModalUpdateIdentity from "@/components/modals/ModalUpdateIdentity.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";

export default {
  name: "IdentitiesComponent",
  components: {
    BaseLayout,
    ModalAddIdentity,
    ModalAddEnrollment,
    ModalUpdateIdentity,
    AgGridVue,
  },

  setup() {
    const { t } = useI18n();
    const Identities = ref();
    const emitter = inject("emitter");
    const state = reactive({
      deleteDialog: false,
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isModalEnrollmentOpen: false,
      isModalUpdateOpen: false,
      isOpen: null,
      selectedId: null,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });
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

    const gridApi = ref(null);
    const gridColumnApi = ref(null);

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
    const attribute = computed(() => {
      return t("ztna.attribute");
    });
    const hostname = computed(() => {
      return t("ztna.hostname");
    });
    const enrolled = computed(() => {
      return t("ztna.enrolled");
    });
    const expirationDate = computed(() => {
      return t("ztna.expirationDate");
    });
    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });

    const columnIdentities = ref([
      {
        headerName: "ID",
        field: "id",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: name,
        field: "name",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: attribute,
        field: "roleAttributes",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: hostname,
        field: "envInfo.hostname",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: enrolled,
        field: "enrollment.ott.jwt",
        cellRenderer: enrollmentCellRendrer,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Token",
        field: "enrollment.ott.jwt",
        cellRenderer: tokenCellRendrer,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: expirationDate,
        field: "enrollment.ott.expiresAt",
        cellRenderer: formatedexpiresAt,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "createdAt",
        cellRenderer: formatedcreatedAt,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Actions",
        field: "actions",
        width: 150,
        cellRenderer: actionCellRenderer,
      },
    ]);
    function tokenCellRendrer(params) {
      let eGui = document.createElement("div");
      let editingCells = params.api.getEditingCells();
      let isCurrentRowEditing = editingCells.some((cell) => {
        return cell.rowIndex === params.node.rowIndex;
      });

      if (params.node.data.enrollment?.ott?.jwt) {
        eGui.innerHTML = `
      <button class="action-button copy" data-action="copy">
        <i class="mdi mdi-content-copy" style="color: #086eae; font-size: 20px;"></i>
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

      if (params.node.data.enrollment?.ott?.jwt) {
        eGui.innerHTML = `<i class="mdi mdi-check-circle" style="color: green; font-size: 20px;"></i>`;
      } else {
        eGui.innerHTML = `
    
      <button class="action-button enroll" data-action="enroll">
        <i class="mdi mdi-alert-circle" style="color: red; font-size: 20px;"></i>
      </button>
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
      switch (action) {
        case "edit":
          // openModalUpdate(rowData);
          console.log('rowData', rowData)
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;


          break;
        case "copy":
          let text = rowData.enrollment.ott.jwt;
          copyContent(text);
          break;
        case "enroll":
          openModalEnrollement(rowData.id);

          break;
        case "delete":
          OpenDelete(rowData.id);

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
    const fetchIdentities = () => {
      let token = document.getElementById("app").getAttribute("token");
      console.log("token", token);
      let IdentitiesString = document
        .getElementById("app")
        .getAttribute("Identities");

      let IdentitiesObject;
      try {
        IdentitiesObject = JSON.parse(IdentitiesString);
        console.log('IdentitiesObject', IdentitiesObject)
      } catch (error) {
        console.error("Failed to parse Identities string:", error);
      }


      Identities.value = IdentitiesObject ? IdentitiesObject : [];
      console.log(' Identities.value', Identities.value)

    };
    async function OpenDelete(itemId) {
      state.selectedId = itemId;
      state.deleteDialog = true;
    }
    onMounted(() => {
      emitter.on("closeidentityModal", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeEnrollmentModal", () => {
        state.isModalEnrollmentOpen = false;
      });
      emitter.on("closeUpdateModal", () => {
        state.isModalUpdateOpen = false;
      });
      fetchIdentities();
    });
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
    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    };

    const openModalEnrollement = (id) => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalEnrollmentOpen = true;
      state.selectedId = id;
    };

    // const openModalUpdate = (row) => {
    //   state.modalMode = "edit";
    //   state.isModalUpdateOpen = true;
    //   state.editRow = row;
    //   state.selectedId = row.id;
    // };

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    function formatedcreatedAt(data) {
      const resultMessage = formatDateTime(data.data.createdAt);
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "--";
      return eGui;
    }
    function formatedexpiresAt(data) {
      if (data.data.enrollment.ott) {
        const resultMessage = formatDateTime(
          data.data.enrollment.ott.expiresAt
        );
        let eGui = document.createElement("div");
        eGui.innerHTML = resultMessage ? `${resultMessage}` : "--";
        return eGui;
      }
    }
    const formatDateTime = (dateTimeStr) => {
      const [datePart, timePart] = dateTimeStr.split("T");
      const formattedDate = `${datePart.slice(0, 10)} ${timePart.slice(0, 5)}`;
      return formattedDate;
    };

    const confirmDelete = async (deletedItemId) => {

      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      axios
        .delete(`/ztna/delete_identities/${deletedItemId}`, {
          headers: {
            "zt-session": token,
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          state.snackbar = true;
          state.color = "success";
          state.textAlert = response.data.message;
          setTimeout(() => {
            location.reload();
          }, 1000);
        })
        .catch((i) => {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = i.response.data.error;
        });

      // console.log("deletedItemId", deletedItemId);
      // try {
      //   let token = document.getElementById("app").getAttribute("token");
      //   const proxyUrl = "https://asguard:3000";
      //   const apiUrl = `/edge/management/v1/identities/${deletedItemId}`; // This part remains the same

      //   const response = await axios.delete(proxyUrl + apiUrl, {
      //     headers: {
      //       "zt-session": token,
      //       "Content-Type": "application/json",
      //     },
      //   });
      //   console.log("response", response);

      //   state.snackbar = true;
      //   state.color = "success";
      //   state.textAlert = "Identity deleted successfully";
      //   setTimeout(() => {
      //     location.reload();
      //   }, 1000);
      //   state.deleteDialog = false;
      // } catch (error) {
      //   state.snackbar = true;
      //   state.color = "red";
      //   state.textAlert = "Delete failure";
      //   console.error(
      //     "Failed to delete item:",
      //     error.response ? error.response.data : error.message
      //   );
      // }
    };

    const onGridReady = (params) => {
      gridApi.value = params.api;
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(Identities.value);
      }
    };

    return {
      state,
      openModalAdd,
      t,
      Identities,
      getCookie,
      emitter,
      fetchIdentities,
      OpenDelete,
      openModalEnrollement,
      // openModalUpdate,
      formatDateTime,
      cancelDelete,
      confirmDelete,
      gridOptions,
      columnIdentities,
      overlayTemplate,
      paginationLocalization,
      onGridReady,
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
