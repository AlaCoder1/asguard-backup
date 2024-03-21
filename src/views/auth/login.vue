<template>
  <!--   
  <v-select
    v-model="lang"
      label="Select"
      :items="['en', 'fr']"
    ></v-select> -->

  <v-sheet class="bg-asguard_primary_light pa-12 h-screen" rounded>
    <v-card
      :elevation="0"
      class="bg-asguard_primary_light mx-auto px-6 py-8"
      max-width="500px"
    >
      <img src="../../assets/images/logo.svg" class="img-center mb-8 mt-15" />

      <!-- <v-btn @click="changeLang('en')" class="ml-9"> english </v-btn>
      <v-btn @click="changeLang('fr')" class="ml-5"> frensh </v-btn> -->

      <v-form v-model="form" class="mt-5" @submit.prevent="connect">
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
          :disabled="!form"
          color="asguard_primary_dark"
          class="d-flex mx-auto w-50"
          size="large"
          type="submit"
          variant="elevated"
        >
          <span class="field-login"> {{ $t("buttons.login") }} </span>
        </v-btn>
        <div class="text-center mt-6 text-asguard_secondary" v-if="message">
          {{ message }}
        </div>
      </v-form>
    </v-card>
    <Footer />
  </v-sheet>
</template>

<script>
import "vuetify/styles";
import axios from "axios";

import Footer from "../../layouts/TheFooter.vue";

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
    };
  },
  mounted() {
    // let error = localStorage.getItem("response-info");
    // if (error) {
    //   let response = JSON.parse(error);
    //   this.message = response.message;
    //   setTimeout(() => {
    //     localStorage.removeItem("response-info");
    //     this.message = "";
    //   }, 1000);
    // }
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
          setTimeout(() => {
            this.message = "";
          }, 1000);
          let hrefPath = localStorage.getItem("href-path") ?? "/dashboard";
          window.location.href = hrefPath;
        })
        .catch((error) => {
          localStorage.setItem(
            "response-info",
            JSON.stringify(error.response.data)
          );
          this.message = error.response.data.message;
          setTimeout(() => {
            this.message = "";
          }, 1000);
        });
    },
  },
};
</script>
