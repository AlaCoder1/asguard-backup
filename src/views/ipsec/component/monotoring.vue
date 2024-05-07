<template>
  <div class="mt-3">
    <v-row>
      <v-col>
        <div class="ml-3 mr-3">
          <v-row class="mt-2 mb-5">
            <MonitoringCards />
          </v-row>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">
              {{$t('monitoringVPN.currentstate')}}
            </div>
          </v-card-item>
          <v-card-text class="content-style">
            <v-row>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#E7F4E4"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    1F <br />{{$t('monitoringVPN.Switch')}}
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#FCE3A8"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    {{$t('monitoringVPN.Router')}} <br />
                    03
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#E7F4E4"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    2F <br />
                    {{$t('monitoringVPN.Switch')}}
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#E7F4E4"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    {{$t('monitoringVPN.Printer')}} <br />03
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#FCE3A8"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    3F <br />
                    {{$t('monitoringVPN.Switch')}}
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#F9DEDE"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    {{$t('monitoringVPN.Printer')}} <br />
                    2F
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col>
                <v-card
                  height="60px"
                  width="80px"
                  hover
                  color="#FCE3A8"
                  class="monitor-status-card"
                >
                  <v-card-text class="content-style">
                    {{$t('monitoringVPN.Printer')}} <br />
                    3F
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.Availablity')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <Apexchart
              width="500"
              type="area"
              :options="chartOptions"
              :series="series"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.OUTtrafficVPN')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <Apexchart
              width="500"
              type="area"
              :options="chartOptions"
              :series="series"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.CPU&MemoryVPN')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <Apexchart
              width="500"
              type="area"
              :options="chartOptions"
              :series="series"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.PacketReceivedVPN')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <Apexchart
              width="500"
              type="area"
              :options="chartOptions"
              :series="series"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-card class="mx-auto ml-3" height=" 400px" hover>
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.PacketSentVPN')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <Apexchart
              width="500"
              type="area"
              :options="chartOptions"
              :series="series"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <br />
    <br />
    <br />
  </div>
</template>

<script>
import MonitoringCards from "./cards.vue";
import { AgGridVue } from "ag-grid-vue3";
import Apexchart from "vue3-apexcharts";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

export default {
  name: "MonotoringOpenvpnComponent",
  components: {
    AgGridVue,
    MonitoringCards,
    Apexchart,
  },
  props: {},
  data() {
    return {
      series: [
        {
          name: "server",
          data: [31, 40, 28, 51, 42, 109, 100],
        },
      ],
      chartOptions: {
        chart: {
          height: 350,
          type: "area",
          zoom: {
            enabled: true,
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: "straight",
        },
        title: {
          text: "",
          align: "left",
        },
        grid: {
          row: {
            colors: ["#f3f3f3", "transparent"], // takes an array which will be repeated on columns
            opacity: 0.5,
          },
        },
        xaxis: {
          categories: [
            "05:00 PM",
            "06:00 PM",
            "07:00 PM",
            "08:00 PM",
            "09:00 PM",
            "10:00 PM",
            "11:00 PM",
          ],
        },
        fill: {
          colors: ["#213E9F"],
          type: "gradient",
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.7,
            opacityTo: 0.9,
            stops: [0, 90, 100],
          },
        },
      },
    };
  },
  computed: {},
};
</script>

<style scoped>
.subTitle {
  position: relative;
  left: 30px;
  display: flex;
  flex-wrap: wrap;
}

.content-style {
  color: #042439;
  font-family: Nunito;
  font-size: 13px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}

.content-style-light {
  color: #042439;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  justify-content: center;
}

.title-card {
  color: #042439;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 800;
  line-height: normal;
}

.center-item {
  margin: auto;
  width: 50%;
  text-align: center;
}

.monitor-status-card {
  width: 60.016px;
  height: 60.016px;
  flex-shrink: 0;
}

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
