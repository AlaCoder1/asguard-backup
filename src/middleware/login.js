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

const app = createApp(login);
const vuetifyComponents = createVuetify({
  components,
  directives,
});

let lang = localStorage.getItem("lang");
if (lang) {
  var langLocle = JSON.parse(lang);
}
const i18n = new createI18n({
  legacy: false,
  locale: langLocle ? langLocle[0].lang.toLowerCase() : "en",
  // locale: "en",
  messages: {
    en: enJson,
    fr: frJson,
  },
});

app.use(store).use(vuetifyComponents).use(vuetify).use(i18n).mount("#app");
