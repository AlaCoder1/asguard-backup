<template>
  <v-col cols="6">
    <v-card class="mx-auto">
      <v-card-item>
        <v-row>
          <v-col cols="7">
            <div class="title-card mb-2">{{$t('Clientsopenvpn.Capacity')}}</div>
            <span class="mb-1 soutitle" style="font-size: 17px"
              >{{$t('Clientsopenvpn.Transferred')}}</span
            >
            <h6 class="daysTitle">{{$t('Clientsopenvpn.Today')}}</h6>
          </v-col>
          <v-col class="mt-4" cols="5" align-self="center">
            <span class="numberTitle">{{ state.transferred }}</span>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="7">
            <span class="mb-1 soutitle" style="font-size: 17px">{{$t('Clientsopenvpn.Received')}}</span>
            <h6 class="daysTitle">{{$t('Clientsopenvpn.Today')}}</h6>
          </v-col>
          <v-col cols="5" align-self="center">
            <span class="mb-1 numberTitle">{{ state.recieved }}</span>
          </v-col>
        </v-row>
      </v-card-item>
    </v-card>
  </v-col>
  <v-col cols="6">
    <v-card class="mx-auto">
      <v-card-item>
        <div class="title-card mb-4">{{$t('Clientsopenvpn.Users')}}</div>
        <v-row class="mb-5 d-flex justify-center align-center">
          <v-col cols="6">
            <div class="text-h6 mb-1">
              <v-row>
                <v-col cols="2">
                  <v-progress-circular
                    :rotate="-180"
                    :size="40"
                    :width="2"
                    v-model="state.activeClient"
                    color="#086EAE"
                  >
                    {{ state.activeClient }}
                  </v-progress-circular>
                </v-col>
                <span class="subTitle"> {{$t('Clientsopenvpn.of')}} {{ state.allClient }}</span>
              </v-row>
            </div>
            <div class="text-caption">{{$t('Clientsopenvpn.ActiveUsers')}}</div>
          </v-col>
          <!-- <v-col cols="6">
            <div class="text-h6 mb-1">
              <v-row>
                <v-col cols="2">
                  <v-progress-circular
                    :rotate="-180"
                    :size="40"
                    :width="2"
                    v-model="state.activeClient"
                    color="#086EAE"
                  >
                    {{ state.activeClient }}
                  </v-progress-circular>
                </v-col>
                <span class="subTitle"> of {{ state.allClient }}</span>
              </v-row>
            </div>
            <div class="text-caption">Active Devices</div>
          </v-col> -->
        </v-row>
      </v-card-item>
    </v-card>
  </v-col>
</template>
<script>
import VueApexCharts from "vue3-apexcharts";
import { watch, ref, reactive, toRefs } from "vue";
export default {
  components: {
    apexchart: VueApexCharts,
  },
  props: {
    dataChart: {
      type: Object,
    },
  },
  setup(props) {
    const { dataChart } = toRefs(props);

    const state = reactive({
      transferred: "",
      recieved: "",
      activeClient: "",
    });

    watch(
      () => dataChart.value,
      (val) => {
        state.transferred =
          Math.round(val.capacity_client_out.capture_size) +
          ` ${val.capacity_client_out.unit}`;
        state.recieved =
          Math.round(val.capacity_client_in.capture_size) +
          ` ${val.capacity_client_in.unit}`;

        state.activeClient = val.client_active;
        state.allClient = val.all_client;
      }
    );

    return {
      state,
    };
  },
};
</script>
<style>
.subTitle {
  position: relative;
  left: 30px;
  display: flex;
  flex-wrap: wrap;
}
</style>
