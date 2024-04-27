<template>
  <v-container fluid width="100%">
    <v-row>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="150"
          height="100%"
          hover
        >
          <v-card-item>
            <div class="title-card mb-6">{{$t('monitoringVPN.ResponseTime')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <v-row>
              <v-col cols="6">
                <div>1ms</div>
              </v-col>
              <v-col cols="6">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="45"
                  height="53"
                  viewBox="0 0 45 53"
                  fill="none"
                >
                  <mask
                    id="mask0_801_746"
                    style="mask-type: luminance"
                    maskUnits="userSpaceOnUse"
                    x="0"
                    y="0"
                    width="45"
                    height="53"
                  >
                    <path
                      d="M44.841 0.347656H0V52.1257H44.841V0.347656Z"
                      fill="white"
                    />
                  </mask>
                  <g mask="url(#mask0_801_746)">
                    <path
                      d="M36.718 12.6812L39.818 9.09919L43.163 12.7102L40.042 16.0842C42.2118 18.8177 43.7051 22.0253 44.4002 25.4454C45.0953 28.8655 44.9726 32.4015 44.042 35.7652C42.7105 40.8767 39.5484 45.3214 35.156 48.2552C25.819 54.7952 13.003 52.6792 5.61396 44.6682C2.06677 40.7034 0.0725661 35.5899 -0.000944691 30.2705C-0.0744555 24.9511 1.77768 19.7844 5.21396 15.7232C11.709 8.09519 24.75 3.89219 36.714 12.6812M20.347 32.3472H25.029V17.7922H20.347V32.3472Z"
                      fill="#213E9F"
                    />
                    <path
                      d="M29.7899 0.347656H15.5089V4.94866H29.7899V0.347656Z"
                      fill="#213E9F"
                    />
                  </g>
                </svg>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="150"
          height="100%"
          hover
        >
          <v-card-item>
            <div class="title-card mb-6">{{$t('monitoringVPN.Availablity')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <v-row>
              <v-col cols="6">
                <div>76%</div>
              </v-col>
              <v-col cols="6">
                <v-progress-circular
                  :size="60"
                  :width="2"
                  :model-value="76"
                  color="#086EAE"
                >
                  <div>{{ 76 }}%</div>
                </v-progress-circular>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="150"
          height="100%"
          hover
        >
          <v-card-item>
            <div class="title-card mb-6">{{$t('monitoringVPN.PacketLoss')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <v-row>
              <v-col cols="6">
                <div>1%</div>
              </v-col>
              <v-col cols="6">
                <v-progress-circular
                  :size="60"
                  :width="2"
                  :model-value="1"
                  color="#086EAE"
                >
                  <div>{{ 1 }}%</div>
                </v-progress-circular>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="200"
          height="100%"
          hover
        >
          <v-card-item>
            <div class="title-card mb-6">{{$t('monitoringVPN.ActiveSessions')}}</div>
          </v-card-item>
          <v-card-text class="content-style">
            <v-row>
              <div class="center-item">138</div>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="200"
          height="100%"
          hover
          color="indigo-darken-3"
          text-color="white"
        >
          <v-card-item>
            <div class="title-card-light mb-6">{{$t('monitoringVPN.ActiveSSLTunnels')}}</div>
          </v-card-item>
          <v-card-text class="content-style-light">
            <v-row>
              <div class="center-item">71</div>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          class="mx-auto"
          max-width="344"
          min-width="200"
          height="100%"
          hover
          color="indigo-darken-3"
          text-color="white"
        >
          <v-card-item>
            <div class="title-card-light center-item mb-6">
              {{ currentTime }} GMT
            </div>
          </v-card-item>
          <v-card-text>
            <v-row>
              <div class="center-item">{{ formattedDate }}</div>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
import { ref } from "vue";

const currentTime = ref("");
const formattedDate = ref("");

const getCurrentTime = () => {
  const date = new Date();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  currentTime.value = `${hours}:${minutes}`;
};
const getCurrentDate = () => {
  const date = new Date();
  const day = date.getDate();
  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const monthIndex = date.getMonth();
  const year = date.getFullYear();
  const month = monthNames[monthIndex];
  formattedDate.value = `${day} ${month} ${year}`;
};

getCurrentTime();
getCurrentDate();

setInterval(() => {
  getCurrentTime();
  getCurrentDate();
}, 1000);
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
  font-size: 18px;
  font-style: normal;
  font-weight: 800;
  line-height: normal;
  justify-content: center;
}

.content-style-light {
  color: #fff;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 800;
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
</style>
