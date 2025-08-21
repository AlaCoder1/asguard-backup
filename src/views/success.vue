<template>
  <div class="centered-container">
    <v-row style="margin: 10%">
      <v-col cols="6">
        <v-img
          class="mt-5"
          :width="500"
          aspect-ratio="16/9"
          cover
          src="https://www.numeryx.fr/wp-content/themes/numeryx/assets/images/bg-Asguard.jpg"
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
import axios from "axios";
import Footer from "../layouts/TheFooter.vue";
export default {
  name: "Success",
  components: {
    Footer,
  },
  mounted() {
    const searchParams = new URLSearchParams(window.location.search);

    let subId = searchParams.get("subscription_id");

    const csrfToken = this.getCookie("csrftoken");
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    if (subId) {
      let payload = {
        status: true,
        subscription_id: +subId,
      };

      axios
        .post("/subscription/payment", payload)
        .then((response) => {
          if (response.status == 200) {
            setTimeout(() => {
              window.location.href = "/dashboard/";
            }, 3000);
          }
        })
        .catch((i) => {});
    }
  },

  methods: {
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
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
