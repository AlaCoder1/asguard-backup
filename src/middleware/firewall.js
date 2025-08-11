import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import firewall from "../views/firewall/firewall.vue";
import mitt from "mitt";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import { get_lang } from '../mixins/storage_language.js';
import { checkFunctionality } from "@/mixins/checkFunctionality.js";

const app = createApp(firewall);

const emitter = mitt();
app.provide("emitter", emitter);

const vuetify = createVuetify({
  components,
  directives,
});

const currentPath = window.location.pathname;
function hrefPath() {
  localStorage.setItem("href-path", currentPath);
}

hrefPath();
startTimer();
checkFunctionality();

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

  app.use(store).use(i18n).use(vuetify).mount('#app');
})();