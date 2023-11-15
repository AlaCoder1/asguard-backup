<template>
  <div class="mt-3 ml-3 mr-3">
    <v-row>
      <v-col cols="12">
        <h4>List Servers</h4>
        <v-divider></v-divider>
        <div style="display: flex; flex-direction: column">
          {{ rowDataServers }}
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3"
            :columnDefs="columnServers"
            :rowData="rowDataServers"
            style="width: 100%"
            :autoGroupColumnDef="autoGroupColumnDef"
            :rowGroupPanelShow="rowGroupPanelShow"
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
            :columnDefs="columnClients"
            :rowData="rowDataClients"
            style="width: 100%"
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
    </v-row>
  </div>
</template>

<script>
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, ref } from "vue";

export default {
  name: "ListingOpenvpnComponent",
  components: {
    AgGridVue,
    VButton,
  },
  setup() {
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
        field: "published",
        sortable: true,
        filter: true,
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
        field: "clientName",
        sortable: true,
        filter: true,
        checkboxSelection: true,
      },
      {
        headerName: "Protocole / Port",
        field: "protocolPort",
        sortable: true,
        filter: true,
      },
      {
        headerName: "Server",
        field: "server",
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
        field: "published",
        sortable: true,
        filter: true,
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

    const rowDataServers = ref([ { "name": "server1", "proto": "udp", "ipv4_tunnel_network": "10.8.1.0/24", "description": "server openvpn" } ]
);
    const rowDataClients = ref([]);

    const autoGroupColumnDef = {
      headerName: "Server Name",
      field: "serverNname",
      minWidth: 300,
      cellRenderer: "agGroupCellRenderer",
      cellRendererParams: {
        checkbox: true,
      },
    };
    const rowGroupPanelShow = ref("always");

    const actionCellRenderer = (params) => {
      return `<div><button @click="yourFunction(${params.data.id})">Action</button></div>`;
    };

    const publishServer = () => {
      console.log("publishServer");
    };

    const addServer = (emitter) => {
      emitter.emit("add-server");
    };

    const publishClient = () => {
      console.log("publishClient");
    };

    const addClient = (emitter) => {
      console.log("addClient");
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

        const processedData = parsedArray.map((server) => ({
          name: server.name,
          proto: server.proto,
          ipv4_tunnel_network: server.ipv4_tunnel_network,
          description: server.description,
          published: server.published,
        }));

        rowDataServers.value = processedData;

        const clientsAttribute =
          document.getElementById("app").attributes["clients"].value;
        const validJsonStringClients = clientsAttribute
          .replace(/'/g, '"')
          .replace(/True/g, "true")
          .replace(/False/g, "false")
          .replace(/None/g, "null");
        const parsedArrayClients = JSON.parse(validJsonStringClients);

        const processedDataClients = parsedArrayClients.map((client) => ({
          clientName: client.name,
          protocolPort: client.protocolPort,
          server: client.server,
          description: client.description,
          published: client.published,
        }));

        rowDataClients.value = processedDataClients;
      } catch (error) {
        console.error("Error setting rowDataServers:", error);
      }
    });

    return {
      columnServers,
      columnClients,
      rowDataServers,
      rowDataClients,
      autoGroupColumnDef,
      rowGroupPanelShow,
      publishServer,
      addServer,
      publishClient,
      addClient,
    };
  },
};
</script>

<style lang="scss">

</style>
