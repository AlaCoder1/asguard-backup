<template>
  <v-col cols="6">
    <h4>Squid authentification</h4>
    <v-divider class="mt-2"></v-divider>
    <v-card class="mt-3">
      <v-row class="mt-1 ml-1">
        <v-col cols="4">
          <label>Authentification</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <input type="checkbox" v-model="state.enable" />
          <label class="ml-2">Enable</label>
        </v-col>
      </v-row>
      <v-row class="d-flex justify-end mt-5 mb-2">
        <div>
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="Save"
            :isLarge="true"
            class="mr-4"
            @click="saveSquid"
          />
        </div> </v-row
    ></v-card>

    <v-row class="mt-1">
      <v-col cols="12">
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            style="width: 100%"
            @grid-ready="onGridReady"
            :columnDefs="columnUser"
            :rowData="rowDataUser.value"
          />
        </div>
      </v-col>
    </v-row>

    <v-row class="d-flex justify-end mt-5">
      <div>
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          label="Add User"
          :isLarge="true"
          class="ml-2"
          @click="openModalAdd"
        />
      </div>
    </v-row>
    <v-dialog v-model="state.deleteDialogSquid" max-width="500px">
      <v-card>
        <v-card-title class="headline">Delete Confirmation</v-card-title>
        <v-card-text>Are you sure you want to delete this user ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDelete">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="confirmDelete"
            >Delete</v-btn
          >
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

      <template v-slot:actions> </template>
    </v-snackbar>
    <ModalSquidUser
      :isOpen="state.isModalOpen"
      :editRow="state.editRow"
      :modalMode="state.modalMode"
    />
  </v-col>
</template>
<script>
import axios from "axios";
import { reactive, ref, onMounted, inject } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidUser from "@/components/modals/ModalSquidUser.vue";
export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidUser,
  },
  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      deleteDialogSquid: false,
      deletedRow: null,
      snackbar: false,
      color: "",
      textAlert: "",
      enable: false,
      modalData: {},
      isOpen: null,
      modalMode: "",
      isModalOpen: false,
      editRow: null,
    });

    const rowDataUser = reactive({});
    const gridApi = ref(null);

    const columnUser = [
      {
        headerName: "Username",
        field: "username",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Actions",
        cellRenderer: actionCellRenderer,
        sortable: true,
        filter: true,
      },
    ];

    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataUser.value);
      } else {
        console.error("Grid API.");
      }
    };

    const openModalAdd = () => {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
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

    const populateSquid = () => {
      const statusEnableAttribute =
        document.getElementById("app").attributes["statusEnable"].value;
      const statusEnable = JSON.parse(statusEnableAttribute);
      state.enable = statusEnable;
    };
    const populateSquidUser = () => {
      const proxyUserAttribute =
        document.getElementById("app").attributes["proxyUser"].value;
      const proxyUser = JSON.parse(proxyUserAttribute);
      

      if (!rowDataUser.value) {
        rowDataUser.value = [];
      }
      rowDataUser.value = proxyUser;
    };

    onMounted(() => {
      populateSquid();
      populateSquidUser();
      emitter.on("closeSquidUserModal", () => {
        state.isModalOpen = false;
      });
    });

    const saveSquid = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let payload = {
        status: state.enable,
      };

      axios
        .post("/proxy/change_auth_status", payload)
        .then((response) => {
          if (response.status == "200") {
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
    };

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      let editingCells = params.api.getEditingCells();
      // checks if the rowIndex matches in at least one of the editing cells
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
      class="action-button delete"
      data-action="delete">
         <i class="fas fa-times" style="color: #086eae; margin-left:10px "></i>
      </button>
    `;
      }

      // Add event listeners to handle button clicks
      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleAction(action, params.node.data, params.node.rowIndex);
        });
      });

      return eGui;
    }

    const handleAction = (action, rowData) => {
      switch (action) {
        case "delete":
          console.log("rowData", rowData);
          state.deleteDialogSquid = true;
          state.deletedRow = rowData;
          break;
        default:
          break;
      }
    };

    const cancelDelete = () => {
      state.deleteDialogSquid = false;
    };
    const confirmDelete = () => {
      const csrfTok = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfTok;

      axios
        .delete(`/proxy/delete_user_squid/${state.deletedRow.id}`)
        .then((response) => {
          if (response.status == 200) {
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
    };

    return {
      state,
      emitter,
      columnUser,
      rowDataUser,
      onGridReady,
      confirmDelete,
      cancelDelete,
      openModalAdd,
      saveSquid,
    };
  },
};
</script>
