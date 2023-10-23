<template>
  <div class="centered-container">
    <v-row style="margin: 10%">
      <v-col cols="6">
        <img
          src="../../images/error-server-picture.svg"
          alt="error-server"
          width="100%"
          height="50%"
        />
      </v-col>
      <v-col cols="6">
        <h1 class="mb-3 title">404 NOT FOUND :(</h1>
        <p class="text" style="margin-top: 5px">Url Not Found.</p>
        <p class="text" style="margin-top: 10px">
          Sorry we couldn't find that page but don't worry you can find plenty
          of other things on our
          <span
            style="
              color: #f8b724;
              cursor: pointer;
              text-decoration-line: underline;
            "
            @click="navigateUrl"
            >homepage.</span
          >
        </p>

        <v-row style="margin-top: 5%">
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
                src="../../images/favAsguard.svg"
                alt="error-server"
                width="8%"
                height="10%"
                style="background: #193286"
              />
              <span
                style="
                  font-size: 16px;
                  font-family: 'Nunito';
                  font-weight: 400;
                  word-wrap: break-word;

                  padding-top: 5px;
                  padding-bottom: 5px;
                "
                >Redirect</span
              >
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <Footer />
  </div>
</template>

<script>
import { mapState, mapActions } from "pinia";

import { useAuthStore } from "@/store/modules/auth.js";
const storeAuth = useAuthStore();
import Footer from "@/components/layout/footer.vue";
export default {
  name: "BaseLayout",
  components: {
    Footer,
  },
  computed: {
    ...mapState(storeAuth, ["user"]),
  },
  mounted(){
    // let test = this.$el.attributes['users'] ? this.$el.attributes['users'].value : '';
    console.log('isd',document.getElementById('app').attributes['users'].value)
  },
  methods: {
    navigateUrl() {
      if (!this.user) {
        window.location.href = "/";
      } else {
        window.location.href = "/dashboard";
      }
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
