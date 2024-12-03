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
  <div class="mr-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
      <h4>{{ $t("sdwan.SDWANRules") }}</h4>
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
              :columnDefs="columnRules"
              :rowData="rowDataRule.value"
              :overlayNoRowsTemplate="overlayTemplate"
              :pagination="true"
              :paginationPageSize="5"
              :localeText="paginationLocalization"
            />
          </div>
          <div class="d-flex justify-end mt-3 mb-15">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              :label="$t('sdwan.addRule')"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="openModalAdd"
            />
          </div>
        </v-col>
      </v-row>
      <ModalSdwanRule
        :isOpen="state.isModalOpen"
        :editRow="state.editRow"
        :modalMode="state.modalMode"
      />
    </div>
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
    </v-snackbar>
  </div>
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
import ModalSdwanRule from "@/components/modals/ModalSdwanRule.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "Sdwan",
  components: {
    ModalSdwanRule,
    BaseLayout,
    AgGridVue,
    VButton,
  },
  setup() {
    const { t } = useI18n();
    const current_user = ref();
    const last_Subscription = ref([]);
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const paginationLocalization = reactive({
      of: "/",
    });

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
      editRow: {},
      isModalOpen: false,
      isOpen: null,
      isLoadingDialogue: false,
      loading: false,
    });

    const ruleName = computed(() => {
      return t("sdwan.ruleName");
    });
    const overlayMessage = computed(() => {
current_user.value= user_privilege('Sdwan') 
console.log('current_user',current_user.value)
  if (current_user.value === "viewer" || current_user.value === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!last_Subscription.value.includes("SDWAN")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
});
    const sourceAddress = computed(() => {
      return t("sdwan.sourceAddress");
    });
    const area = computed(() => {
      return t("sdwan.area");
    });
    const algorythmType = computed(() => {
      return t("sdwan.algorythmType");
    });

    const columnRules = ref([
      {
        headerName: ruleName,
        field: "name",
        sortable: true,
        autoHeight: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: sourceAddress,
        field: "source_address",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: area,
        autoHeight: true,
        field: "area_name",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: algorythmType,
        autoHeight: true,
        field: "algorythme_type",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      // {
      //   headerName: "Destination address",
      //   autoHeight: true,
      //   field: "destination_address",
      //   sortable: true,
      //   filter: true,
      // },
      {
        headerName: "Actions",
        cellRenderer: actionCellRendererArea,
        field: "action",
        width: 150,
        sortable: true,
        filter: true,
      },
    ]);

    const rowDataRule = reactive({});

    const gridApi = ref(null);

    const onGridReady = (params) => {
      // gridApi.value = params.api;
      // gridApi.value.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     gridApi.value.sizeColumnsToFit();
      //   });
      // });
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
        if (!params.data.rule_status) {
          eGui.innerHTML = `

      <button
        id="play"
        class="action-button play"
        data-action="play" title=${t("sdwan.startServer")}>
            <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
        </button>
        <button
        class="action-button edit"
        data-action="edit">
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
        <button
        class="action-button delete"
        data-action="delete">
          <i class="mdi mdi-delete-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>


    `;
        } else if (params.data.rule_status) {
          eGui.innerHTML = `
        <button
        id="stop"
        class="action-button stop"
        data-action="stop" title=${t("sdwan.stop")}>
            <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
        </button>
        <button
        class="action-button edit"
        data-action="edit">
            <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
        </button>
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
      const user = user_privilege("Sdwan");
      switch (action) {
        case "play":
      if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("SDWAN") ) {
          console.log("play", rowData);
          state.loading = true;
          state.isLoadingDialogue = true;
          axios
            .put(`/sdwan/startSdwanRule/${rowData.id}`)
            .then((response) => {
              state.snackbar = true;
              state.color = "success";
              state.textAlert = response.data.msg;
              state.loading = false;
              state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;
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
          break;
        case "stop":
        if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("SDWAN") ) {
          console.log("stop", rowData);

            state.loading = true;
            state.isLoadingDialogue = true;
            axios
              .put(`/sdwan/stopSdwanRule/${rowData.id}`)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;
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
          break;
        case "edit":
        if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("SDWAN") ) {
          console.log("edit", rowData);
          state.modalMode = "edit";
          state.isModalOpen = true;
          state.editRow = rowData;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          }
          break;
        case "delete":
        if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("SDWAN") ) {
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

    const openModalAdd = () => {
      const user = user_privilege('Sdwan');
      if (user && user !=='viewer' && user !=='default' && last_Subscription.value.includes("SDWAN") ) {
      state.modalData = {};
      state.modalMode = "create";
      state.isModalOpen = true;
    } else {
            state.isviewModal = true;
            state.viewModal = true;
            };
    };

    onMounted(() => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      emitter.on("closeSdwanModalRule", () => {
        state.isModalOpen = false;
        state.isOpen = false;
        state.modalMode = "";
        state.editRow = {};
      });
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)

      let allRule = document.getElementById("app").attributes["allRule"].value;
      let parsedArray = JSON.parse(allRule);
      console.log("parsedArray", parsedArray);

      if (!rowDataRule.value) rowDataRule.value = [];
      rowDataRule.value = parsedArray;
    });

    const cancelDelete = () => {
      state.deleteDialog = false;
    };
    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .delete(`/sdwan/deleteSdwanRule/${state.deletedRow.id}`)
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

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    return {
      close,
      overlayMessage,
      state,
      columnRules,
      overlayTemplate,
      rowDataRule,
      paginationLocalization,
      defaultColDef,
      actionCellRendererArea,
      openModalAdd,
      onGridReady,
      cancelDelete,
      confirmDelete,
    };
  },
};
</script>
<style>
.white-link {
  color: white;
  text-decoration: underline;
}
</style>