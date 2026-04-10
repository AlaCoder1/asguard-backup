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
import mitt from "mitt";
import { get_lang } from "../mixins/storage_language.js";

const emitter = mitt();

const app = createApp(home);
const vuetify = createVuetify({
  components,
  directives,
});
app.provide("emitter", emitter);

const currentPath = window.location.pathname;
function hrefPath() {
  localStorage.setItem("href-path", currentPath);
}

hrefPath();
startTimer();

(async () => {
  const locale = await get_lang();

  const i18n = new createI18n({
    legacy: false,
    locale,
    messages: {
      en: enJson,
      fr: frJson,
    },
  });

  app.use(store).use(VueApexCharts).use(i18n).use(vuetify).mount("#app");
})();
