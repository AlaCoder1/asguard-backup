<template>
  <div
    class="bg-asguard_primary_light"
    style="width: 1920, height: 1080, secondary: '#213E9F'"
    justify="center"
  >
  
    <v-row align="center" justify="center" style="justify-content: center">
      <v-col cols="16" sm="7" md="5" class="text-center pos" justify="center">
        <img
          src="../../assets/images/logo.svg"
          height="100"
          width="100"
          class="img-center"
        />
        <div class="mt-5">
          <v-form @submit.prevent="connect">
            <div
              style="
                color: white;
                font-size: 16px;
                font-family: 'Nunito';
                font-weight: 400;
                word-wrap: break-word;
                margin-top: 51px;
                margin-left: 10%;
              "
            >
              User name
            </div>
            <v-text-field
              rounded
              v-model="username"
              label="Enter user name"
              required
              class="input-w"
              style="margin-bottom: 11.5px"
            ></v-text-field>
            <div
              style="
                color: white;
                font-size: 16px;
                font-family: 'Nunito';
                font-weight: 400;
                word-wrap: break-word;
                margin-top: 51px;
                margin-left: 10%;
              "
            >
              Password
            </div>
            <v-text-field
              rounded
              v-model="password"
              label="Enter password"
              required
              type="password"
              style="margin-bottom: 11.5px"
              class="input-w"
            ></v-text-field>
            <div
              rounded
              style="
                width: 188px;
                height: 43px;
                background: #213e9f;
                margin-top: 74px;
                margin-left: 39%;
                justify-content: center;
              "
            >
              <v-btn
                rounded
                type="submit"
                style="
                  justify-content: center;

                  width: 100%;
                  height: 100%;
                  background: #193286;
                  color: white;
                "
              >
                <span
                  style="
                    font-size: 16px;
                    font-family: 'Nunito';
                    font-weight: 400;
                    word-wrap: break-word;
                  "
                  >Login</span
                >
              </v-btn>
            </div>
            <div
              style="
                color: #ffc300;
                font-size: 20px;
                font-family: 'Nunito';
                font-weight: 400;
                word-wrap: break-word;
                justify-content: center;
                margin-top: 5%;
                margin-left: 11px;
              "
              align="center"
              justify="center"
              v-if="invalid"
            >
              <!-- {{ messageStore }} -->
            </div>
          </v-form>
        </div>
      </v-col>
    </v-row>
    <Footer />
  </div>
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
<style scoped>
.main-content {
  margin-top: 80px;
  margin-bottom: 80px;
}

.dms-login-container {
  margin-top: 357px;
}

.img-center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 33%;
  height: 33%;
}

.input-w {
  background-color: white;
}
</style>
