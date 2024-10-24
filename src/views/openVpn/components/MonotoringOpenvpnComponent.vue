<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
        <v-card-text>
          You do not have the required permissions to perform any
          actions.<br />
          Please contact the administrator if you believe this is an
          error.
        </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" label="Close" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
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
    <v-row class="ml-1 mb-3 d-flex justify-start">
      <v-col cols="3">
        <v-select
          :label="$t('Clientsopenvpn.Server')"
          density="compact"
          v-model="state.server"
          item-title="name"
          item-value="id"
          return-object
          :items="state.serverList"
        ></v-select>
        <p class="error-feedback mb-5" v-if="v$.server.$errors.length">
          {{ v$.server.$errors?.[0].$message }}
        </p>
        <!-- @update:modelValue="serve" -->
      </v-col>
      <v-col cols="3">
        <v-text-field
          :append-inner-icon="state.show1 ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="state.show1 = !state.show1"
          :type="state.show1 ? 'text' : 'password'"
          density="compact"
          :label="$t('form.password')"
          v-model="state.password"
        ></v-text-field>
        <p class="error-feedback mb-5" v-if="v$.password.$errors.length">
          {{ v$.password.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="3" style="">
        <v-btn
          style="
            display: flex;
            justify-content: center;
            align-items: center;
            height: 38px;
            width: 60%;
          "
          label-color="#213E9F"
          color="indigo-darken-3"
          @click="serve"
        >
          <span class="text-white pr-3 pl-3">{{ $t("buttons.Load") }}</span>
        </v-btn>
      </v-col>
    </v-row>

    <v-row class="mt-n10 ">
      <v-col cols="12">
        <div class="ml-3 mr-3">
          <v-row class="mt-0 mb-5">
            <monitoringCards :dataChart="state.dataChart" />
          </v-row>
          <v-row class="mt-2 mb-15">
            <v-col cols="6">
              <v-card hover>
                <v-card-title>
                  {{ $t("Clientsopenvpn.Trafficdistribution") }}
                </v-card-title>
                <v-card-item>
                  <apexchart
                    ref="chartTraffic"
                    :options="state.chartOptionsPie"
                    :series="state.chartOptionsPie.series"
                  ></apexchart>
                </v-card-item>
              </v-card>
            </v-col>
            <v-col cols="6">
              <div class="ml-3 mr-3" >
                <ag-grid-vue
                  id="grid-wrapper"
                  domLayout="autoHeight"
                  class="ag-theme-alpine mt-3 ag-header-cell-text"
                  :columnDefs="columns"
                  :rowData="rowData.value"
                  :overlayNoRowsTemplate="overlayTemplate"
                  @grid-ready="onGridReady"
                  :localeText="paginationLocalization"
                  :pagination="true"
                  :paginationPageSize="7"
                />
              </div>
            </v-col>
            <v-col cols="6">
              <v-card hover>
                <v-card-title>
                  {{ $t("Clientsopenvpn.TopTraffic") }}
                </v-card-title>
                <v-card-item>
                  <apexchart
                    ref="apexChart"
                    id="top-trafic-chart"
                    type="bar"
                    height="350"
                    :options="state.chartOptions"
                    :series="state.chartOptions.series"
                  />
                </v-card-item>
              </v-card>
            </v-col>

            <v-col cols="6">
              <v-card hover>
                <v-card-title>
                  {{ $t("Clientsopenvpn.Top2ClientNetworkActivity") }}
                </v-card-title>
                <v-card-item>
                  <apexchart
                    ref="apexChartNetwork"
                    height="350"
                    :options="state.chartOptionsNetwork"
                    :series="state.chartOptionsNetwork.series"
                  ></apexchart>
                </v-card-item>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>

    <v-snackbar
      :timeout="2000"
      v-model="state.snackbar"
      location="bottom right"
      :color="state.color"
    >
      {{ state.textAlert }}
    </v-snackbar>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";
import useValidate from "@vuelidate/core";
import { required, helpers } from "@vuelidate/validators";
import { reactive, onMounted, ref, computed } from "vue";
import monitoringCards from "./monitoringCards.vue";
import { AgGridVue } from "ag-grid-vue3";
import VueApexCharts from "vue3-apexcharts";
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "MonotoringOpenvpnComponent",
  components: {
    AgGridVue,
    monitoringCards,
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
      show1: false,
      isviewModal: false,
      viewModal: false,
      server: "",
      snackbar: false,
      color: "",
      textAlert: "",
      password: "",
      serverList: [],
      modal: false,
      socket: null,
      dataChart: null,
      chartOptions: {
        chart: {
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
        series: [10, 20, 30, 40, 50],
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
    const specificform = computed(() => {
      return t("errors.formsepcificpassword");
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });
    const rules = computed(() => {
      return {
        password: {
          required: helpers.withMessage(error, required),
          isValidPassword: helpers.withMessage(
            specificform,

            helpers.regex(
              /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])[A-Za-z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{20,}$/
            )
          ),
        },
        server: { required: helpers.withMessage(error, required) },
      };
    });

    const v$ = useValidate(rules, state);
    var usedColors = [];

    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    const getRandomColor = () => {
      var letters = "0123456789ABCDEF";
      var color;
      do {
        color = "#";
        for (var i = 0; i < 6; i++) {
          color += letters[Math.floor(Math.random() * 16)];
        }
      } while (usedColors.includes(color));
      usedColors.push(color);
      return color;
    };
    const Usernam = computed(() => {
      return t("form.username");
    });
    const LoginTime = computed(() => {
      return t("form.LoginTime");
    });
    const country = computed(() => {
      return t("certificat.country");
    });
    const address = computed(() => {
      return t("agGrid.address");
    });

    const columns = ref([
      {
        headerName: Usernam,
        field: "username",
        width: 90,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: LoginTime,
        field: "login_time",
        width: 90,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: country,
        field: "location",
        width: 300,
        minWidth: 150,
        flex: 1,
        autoHeight: true,
        resizable: true,
      },
      {
        headerName: address,
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
    overlayTemplate.value = `
      <span aria-live="polite" aria-atomic="true">  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 88" width=50px >
      <path
        d="m86.69 32.608-8.65-4.868 8.65-4.868a1 1 0 0 0 0-1.744l-32-18a1.002 1.002 0 0 0-.98 0L44 8.593l-9.71-5.465a1.002 1.002 0 0 0-.98 0l-32 18a1 1 0 0 0 0 1.744l8.65 4.868-8.65 4.868a1 1 0 0 0 0 1.744l9.69 5.45V66a1.001 1.001 0 0 0 .51.872l32 18A1.203 1.203 0 0 0 44 85a1.232 1.232 0 0 0 .49-.128l32-18A1.001 1.001 0 0 0 77 66V39.802l9.69-5.45a1 1 0 0 0 0-1.744zM43 44.03 14.04 27.74 43 11.45zm2-32.58 28.96 16.29L45 44.03zm9.2-6.303L84.161 22 76 26.593 46.04 9.74zm-20.4 0 8.16 4.593-22.47 12.64L12 26.593 3.839 22zM12 28.887 41.96 45.74l-8.16 4.593L3.839 33.48zm1 12.042 20.31 11.423a1 1 0 0 0 .98 0L43 47.45v34.84L13 65.415zm62 0v24.486L45 82.29V47.45l8.71 4.901a1 1 0 0 0 .98 0zm-20.8 9.404-8.16-4.593L76 28.888l8.161 4.592z"
        style="fill: #E8EAF6"
        data-name="Unbox"
      />
     </svg></span>`;
    const onGridReady = (params) => {
      gridApi.value = params.api;

      if (gridApi.value) {
        gridApi.value.setRowData(rowData.value);
      } else {
        console.error("Grid API.");
      }
    };

    const serve = async () => {
      const result = await v$.value.$validate();
      const user = user_privilege('Openvpn');
      if (user && user !== 'viewer') {

      if (result) {
        if (state.server) {
          state.modal = false;
          setTimeout(() => {
            initializeWebSocket();
          }, 1000);
        }
      }
    } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
    };

    const cancel = () => {
      state.modal = false;
    };

    const apexChart = ref(null);
    const chartTraffic = ref(null);
    const apexChartNetwork = ref(null);

    const initializeWebSocket = () => {
      state.socket = new WebSocket(
        "wss://" + window.location.host + "/ws/vpnmonitoring/"
      );

      state.socket.onopen = () => {
        console.log("WebSocket connection opened.");
        state.socket.send(
          JSON.stringify({
            id: state.server.id,
            password: state.password,
          })
        );
      };
      state.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // console.log("dataaa", data);

        if (typeof data === "object") {
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

          const timestamp = new Date(
            data.top_network.timestamp * 1000
          ).getTime();

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
        } else if (typeof data === "string") {
          state.snackbar = true;
          state.color = "red";
          state.textAlert = data;
        }
      };

      state.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
    };

    return {
      state,
      close,
      v$,
      overlayTemplate,
      apexChart,
      apexChartNetwork,
      chartTraffic,
      rowData,
      columns,
      gridApi,
      paginationLocalization,
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
