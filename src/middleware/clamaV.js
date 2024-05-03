import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import mitt from 'mitt'
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import clamaV from "../views/clamaV/index.vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import { startTimer } from "../mixins/timer_token.js";

import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";

const app = createApp(clamaV);
const vuetify = createVuetify({
  components,
  directives,
});
const emitter = mitt()
app.provide('emitter', emitter)
let lang = localStorage.getItem("lang");
if (lang) {
  var langLocle = JSON.parse(lang);
}

const i18n = new createI18n({
  legacy: false,
  locale: langLocle ? langLocle[0].lang.toLowerCase() : "en",
  messages: {
    en: enJson,
    fr: frJson,
  },
});



const currentPath = window.location.pathname;
function hrefPath(){
  localStorage.setItem('href-path', currentPath)
}

hrefPath()
startTimer();

app.use(ElementPlus).use(store).use(vuetify).use(i18n).mount("#app");
