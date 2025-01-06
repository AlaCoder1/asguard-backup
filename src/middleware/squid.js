import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import mitt from "mitt";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import squid from "../views/squid/index.vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import "dayjs/locale/fr";
import fr from "element-plus/es/locale/lang/fr";
import en from "element-plus/es/locale/lang/en";
import { get_lang } from "../mixins/storage_language.js";

const app = createApp(squid);
const vuetify = createVuetify({
  components,
  directives,
});

const emitter = mitt();
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

  app
    .use(store)
    .use(ElementPlus, {
      locale: locale ? (locale === "fr" ? fr : en) : en,
    })
    .use(i18n)
    .use(vuetify)
    .mount("#app");
})();
