<template>
  <div>
    <v-row>
      <v-col cols="8">
        <div id="map" class="mt-6" style="height: 70vh"></div>
      </v-col>
      <v-col cols="4">
        <h4>{{ $t("Waf.attacks") }}</h4>
        <v-divider class="mb-1"></v-divider>
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-1"
            style="width: 100%"
            @grid-ready="onGridReadyAttacks"
            :columnDefs="columnAttacks"
            :rowData="rowDataAttacks.value"
            :pagination="true"
            :paginationPageSize="4"
            :overlayNoRowsTemplate="overlayTemplate"
            :localeText="paginationLocalization"
          />
        </div>
        <h4 class="mt-3">{{ $t("Waf.topCountries") }}</h4>
        <v-divider class="mb-1"></v-divider>
        <div style="overflow: hidden; flex-grow: 1">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-1"
            style="width: 100%"
            @grid-ready="onGridReadyCountry"
            :columnDefs="columnCountry"
            :rowData="rowDataCountry.value"
            :pagination="true"
            :paginationPageSize="4"
            :overlayNoRowsTemplate="overlayTemplate"
            :localeText="paginationLocalization"
          />
        </div>
      </v-col>
    </v-row>

    <h4 class="mt-3">{{ $t("Waf.blockedRequests") }}</h4>
    <v-divider class="mb-1"></v-divider>
    <div class="mb-10" style="overflow: hidden; flex-grow: 1">
      <ag-grid-vue
        id="grid-wrapper"
        domLayout="autoHeight"
        class="ag-theme-alpine mt-1"
        style="width: 100%"
        @grid-ready="onGridReady"
        :columnDefs="columnRules"
        :rowData="rowDataRules.value"
        :pagination="true"
        :paginationPageSize="4"
        :overlayNoRowsTemplate="overlayTemplate"
        :localeText="paginationLocalization"
      />
    </div>
  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import * as L from "leaflet";
import { useI18n } from "vue-i18n";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { reactive, ref, computed, onMounted, inject } from "vue";

export default {
  name: "Rules",
  components: {
    AgGridVue,
  },
  setup() {
    const { t } = useI18n();
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({});

    const Country = computed(() => {
      return t("Waf.country");
    });
    const Attacks = computed(() => {
      return t("Waf.attacks");
    });

    const violation = computed(() => {
      return t("Waf.violation");
    });
    const countOfRecord = computed(() => {
      return t("Waf.countOfRecord");
    });
    const timestamp = computed(() => {
      return t("Waf.timestamp");
    });
    const method = computed(() => {
      return t("Waf.method");
    });

    const columnAttacks = ref([
      {
        headerName: violation,
        field: "violation",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: countOfRecord,
        field: "countOfRecord",
        autoHeight: true,
      },
    ]);

    const columnRules = ref([
      {
        headerName: Country,
        field: "country",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: timestamp,
        field: "timestamp",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },

      {
        headerName: violation,
        field: "violation",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "source",
        field: "source",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: method,
        field: "method",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "message",
        field: "message",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "URL",
        field: "URL",
        autoHeight: true,
        width: 150,
      },
    ]);

    const columnCountry = ref([
      {
        headerName: Country,
        field: "country",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: Attacks,
        field: "attacks",
        autoHeight: true,
        width: 150,
      },
    ]);
    const rowDataRules = reactive({});
    const rowDataAttacks = reactive({});
    const rowDataCountry = reactive({});
    const gridApi = ref(null);
    const overlayTemplate = ref("");

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataRules.value);
      } else {
        console.error("Grid API.");
      }
    };
    const onGridReadyAttacks = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataAttacks.value);
      } else {
        console.error("Grid API.");
      }
    };
    const onGridReadyCountry = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataCountry.value);
      } else {
        console.error("Grid API.");
      }
    };
    onMounted(() => {
      overlayTemplate.value = `
        <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
        <path
          d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
          style="fill: #E8EAF6"
          data-name="Unbox"
        />
       </svg></span>`;

      setTimeout(() => {
        const map = L.map("map").setView([48, 2], 6);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(map);
        let century21icon = L.icon({
          iconUrl:
            "https://img.icons8.com/?size=100&id=uvp0RebVme9d&format=png&color=000000",
          iconSize: [30, 30],
        });

        const locations = [
          { lat: 51.505, lng: -0.09, name: "souhail 1" },
          { lat: 52.505, lng: -0.19, name: "souhail 2" },
          { lat: 48, lng: -0.19, name: "souhail 3" },
          { lat: 70, lng: -0.19, name: "souhail 4" },
        ];

        locations.forEach((loc, idx) => {
          const marker = L.marker([loc.lat, loc.lng], {
            draggable: false,
            icon: century21icon,
          }).bindPopup(`${loc.name}`);
          marker.addTo(map);

          map.setView([locations[0].lat, locations[0].lng], 4);
        });
      }, 1000);
    });

    return {
      state,
      onGridReady,
      onGridReadyAttacks,
      onGridReadyCountry,
      columnRules,
      rowDataRules,
      columnCountry,
      rowDataCountry,
      columnAttacks,
      rowDataAttacks,
      overlayTemplate,
      paginationLocalization,
    };
  },
};
</script>
<style>
.leaflet-control-attribution {
  display: none;
}
</style>
