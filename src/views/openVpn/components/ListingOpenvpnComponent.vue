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
            rowSelection="multiple"
            animateRows="true"
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
  </div>
</template>

<script>
import VButton from "@/components/VButton.vue";
import { AgGridVue } from "ag-grid-vue3";
import { onMounted, reactive, ref } from "vue";

import "ag-grid-community/styles/ag-grid.css"; // Core grid CSS, always needed
import "ag-grid-community/styles/ag-theme-alpine.css"; // Optional theme CSS

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
        headerName: "Published",
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
    const rowDataServers = reactive({});

    const gridApi = ref(null); // Optional - for accessing Grid's API

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

    // actionCellRenderer
    function actionCellRenderer(params) {
      const eDiv = document.createElement("div");
      eDiv.innerHTML = `
        <v-icon color="#213E9F" class="mr-2">mdi-pencil</v-icon>
        <v-icon color="#213E9F">mdi-delete</v-icon>
      `;
      return eDiv;
    }
    const publishServer = () => {
      console.log("publishServer");
    };

    const addServer = (emitter) => {
      emitter.emit("add-server");
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
      } catch (error) {
        console.error("Error setting rowDataServers:", error);
      }
    });

    return {
      columnServers,
      rowDataServers,
      defaultColDef,
      cellWasClicked: (event) => {
        // Example of consuming Grid Event
        console.log("cell was clicked", event);
      },
      deselectRows: () => {
        gridApi.value.deselectAll();
      },
      actionCellRenderer,
      onGridReady,
      publishServer,
      addServer,
    };
  },
};
</script>

<style lang="scss"></style>
