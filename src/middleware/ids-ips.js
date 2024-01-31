import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import mitt from "mitt";
import IdsIps from "../views/ids_ips/IdsIps";
import { startTimer } from "../mixins/timer_token.js";

const emitter = mitt();

const app = createApp(IdsIps);

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

app.use(store).use(vuetify).mount("#app");
