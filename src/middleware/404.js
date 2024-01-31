import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import error from "../views/404.vue";

const app = createApp(error);
const vuetify = createVuetify({
  components,
  directives,
});

app.use(store).use(vuetify).mount("#app");
