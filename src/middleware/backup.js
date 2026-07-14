import '../assets/scss/backup.scss';
import '../assets/scss/backup-monitoring.scss';
import { createApp } from "vue";
import { createI18n } from "vue-i18n";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import Backup from "../views/backup/index.vue";
import { startTimer } from "../mixins/timer_token.js";
import { get_lang } from "../mixins/storage_language.js";
import mitt from "mitt";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import { checkFunctionality } from "@/mixins/checkFunctionality.js";

const emitter = mitt();

const app = createApp(Backup);
const vuetify = createVuetify({
  components,
  directives,
});

app.provide("emitter", emitter);

const currentPath = window.location.pathname;
localStorage.setItem("href-path", currentPath);

startTimer();
checkFunctionality();

(async () => {
  const locale = await get_lang();

  const i18n = createI18n({
    legacy: false,
    locale,
    messages: {
      en: enJson,
      fr: frJson,
    },
  });

  app.use(store).use(i18n).use(vuetify).mount("#app");
})();