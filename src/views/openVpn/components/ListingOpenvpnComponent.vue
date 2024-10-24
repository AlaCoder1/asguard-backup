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
  <div class="mt-3 ml-3 mr-3">
    <v-overlay v-model="loading">
      <v-dialog v-model="isLoadingDialogue" :scrim="false" persistent width="auto">
        <v-card color="#193286">
          <v-card-text>
            {{ $t("requiredfield.attente") }}
            <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("Clientsopenvpn.ListServers") }}</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
            :columnDefs="columnServers" :rowData="rowDataServers.value" :defaultColDef="defaultColDef"
            :rowGroupPanelShow="rowGroupPanelShow" :overlayNoRowsTemplate="overlayTemplate" @grid-ready="onGridReady"
            :pagination="true" :paginationPageSize="4" :localeText="paginationLocalization" />
          <div class="d-flex justify-end mt-3">
            <VButton rounded outlined color="#213E9F" label-color="#ffffff" :label="$t('button.addServer')"
              :isLarge="true" type="submit" class="ml-2" @click="addServer" />
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h4>{{ $t("Clientsopenvpn.ListClients") }}</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          <ag-grid-vue id="grid-wrapper" domLayout="autoHeight" class="ag-theme-alpine mt-3" style="width: 100%"
            :columnDefs="columnClients" :rowData="rowDataClients.value" :defaultColDef="defaultColDef"
            :rowGroupPanelShow="rowGroupPanelShow" :overlayNoRowsTemplate="overlayTemplate" :pagination="true"
            :paginationPageSize="4" :localeText="paginationLocalization" />
          <div class="d-flex justify-end mt-3 mb-10">
            <VButton rounded outlined color="#213E9F" label-color="#ffffff" :label="$t('button.addClient')"
              :isLarge="true" type="submit" class="ml-2" @click="addClient" />
          </div>
          <br />
        </div>
      </v-col>

      <v-dialog v-model="dialogDelete" max-width="500px">
        <v-card>
          <v-card-title class="headline">{{
            $t("delete.DeleteConfirmation")
            }}</v-card-title>
          <v-card-text>{{ $t("delete.Delete") }}
            {{ isDeletedType === "server" ? $t("agGrid.server") : "Client" }}
            ?</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialogDelete = false">{{
              $t("buttons.cancel")
              }}</v-btn>
            <v-btn color="blue darken-1" text @click="confirmDelete">{{
              $t("buttons.delete")
              }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-snackbar :timeout="2000" v-model="snackbar" location="bottom right" :color="color">
        {{ textAlert }}
      </v-snackbar>
    </v-row>

    <ModalCreateClient :isOpen="state.isModalOpen" :editRow="state.editRow" />
    <ModalListClient :isOpenListView="state.isModalOpenListView" :editRow="state.editRow" />
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref, computed } from "vue";
import { inject } from "vue";
import CertStatusRenderVue from "./agGridCustomRender/CertStatusRenderVue.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalCreateClient from "@/components/modals/ModalCreateClient.vue";
import ModalListClient from "@/components/modals/ModalListClient.vue";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "ListingOpenvpnComponent",
  components: {
    AgGridVue,
    VButton,
    CertStatusRenderVue,
    ModalCreateClient,
    ModalListClient,
  },
  setup() {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const emitter = inject("emitter");
    const overlayTemplate = ref("");
    const dialogDelete = ref(false);
    const isDeletedType = ref("");
    const rowID = ref("");
    const deleteRow = ref(null);
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);
    const loading = ref(false);
    const isLoadingDialogue = ref(false);

    const state = reactive({
      isviewModal: false,
      viewModal: false,
      isModalOpen: false,
      isModalOpenListView: false,
      editRow: {},
    });
    const ServerNam = computed(() => {
      return t("PageGeneral.ServerName");
    });
    const Protocol = computed(() => {
      return t("Clientsopenvpn.Protocol/Port");
    });
    const Protocol1 = computed(() => {
      return t("Clientsopenvpn.Protocol/Port");
    });
    const NetworkTunnel = computed(() => {
      return t("Clientsopenvpn.NetworkTunnel");
    });
    const CertificatStatus = computed(() => {
      return t("Clientsopenvpn.CertificatStatus");
    });
    const CertificatStatus1 = computed(() => {
      return t("Clientsopenvpn.CertificatStatus");
    });
    const Clientname = computed(() => {
      return t("openvpn.Clientname");
    });

    const server = computed(() => {
      return t("Clientsopenvpn.Server");
    });

    const columnServers = ref([
      {
        headerName: ServerNam,
        field: "name",
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
        sortable: true,
        filter: true,
        checkboxSelection: true,
      },
      {
        headerName: Protocol,
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
        cellRenderer: formatedProtocServer,
        sortable: true,
        filter: true,
      },
      {
        headerName: NetworkTunnel,
        field: "ipv4_tunnel_network",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
      },
      {
        headerName: "Description",
        field: "description",
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
      },
      {
        headerName: CertificatStatus,
        field: "cert_status",
        sortable: true,
        filter: true,
        cellRendererSelector: function (params) {
          const cert_status = {
            component: "CertStatusRenderVue",
            params: params.data.cert_status,
          };
          return cert_status;
        },
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRenderer,
        width: 200,
        field: "action",
        minWidth: 150,
        sortable: true,
        filter: true,
        autoHeight: true,
      },
    ]);
    const columnClients = ref([
      {
        headerName: Clientname,
        field: "name",
        sortable: true,
        autoHeight: true,
        filter: true,
        checkboxSelection: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: Protocol1,
        cellRenderer: formatedProtocClient,
        sortable: true,
        filter: true,
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: server,
        autoHeight: true,
        cellRenderer: formatedServer,
        sortable: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        sortable: true,
        autoHeight: true,
        filter: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: CertificatStatus1,
        field: "cert_status",
        sortable: true,
        filter: true,
        cellRendererSelector: function (params) {
          const cert_status = {
            component: "CertStatusRenderVue",
            params: params.data.cert_status,
          };
          return cert_status;
        },
        width: 90,
        minWidth: 50,
        flex: 1,
        autoHeight: true,
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRendererClient,
        width: 200,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
        autoHeight: true,
      },
    ]);
    const rowDataServers = reactive({});
    const rowDataClients = reactive({});
    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
    };
    const defaultColDef = {
      sortable: true,
      filter: true,
      // flex: 1,
    };

    const rowGroupPanelShow = ref("always");
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
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

    function actionCellRenderer(params) {
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
        if (
          rowDataServers.value[params.node.rowIndex].server_status === false
        ) {
          eGui.innerHTML = `
        
        <button
          id="account"
          class="action-button account"
          data-action="account" title="Client">
             <i class="mdi mdi-account" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button 
          class="action-button show "  
          data-action="show">
          <i class="mdi mdi-eye" style="color: #086eae;font-size: 20px;"></i>
          </button>
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
        } else {
          eGui.innerHTML = `

          <button
          id="account"
          class="action-button account"
          data-action="account" title="Client">
             <i class="mdi mdi-account" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button 
          class="action-button show "  
          data-action="show">
          <i class="mdi mdi-eye" style="color: #086eae;font-size: 20px;"></i>
          </button>
          <button
          id="restart"
          class="action-button restart"
          data-action="restart" title=${t("interface.restart")}>
             <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
          </button>
        
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
          handleActionServer(action, params.node.data);
        });
      });
      return eGui;
    }
    const handleActionServer = (action, rowData, index) => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const user = user_privilege('Openvpn');

      switch (action) {
        case "play":
        if (user && user !== 'viewer' && user!=='default') {

          loading.value = true;
          isLoadingDialogue.value = true;
          axios
            .post(`/openvpn/startServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;
              loading.value = false;
              isLoadingDialogue.value = false;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
              loading.value = false;
              isLoadingDialogue.value = false;
              setTimeout(() => {
                location.reload();
              }, 1000);
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "edit":
        if (user && user !== 'viewer' && user!=='default') {

          emitter.emit("add-server");
          setTimeout(() => {
            emitter.emit("edit-server", rowData);
          }, 1000);
          break;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
        case "stop":
        if (user && user !== 'viewer' && user!=='default') {

          loading.value = true;
          isLoadingDialogue.value = true;
          axios
            .delete(`/openvpn/stopServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;
              loading.value = false;
              isLoadingDialogue.value = false;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
              loading.value = false;
              isLoadingDialogue.value = false;
              setTimeout(() => {
                location.reload();
              }, 1000);
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "restart":
        if (user && user !== 'viewer' && user!=='default') {

          loading.value = true;
          isLoadingDialogue.value = true;
          axios
            .put(`/openvpn/restartServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;
              loading.value = false;
              isLoadingDialogue.value = false;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
              loading.value = false;
              isLoadingDialogue.value = false;
              setTimeout(() => {
                location.reload();
              }, 1000);
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "delete":
        if (user && user !== 'viewer' && user!=='default') {

          isDeletedType.value = "server";
          deleteRow.value = rowData;
          dialogDelete.value = true;
          rowID.value = rowData.id;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;

        case "account":
        if (user && user !== 'viewer' && user!=='default') {

          state.isModalOpen = true;
          state.editRow = rowData;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        case "show":
        if (user && user !== 'viewer' && user!=='default') {

          state.isModalOpenListView = true;
          state.editRow = rowData;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;

        default:
          break;
      }
    };

    function actionCellRendererClient(params) {
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
          class="action-button download"
          data-action="download">
             <i class="mdi mdi-download-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button editClient"
          data-action="editClient">
             <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button delete"
          data-action="delete">
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
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      const user = user_privilege('Openvpn');

      switch (action) {
        case "download":
        if (user && user !== 'viewer' && user!=='default') {

          let id = rowData.id;
          let fileExtention = `${rowData.name}.ovpn`;

          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .post(`/openvpn/exportClientOpenvpn/${id}`)
            .then((response) => {
              const text = response.data.client;
              const blob = new Blob([text], {
                type: "application/x-x509-ca-cert",
              });

              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.style.display = "none";
              a.href = url;
              a.download = fileExtention;

              document.body.appendChild(a);
              a.click();

              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);
            })
            .catch((i) => {
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
          } else {
            state.isviewModal = true;
            state.viewModal = true;
          };

          break;
        case "editClient":
        if (user && user !== 'viewer' && user!=='default') {

          emitter.emit("add-client");
          setTimeout(() => {
            emitter.emit("edit-client", rowData);
          }, 1000);
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;

        case "delete":
        if (user && user !== 'viewer' && user!=='default') {

          isDeletedType.value = "client";
          deleteRow.value = rowData;
          dialogDelete.value = true;
          rowID.value = rowData.id;
        } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
          break;
        default:
          break;
      }
    };

    function formatedServer(data) {
      let eGui = document.createElement("div");
      let mapedServer = data.data.server_remote
        .map((i) => {
          return i.host;
        })
        .join("<br>");

      eGui.innerHTML = `
         ${mapedServer}
        `;
      eGui.style.lineHeight = "3";

      return eGui;
    }
    function formatedProtocServer(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
         ${data.data.proto} / ${data.data.port}
        `;
      eGui.style.lineHeight = "3";

      return eGui;
    }
    function formatedProtocClient(data) {
      let mapedServer = data.data.server_remote
        .map((i) => {
          return `${i.port}`;
        })
        .join("<br>");

      let eGui = document.createElement("div");

      eGui.innerHTML = `
         ${data.data.proto} / ${mapedServer}
        `;
      eGui.style.lineHeight = "3";

      return eGui;
    }

    const publishServer = () => { };

    const addServer = () => {
      const user = user_privilege('Openvpn');
      if (user && user !== 'viewer' && user!=='default') {
        emitter.emit("add-server");
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
    };

    const publishClient = () => { };

    const addClient = () => {
      const user = user_privilege('Openvpn');
      if (user && user !== 'viewer' && user!=='default') {
        emitter.emit("add-client");
      } else {
        state.isviewModal = true;
        state.viewModal = true;
      };
    };

    onMounted(async () => {
      emitter.on("closeModalClient", () => {
        state.isModalOpenListView = false;
      });
      overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
      emitter.on("closeModalCreateClient", () => {
        state.isModalOpen = false;
      });

      try {
        const serversAttribute =
          document.getElementById("app").attributes["servers"].value;
        const validJsonString = serversAttribute
          .replace(/'/g, '"')
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        const parsedArray = JSON.parse(validJsonString);

        // const processedData = parsedArray.map((server) => ({
        //   id: server.id,
        //   name: server.name,
        //   proto: server.proto,
        //   ipv4_tunnel_network: server.ipv4_tunnel_network,
        //   description: server.description,
        //   cert_status: server.cert_status,
        //   server_status: server.server_status,
        // }));

        rowDataServers.value = parsedArray;

        const clientsAttribute =
          document.getElementById("app").attributes["clients"].value;
        const validJsonStringClients = clientsAttribute
          .replace(/'/g, '"')
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        const parsedArrayClients = JSON.parse(validJsonStringClients);

        rowDataClients.value = parsedArrayClients;
      } catch (error) {
        console.error("Error setting rowDataServers:", error);
      }
    });

    const confirmDelete = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (isDeletedType.value === "server") {
        axios
          .delete(`/openvpn/deleteServerOpenvpn/${rowID.value}`)
          .then((response) => {
            snackbar.value = true;
            color.value = "success";
            textAlert.value = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            snackbar.value = true;
            color.value = "red";
            textAlert.value = i.response.data.error;
          });
      } else if (isDeletedType.value === "client") {
        axios
          .delete(`/openvpn/deleteClientOpenvpn/${rowID.value}`)
          .then((response) => {
            snackbar.value = true;
            color.value = "success";
            textAlert.value = response.data.msg;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            snackbar.value = true;
            color.value = "red";
            textAlert.value = i.response.data.error;
          });
      }
    };

    return {
      state,
      deleteRow,
      rowID,
      isDeletedType,
      dialogDelete,
      overlayTemplate,
      loading,
      isLoadingDialogue,
      columnServers,
      columnClients,
      rowDataServers,
      rowDataClients,
      defaultColDef,
      rowGroupPanelShow,
      paginationLocalization,
      emitter,
      color,
      snackbar,
      textAlert,
      confirmDelete,
      actionCellRendererClient,
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      formatedServer,
      formatedProtocServer,
      formatedProtocClient,
      actionCellRenderer,
      onGridReady,
      close,
      publishServer,
      addServer,
      publishClient,
      addClient,
      getCookie,
    };
  },
};
</script>

<style lang="scss"></style>
