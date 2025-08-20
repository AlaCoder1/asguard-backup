<template>
  <v-container>
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            {{ $t("sdwan.pleaseWait") }}
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>

    <v-card class="pa-5 mt-2 mb-7">
      <v-card-title style="margin-left: -15px" class="text-h5">{{
        $t("doubleMask.services")
      }}</v-card-title>

      <v-switch
        v-model="enabled"
        label="Activer les doubles masques du filtre IP"
        color="#213E9F"
        @change="confirmSwitch"
        class="mt-3"
      ></v-switch>

      <v-dialog v-model="dialog" persistent max-width="410px">
        <v-card>
          <v-card-title>Confirmation</v-card-title>
          <v-card-text
            >{{ $t("doubleMask.ask") }}
            {{
              !tempValue
                ? $t("doubleMask.activate")
                : $t("doubleMask.deactivate")
            }}
            {{ $t("doubleMask.option") }} ?</v-card-text
          >
          <v-card-actions>
            <v-spacer></v-spacer>
            <!-- <v-btn color="red" @click="cancelSwitch">Non</v-btn>
            <v-btn color="green" @click="confirmEnable">Oui</v-btn> -->
            <v-btn
              rounded
              outlined
              color="#213E9F"
              :isLarge="true"
              variant="outlined"
              class="ml-2"
              @click="cancelSwitch"
            >
              <span style="color: #213e9f" class="pr-3 pl-3">{{ $t("doubleMask.no") }}</span>
            </v-btn>
            <v-btn
              rounded
              outlined
              style="background-color: #213e9f"
              color="#213E9F"
              label-color="#213E9F"
              :isLarge="true"
              class="ml-2"
              @click="confirmEnable"
            >
              <span class="text-white pr-3 pl-3"> {{ $t("doubleMask.yes") }}</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Save Button -->
      <!-- <v-btn color="blue" @click="saveSettings">Save</v-btn>
        -->
      <!-- <v-btn
        large
        rounded
        outlined
        label-color="#213E9F"
        type="submit"
        color="indigo-darken-3"
        :rounded="true"
        variant="flat"
        class="mt-3 btn-add"
      >
        <span class="text-white"> {{ $t("buttons.save") }}</span>
      </v-btn> -->

      <!-- Performance Info -->
      <v-alert variant="outlined" type="info" color="#213E9F">
        <div>{{ chartOptions.series[0] }}% {{ $t("doubleMask.performanceGain") }}</div>
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-title
              >{{ $t("doubleMask.initialRules") }} :
              {{ initialRules }}</v-expansion-panel-title
            >
          </v-expansion-panel>
          <v-expansion-panel>
            <v-expansion-panel-title
              >{{ $t("doubleMask.currentRules") }}  :
              {{ actualRules }}</v-expansion-panel-title
            >
          </v-expansion-panel>
        </v-expansion-panels>
      </v-alert>

      <!-- Compression Gauge -->
      <v-card class="mt-5">
        <div id="chart" class="mt-3 mr-2">
          <apexchart
            ref="apexChart"
            height="350"
            :options="chartOptions"
            :series="chartOptions.series"
          >
          </apexchart>
        </div>

        <!-- <v-sheet class="pa-5 d-flex flex-column align-center">
          <v-progress-circular
            :model-value="compressionRate"
            :rotate="-90"
            :size="150"
            :width="15"
            color="green"
          >
            <span class="text-h6">{{ compressionRate }}%</span>
          </v-progress-circular>
          <div class="mt-3 text-subtitle1">TAUX DE COMPRESSION</div>
        </v-sheet> -->
      </v-card>

      <v-snackbar
        :timeout="2000"
        v-model="state.snackbar"
        location="bottom right"
        :color="state.color"
      >
        {{ state.textAlert }}

        <template v-slot:actions> </template>
      </v-snackbar>
    </v-card>
  </v-container>
</template>

<script>
import { useI18n } from "vue-i18n";
import { ref, reactive, onMounted } from "vue";
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import VueApexCharts from "vue3-apexcharts";

export default {
  name: "DoubleMaskComponent",
  components: {
    apexchart: VueApexCharts,
  },

  setup() {

    const { t } = useI18n();
    
    onMounted(() => {
      getInfo();
    });

    const getInfo = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      axios
        .get("/double_mask/getstatus")
        .then((response) => {
          enabled.value = response.data.msg?.active;
          chartOptions.value.series = [response.data.msg?.ratio];
          actualRules.value = response.data.msg?.n_actuel;
          initialRules.value = response.data.msg?.n_init;
        })
        .catch((e) => {
        });
    };

    const changeStatus = (status) => {
      state.loading = true;
      state.isLoadingDialogue = true;

      axios
        .put(`/double_mask/${status}`)
        .then((response) => {
          if (response.status == "200") {
            state.snackbar = true;
            state.loading = false;
            state.isLoadingDialogue = false;
            state.color = "success";
            state.textAlert = response.data.msg;
            setTimeout(() => {
              location.reload();
            }, 1000);
          }
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
            state.textAlert = i.response.data.error;
          }
        });
    };

    const enabled = ref(false);
    const dialog = ref(false);
    const tempValue = ref(false);

    const confirmSwitch = () => {
      tempValue.value = !enabled.value;
      dialog.value = true;
    };

    const confirmEnable = () => {
      dialog.value = false;
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (enabled.value) {
        changeStatus("activate");
      } else {
        changeStatus("deactivate");
      }
    };

    const cancelSwitch = () => {
      dialog.value = false;
      enabled.value = tempValue.value;
    };

    const initialRules = ref(0);
    const actualRules = ref(0);
    const performanceGain = ref(0);
    const compressionRate = ref(90);
    const chartOptions = ref({
      series: [0],
      chart: {
        height: 350,
        type: "radialBar",
        offsetY: -10,
      },

      colors: ["#213E9F"],
      plotOptions: {
        radialBar: {
          startAngle: -135,
          endAngle: 135,
          dataLabels: {
            name: {
              fontSize: "16px",
              color: "#213E9F",
              offsetY: 120,
            },
            value: {
              offsetY: 76,
              fontSize: "22px",
              color: "#213E9F",
              formatter: function (val) {
                return val + "%";
              },
            },
          },
          track: {
            background: "#f2f2f2",
          },
          hollow: {
            size: "65%",
          },
        },
      },
      fill: {
        type: "gradient",
        gradient: {
          shade: "dark",
          shadeIntensity: 0.15,
          inverseColors: false,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100],
          colorStops: [
            {
              offset: 0,
              color: "#213E9F",
              opacity: 1,
            },
            {
              offset: 100,
              color: "#CC0000",
              opacity: 1,
            },
          ],
        },
      },
      stroke: {
        dashArray: 4,
        // lineCap: 'round'
      },
      labels: [t('doubleMask.ratio')],
    });

    const state = reactive({
      loading: false,
      isLoadingDialogue: false,
      snackbar: false,
      color: "",
      textAlert: "",
    });

    return {
      confirmEnable,
      cancelSwitch,
      confirmSwitch,
      state,
      tempValue,
      dialog,
      enabled,
      initialRules,
      actualRules,
      performanceGain,
      compressionRate,
      chartOptions,
    };
  },
};
</script>

<style scoped>
.text-subtitle1 {
  font-weight: bold;
}
</style>
