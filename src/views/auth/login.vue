<template>
  <v-sheet class="bg-asguard_primary_light pa-12 h-screen" rounded>
    <v-card
      :elevation="0"
      class="bg-asguard_primary_light mx-auto px-6 py-8"
      max-width="500px"
    >
      <img src="../../assets/images/logo.svg" class="img-center mb-8 mt-15" />
      <v-form v-model="form" @submit.prevent="connect">
        <label for="" class="field-auth ml-9">User name</label>
        <v-text-field
          rounded
          v-model="username"
          label="Enter user name"
          variant="solo"
          required
          prepend-inner-icon="mdi-account-outline"
          density="compact"
          single-line
          hide-details
          class="mb-6 mt-3"
        ></v-text-field>
        <label for="" class="field-auth ml-9">Password</label>
        <v-text-field
          rounded
          v-model="password"
          :append-inner-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
          prepend-inner-icon="mdi-lock-outline"
          :type="show1 ? 'text' : 'password'"
          label="Enter password"
          density="compact"
          variant="solo"
          required
          single-line
          hide-details
          type="password"
          @click:append-inner="show1 = !show1"
          class="field-placeholder mb-6 mt-3"
        ></v-text-field>

        <br />

        <v-btn
          rounded
          :disabled="!form"
          color="asguard_primary_dark"
          class="d-flex mx-auto w-50"
          size="large"
          type="submit"
          variant="elevated"
        >
          <span class="field-login"> Login </span>
        </v-btn>
        <div class="text-center mt-6 text-asguard_secondary">
          Test User Login
        </div>
      </v-form>
    </v-card>
    <Footer />
  </v-sheet>
</template>

<script>
import { useAuthStore } from "../../store/modules/auth";
const storeAuth = useAuthStore();

import Footer from "../../layouts/TheFooter.vue";
// import { mapState } from "pinia";

export default {
  name: "HomeComponent",
  components: {
    Footer,
  },
  data() {
    return {
      users: "",
      show1: false,
      test: [],
      username: "",
      password: "",
      invalid: false,
      message: "",
    };
  },
  beforeMount: async function () {
    // this.users = this.$root.$data.tab;
  },
  computed: {
    // ...mapState(storeAuth, ["messageStore"]),
  },
  methods: {
    connect() {
      const user = {
        username: this.username,
        password: this.password,
      };

      storeAuth.login(user).then((response) => {
        this.invalid = true;
      });
    },
  },
};
</script>
