<template>
  <v-sheet class="bg-asguard_primary_light pa-12 h-screen" rounded>
    <v-card
      :elevation="0"
      class="bg-asguard_primary_light mx-auto px-6 py-8"
      max-width="500px"
    >
      <img src="../../assets/images/logo.svg" class="img-center mb-8 mt-15" />

      <v-form class="mt-5" @submit.prevent="connect" v-if="!isVerification">
        <label for="" class="field-auth ml-9">{{ $t("form.username") }}</label>
        <v-text-field
          rounded
          v-model="username"
          :placeholder="$t('placeholder.enterUserName')"
          variant="solo"
          required
          prepend-inner-icon="mdi-account-outline"
          density="compact"
          single-line
          hide-details
          class="mb-6 mt-3"
        ></v-text-field>
        <label for="" class="field-auth ml-9">{{ $t("form.password") }}</label>
        <v-text-field
          rounded
          v-model="password"
          :append-inner-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
          prepend-inner-icon="mdi-lock-outline"
          :type="show1 ? 'text' : 'password'"
          :placeholder="$t('placeholder.enterPassword')"
          density="compact"
          variant="solo"
          required
          single-line
          hide-details
          @click:append-inner="show1 = !show1"
          class="field-placeholder mb-6 mt-3"
        ></v-text-field>

        <br />

        <v-btn
          @click.prevent="connect"
          rounded
          color="asguard_primary_dark"
          class="d-flex mx-auto w-50"
          size="large"
          type="submit"
          variant="elevated"
        >
          <span class="field-login"> {{ $t("buttons.login") }} </span>
        </v-btn>
      </v-form>
    </v-card>

    <v-card
      class="py-8 px-6 text-center mx-auto mt-n6"
      elevation="12"
      max-width="400"
      width="100%"
      v-if="isVerification"
    >
      <h3 class="text-h6 mb-4">{{ $t("login.verifyYourAccount") }}</h3>

      <div class="text-body-2">
        {{ $t("login.send") }} {{ mail }} <br />

        {{ $t("login.pleaseMail") }}
      </div>

      <v-sheet color="surface">
        <v-otp-input v-model="otp" type="text" variant="solo"></v-otp-input>
      </v-sheet>

      <v-btn
        class="my-4 text-white"
        color="#FFC300"
        height="40"
        :text="$t('login.verify')"
        variant="flat"
        width="70%"
        @click="verifyOtp"
      ></v-btn>

      <div class="text-caption">
        {{ $t("login.receiveCode") }}
        <a href="#" @click.prevent="resendOtp">{{ $t("login.resend") }}</a>
      </div>
    </v-card>
    <div class="text-center mt-6 text-asguard_secondary" v-if="message">
      {{ message }}
    </div>
    <Footer />
  </v-sheet>
</template>

<script>
import "vuetify/styles";
import axios from "axios";
import Footer from "../../layouts/TheFooter.vue";
import { getCookie } from "@/mixins/csrftoken.js";

export default {
  name: "HomeComponent",
  components: {
    Footer,
  },

  data() {
    return {
      lang: "en",
      users: "",
      show1: false,
      username: "",
      password: "",
      invalid: false,
      message: "",
      //
      otp: "",
      mail: "",
      idUser: "",
      isVerification: false,
      last_Subscription: [],
    };
  },
  mounted() {
    const csrfToken = getCookie("csrftoken");
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios
      .get("/subscription/list_features_about_last_subscription")
      .then((response) => {
        this.last_Subscription = response.data.list_features;
      });
  },
  methods: {
    changeLang(item) {
      this.$i18n.locale = item;
    },
    async connect() {
      const user = {
        username: this.username,
        password: this.password,
      };

      await axios
        .post("/auth/authentification", user)
        .then((response) => {
          localStorage.setItem("user-info", JSON.stringify(response.data));

          this.message = response.data.message;
          if (response.data?.currentUser?.is_enable_2FA) {
            this.isVerification = true;
            this.mail = response.data?.currentUser?.email;
            this.idUser = response.data?.currentUser?.id;
          } else {
            let hrefPath =
              this.last_Subscription.length > 0
                ? localStorage.getItem("href-path") ?? "/dashboard"
                : "/asguard/license";
            window.location.href = hrefPath;
          }

          setTimeout(() => {
            this.message = "";
          }, 1000);
        })
        .catch((error) => {
          localStorage.setItem(
            "response-info",
            JSON.stringify(error.response.data)
          );
          this.message = error.response.data.message;
          setTimeout(() => {
            this.message = "";
          }, 3000);
        });
    },

    async resendOtp() {
      this.otp = "";

      await axios
        .post(`/auth/resend_verification_code/${this.idUser}`)
        .then((response) => {

          this.message = response.data.message;

          setTimeout(() => {
            this.message = "";
          }, 1000);
        })
        .catch((error) => {
          this.message = error.response.data.message;
          setTimeout(() => {
            this.message = "";
          }, 2000);
        });
    },
    async verifyOtp() {
      let payload = {
        verification_code: this.otp,
      };

      await axios
        .post(`/auth/verify_code/${this.idUser}`, payload)
        .then((response) => {
          if (response.status == "200") {
            this.message = response.data.message;
            setTimeout(() => {
              let hrefPath = localStorage.getItem("href-path") ?? "/dashboard";
              window.location.href = hrefPath;
            }, 1000);
          } else {
            this.message = response.data.message;
          }

          setTimeout(() => {
            this.message = "";
          }, 1000);
        })
        .catch((error) => {
          this.message = error.response.data.message;
          setTimeout(() => {
            this.message = "";
          }, 2000);
        });
    },
  },
};
</script>
