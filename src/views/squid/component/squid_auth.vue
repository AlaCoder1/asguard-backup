<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
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
  <v-col cols="6">
    <h4>{{ $t("squid.squidAuthentification") }}</h4>
    <v-divider style="margin-top: 14px"></v-divider>
    <v-card class="mt-3">
      <v-row class="mt-1 ml-1">
        <v-col cols="4">
          <label>Authentification</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <input type="checkbox" v-model="state.enable" />
          <label class="ml-2">{{ $t("squid.disable") }}</label>
        </v-col>
      </v-row>
      <v-row class="d-flex justify-end mt-5 mb-2">
        <div>
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            :label="$t('buttons.save')"
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
            :gridOptions="gridOptions"
            :columnDefs="columnUser"
            :rowData="rowDataUser.value"
            :localeText="paginationLocalization"
            :overlayNoRowsTemplate="overlayTemplate"
            :pagination="true"
            :paginationPageSize="4"
          />
        </div>
      </v-col>
    </v-row>

    <v-row class="d-flex justify-end mt-5 mr-0">
      <div>
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          :label="$t('squid.addUser')"
          :isLarge="true"
          @click="openModalAdd"
        />
      </div>
    </v-row>
    <v-dialog v-model="state.deleteDialogSquid" max-width="500px">
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
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject, computed, watch } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalSquidUser from "@/components/modals/ModalSquidUser.vue";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  components: {
    AgGridVue,
    VButton,
    ModalSquidUser,
  },
  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const emitter = inject("emitter");
    const state = reactive({
      isviewModal: false,
      viewModal: false,
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

    const paginationLocalization = reactive({
      of: "/",
    });

    const gridOptions = {};

    const username = computed(() => {
      return t("form.username");
    });

    const columnUser = ref([
      {
        headerName: username,
        cellRenderer: formatedUsername,
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        width: 150,
        cellRenderer: actionCellRenderer,
      },
    ]);

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataUser.value);
      } else {
        console.error("Grid API.");
      }
    };

    const openModalAdd = () => {
      const user = user_privilege('Proxy');
      if (user && user !== 'viewer' && user !=='default') {
        state.modalData = {};
        state.modalMode = "create";
        state.isModalOpen = true;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
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

    function formatedUsername(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
         ${data.data.username} ( ${data.data.email ?? "--"}  )
        `;

      return eGui;
    }

    onMounted(() => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      populateSquid();
      populateSquidUser();
      emitter.on("closeSquidUserModal", () => {
        state.isModalOpen = false;
      });
    });

    const saveSquid = () => {
      const user = user_privilege('Proxy');
      if (user && user !== 'viewer' && user !=='default') {
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
        state.isviewModal = true;
        state.viewModal = true;
      }
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

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const handleAction = (action, rowData) => {
      const user = user_privilege("Proxy");
      switch (action) {
        case "delete":
      if (user && user !== 'viewer' && user !=='default') {
          console.log("rowData", rowData);
          state.deleteDialogSquid = true;
          state.deletedRow = rowData;
        } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
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

    return {
      close,
      state,
      paginationLocalization,
      emitter,
      columnUser,
      rowDataUser,
      overlayTemplate,
      gridOptions,
      onGridReady,
      formatedUsername,
      confirmDelete,
      cancelDelete,
      openModalAdd,
      saveSquid,
    };
  },
};
</script>
