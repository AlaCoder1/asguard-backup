import axios from 'axios'
import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import UserManagement from '../views/system/user/UserAndCertificateManagement';

const app = createApp(UserManagement);
const vuetify = createVuetify({
    components,
    directives
  })
  
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      
      if ((error.response.status === 401 )||(error.response.status === 403)) {
        window.location.href = '/';
      }
      return Promise.reject(error);
    }
  );

app
.use(store)
.use(vuetify)
.mount('#app');