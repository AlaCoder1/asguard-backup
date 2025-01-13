import { createApp } from "vue";
import store from "../store/index.js";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import success from "../views/success.vue";
import { createI18n } from "vue-i18n";
import enJson from "../locales/en.json";
import frJson from "../locales/fr.json";
import { get_lang } from '../mixins/storage_language.js';

const app = createApp(success);
const vuetify = createVuetify({
  components,
  directives,
});


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

  app.use(store).use(i18n).use(vuetify).mount('#app');
})();
