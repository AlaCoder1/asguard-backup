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
            :columnDefs="columnServers"
            :rowData="rowDataServers"
            style="width: 100%"
            :autoGroupColumnDef="autoGroupColumnDef"
            :rowGroupPanelShow="rowGroupPanelShow"
          />
          <div class="d-flex justify-end mt-3">
            <v-btn
              large
              rounded
              outlined
              color="primary"
              class="mr-3"
              @click="publishServer"
              >Publish Server</v-btn
            >
            <v-btn
              large
              rounded
              outlined
              color="primary"
              class="mr-3"
              @click="addServer"
              >Add Server</v-btn
            >
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
            <v-btn
              large
              rounded
              outlined
              color="primary"
              class="mr-3"
              @click="publishClient"
              >Publish Client</v-btn
            >
            <v-btn
              large
              rounded
              outlined
              color="primary"
              class="mr-3"
              @click="addClient"
              >Add Client</v-btn
            >
          </div>
          <br />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";

export default {
  name: "ListingOpenvpnComponent",
  components: {
    AgGridVue,
  },
  props: {},
  data() {
    return {
      columnServers: [
        {
          headerName: "Server Name",
          field: "serverNname",
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
          headerName: "Network Tunnel",
          field: "networkTunnel",
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
          headerName: "Published",
          field: "published",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Action",
          cellRenderer: this.actionCellRenderer,
          minWidth: 150,
          field: "action",
          sortable: true,
          filter: true,
        },
      ],
      rowDataServers: [],
      columnClients: [
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
        { headerName: "Server", field: "server", sortable: true, filter: true },
        {
          headerName: "Description",
          field: "description",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Published",
          field: "published",
          sortable: true,
          filter: true,
        },
        {
          headerName: "Action",
          cellRenderer: this.actionCellRenderer,
          minWidth: 150,
          field: "action",
          sortable: true,
          filter: true,
        },
      ],
      rowDataClients: [],
    };
  },
  created() {
    this.autoGroupColumnDef = {
      headerName: "Server Name",
      field: "serverNname",
      minWidth: 300,
      cellRenderer: "agGroupCellRenderer",
      cellRendererParams: {
        checkbox: true,
      },
    };
    this.rowGroupPanelShow = "always";
  },
  computed: {},
  methods: {
    publishServer() {
      console.log("publishServer");
    },
    addServer() {
      console.log("addServer");
    },
    publishClient() {
      console.log("publishClient");
    },
    addClient() {
      console.log("addClient");
    },
  },
  mounted: async function () {
    console.log("beforeUnmount");
    console.log(this.rowDataServers);
    console.log(
      "document.getElementById('app')",
      document.getElementById("app")
    );

    this.rowDataServers =
      document.getElementById("app").attributes["servers"].value;
    let validJsonString = this.rowDataServers
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray = JSON.parse(validJsonString);
    this.rowDataServers = parsedArray;
    this.rowDataClients =
      document.getElementById("app").attributes["clients"].value;
    let validJsonString2 = this.rowDataClients
      .replace(/'/g, '"')
      .replace(/True/g, "true")
      .replace(/False/g, "false")
      .replace(/None/g, "null");
    let parsedArray2 = JSON.parse(validJsonString2);
    this.rowDataClients = parsedArray2;
  },
};
</script>

<style lang="scss">
@import "~ag-grid-community/dist/styles/ag-grid.css";
@import "~ag-grid-community/dist/styles/ag-theme-alpine.css";
</style>
