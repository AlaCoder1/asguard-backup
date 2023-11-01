import {createApp } from 'vue';
import vuetify from '@/plugins/vuetify';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import login from '../views/auth/login.vue';

import { createI18n } from 'vue-i18n';
import enJson from '../locales/en.json'; 
import frJson from '../locales/fr.json';


const app = createApp(login);
const vuetifyComponents = createVuetify({
    components,
    directives
  })

  const i18n = new createI18n({
  locale: 'en',
  messages: {
    en: enJson, 
    fr: frJson, 
  },
});

app
.use(store)
.use(vuetifyComponents)
.use(vuetify)
.use(i18n)
.mount('#app');
