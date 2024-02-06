import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import UserManagement from "../views/system/user/UserAndCertificateManagement";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import mitt from "mitt";

const emitter = mitt();

const app = createApp(UserManagement);
const vuetify = createVuetify({
  components,
  directives,
});
app.provide("emitter", emitter);

console.log("emitter", emitter);
let lang = localStorage.getItem("lang");
if (lang) {
  var langLocle = JSON.parse(lang);
}

const i18n = new createI18n({
  // locale: "fr",
  locale: langLocle ? langLocle[0].lang.toLowerCase() : "en",
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
