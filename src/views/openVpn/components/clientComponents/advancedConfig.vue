<template>
  <div class="mt-3">
    <h4 class="mt-6">Advanced Configuration</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>Verbosity level</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select label="Verbosity level"></v-select>
      </v-col>
    </v-row>
  </div>
  <div class="mt-2">
    <h4 class="mt-6">Remote server</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>Remote server at random</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Select remote server at random</label>
      </v-col>
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-3"
        :columnDefs="columnClient"
        :rowData="rowDataClient"
        :alwaysShowHorizontalScroll="false"
        :alwaysShowVarticalScroll="false"
        :gridOptions="gridOptions"
        style="width: 100%; height: 100%"
        @grid-ready="onGridReady"
      />
    </v-row>
    <v-row class="py-8">
      <v-col cols="12" class="mb-n6">
        <v-data-table :headers="headers" :items="items" class="elevation-1">
          <template v-slot:item.action="{ item }">
            <div class="flex">
              <v-btn small color="primary" @click="editItem(item)">
                <i class="far fa-edit"></i>
              </v-btn>
              <v-btn small color="error" @click="deleteItem(item)">
                <i class="fas fa-times"></i>
              </v-btn>
            </div>
          </template>
          <template v-slot:item.serverName="{ item }">
            <v-text-field
              v-model="item.serverName"
              outlined
              class="mt-8"
            ></v-text-field>
          </template>
          <template v-slot:item.protocolPort="{ item }">
            <v-text-field
              v-model="item.protocolPort"
              outlined
              class="mt-8"
            ></v-text-field>
          </template>
        </v-data-table>
      </v-col>
      <v-row class="flex py-3">
        <v-col cols="6"> </v-col>
        <v-col>
          <div class="mr-1 flex center">
            <v-btn class="mr-5" large rounded color="#213E9F">
              <span class="text-white c-o">Cancel</span>
            </v-btn>
            <v-btn large rounded color="#213E9F">
              <span class="text-white c-o">Save</span>
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-row>
  </div>
</template>

<script>

import { AgGridVue } from "ag-grid-vue3";
export default {
  components: {
    AgGridVue,
  },
  data() {
    return {
      columnClient: [
        { headerName: "Server Name", field: "server", minWidth: 150 },
        { headerName: "Protocole/port", field: "protocol", minWidth: 200 },
        {
          headerName: "Actions",
          minWidth: 150,
          editable: false,
          sortable: false,
          filter: false,
        },
      ],
      rowDataClient: [{ server: "test", protocol: "test2", price: 35000 }],
    };
  },
};
</script>
<style lang="scss">
@import "font-awesome/css/font-awesome.css";
@import "~@mdi/font/css/materialdesignicons.min.css";
</style>