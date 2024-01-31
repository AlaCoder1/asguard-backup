import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import keyPair from "../views/keyPair/index.vue";
import { startTimer } from "../mixins/timer_token.js";

import mitt from "mitt";

const emitter = mitt();

const app = createApp(keyPair);
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

app.use(store).use(vuetify).mount("#app");
