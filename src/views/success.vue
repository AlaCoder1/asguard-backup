<template>
  <div class="centered-container">
    <v-row style="margin: 10%">
      <v-col cols="6">
        <v-img
          class="mt-5"
          :width="500"
          aspect-ratio="16/9"
          cover
          src="https://www.numeryx.fr/sites/default/files/gallery/ASGUARD%20bannirere%20site.png"
        ></v-img>
      </v-col>
      <v-col cols="6" class="mt-6">
        <h1 class="mb-3 title">Success :)</h1>
        <p class="text" style="margin-top: 5px">Success Payment.</p>
        <p class="text" style="margin-top: 10px">
          Success! Your payment has been processed and confirmed. Thank you for
          your purchase.
        </p>

        <!-- <v-row style="margin-top: 5%">
          <v-col cols="8">
            <p class="smallText">Redirect To Dashboard Page.</p>
          </v-col>
          <v-col cols="4">
            <v-btn
              rounded
              type="submit"
              style="background: #193286; color: white; margin-bottom: 5px"
              @click="navigateUrl"
            >
              <img
                src="../assets/images/favAsguard.svg"
                alt="error-server"
                width="8%"
                height="10%"
                style="background: #193286"
              />
              Redirect
            </v-btn>
          </v-col>
        </v-row> -->
      </v-col>
    </v-row>
    <Footer />
  </div>
</template>

<script>
import Footer from "../layouts/TheFooter.vue";
export default {
  name: "Success",
  components: {
    Footer,
  },
  mounted() {
    setTimeout(() => {
      window.location.href = "/dashboard/";
    }, 3000);
  },
  methods: {
    // navigateUrl() {
    //   window.location.href = "/dashboard/";
    // },
  },
};
</script>
<style>
.centered-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin-right: 11%;
}
.title {
  color: #193286;
  font-family: Nunito;
  font-style: normal;
  font-weight: 900;
  line-height: normal;
  letter-spacing: 2.88px;
  margin-bottom: 15px;
}
.text {
  color: #193286;
  text-align: justify;
  font-family: Nunito;
  font-size: 16px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}
.smallText {
  color: #f8b724;
  text-align: justify;
  font-family: Nunito;
  font-size: 16px;
  font-style: normal;
  font-weight: 400;
  margin-top: 10px;
  line-height: normal;
}
</style>
