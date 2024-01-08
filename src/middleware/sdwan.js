import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import mitt from 'mitt'
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import sdwan from "../views/sdwan/index.vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import axios from "axios";
const app = createApp(sdwan);
const vuetify = createVuetify({
  components,
  directives,
});
const emitter = mitt()
app.provide('emitter', emitter)

axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401 || error.response.status === 403) {
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

app.use(ElementPlus).use(store).use(vuetify).mount("#app");
