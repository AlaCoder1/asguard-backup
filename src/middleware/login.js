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
import axios from 'axios'

const app = createApp(login);
const vuetifyComponents = createVuetify({
    components,
    directives
  })

 
  axios.interceptors.response.use(
    (response) => {
      
      console.log('response000.login',response)
      return response;
    },
    (error) => {
      console.log('errorMainlogin',error)
      
      if ((error.response.status === 401 )||(error.response.status === 403)) {
     
        console.log('Token expired or unauthorized. Redirecting to login.');
        window.location.href = '/';
      }
      return Promise.reject(error);
    }
  );

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
