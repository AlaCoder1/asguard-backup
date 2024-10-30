<template>
   <v-overlay v-model="state.viewModal">
    <v-dialog v-model="state.isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img src="@/assets/images/view.png" alt="logo" class="img-view" width="100" height="100" /></v-card-title>
          <v-card-text v-html="overlayMessage">
          </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton rounded outlined color="#ffffff" label-color="#213E9F" :label="$t('buttons.close')" :isLarge="true"
            @click="close" />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <div class="mt-3">
    <v-row class="ml-1 mb-0 d-flex justify-start">
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
      </v-col>
      <v-col cols="3">
        <v-select
          :label="$t('clamaV.time')"
          density="compact"
          v-model="state.date"
          item-title="name"
          item-value="time_value"
          return-object
          :items="state.dateList"
        ></v-select>
        <p class="error-feedback mb-5" v-if="v$.date.$errors.length">
          {{ v$.date.$errors?.[0].$message }}
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
    <v-row>
      <v-col>
        <div class="ml-3 mr-3">
          <v-row class="mb-5">
            <MonitoringCards :lasObj="state.lasObj" />
          </v-row>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-card class="ml-3" hover>
          <v-card-title>
            {{ $t("monitoringVPN.Availablity") }}
          </v-card-title>
          <v-card-item>
            <apexchart
              class="mb-5"
              ref="chartOptionsAvailability"
              height="350"
              :options="state.chartOptionsAvailability"
              :series="state.chartOptionsAvailability.series"
            ></apexchart>
          </v-card-item>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card class="ml-3" hover>
          <v-card-title>
            {{ $t("monitoringVPN.OUTtrafficVPN") }}
          </v-card-title>
          <v-card-item>
            <apexchart
              class="mb-5"
              ref="chartOptionOutTraffic"
              height="350"
              :options="state.chartOptionOutTraffic"
              :series="state.chartOptionOutTraffic.series"
            ></apexchart>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-card class="ml-3" hover>
          <v-card-title>
            {{ $t("monitoringVPN.PacketReceivedVPN") }}
          </v-card-title>
          <v-card-item>
            <apexchart
              class="mb-5"
              ref="chartOptionPacketReceived"
              height="350"
              :options="state.chartOptionPacketReceived"
              :series="state.chartOptionPacketReceived.series"
            ></apexchart>
          </v-card-item>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card class="ml-3" hover>
          <v-card-title>
            {{ $t("monitoringVPN.PacketSentVPN") }}
          </v-card-title>
          <v-card-item>
            <apexchart
              class="mb-5"
              ref="chartOptionPacketSent"
              height="350"
              :options="state.chartOptionPacketSent"
              :series="state.chartOptionPacketSent.series"
            ></apexchart>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>
    <br />
    <br />
    <br />
  </div>
</template>

<script>
import useValidate from "@vuelidate/core";
import { required, helpers } from "@vuelidate/validators";
import { getCookie } from "@/mixins/csrftoken.js";
import axios from "axios";
import { reactive, onMounted, ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import MonitoringCards from "./cards.vue";
import { AgGridVue } from "ag-grid-vue3";
import Apexchart from "vue3-apexcharts";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "MonotoringOpenvpnComponent",
  components: {
    AgGridVue,
    MonitoringCards,
    Apexchart,
    VButton,
  },

  setup() {
    const { t } = useI18n();

    const availability = computed(() => {
      return t("monitoringVPN.Availablity");
    });
    const overlayMessage = computed(() => {
this.current_user= user_privilege('Ipsec') 
  if (this.current_user === "viewer" || this.current_user === "default") {
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  } else if (!this.last_Subscription.includes("VPN IPSEC")) {
    return `${t("firewall.msg_subscription")}<br /><a href="/asguard/subscription/" class="white-link"> ${t("firewall.sub_page")}</a>`;
  } else{
    return ` ${t("profil.NoPermission")} <br /> ${t("profil.ContactAdmin")}`;
  }
});
    const OutTraffic = computed(() => {
      return t("monitoringVPN.OutTraffic");
    });
    const PacketReceived = computed(() => {
      return t("monitoringVPN.PacketReceived");
    });
    const PacketSent = computed(() => {
      return t("monitoringVPN.PacketSent");
    });
    const state = reactive({
      current_user :"",
      last_Subscription :[],
      isviewModal: false,
      viewModal: false,
      server: "",
      lasObj: null,
      date: "",
      snackbar: false,
      color: "",
      textAlert: "",
      serverList: [],
      dateList: [
        { name: "LAST 24 HOURS", time_value: "24", time_unit: "hours" },
      ],
      socket: null,
      dataChart: null,
      chartOptionsAvailability: {
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
            name: availability,
            data: [],
          },
        ],
      },
      chartOptionOutTraffic: {
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
            name: OutTraffic,
            data: [],
          },
        ],
      },
      chartOptionPacketReceived: {
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
            name: PacketReceived,
            data: [],
          },
        ],
      },
      chartOptionPacketSent: {
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
            name: PacketSent,
            data: [],
          },
        ],
      },
    });

    const getAllListServer = () => {
      const serversAttribute =
        document.getElementById("app").attributes["servers"].value;

      const parsedArray = JSON.parse(serversAttribute);
      let servers = parsedArray.map((i) => {
        return {
          id: i.id,
          name: i.conn_name,
        };
      });

      state.serverList = servers;
    };

    onMounted(async () => {
      const lastSubscription =
        document.getElementById("app").attributes["last_subscription"].value;
      let parsedArraySubscription = JSON.parse(lastSubscription);
      last_Subscription.value = parsedArraySubscription;
      console.log("last_Subscription",last_Subscription.value)
      getAllListServer();
    });
    const error = computed(() => {
      return t("errors.valueRequired");
    });

    const rules = computed(() => {
      return {
        date: { required: helpers.withMessage(error, required) },
        server: { required: helpers.withMessage(error, required) },
      };
    });

    const v$ = useValidate(rules, state);

    const serve = async () => {
      const user = user_privilege('Ipsec');
      if (user && user !== 'viewer' && user !=='default' && this.last_Subscription.includes("VPN IPSEC")) {
      const result = await v$.value.$validate();

      if (result) {
        setTimeout(() => {
          initializeWebSocket();
        }, 1000);
      }
    } else {
            state.isviewModal = true;
            state.viewModal = true;
          };
    };

    const apexChart = ref(null);
    const chartTraffic = ref(null);
    const chartOptionsAvailability = ref(null);
    const chartOptionOutTraffic = ref(null);
    const chartOptionPacketReceived = ref(null);
    const chartOptionPacketSent = ref(null);

    const initializeWebSocket = () => {
      state.socket = new WebSocket(
        "wss://" + window.location.host + "/ws/ipsecmonitoring/"
      );

      state.socket.onopen = () => {
        console.log("WebSocket connection opened.");
        state.socket.send(
          JSON.stringify({
            id: state.server.id,
            time: {
              time_value: +state.date.time_value,
              time_unit: state.date.time_unit,
            },
          })
        );
      };
      state.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const lastIndex = data.length - 1;
        const lastObject = data[lastIndex];
        state.lasObj = lastObject;

        state.chartOptionsAvailability.series[0].data = [];
        state.chartOptionOutTraffic.series[0].data = [];

        state.chartOptionPacketReceived.series[0].data = [];

        state.chartOptionPacketSent.series[0].data = [];

        data.forEach((element) => {
          state.chartOptionsAvailability.series[0].data.push({
            x: new Date(element.timestamp * 1000).getTime(),
            y: element.availability_bytes,
          });
          state.chartOptionOutTraffic.series[0].data.push({
            x: new Date(element.timestamp * 1000).getTime(),
            y: element.total_bytes,
          });
          state.chartOptionPacketReceived.series[0].data.push({
            x: new Date(element.timestamp * 1000).getTime(),
            y: element.bytes_in,
          });
          state.chartOptionPacketSent.series[0].data.push({
            x: new Date(element.timestamp * 1000).getTime(),
            y: element.bytes_out,
          });
        });
        const maxDataPoints = 10;
        if (
          state.chartOptionsAvailability.series[0].data.length > maxDataPoints
        ) {
          state.chartOptionsAvailability.series[0].data.shift();
        }

        chartOptionsAvailability.value.updateOptions({});

        if (state.chartOptionOutTraffic.series[0].data.length > maxDataPoints) {
          state.chartOptionOutTraffic.series[0].data.shift();
        }

        chartOptionOutTraffic.value.updateOptions({});
        if (
          state.chartOptionPacketReceived.series[0].data.length > maxDataPoints
        ) {
          state.chartOptionPacketReceived.series[0].data.shift();
        }

        chartOptionPacketReceived.value.updateOptions({});
        if (state.chartOptionPacketSent.series[0].data.length > maxDataPoints) {
          state.chartOptionPacketSent.series[0].data.shift();
        }

        chartOptionPacketSent.value.updateOptions({});
      };

      state.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
    };
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };

    return {
      close,
      v$,
      overlayMessage,
      state,
      apexChart,
      chartOptionsAvailability,
      chartOptionOutTraffic,
      chartOptionPacketReceived,
      chartOptionPacketSent,
      chartTraffic,
      serve,
    };
  },
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

.white-link {
  color: white;
  text-decoration: underline;
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
