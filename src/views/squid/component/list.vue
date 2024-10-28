<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
          <v-card-text v-html="overlayMessage">
          </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("subtitle.rules") }}</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-5">
          <v-col cols="12" md="6">
            <v-text-field
              id="filter-text-box"
              density="compact"
              class="w-75"
              variant="solo"
              rounded
              :label="$t('squid.search')"
              append-inner-icon="mdi-magnify"
              single-line
              hide-details
              @input="onFilterTextBoxChanged"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine"
              :columnDefs="columnRules"
              :rowData="rowDataRules.value"
              @grid-ready="onGridReady"
              :rowDrag="true"
              :defaultColDef="defaultColDef"
              style="width: 100%"
              :localeText="paginationLocalization"
              :overlayNoRowsTemplate="overlayTemplate"
              :pagination="true"
              :paginationPageSize="4"
            >
            </ag-grid-vue>
          </div>
        </v-row>
        <div class="error-feedback mt-5">{{ textAlert }}</div>
      </v-col>
    </v-row>
    <v-row class="d-flex justify-end mt-5">
      <div>
        <VButton
          rounded
          outlined
          color="#213E9F"
          label-color="#ffffff"
          :label="$t('buttons.Add')"
          :isLarge="true"
          class="ml-2"
          @click="openModalRule"
        />
      </div>
    </v-row>
    <v-dialog v-model="state.deleteDialogRule" max-width="500px">
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
    <ModalAddRule
      :isOpenModal="state.isModalOpenRule"
      :editRowRule="state.editRowRule"
      :modalModeRule="state.modalModeRule"
    />

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
import { useI18n } from "vue-i18n";
import axios from "axios";
import { reactive, ref, onMounted, inject, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalAddRule from "@/components/modals/ModalAddRule.vue";
import CertStatusRenderVue from "../agGridCustomRender/CertStatusRenderVue.vue";
import CertAllowStatus from "../agGridCustomRender/CertAllowStatus.vue";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  components: {
    AgGridVue,
    VButton,
    ModalAddRule,
    CertStatusRenderVue,
    CertAllowStatus,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const current_user = ref();
    const last_Subscription = ref([]);
    const overlayTemplate = ref("");
    const state = reactive({
      deleteDialogRule: false,
      isviewModal: false,
      viewModal: false,
      deletedRow: null,
      modalDataRule: {},
      isOpenModal: null,
      modalModeRule: "",
      isModalOpenRule: false,
      editRowRule: {},
      textAlert: "",
      color: "",
      snackbar: false,
    });
    const rowDataRules = reactive({});
    const gridColumnApi = ref(null);
    const paginationLocalization = reactive({
      of: "/",
    });
    const textAlert = ref(null);
    const gridApi = ref(null);
    const defaultColDef = ref({
      // flex: 1,
      cellDataType: false,
    });

    const ruleName = computed(() => {
      return t("sdwan.ruleName");
    });
    const overlayMessage = computed(() => {
current_user.value= user_privilege() 
console.log('current_user',current_user.value)
  if (current_user.value === "viewer" || current_user.value === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("Proxy")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } 
});
    const routageType = computed(() => {
      return t("squid.routageType");
    });
    const value = computed(() => {
      return t("squid.value");
    });
    const allowedByAuth = computed(() => {
      return t("squid.allowedByAuth");
    });
    const start = computed(() => {
      return t("squid.start");
    });
    const end = computed(() => {
      return t("squid.end");
    });
    const status = computed(() => {
      return t("squid.status");
    });
    const columnRules = ref([
      {
        headerName: ruleName,
        field: "rule_name",
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: routageType,
        field: "type",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: value,
        field: "value",
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: allowedByAuth,
        field: "allow_by_auth",
        cellRendererSelector: function (params) {
          const allow_by_auth = {
            component: "CertAllowStatus",
            params: params.data.allow_by_auth,
          };
          return allow_by_auth;
        },
        width: 90,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
      },
      {
        headerName: start,
        field: "time_from",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: end,
        field: "time_to",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: status,
        field: "status",
        cellRendererSelector: function (params) {
          const status = {
            component: "CertStatusRenderVue",
            params: params.data.status,
          };
          return status;
        },
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
      gridColumnApi.value = params.columnApi;
      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("Grid API.");
      }
    };

    const onFilterTextBoxChanged = () => {
      gridApi.value.setQuickFilter(
        document.getElementById("filter-text-box").value
      );
    };

    function actionCellRenderer(params) {
      let eGui = document.createElement("div");

      if (params.data.time_from === "--") {
        eGui.innerHTML = `
        <button
      class="action-button edit"
      data-action="edit">
         <i class="far fa-edit" style="color: #086eae;"></i>
      </button>
  
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;
      } else {
        eGui.innerHTML = `
      <button
        class="action-button delete"
        data-action="delete">
          <i class="fas fa-times" style="color: #086eae;"></i>
      </button>
      `;
      }

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
        case "edit":
          if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("Proxy")) {
            state.modalDataRule = {};
            state.modalModeRule = "edit";
            state.isModalOpenRule = true;
            state.editRowRule = rowData;
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        case "delete":
          if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("Proxy")) {
            state.deleteDialogRule = true;
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

    const openModalRule = () => {
      const user = user_privilege('Proxy');
      if (user && user !== 'viewer' && user !=='default' && last_Subscription.value.includes("Proxy")) {
        state.modalDataRule = {};
        state.modalModeRule = "create";
        state.isModalOpenRule = true;
      } else {
        state.isviewModal = true;
        state.viewModal = true;
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
    const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)
      emitter.on("closeAddRuleModal", () => {
        state.isModalOpenRule = false;
        state.modalDataRule = {};
        state.modalModeRule = "";
        state.editRowRule = {};
      });

      const proxyRuleAttribute =
        document.getElementById("app").attributes["proxyRule"].value;
      const proxyRule = JSON.parse(proxyRuleAttribute);

      let mapedRule = proxyRule.map((i) => {
        return {
          id: i.id,
          rule_name: i.rule_name,
          days: i.days,
          status: i.status === false ? "Disable" : "Enable",
          allow_by_auth: i.allow_by_auth === false ? "Disable" : "Enable",
          time_from: i.time_from ?? "--",
          time_to: i.time_to ?? "--",
          type: i.type,
          value: i.value,
        };
      });

      if (!rowDataRules.value) {
        rowDataRules.value = [];
      }
      rowDataRules.value = mapedRule;
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
    const cancelDelete = () => {
      state.deleteDialogRule = false;
    };
    const confirmDelete = () => {
      const csrfTok = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfTok;

      axios
        .delete(`/proxy/deleteRuleSquid/${state.deletedRow.id}`)
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
      state,
      close,
      cancelDelete,
      confirmDelete,
      textAlert,
      overlayMessage,
      columnRules,
      gridColumnApi,
      rowDataRules,
      overlayTemplate,
      onGridReady,
      emitter,
      openModalRule,
      actionCellRenderer,
      defaultColDef,
      paginationLocalization,
      onFilterTextBoxChanged,
    };
  },
};
</script>
<style>
.error-feedback {
  color: red;
  font-size: 0.85em;
}
.white-link {
  color: white;
  text-decoration: underline;
}

</style>
