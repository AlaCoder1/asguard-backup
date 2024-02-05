import { createApp } from "vue";
import store from "../store/index.js";
import VueApexCharts from "vue3-apexcharts";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import home from "../views/dashboard/dashboard.vue";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";

const app = createApp(home);
const vuetify = createVuetify({
  components,
  directives,
});

const i18n = new createI18n({
  locale: "en",
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
app.use(VueApexCharts).use(store).use(vuetify).use(i18n).mount("#app");
