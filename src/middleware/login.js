import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import vuetify from "@/plugins/vuetify";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import login from "../views/auth/login.vue";

import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";

import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";

const csrfToken = getCookie("csrftoken");
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
const app = createApp(login);
const vuetifyComponents = createVuetify({
  components,
  directives,
});

async function get_lang() {
  let lang = null;
  try {
    let res = await axios.get(`/settings/getLanguage`);
    lang = res.data.language;
    return lang;
  } catch (error) {
    console.error(error);
  }
}
get_lang();

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

  app.use(store).use(i18n).use(vuetifyComponents).use(vuetify).mount("#app");
})();
