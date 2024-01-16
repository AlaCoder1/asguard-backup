import { createApp } from "vue";
import vuetify from "@/plugins/vuetify";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import login from "../views/auth/login.vue";

import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import axios from "axios";

const app = createApp(login);
const vuetifyComponents = createVuetify({
  components,
  directives,
});

axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401 || error.response.status === 403) {
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

const i18n = new createI18n({
  locale: "en",
  messages: {
    en: enJson,
    fr: frJson,
  },
});
// function getCookie(name) {
//   let cookieValue = null;
//   if (document.cookie && document.cookie !== "") {
//     const cookies = document.cookie.split(";");
//     for (let i = 0; i < cookies.length; i++) {
//       const cookie = cookies[i].trim();
//       if (cookie.substring(0, name.length + 1) === name + "=") {
//         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//         break;
//       }
//     }
//   }
//   return cookieValue;
// }

// const csrfToken = getCookie("csrftoken");
// const currentPathHref = window.location.href;
// var url = currentPathHref;
// var substring = "?next=/asguard/subscription/";

// if (url.includes(substring) && csrfToken) {
//   // window.location.href = "/asguard/subscription/";
// } else {
//   console.log("not found.");
// }

app.use(store).use(vuetifyComponents).use(vuetify).use(i18n).mount("#app");
