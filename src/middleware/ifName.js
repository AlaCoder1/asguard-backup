import {createApp } from 'vue';
import store from '../store/index.js'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import ifName from '../views/network/ifName.vue';
import axios from 'axios'
const app = createApp(ifName);
const vuetify = createVuetify({
    components,
    directives
  })

  axios.interceptors.response.use(
    (response) => {
      
      console.log('response000.frame',response)
      return response;
    },
    (error) => {
      console.log('errorMainframe',error)
      
      if ((error.response.status === 401 )||(error.response.status === 403)) {
     
        console.log('Token expired or unauthorized. Redirecting to login.');
        window.location.href = '/';
      }
      return Promise.reject(error);
    }
  );

app
.use(store)
.use(vuetify)
.mount('#app');
