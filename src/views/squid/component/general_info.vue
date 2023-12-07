<template>
  <div class="mt-6 ml-5" style="display: flex; flex-direction: column">
    <v-row>
      <v-col cols="6">
        <h4>General information</h4>
        <v-divider class="mt-2"></v-divider>

        <v-row class="mt-1">
          <v-col cols="4">
            <label>Enable</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.off" />
            <label class="ml-2">Off</label>
            <br />
            <input type="checkbox" v-model="state.on" />
            <label class="ml-2">On</label>
          </v-col>

          <v-col cols="4" class="mt-7">
            <label>Proxy port</label>
          </v-col>
          <v-col cols="5" class="mt-3">
            <v-text-field
              label="Proxy Port"
              v-model="state.proxyPort"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-col>

      <v-col cols="6">
        <h4>Squid authentification</h4>
        <v-divider class="mt-2"></v-divider>
        <v-row class="mt-1">
          <v-col cols="4">
            <label>Authentification</label>
          </v-col>
          <v-col cols="8" class="mb-n6">
            <input type="checkbox" v-model="state.enable" />
            <label class="ml-2">Enable</label>
          </v-col>

          <div style="overflow: hidden; flex-grow: 1">
            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              style="width: 100%"
              @grid-ready="onGridReady"
              :columnDefs="columnUser"
              :rowData="rowDataUser.value"
            />
          </div>
        </v-row>
        <v-row class="d-flex justify-end mt-5">
          <div>
            <VButton
              rounded
              outlined
              color="#213E9F"
              label-color="#ffffff"
              label="Add User"
              :isLarge="true"
              type="submit"
              class="ml-2"
              @click="openModalAddUser"
            />
          </div>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { reactive, ref } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VButton from "@/components/VButton.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
export default {
  components: {
    AgGridVue,
    VButton,
  },
  setup() {
    const state = reactive({
      off: false,
      on: false,
      proxyPort: "",
      enable: false,
    });
    const rowDataUser = reactive({});
    const gridApi = ref(null);

    const columnUser = [
      {
        headerName: "Username",
        field: "username",
        sortable: true,
        autoHeight: true,
        filter: true,
      },
      {
        headerName: "Actions",
        field: "action",
        sortable: true,
        filter: true,
      },
    ];

    const onGridReady = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataUser.value);
      } else {
        console.error("Grid API.");
      }
    };
    return {
      state,
      columnUser,
      rowDataUser,
      onGridReady,
    };
  },
};
</script>
