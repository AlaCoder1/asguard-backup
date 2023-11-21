<template>
  <div class="mt-3 ml-3 mr-3">
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
            @cell-clicked="cellWasClicked"
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
      <v-snackbar
        :timeout="2000"
        v-model="snackbar"
        location="bottom right"
        :color="color"
      >
        {{ textAlert }}
      </v-snackbar>
    </v-row>
  </div>
</template>

<script>
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";
import { inject } from "vue";
import CertStatusRenderVue from "./agGridCustomRender/CertStatusRenderVue.vue";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS

export default {
  name: "ListingOpenvpnComponent",
  components: {
    AgGridVue,
    VButton,
    CertStatusRenderVue,
  },
  setup() {
    const emitter = inject("emitter");
    const color = ref(null);
    const snackbar = ref(false);
    const textAlert = ref(false);

  
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
        field: "proto",
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
        field: "proto",
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

    // Obtain API from grid's onGridReady event
    const onGridReady = (params) => {
      gridApi.value = params.api;
    };

    // DefaultColDef sets props common to all Columns
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
          console.log("play", rowData);
          axios
            .post(`/openvpn/startServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              console.log("i", i.response.data.error);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
          break;
        case "edit":
          console.log("edit", rowData);
          emitter.emit("add-server");
          emitter.emit("edit-server", rowData);
          break;
        case "stop":
          console.log("stop", rowData);
          axios
            .delete(`/openvpn/stopServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              console.log("i", i.response.data.error);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
          break;
        case "restart":
          console.log("restart", rowData);
          axios
            .put(`/openvpn/restartServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              console.log("i", i.response.data.error);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });

          break;
        case "delete":
          console.log("delete", rowData);

          axios
            .delete(`/openvpn/deleteServerOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              console.log("i", i.response.data.error);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
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
          console.log("download", rowData);

          let id = rowData.id;
          let fileExtention = `${rowData.name}.ovpn`;

          const csrfToken = getCookie("csrftoken");
          axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

          axios
            .post(`/openvpn/exportClientOpenvpn/${id}`)
            .then((response) => {
              console.log("res", response.data.client);

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

              if (response.status == "201") {
                console.log("success");
              } else {
                console.log("error");
              }
            })
            .catch((i) => {
              console.log("i", i.response);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });

          break;
        case "editClient":
          console.log("edit", rowData);
          emitter.emit("add-client");
          setTimeout(() => {
            emitter.emit("edit-client", rowData);
          }, 1000);

          break;

        case "delete":
          console.log("delete", rowData);

          axios
            .delete(`/openvpn/deleteClientOpenvpn/${rowData.id}`)
            .then((response) => {
              snackbar.value = true;
              color.value = "success";
              textAlert.value = response.data.msg;

              setTimeout(() => {
                location.reload();
              }, 1000);
            })
            .catch((i) => {
              console.log("i", i.response.data.error);
              snackbar.value = true;
              color.value = "red";
              textAlert.value = i.response.data.error;
            });
          break;
        default:
          break;
      }
    };

    function formatedServer(data) {
      let eGui = document.createElement("div");
      let mapedServer = data.data.server_remote
        .map((i) => {
          return i.host + ` : ${i.port}`;
        })
        .join("<br>");

      eGui.innerHTML = `
         ${mapedServer}
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
        console.log("parsedArrayClients", parsedArrayClients);

        rowDataClients.value = parsedArrayClients;
      } catch (error) {
        console.error("Error setting rowDataServers:", error);
      }
    });

    return {
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
      actionCellRendererClient,
      cellWasClicked: (event) => {
        // Example of consuming Grid Event
        console.log("cell was clicked", event);
      },
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      formatedServer,
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
