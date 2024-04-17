<template>
  <div class="mt-3">
    <!-- <v-dialog v-model="state.modal" persistent class="mx-auto" width="450">
      <v-card color="#193286" class="ml-16 mr-16 mx-auto">
        <v-card-text>
          <v-select
            label="Choose Server"
            v-model="state.server"
            item-title="name"
            item-value="id"
            return-object
            :items="state.serverList"
          ></v-select>
          <div class="d-flex justify-center">
            <v-btn
              class="mr-4"
              large
              rounded
              outlined
              label-color="#000"
              @click="serve"
              color="#fff-darken-3"
              :rounded="true"
              variant="flat"
            >
              <span color="#000" class="pr-3 pl-3">Serve</span>
            </v-btn>
            <v-btn
              large
              rounded
              outlined
              label-color="#000"
              @click="cancel"
              color="#fff-darken-3"
              :rounded="true"
              variant="flat"
            >
              <span color="#000" class="pr-3 pl-3">Cancel</span>
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog> -->
    <!-- <div class="d-flex justify-end mr-1 mt-0" v-if="!state.modal">
      <i
        class="mdi mdi-server-network"
        style="color: #213e9f; font-size: 30px; cursor: pointer; padding: 10px"
        @click="state.modal = true"
        title="Choose Server"
      ></i>
    </div> -->
    <v-row class="ml-1 d-flex justify-start">
      <v-col cols="2">
        <v-select
          label="Server"
          density="compact"
          v-model="state.server"
          item-title="name"
          item-value="id"
          return-object
          :items="state.serverList"
        ></v-select>
        <!-- @update:modelValue="serve" -->
      </v-col>
      <v-col cols="2">
        <v-text-field
          density="compact"
          label="Password"
          v-model="state.password"
        ></v-text-field>
      </v-col>
      <v-col cols="2" class="mt-2" style="">
        <v-btn
          rounded
          style="
            display: flex;
            justify-content: center;
            align-items: center;
            height: 30px;
            width: 60%;
          "
          label-color="#213E9F"
          color="indigo-darken-3"
          @click="serve"
        >
          <span class="text-white pr-3 pl-3">Load</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="mt-n10">
      <v-col cols="7">
        <div class="ml-3 mr-3">
          <v-row class="mt-0 mb-5">
            <monitoringCards :dataChart="state.dataChart" />
          </v-row>
          <v-row class="mt-2 mb-10">
            <v-col cols="6">
              <v-card-title> Top Traffic </v-card-title>
              <v-card-item>
                <apexchart
                  ref="apexChart"
                  id="top-trafic-chart"
                  type="bar"
                  :options="state.chartOptions"
                  :series="state.chartOptions.series"
                />
              </v-card-item>
            </v-col>
            <v-col cols="6">
              <v-card elevation="0">
                <v-card-title> Traffic distribution </v-card-title>
                <v-card-item style="margin-left: -19%">
                  <apexchart
                    ref="chartTraffic"
                    :options="state.chartOptionsPie"
                    :series="state.chartOptionsPie.series"
                  ></apexchart>
                </v-card-item>
              </v-card>
            </v-col>
            <!-- <v-col cols="6">
              <apexchart
                id="top-loggins-chart"
                type="bar"
                :options="chartOptions"
                :series="chartSeries"
              />
            </v-col> -->
            <v-col cols="12">
              <v-card-title> Top 2 Client Network Activity </v-card-title>
              <v-card-item>
                <apexchart
                  ref="apexChartNetwork"
                  height="350"
                  :options="state.chartOptionsNetwork"
                  :series="state.chartOptionsNetwork.series"
                ></apexchart>
              </v-card-item>
            </v-col>
          </v-row>
        </div>
      </v-col>
      <v-col cols="5">
        <div class="ml-3 mr-3">
          <ag-grid-vue
            id="grid-wrapper"
            domLayout="autoHeight"
            class="ag-theme-alpine mt-3 ag-header-cell-text"
            :columnDefs="columns"
            :rowData="rowData.value"
            @grid-ready="onGridReady"
          />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { reactive, onMounted, ref } from "vue";
import monitoringCards from "./monitoringCards.vue";
import { AgGridVue } from "ag-grid-vue3";
import VueApexCharts from "vue3-apexcharts";
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "MonotoringOpenvpnComponent",
  components: {
    AgGridVue,
    monitoringCards,
    apexchart: VueApexCharts,
  },
  setup() {
    const state = reactive({
      server: "",
      password: "",
      serverList: [],
      modal: false,
      socket: null,
      dataChart: null,
      chartOptions: {
        chart: {
          height: "250px",
          type: "bar",
          zoom: {
            enabled: false,
          },
        },
        colors: [],
        plotOptions: {
          bar: {
            columnWidth: "70%",
            distributed: true,
            width: "10%",
          },
        },
        legend: {
          enabled: true,
          position: "top",
        },
        xaxis: {
          categories: [],
        },

        series: [
          {
            name: [],
            data: [],
          },
        ],
      },
      chartOptionsNetwork: {
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

      chartOptionsPie: {
        series: [],
        chart: {
          width: 380,
          type: "donut",
        },
        labels: [],
        legend: {
          enabled: true,
          position: "top",
        },
        colors: [],
        responsive: [
          {
            breakpoint: 480,
            options: {
              chart: {
                width: 200,
              },

              // style: {
              //   fontSize: "10px",
              //   fontFamily: "DM sans",
              //   fontWeight: "light",
              // },
              legend: {
                enabled: true,
                // position: "top",
              },
            },
          },
        ],
      },
    });

    var usedColors = [];

    const getRandomColor = () => {
      var letters = "0123456789ABCDEF";
      var color;
      do {
        color = "#";
        for (var i = 0; i < 6; i++) {
          color += letters[Math.floor(Math.random() * 16)];
        }
      } while (usedColors.includes(color));
      return color;
    };

    const columns = ref([
      {
        headerName: "Username",
        field: "username",
        width: 90,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: "Login Time",
        field: "login_time",
        width: 90,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: "Country",
        field: "location",
        width: 300,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: "Address",
        field: "address",
        width: 300,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: "Rx",
        field: "rx",
        width: 300,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
        cellRenderer: actionCellRenderer,
      },
      {
        headerName: "Tx",
        field: "tx",
        width: 300,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
        cellRenderer: actionCellRendererSent,
      },
    ]);
    const rowData = reactive([]);
    const gridApi = ref(null);

    function actionCellRenderer(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `${Math.round(data.data.bytes_recv.capture_size)} ${
        data.data.bytes_recv.unit
      }`;

      return eGui;
    }
    function actionCellRendererSent(data) {
      let eGui = document.createElement("div");

      eGui.innerHTML = `${Math.round(data.data.bytes_sent.capture_size)} ${
        data.data.bytes_sent.unit
      }`;

      return eGui;
    }

    const getAllListServer = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios.get("/openvpn/getAllServerOpenvpn").then(
        (response) => {
          let servers = response.data.map((i) => {
            return {
              id: i.id,
              name: i.name,
            };
          });

          state.serverList = servers;
        },
        (error) => {
          console.log(error);
        }
      );
    };

    onMounted(async () => {
      getAllListServer();
    });

    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("Grid API.");
      }
    };

    const serve = () => {
      if (state.server) {
        state.modal = false;
        setTimeout(() => {
          initializeWebSocket();
        }, 1000);
      }
    };

    const cancel = () => {
      state.modal = false;
    };

    const apexChart = ref(null);
    const chartTraffic = ref(null);
    const apexChartNetwork = ref(null);

    const initializeWebSocket = () => {
      state.socket = new WebSocket(
        "ws://" + window.location.host + "/ws/vpnmonitoring/"
      );

      state.socket.onopen = () => {
        console.log("WebSocket connection opened.");
        state.socket.send(
          JSON.stringify({
            id: state.server.id,
          })
        );
      };
      state.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // console.log("dataaa", data);
        state.dataChart = data;

        rowData.value = [];

        rowData.value = data.info_clients;

        state.chartOptions.xaxis.categories = [];
        state.chartOptions.series[0].data = [];
        state.chartOptionsPie.labels = [];
        state.chartOptionsPie.series = [];

        data.info_clients.forEach((element) => {
          state.chartOptionsPie.labels.push(element.username);
          state.chartOptionsPie.series.push(
            parseFloat(element.traffic_distr.toFixed(2))
          );
        });

        data.top_traffic.forEach((element) => {
          state.chartOptions.series[0].data.push({
            x: element.username + `( ${element.total_traffic.unit} )`,
            y: Math.round(element.total_traffic.capture_size),
          });
        });

        for (var i = 0; i < state.chartOptionsPie.labels.length; i++) {
          state.chartOptionsPie.colors.push(getRandomColor());
        }
        for (var i = 0; i < state.chartOptions.series[0].data.length; i++) {
          state.chartOptions.colors.push(getRandomColor());
        }
        chartTraffic.value.updateOptions(state.chartOptionsPie);

        apexChart.value.updateOptions(state.chartOptions);

        const timestamp = new Date(data.top_network.timestamp * 1000).getTime();

        state.chartOptionsNetwork.series[0].name = "First Network";
        state.chartOptionsNetwork.series[1].name = "Second Network";

        if (data.top_network.first_network.capture_size) {
          state.chartOptionsNetwork.series[0].data.push([
            timestamp,
            data.top_network.first_network.capture_size.toFixed(2),
          ]);
        }

        if (
          data.top_network.second_network &&
          data.top_network.second_network.capture_size
        ) {
          state.chartOptionsNetwork.series[1].data.push([
            timestamp,
            data.top_network.second_network.capture_size.toFixed(2),
          ]);
        }

        const maxDataPoints = 10;
        if (state.chartOptionsNetwork.series[0].data.length > maxDataPoints) {
          state.chartOptionsNetwork.series[0].data.shift();
          state.chartOptionsNetwork.series[1].data.shift();
        }

        apexChartNetwork.value.updateOptions({});
      };

      state.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
    };

    return {
      state,
      apexChart,
      apexChartNetwork,
      chartTraffic,
      rowData,
      columns,
      gridApi,
      onGridReady,
      serve,
      cancel,
    };
  },
};
</script>

<style lang="scss" scoped>
#grid-wrapper {
  width: 100%;
}

.ag-header-cell-text {
  font-size: 10px;
}
body {
  font-family: "Open Sans", sans-serif;
}
</style>
