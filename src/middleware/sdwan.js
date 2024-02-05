import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import mitt from "mitt";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import sdwan from "../views/sdwan/index.vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import { startTimer } from "../mixins/timer_token.js";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
const app = createApp(sdwan);
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
const emitter = mitt();
app.provide("emitter", emitter);

const currentPath = window.location.pathname;
function hrefPath() {
  localStorage.setItem("href-path", currentPath);
}

hrefPath();
startTimer();

app.use(ElementPlus).use(store).use(i18n).use(vuetify).mount("#app");
