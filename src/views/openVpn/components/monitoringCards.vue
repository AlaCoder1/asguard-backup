<template>
  <v-col cols="4">
    <v-card class="mx-auto">
      <v-card-item>
        <v-row>
          <v-col cols="7">
            <div class="title-card mb-2">Capacity</div>
            <span class="mb-1 soutitle">Transferred</span>
            <h6 class="daysTitle">Today</h6>
          </v-col>
          <v-col class="mt-4" cols="5" align-self="center">
            <span  class="numberTitle">2.23 GB</span>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="7">
            <span class="mb-1 soutitle">Recieved</span>
            <h6 class="daysTitle">Today</h6>
          </v-col>
          <v-col cols="5" align-self="center">
            <span class="mb-1 numberTitle">2.23 GB</span>
          </v-col>
        </v-row>
      </v-card-item>
    </v-card>
  </v-col>
  <v-col cols="5">
    <v-card class="mx-auto">
      <v-card-item>
        <div class="title-card mb-6">Users</div>
        <v-row>
          <v-col cols="6">
            <div class="text-h6 mb-1">
              <v-row>
                <v-col cols="2">
                  <v-progress-circular
                    :rotate="-180"
                    :size="40"
                    :width="2"
                    :model-value="50"
                    color="#086EAE"
                  >
                    50
                  </v-progress-circular>
                </v-col>
                <span class="subTitle"> of 100</span>
              </v-row>
            </div>
            <div class="text-caption">Active Users</div>
          </v-col>
          <v-col cols="6">
            <div class="text-h6 mb-1">
              <v-row>
                <v-col cols="2">
                  <v-progress-circular
                    :rotate="-180"
                    :size="40"
                    :width="2"
                    :model-value="25"
                    color="#086EAE"
                  >
                    25
                  </v-progress-circular>
                </v-col>
                <span class="subTitle"> of 100</span>
              </v-row>
            </div>
            <div class="text-caption">Active Devices</div>
          </v-col>
        </v-row>
      </v-card-item>
    </v-card>
  </v-col>
  <v-col cols="3">
    <v-card class="mx-auto">
      <v-card-item>
        <div>
          <div class="mb-3 title-card">Traffic distribution</div>
          <div class="text-caption">client1</div>
          <div class="text-caption">client2</div>
          <div class="text-caption">client3</div>
          <div class="text-caption">client4</div>
        </div>
      </v-card-item>
    </v-card>
  </v-col>
</template>
<script>
export default {
  data() {
    return {};
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
