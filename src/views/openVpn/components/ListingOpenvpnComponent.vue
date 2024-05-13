<template>
  <div class="mt-3 ml-3 mr-3">
    <v-overlay v-model="loading">
      <v-dialog
        v-model="isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <v-row>
      <v-col cols="12">
        <h4>List Servers</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            style="width: 100%"
            :columnDefs="columnServers"
            :rowData="rowDataServers.value"
            :defaultColDef="defaultColDef"
            :rowGroupPanelShow="rowGroupPanelShow"
            @grid-ready="onGridReady"
          />
          <div class="d-flex justify-end mt-3">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add Server"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="addServer"
            />
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h4>List Clients</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            style="width: 100%"
            :columnDefs="columnClients"
            :rowData="rowDataClients.value"
            :defaultColDef="defaultColDef"
            :rowGroupPanelShow="rowGroupPanelShow"
          />
          <div class="d-flex justify-end mt-3">
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add Client"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="addClient"
            />
          </div>
          <br />
        </div>
      </v-col>

      <v-dialog v-model="dialogDelete" max-width="500px">
        <v-card>
          <v-card-title class="headline">Delete Confirmation</v-card-title>
          <v-card-text
            >Are you sure you want to delete this
            {{ isDeletedType === "server" ? "Server" : "Client" }}
            ?</v-card-text
          >
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialogDelete = false"
              >Cancel</v-btn
            >
            <v-btn color="blue darken-1" text @click="confirmDelete"
              >Delete</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-snackbar
        :timeout="2000"
        v-model="snackbar"
        location="bottom right"
        :color="color"
      >
        {{ textAlert }}
      </v-snackbar>
    </v-row>

    <ModalCreateClient :isOpen="state.isModalOpen" :editRow="state.editRow" />
    <ModalListClient
      :isOpenListView="state.isModalOpenListView"
      :editRow="state.editRow"
    />
  </div>
</template>

<script>
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";
import { inject } from "vue";
import CertStatusRenderVue from "./agGridCustomRender/CertStatusRenderVue.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import ModalCreateClient from "@/components/modals/ModalCreateClient.vue";
import ModalListClient from "@/components/modals/ModalListClient.vue";

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
    const emitter = inject("emitter");
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
      isModalOpen: false,
      isModalOpenListView: false,
      editRow: {},
    });

    const columnServers = [
      {
        headerName: "Server Name",
        field: "name",

        sortable: true,
        filter: true,
        checkboxSelection: true,
      },
      {
        headerName: "Protocole / Port",

        cellRenderer: formatedProtocServer,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Network Tunnel",
        field: "ipv4_tunnel_network",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Description",
        field: "description",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Certificat status",
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
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRenderer,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];
    const columnClients = [
      {
        headerName: "Client Name",
        field: "name",
        sortable: true,
        autoHeight: true,
        filter: true,
        checkboxSelection: true,
      },
      {
        headerName: "Protocole / Port",
        cellRenderer: formatedProtocClient,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Server",
        autoHeight: true,
        cellRenderer: formatedServer,
        sortable: true,
        filter: true,
      },
      {
        headerName: "Description",
        field: "description",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Certificat status",
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
      },
      {
        headerName: "Action",
        cellRenderer: actionCellRendererClient,
        minWidth: 150,
        field: "action",
        sortable: true,
        filter: true,
      },
    ];
    const rowDataServers = reactive({});
    const rowDataClients = reactive({});
    const gridApi = ref(null);

    const onGridReady = (params) => {
      gridApi.value = params.api;
    };
    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };

    const rowGroupPanelShow = ref("always");

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
          data-action="play" title="Start Server">
             <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
          </button>

          <button
          class="action-button edit"
          data-action="edit" title="Edit Server">
             <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button delete"
          data-action="delete" title="Delete Server">
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
          data-action="restart" title="Restart Server">
             <i class="mdi mdi-play-circle" style="color: #4CAF50; font-size: 20px;"></i>
          </button>
        
       <button
          id="stop"
          class="action-button stop"
          data-action="stop" title="Stop Server">
             <i class="mdi mdi-stop-circle" style="color: #B00020; font-size: 20px;"></i>
          </button>

          <button
          class="action-button edit"
          data-action="edit" title="Edit Server">
             <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button delete"
          data-action="delete" title="Delete Server">
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
      switch (action) {
        case "play":
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
          break;
        case "edit":
          emitter.emit("add-server");
          emitter.emit("edit-server", rowData);
          break;
        case "stop":
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
          break;
        case "restart":
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

          break;
        case "delete":
          isDeletedType.value = "server";
          deleteRow.value = rowData;
          dialogDelete.value = true;
          rowID.value = rowData.id;

          break;

        case "account":
          state.isModalOpen = true;
          state.editRow = rowData;

          break;
        case "show":
          state.isModalOpenListView = true;
          state.editRow = rowData;

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
          data-action="download" title="download">
             <i class="mdi mdi-download-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button editClient"
          data-action="editClient" title="Edit Client">
             <i class="mdi mdi-pencil-circle" style="color: #086EAE; font-size: 20px;"></i>
          </button>
          <button
          class="action-button delete"
          data-action="delete" title="Delete Server">
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
      switch (action) {
        case "download":
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

          break;
        case "editClient":
          emitter.emit("add-client");
          setTimeout(() => {
            emitter.emit("edit-client", rowData);
          }, 1000);

          break;

        case "delete":
          isDeletedType.value = "client";
          deleteRow.value = rowData;
          dialogDelete.value = true;
          rowID.value = rowData.id;
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
      eGui.style.lineHeight = "2";

      return eGui;
    }
    function formatedProtocServer(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `
         ${data.data.proto} / ${data.data.port}
        `;
      eGui.style.lineHeight = "2";

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
      eGui.style.lineHeight = "2";

      return eGui;
    }

    const publishServer = () => {};

    const addServer = () => {
      emitter.emit("add-server");
    };

    const publishClient = () => {};

    const addClient = () => {
      emitter.emit("add-client");
    };

    onMounted(async () => {
      emitter.on("closeModalClient", () => {
        state.isModalOpenListView = false;
      });
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
      loading,
      isLoadingDialogue,
      columnServers,
      columnClients,
      rowDataServers,
      rowDataClients,
      defaultColDef,
      rowGroupPanelShow,
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
