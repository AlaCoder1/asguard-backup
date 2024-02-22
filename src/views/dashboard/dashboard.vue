<template>
  <v-app id="inspire">
    <base-layout :title="t('sideBar.dashboard')" active-menu="home">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>{{ t("home.systemInformation") }}</h4>
            <v-divider></v-divider>

            <ag-grid-vue
              id="grid-wrapper"
              domLayout="autoHeight"
              class="ag-theme-alpine mt-3"
              :columnDefs="columns"
              :alwaysShowHorizontalScroll="false"
              :alwaysShowVarticalScroll="false"
              :defaultColDef="defaultColDef"
              :rowData="rowData.value"
              :overlayNoRowsTemplate="overlayTemplate"
              style="width: 100%; height: 100%"
              @grid-ready="onGridReady"
            />
          </div>
          <div id="chart" class="mt-3 mr-2">
            <apexchart
              ref="apexChart"
              height="350"
              :options="state.chartOptions"
              :series="state.chartOptions.series"
            ></apexchart>
          </div>

          <div style="margin-bottom: 150px">
            <v-row class="mt-6 ml-2">
              <v-col cols="12">
                Services
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnsService"
                  :defaultColDef="defaultColDef"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :rowData="rowDataServices.value"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                  @grid-ready="onGridReady"
                />
              </v-col>
            </v-row>
            <v-row class="mt-6 ml-2">
              <v-col cols="6">
                Interfaces
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnInterfaces"
                  :defaultColDef="defaultColDef"
                  :rowData="rowDataInterfaces.value"
                  @grid-ready="onGridReady"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                />
              </v-col>
              <v-col cols="6">
                Gateways
                <v-divider></v-divider>

                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnGateways"
                  :defaultColDef="defaultColDef"
                  :rowData="rowDataGateways.value"
                  @grid-ready="onGridReady"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                />
              </v-col>
            </v-row>
          </div>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { useI18n } from "vue-i18n";
import { reactive, ref, onMounted, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VueApexCharts from "vue3-apexcharts";
import BaseLayout from "../../layouts/layout.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    AgGridVue,
    apexchart: VueApexCharts,
  },

  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const state = reactive({
      information: null,
      infoParser: null,
      socket: null,
      dataChart: null,
      chartOptions: {
        chart: {
          type: "area",
          zoom: {
            enabled: false,
          },
        },
        xaxis: {
          type: "datetime",
        },

        series: [
          {
            name: "",
            data: [],
          },
          {
            name: "",
            data: [],
          },
        ],
      },
    });
    const name = computed(() => {
      return t("agGrid.name");
    });
    const cpuType = computed(() => {
      return t("agGrid.cpuType");
    });
    const systemLoad = computed(() => {
      return t("agGrid.systemLoad");
    });
    const lConfChange = computed(() => {
      return t("agGrid.lConfChange");
    });
    const operatingTime = computed(() => {
      return t("agGrid.operatingTime");
    });
    const speed = computed(() => {
      return t("agGrid.speedUplex");
    });
    const address = computed(() => {
      return t("agGrid.address");
    });
    const status = computed(() => {
      return t("agGrid.status");
    });
    const NoRow = computed(() => {
      return t("agGrid.noRowsToShow");
    });

    const columns = ref([
      { headerName: name, field: "nom", width: 90, minWidth: 50, flex: 1 },
      {
        headerName: "Version",
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        cellRenderer: actionCellRenderer,
      },
      {
        headerName: cpuType,
        autoHeight: true,
        width: 90,
        minWidth: 50,
        flex: 1,
        cellRenderer: actionCpuType,
      },
      {
        headerName: systemLoad,
        field: "system_load",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: lConfChange,
        field: "last_cong",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: operatingTime,
        field: "operating",
        editable: false,
        sortable: false,
        filter: false,
        width: 250,
      },
    ]);
    const columnsService = ref([
      { headerName: "Service", field: "service" },
      { headerName: "Description", field: "description" },
      {
        headerName: "Actions",
        lockPosition: "right",
        cellClass: "locked-col",
        cellRenderer: actionCellRendererService,
      },
    ]);
    const columnInterfaces = ref([
      { headerName: name, field: "name" },
      { headerName: speed, field: "speed_uplex" },
      { headerName: address, field: "address" },
    ]);
    const columnGateways = ref([
      { headerName: name, field: "name" },
      { headerName: address, field: "address" },
      { headerName: status, field: "status" },
    ]);
    const gridApi = ref(null);

    const rowData = reactive([]);
    const rowDataServices = reactive([]);
    const rowDataInterfaces = reactive([]);
    const rowDataGateways = reactive([]);

    const gridOptions = ref({
      pagination: true,
      paginationPageSize: 5,
      rowSelection: "single",
    });

    function actionCellRenderer() {
      let eGui = document.createElement("div");

      eGui.innerHTML = `Asguard V${state.infoParser.version_asguard}<br/> System V${state.infoParser.system_version}
          <br/>${state.infoParser.version_openssl}
          `;
      eGui.style.lineHeight = "2";

      return eGui;
    }
    const apexChart = ref(null);
    function actionCpuType() {
      const longString = state.infoParser.cpu_type;
      const chunks = longString.match(/.{1,20}/g);

      const resultWithBr = chunks.map((chunk) => chunk + "<br>").join("");

      let eGui = document.createElement("div");

      eGui.innerHTML = `${resultWithBr}
        `;
      eGui.style.lineHeight = "2";
      return eGui;
    }
    function actionCellRendererService() {
      let eGui = document.createElement("div");

      {
        eGui.innerHTML = `
          <button class="action-button edit" data-action="edit">
            <span class="mdi mdi-play-circle fa-2x" style="color: green"></span>
          </button>
          <button class="action-button delete" data-action="delete">
            <span class="mdi mdi-reload fa-2x"></span>
          </button>
          <button class="action-button delete" data-action="delete">
            <span class="mdi mdi-stop-circle fa-2x" style="color: red"></span>
          </button>
        `;
      }

      return eGui;
    }

    const onGridReady = (params) => {
      gridApi.value = params.api;
      // gridApi.value.sizeColumnsToFit();
      // window.addEventListener("resize", function () {
      //   setTimeout(function () {
      //     gridApi.value.sizeColumnsToFit();
      //   });
      // });

      // gridApi.value.sizeColumnsToFit();

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataServices.value);
      } else {
        console.error("Grid API.");
      }
    };
    const defaultColDef = {
      // flex: 2,
    };

    const initializeWebSocket = () => {
      state.socket = new WebSocket(
        "wss://" + window.location.host + "/ws/data/"
      );

      state.socket.onopen = () => {
        console.log("WebSocket connection opened.");
      };

      state.socket.onmessage = (event) => {
        if (state.socket.readyState === WebSocket.OPEN) {
          const data = JSON.parse(event.data);
          state.dataChart = data;

          const currentDate = new Date();
          const currentTime = currentDate.toLocaleTimeString();
          rowData.value = [
            {
              nom: "Asguard",
              system_load: data.uptime,
              last_cong: currentTime,
              operating: data.current_date,
            },
          ];
         

          const timestamp = new Date(data.timestamp * 1000).getTime();

          state.chartOptions.series[0].name = t("home.cpuPercentage");
          state.chartOptions.series[1].name = t("home.memoryPercentage");

          state.chartOptions.series[0].data.push([
            timestamp,
            data.cpu_percentage.toFixed(2),
          ]);
          state.chartOptions.series[1].data.push([
            timestamp,
            data.memory_percentage.toFixed(2),
          ]);

          const maxDataPoints = 10;
          if (state.chartOptions.series[0].data.length > maxDataPoints) {
            state.chartOptions.series[0].data.shift();
            state.chartOptions.series[1].data.shift();
          }

          apexChart.value.updateOptions({});
        } else {
          console.log(
            "WebSocket is not in the OPEN state. Unable to send a message."
          );
        }
      };

      state.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
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

    onMounted(async () => {
      overlayTemplate.value = `<span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
    </svg></span>`;
      let infoData =
        document.getElementById("app").attributes["informations"].value;
      let gateways =
        document.getElementById("app").attributes["gateways"].value;
      let interfaces =
        document.getElementById("app").attributes["interfaces"].value;

      initializeWebSocket();
      let information = infoData;
      const info = JSON.parse(information);
      state.infoParser = info;

      let infoService = info.list_info_services.map((i) => {
        const element = JSON.parse(i);
        return {
          service: element.service_name,
          description: element.description,
        };
      });
      rowDataServices.value = infoService;

      const element = JSON.parse(gateways);

      let infoGateways = element.map((i) => {
        return {
          name: i?.gwname,
          address: i?.gwaddress,
          status: i?.gwstatus ?? "Online",
        };
      });
      rowDataGateways.value = infoGateways;

      let parsedArray = JSON.parse(interfaces);

      let infoInterfaces = parsedArray.map((element) => {
        return {
          name: element.name_interface,
          speed_uplex: element.speed_duplex,
          address: element.ip_address,
        };
      });
      rowDataInterfaces.value = infoInterfaces;
    });

    return {
      t,
      overlayTemplate,
      NoRow,
      state,
      columns,
      rowData,
      defaultColDef,
      columnsService,
      rowDataInterfaces,
      rowDataGateways,
      rowDataServices,
      columnGateways,
      actionCpuType,
      gridApi,
      apexChart,
      gridOptions,
      actionCellRenderer,
      onGridReady,
      columnInterfaces,
      initializeWebSocket,
      actionCellRendererService,
      getCookie,
    };
  },
};
</script>
