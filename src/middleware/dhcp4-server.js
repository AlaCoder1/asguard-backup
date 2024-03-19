import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import mitt from "mitt";
import Dhcp4Server from "../views/dhcp4_server/Dhcp4Server";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";

const emitter = mitt();

const app = createApp(Dhcp4Server);

app.provide("emitter", emitter);

const vuetify = createVuetify({
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

const currentPath = window.location.pathname;
function hrefPath() {
  localStorage.setItem("href-path", currentPath);
}

hrefPath();
startTimer();

app.use(store).use(vuetify).use(i18n).mount("#app");