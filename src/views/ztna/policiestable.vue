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
                <v-card-text v-html="overlayMessage">
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
  <v-container class="axe-media-print-hide" fluid>
    <div class="mt-6" style="display: flex; flex-direction: column">
      <h4>{{ $t("ztna.edgeRelaysPolicies") }}</h4>
      <v-divider></v-divider>
    </div>
    <div style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue
        id="grid-wrapperRouter"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-3"
        style="width: 100%"
        @grid-ready="onGridReadyRouter"
        :columnDefs="columnsALLRouter"
        :rowData="rowDataRouter.value"
        :gridOptions="gridOptions"
        :overlayNoRowsTemplate="overlayTemplate"
        :localeText="paginationLocalization"
      />
    </div>
    <div class="d-flex justify-end mt-3">
      <v-btn
        class="add-button"
        :rounded="true"
        color="indigo-darken-3"
        :disabled="!tokenStatus"
        @click="openModalRouter"
      >
        {{ $t("ztna.addRelaysPolicy") }}
      </v-btn>
    </div>
    <serviceAgGrid />
    <policyAgGrid />
    <modal-router-policy
      :isOpen="state.isModalOpenRouter"
      :selectedId="state.selectedId"
      :editRow="state.editRow"
      :modalMode="state.modalMode"
    />
    <!-- <ModalUpdateRouterP
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
          <v-btn
            color="blue darken-1"
            text
            @click="confirmDelete(state.selectedId)"
            >{{ $t("buttons.delete") }}</v-btn
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
    </v-snackbar>
  </v-container>
</template>
<script>
import { getCookie } from "@/mixins/csrftoken.js";
import ModalRouterPolicy from "@/components/modals/ModalRouterPolicy.vue";
import ModalUpdateRouterP from "@/components/modals/ModalUpdateRouterP.vue";
import serviceAgGrid from "./serviceAgGrid.vue";
import policyAgGrid from "./policyAgGrid.vue";
import { useI18n } from "vue-i18n";
import { ref, onMounted, reactive, inject, computed } from "vue";
import BaseLayout from "@/layouts/layout.vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import axios from "axios";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    ModalUpdateRouterP,
    serviceAgGrid,
    policyAgGrid,
    ModalRouterPolicy,
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const current_user = ref();
    const last_Subscription = ref([]);
    const tokenStatus = ref('')

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      modalData: {},
      modalMode: "create",
      isModalOpen: false,
      isOpen: null,
      deleteDialog: false,
      selectedId: null,
      modalDataRouter: {},
      modalModeRouter: "create",
      isModalOpenRouter: false,
      snackbar: false,
      color: null,
      textAlert: "",
      editRow: {},
    });

    const rowDataRouter = reactive([]);
    const overlayTemplate = ref(`
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`);

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
    const overlayMessage = computed(() => {
current_user.value= user_privilege('Ztna') 
console.log('current_user',current_user.value)
  if (current_user.value === "viewer" || current_user.value === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("ZTNA")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
});
    const semantic = computed(() => {
      return t("ztna.semantic");
    });

    const edgeRelaysRole = computed(() => {
      return t("ztna.edgeRelaysRole");
    });
    const identityRole = computed(() => {
      return t("ztna.identityRole");
    });
    const creationDate = computed(() => {
      return t("ztna.creationDate");
    });

    const columnsALLRouter = ref([
      {
        headerName: name,
        field: "name",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: edgeRelaysRole,
        field: "relay_attribute",
        cellRenderer: formatededgeRouterRoles,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: identityRole,
        field: "identity_attribute",
        cellRenderer: formatedidentityRoles,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: semantic,
        field: "semantique",
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: creationDate,
        field: "date_creation",
        cellRenderer: formatedcreatedAt,
        autoHeight: true,
        resizable: true,
        width: 90,
        minWidth: 150,
        flex: 1,
      },
      {
        headerName: "Actions",
        field: "actions",
        cellRenderer: actionCellRenderer,
        autoHeight: true,
        resizable: true,

        width: 150,
        sortable: false,
      },
    ]);

    const gridApiRouter = ref(null);

    const onGridReadyRouter = (params) => {
      gridApiRouter.value = params.api;
      if (gridApiRouter.value) {
        gridApiRouter.value.setRowData(rowDataRouter.value);
      }
    };

    function formatededgeRouterRoles(data) {
      const resultMessage = data.data.relay_attribute;
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "";
      return eGui;
    }

    function formatedidentityRoles(data) {
      const resultMessage = data.data.identity_attribute;
      let eGui = document.createElement("div");
      eGui.innerHTML = `${resultMessage}`;
      return eGui;
    }

    function formatedcreatedAt(data) {
      const resultMessage = formatDateTime(data.data.date_creation);
      let eGui = document.createElement("div");
      eGui.innerHTML = resultMessage ? `${resultMessage}` : "";
      return eGui;
    }
    const formatDateTime = (dateTimeStr) => {
      const [datePart, timePart] = dateTimeStr.split("T");
      const formattedDate = `${datePart.slice(0, 10)} ${timePart.slice(0, 5)}`;
      return formattedDate;
    };
    function actionCellRenderer(params) {
      let eGui = document.createElement("div");
      if (!tokenStatus.value) {
        eGui.innerHTML = `
        <button class="action-button edit" disabled>
          <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button class="action-button delete" disabled>
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
      `;
      } else {
        eGui.innerHTML = `
        <button class="action-button edit" data-action="edit">
          <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button class="action-button delete" data-action="delete">
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
    const handleActionClient = (action, rowData) => {
      const user = user_privilege("Ztna");

      switch (action) {
        case "edit":
        if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("ZTNA")) {
          state.modalMode = "edit";
          state.isModalOpenRouter = true;
          state.editRow = rowData;
          state.selectedId = rowData.id;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }

          break;
        case "delete":
        if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("ZTNA")) {
          OpenDelete(rowData.id);
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        default:
          break;
      }
    };
    async function OpenDelete(itemId) {
      state.selectedId = itemId;
      state.deleteDialog = true;
    }

    const cancelDelete = () => {
      state.deleteDialog = false;
    };

    const confirmDelete = async (itemId) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      let token = document.getElementById("app").getAttribute("token");

      axios
        .delete(`/ztna/delete_edge_routers_policies/${itemId}`, {
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

    onMounted(() => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)

      let token = document.getElementById("app").getAttribute("token");

      let router_policiesString = document
        .getElementById("app")
        .getAttribute("router_policies");

      let router_policiesObject = JSON.parse(router_policiesString);

      console.log("router_policiesObject", router_policiesObject);

      rowDataRouter.value = router_policiesObject ? router_policiesObject : [];
      if (token && token !== "null") {
        tokenStatus.value = true;
      } else {
        tokenStatus.value = false;
      }
      if (gridApiRouter.value) {
        gridApiRouter.value.setRowData(rowDataRouter.value);
      }
      emitter.on("closeRouteModal", () => {
        state.isModalOpenRouter = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      emitter.on("closeUpdateModal", () => {
        state.isModalUpdateOpen = false;
      });
      console.log("relay:", rowDataRouter);
    });

    const openModalRouter = () => {
      const user = user_privilege('Ztna');
      if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("ZTNA")) {
        state.modalDataRouter = {};
        state.modalMode = "create";
        state.isModalOpenRouter = true;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      }
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    return {
      close,
      t,
      emitter,
      state,
      openModalRouter,
      gridOptions,
      onGridReadyRouter,
      // openModalUpdate,
      confirmDelete,
      overlayMessage,
      cancelDelete,
      overlayTemplate,
      paginationLocalization,
      columnsALLRouter,
      rowDataRouter,
      tokenStatus,
    };
  },
};
</script>

<style>
.white-link {
  color: white;
  text-decoration: underline;
}

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
