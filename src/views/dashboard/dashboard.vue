<template>
  <v-app id="inspire">
    <base-layout title="Dashboard" active-menu="home">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>System informations</h4>
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
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :rowData="rowDataServices.value"
                  style="width: 100%; height: 100%"
                  @grid-ready="onGridReadyService"
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
                  :rowData="rowDataInterfaces.value"
                  @grid-ready="onGridReadyInterfaces"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
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
                  :rowData="rowDataGateways.value"
                  @grid-ready="onGridReadyGateways"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
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
import { reactive, ref, onMounted } from "vue";
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
            name: "CPU Percentage (%)",
            data: [],
          },
          {
            name: "Memory Percentage (%)",
            data: [],
          },
        ],
      },
    });

    const columns = ref([
      { headerName: "Name", field: "nom", width: 150 },
      {
        headerName: "Version",
        autoHeight: true,
        cellRenderer: actionCellRenderer,
      },
      {
        headerName: "CPU type",
        autoHeight: true,
        cellRenderer: actionCpuType,
      },
      { headerName: "System load", field: "system_load", minWidth: 50 },
      {
        headerName: "L.Conf Change",
        field: "last_cong",
        maxWidth: 200,
      },
      {
        headerName: "Operating time",
        field: "operating",
        minWidth: 230,
        editable: false,
        sortable: false,
        filter: false,
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
      { headerName: "Name", field: "name", minWidth: 150 },
      { headerName: "Speed and uplex", field: "speed_uplex", minWidth: 50 },
      { headerName: "Address", field: "address", minWidth: 150 },
    ]);
    const columnGateways = ref([
      { headerName: "Name", field: "name", minWidth: 150 },
      { headerName: "Address", field: "address", minWidth: 50 },
      { headerName: "Status", field: "status", minWidth: 150 },
    ]);

    const rowData = reactive([]);
    const rowDataServices = reactive([]);
    const rowDataInterfaces = reactive([]);
    const rowDataGateways = reactive([]);

    const gridApi = ref(null);
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
      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("Grid API.");
      }
    };
    const onGridReadyService = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      gridApi.value.sizeColumnsToFit();

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataServices.value);
      } else {
        console.error("Grid API.");
      }
    };
    const defaultColDef = {
      sortable: true,
      filter: true,
      flex: 1,
    };

    const initializeWebSocket = () => {
      state.socket = new WebSocket(
        "ws://" + window.location.host + "/ws/data/"
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

    const onGridReadyInterfaces = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      gridApi.value.sizeColumnsToFit();

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataInterfaces.value);
      } else {
        console.error("Grid API.");
      }
    };
    const onGridReadyGateways = (params) => {
      gridApi.value = params.api;

      gridApi.value.sizeColumnsToFit();
      window.addEventListener("resize", function () {
        setTimeout(function () {
          gridApi.value.sizeColumnsToFit();
        });
      });

      gridApi.value.sizeColumnsToFit();

      if (gridApi.value) {
        gridApi.value.setRowData(rowDataGateways.value);
      } else {
        console.error("Grid API.");
      }
    };

    onMounted(async () => {
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
      state,
      columns,
      rowData,
      defaultColDef,
      columnsService,
      rowDataInterfaces,
      onGridReadyService,
      onGridReadyInterfaces,
      rowDataGateways,
      rowDataServices,
      columnGateways,
      actionCpuType,
      gridApi,
      apexChart,
      gridOptions,
      actionCellRenderer,
      onGridReadyGateways,
      onGridReady,
      columnInterfaces,
      initializeWebSocket,
      actionCellRendererService,
      getCookie,
    };
  },
};
</script>
