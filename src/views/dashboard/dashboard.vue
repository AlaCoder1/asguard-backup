<template>
  <v-app id="inspire">
    <base-layout :title="t('sideBar.dashboard')" active-menu="home">
      <template #content>
        <div class="mr-3">
          <v-overlay v-model="state.loading">
            <v-dialog
              v-model="state.isLoadingDialogue"
              :scrim="false"
              persistent
              width="auto"
            >
              <v-card color="#193286">
                <v-card-text>
                  {{ $t("requiredfield.attente") }}
                  <v-progress-linear
                    indeterminate
                    color="white"
                    class="mb-0"
                  ></v-progress-linear>
                </v-card-text>
              </v-card>
            </v-dialog>
          </v-overlay>
          <v-overlay v-model="state.viewModal">
            <v-dialog v-model="state.isviewModal" :scrim="false" width="auto">
              <v-card color="#193286" class="alert-box">
                <v-card-title class="img-containter">
                  <img
                    src="@/assets/images/view.png"
                    alt="logo"
                    class="img-view"
                    width="100"
                    height="100"
                /></v-card-title>
                <v-card-text>
                  {{ $t("profil.NoPermission") }}
                  <br />
                  {{ $t("profil.ContactAdmin") }}
                </v-card-text>

                <div class="mr-3 mb-5 d-flex justify-end">
                  <VButton
                    rounded
                    outlined
                    color="#ffffff"
                    label-color="#213E9F"
                    :label="$t('buttons.close')"
                    :isLarge="true"
                    @click="close"
                  />
                </div>
              </v-card>
            </v-dialog>
          </v-overlay>
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
              @grid-ready="onGridReadyInfo"
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
                  :pagination="true"
                  :paginationPageSize="4"
                  :localeText="paginationLocalization"
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
                  :pagination="true"
                  :paginationPageSize="4"
                  :localeText="paginationLocalization"
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
                  :pagination="true"
                  :paginationPageSize="4"
                  :localeText="paginationLocalization"
                  :overlayNoRowsTemplate="overlayTemplate"
                  style="width: 100%; height: 100%"
                />
              </v-col>
              <v-snackbar
                :timeout="2000"
                v-model="state.snackbar"
                location="bottom right"
                :color="state.color"
              >
                {{ state.textAlert }}
              </v-snackbar>
            </v-row>
          </div>
        </div>
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import { reactive, ref, onMounted, computed } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import VueApexCharts from "vue3-apexcharts";
import BaseLayout from "../../layouts/layout.vue";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "HomeComponent",
  components: {
    BaseLayout,
    AgGridVue,
    apexchart: VueApexCharts,
    VButton,
  },

  setup() {
    const { t } = useI18n();
    const overlayTemplate = ref("");
    const paginationLocalization = reactive({
      of: "/",
    });
    const state = reactive({
      isviewModal: false,
      viewModal: false,
      snackbar: false,
      color: "",
      textAlert: "",
      isLoadingDialogue: false,
      loading: false,
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
        yaxis: {
          min: 0,
          max: 100,
          labels: {
            formatter: function (value) {
              return value.toFixed(0) + "%";
            },
          },
          // title: {
          //   text: "Percentage (%)",
          // },
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
      {
        headerName: "Service",
        field: "service",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Description",
        field: "description",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: "Actions",
        width: 150,
        lockPosition: "right",
        cellClass: "locked-col",
        cellRenderer: actionCellRendererService,
      },
    ]);
    const columnInterfaces = ref([
      {
        headerName: name,
        field: "name_interface",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: speed,
        field: "speed_duplex",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      {
        headerName: address,
        field: "ip_address",
        width: 150,
        minWidth: 50,
      },
    ]);
    const columnGateways = ref([
      { headerName: name, field: "name", width: 90, minWidth: 50, flex: 1 },
      {
        headerName: address,
        field: "address",
        width: 90,
        minWidth: 50,
        flex: 1,
      },
      { headerName: status, field: "status", width: 150, minWidth: 50 },
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
    function actionCellRendererService(params) {
      let eGui = document.createElement("div");

      if (params.data.status_started) {
        eGui.innerHTML = `
         <button class="action-button stop" data-action="stop">
            <span class="mdi mdi-stop-circle fa-2x" style="color: red"></span>
          </button>
          <button class="action-button restart" data-action="restart">
            <span class="mdi mdi-reload fa-2x"></span>
          </button>

        `;
      } else if (!params.data.status_started) {
        eGui.innerHTML = `
          <button class="action-button start" data-action="start">
            <span class="mdi mdi-play-circle fa-2x" style="color: green"></span>
          </button>
          <button class="action-button restart" data-action="restart">
            <span class="mdi mdi-reload fa-2x"></span>
          </button>

        `;
      }

      eGui.querySelectorAll(".action-button").forEach((button) => {
        button.addEventListener("click", () => {
          const action = button.getAttribute("data-action");
          handleActionServer(action, params.node.data);
        });
      });

      return eGui;
    }
    const handleActionServer = (action, rowData, index) => {
      const user = user_privilege();
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      switch (action) {
        case "start":
          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;
            let payloadStart = {
              action: "start",
              service: rowData.service,
            };

            axios
              .put("/monitoring/action", payloadStart)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }

          break;
        case "restart":
          console.log("restart", rowData);
          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;
            let payloadRestart = {
              action: "restart",
              service: rowData.service,
            };
            axios
              .put("/monitoring/action", payloadRestart)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;
                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }
          break;
        case "stop":
          console.log("stop", rowData);
          if (user === "viewer") {
            console.log("View Mode");
            state.isviewModal = true;
            state.viewModal = true;
          } else {
            state.loading = true;
            state.isLoadingDialogue = true;

            let payloadStop = {
              action: "stop",
              service: rowData.service,
            };
            axios
              .put("/monitoring/action", payloadStop)
              .then((response) => {
                state.snackbar = true;
                state.color = "success";
                state.textAlert = response.data.msg;
                state.loading = false;
                state.isLoadingDialogue = false;

                setTimeout(() => {
                  location.reload();
                }, 1000);
              })
              .catch((i) => {
                state.loading = false;
                state.isLoadingDialogue = false;

                if (i.response.status === 500) {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = t("errors.errorServer");
                } else {
                  state.snackbar = true;
                  state.color = "red";
                  state.textAlert = i.response.data.msg;
                }
              });
          }
          break;

        default:
          break;
      }
    };

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
    const onGridReady = (params) => {
      gridApi.value = params.api;
    };
    const onGridReadyInfo = (params) => {
      gridApi.value = params.api;
      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
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

    onMounted(async () => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
        localStorage.setItem("lastSubscription", lastSubscription);

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
          status_enabled: element.status_enabled,
          status_started: element.status_started,
          status_install: element.status_install,
        };
      });
      rowDataServices.value = infoService;
      console.log("rowDataServices.value", rowDataServices.value);

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
      rowDataInterfaces.value = parsedArray;
    });

    return {
      t,
      overlayTemplate,
      NoRow,
      state,
      close,
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
      paginationLocalization,
      apexChart,
      gridOptions,
      actionCellRenderer,
      onGridReady,
      onGridReadyInfo,
      columnInterfaces,
      initializeWebSocket,
      actionCellRendererService,
    };
  },
};
</script>
<style>
/* .alert-box {
  margin-top: 20px;
  padding: 20px;
  background-color: #e3f2fd;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.alert-box p {
  margin-bottom: 10px;
  font-weight: bold;
} */
.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}
.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>
