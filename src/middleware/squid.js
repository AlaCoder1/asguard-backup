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

app.use(ElementPlus).use(store).use(vuetify).mount("#app");
