<template>
  <v-app id="inspire">
    <base-layout title="Dashboard" active-menu="home">
      <template #content>
        <div class="mr-3">
          <div
            class="certificats-management mt-6 ml-5"
            style="display: flex; flex-direction: column"
          >
            <h4>System information</h4>
            <v-divider></v-divider>
            <ag-grid-vue
              id="grid-wrapper"
              class="ag-theme-alpine mt-3"
              :columnDefs="columnAuthority"
              :rowData="rowDataAuthority"
              :enableColResize="false"
              style="width: 100%; height: 155px"
              :gridOptions="gridOptions"
            />
          </div>
          <div id="chart" class="mt-3 mr-2">
            <apexchart
              ref="apexChart"
              height="350"
              :options="chartOptions"
              :series="chartOptions.series"
            ></apexchart>
          </div>

          <div>
            <v-row class="mt-6 ml-2">
              <v-col cols="12">
                Services
                <v-divider></v-divider>
                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3"
                  :columnDefs="columnServices"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  :rowData="rowDataServices"
                  style="width: 100%; height: 100%"
                  :gridOptions="gridOptionsService"
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
                  :rowData="rowDataInterfaces"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  style="width: 100%; height: 100%"
                  :gridOptions="gridOptionsService"
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
                  :rowData="rowDataGateways"
                  :alwaysShowHorizontalScroll="false"
                  :alwaysShowVerticalScroll="false"
                  style="width: 100%; height: 100%"
                  :gridOptions="gridOptionsService"
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
import { AgGridVue } from "ag-grid-vue";
import ApexCharts from "vue-apexcharts";
import BaseLayout from "@/pages/layout.vue";
import GroupManagement from "@/pages/group-management.vue";
import NetworkServerManagement from "@/pages/network-server-management.vue";
import CertificatsManagement from "@/pages/certificats-management.vue";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    NetworkServerManagement,
    GroupManagement,
    CertificatsManagement,
    AgGridVue,
    apexchart: ApexCharts,
  },
  watch: {
    dataChart: {
      handler(newData) {
        this.uptime = newData;
      },
      immediate: true,
      deep: true,
    },
  },
  computed: {
    rowDataAuthority() {
      const currentDate = new Date();
      const currentTime = currentDate.toLocaleTimeString();
      let authority = [
        {
          nom: "Asguard",
          system_load: this.uptime.uptime,
          last_cong: currentTime,
          operating: this.uptime.current_date,
        },
      ];

      return authority;
    },
  },
  data() {
    return {
      socket: null,
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
      information: "",
      infoParser: "",
      data: [],
      columnAuthority: [
        { headerName: "Name", field: "nom", maxWidth: 100 },
        {
          headerName: "Version",
          cellRenderer: this.actionCellRenderer,
          minWidth: 50,
        },
        {
          headerName: "CPU type",
          cellRenderer: this.actionCpuType,
          minWidth: 100,
        },
        { headerName: "System load", field: "system_load", minWidth: 50 },
        {
          headerName: "Last configuration change",
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
      ],
      columnServices: [
        { headerName: "Service", field: "service", minWidth: 500 },
        { headerName: "Description", field: "description", minWidth: 500 },
        {
          headerName: "Actions",
          cellRenderer: this.actionCellRendererService,
        },
      ],
      rowDataServices: null,

      columnInterfaces: [
        { headerName: "Name", field: "name", minWidth: 150 },
        { headerName: "Speed and uplex", field: "speed_uplex", minWidth: 50 },
        { headerName: "Address", field: "address", minWidth: 150 },
      ],
      rowDataInterfaces: [],
      columnGateways: [
        { headerName: "Name", field: "name", minWidth: 150 },
        { headerName: "Address", field: "address", minWidth: 50 },
        { headerName: "Status", field: "status", minWidth: 150 },
      ],
      rowDataGateways: [],
      gridOptions: {
        rowHeight: 90,
      },
      gridOptionsService: {
        pagination: true,
        paginationPageSize: 5,
        rowSelection: "single",
      },
      dataChart: "",
      uptime: "",
      gateways: null,
      interfaces: [],
    };
  },
  methods: {
    initializeWebSocket() {
      this.socket = new WebSocket("wss://" + window.location.host + "/ws/data/"); // Replace with your WebSocket URL

      this.socket.onopen = () => {
        console.log("WebSocket connection opened.");
      };

      this.socket.onmessage = (event) => {
        if (this.socket.readyState === WebSocket.OPEN) {
          const data = JSON.parse(event.data);
          this.dataChart = data;

          const timestamp = new Date(data.timestamp * 1000).getTime();

          this.chartOptions.series[0].data.push([
            timestamp,
            data.cpu_percentage.toFixed(2),
          ]);
          this.chartOptions.series[1].data.push([
            timestamp,
            data.memory_percentage.toFixed(2),
          ]);

          const maxDataPoints = 10;
          if (this.chartOptions.series[0].data.length > maxDataPoints) {
            this.chartOptions.series[0].data.shift();
            this.chartOptions.series[1].data.shift();
          }

          this.$refs.apexChart.updateOptions({});
        } else {
          console.log(
            "WebSocket is not in the OPEN state. Unable to send a message."
          );
        }
      };

      this.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
    },
    actionCellRenderer() {
      let eGui = document.createElement("div");

      eGui.innerHTML = `Asguard V${this.infoParser.version_asguard}<br/> System V${this.infoParser.system_version}
        <br/>${this.infoParser.version_openssl}
        `;
      eGui.style.lineHeight = "2";

      return eGui;
    },
    actionCpuType() {
      const longString = this.infoParser.cpu_type;
      const chunks = longString.match(/.{1,20}/g);

      const resultWithBr = chunks.map((chunk) => chunk + "<br>").join("");

      let eGui = document.createElement("div");

      eGui.innerHTML = `${resultWithBr}
      `;
      eGui.style.lineHeight = "2";
      return eGui;
    },

    actionCellRendererService() {
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
    },
    setData() {
      const validJsonString = this.$root.$data.tab
        .replace(/'/g, '"')
        .replace(/True/g, "true")
        .replace(/False/g, "false")
        .replace(/None/g, "null");
      const parsedArray = JSON.parse(validJsonString);
      this.data = parsedArray;
    },
  },

  beforeMount: async function () {
    this.initializeWebSocket();
    this.information = this.$root.$data.tab;
    const info = JSON.parse(this.information);
    this.infoParser = info;

    let infoService = info.list_info_services.map((i) => {
      const element = JSON.parse(i);
      return {
        service: element.service_name,
        description: element.description,
      };
    });
    this.rowDataServices = infoService;
    this.gateways = this.$root.$data.gateways;

    const element = JSON.parse(this.gateways);

    let infoGateways = element.map((i) => {
      return {
        name: i?.gwname,
        address: i?.gwaddress,
        status: i?.gwstatus ?? "Online",
      };
    });
    this.rowDataGateways = infoGateways;

    this.interfaces = this.$root.$data.interfaces;

    let parsedArray = JSON.parse(this.interfaces);

    let infoInterfaces = parsedArray.map((element) => {
      return {
        name: element.name_interface,
        speed_uplex: element.speed_duplex,
        address: element.ip_address,
      };
    });
    this.rowDataInterfaces = infoInterfaces;
  },
};
</script>
